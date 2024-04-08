import asyncio
import copy
import json
import os
import time
from typing import Union

from authlib.integrations.requests_client import OAuth2Session
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi_versionizer.versionizer import api_version, versionize
from jinja2 import Template
from starlette.config import Config
from starlette.requests import Request
from starlette.responses import JSONResponse

from ska_src_compute_api import models
from ska_src_compute_api.common.constants import Constants
from ska_src_compute_api.common.exceptions import handle_exceptions, PermissionDenied
from ska_src_compute_api.common.utility import (
    convert_readme_to_html_docs,
    get_api_server_url_from_request,
    get_base_url_from_request,
    get_url_for_app_from_request,
)
from ska_src_permissions_api.client.permissions import PermissionsClient
from response_example import (
    query_resources,
    provision_resources,
    submit_job,
    job_status,
)

from sqlalchemy.orm import Session
from ska_src_compute_api.database.database import SessionLocal

config = Config(".env")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Debug mode (runs unauthenticated)
#
DEBUG = True if config.get("DISABLE_AUTHENTICATION", default=None) == "yes" else False


# Instantiate FastAPI() allowing CORS. Static mounts must be added later after the versionize() call.
#

app = FastAPI()
CORSMiddleware_params = {
    "allow_origins": ["*"],
    "allow_credentials": True,
    "allow_methods": ["*"],
    "allow_headers": ["*"],
}
app.add_middleware(CORSMiddleware, **CORSMiddleware_params)

# Add HTTPBearer authz.
#
security = HTTPBearer()

# Instantiate an OAuth2 request session for the ska_src_compute_api client.
#
API_IAM_CLIENT = OAuth2Session(
    config.get("API_IAM_CLIENT_ID"),
    config.get("API_IAM_CLIENT_SECRET"),
    scope=config.get("API_IAM_CLIENT_SCOPES", default=""),
)

# Get instance of Constants.
#
CONSTANTS = Constants(client_conf_url=config.get("IAM_CLIENT_CONF_URL"))

# Get templates.
#
TEMPLATES = Jinja2Templates(directory="templates")

# Instantiate the permissions client.
#
PERMISSIONS = PermissionsClient(config.get("PERMISSIONS_API_URL"))
PERMISSIONS_SERVICE_NAME = config.get("PERMISSIONS_SERVICE_NAME")
PERMISSIONS_SERVICE_VERSION = config.get("PERMISSIONS_SERVICE_VERSION")

# Store service start time.
#
SERVICE_START_TIME = time.time()

# Keep track of number of managed requests.
#
REQUESTS_COUNTER = 0
REQUESTS_COUNTER_LOCK = asyncio.Lock()


# Dependencies.
# -------------
#
# Increment the request counter.
#
@handle_exceptions
async def increment_request_counter(request: Request) -> Union[dict, HTTPException]:
    global REQUESTS_COUNTER
    async with REQUESTS_COUNTER_LOCK:
        REQUESTS_COUNTER += 1


# Check service route permissions from user token groups.
#
@handle_exceptions
async def verify_permission_for_service_route(
    request: Request, authorization: str = Depends(security)
) -> Union[HTTPException, bool]:
    if authorization.credentials is None:
        raise PermissionDenied
    access_token = authorization.credentials
    rtn = PERMISSIONS.authorise_route_for_service(
        service=PERMISSIONS_SERVICE_NAME,
        version=PERMISSIONS_SERVICE_VERSION,
        route=request.scope["route"].path,
        method=request.method,
        token=access_token,
        body=request.path_params,
    ).json()
    if rtn.get("is_authorised", False):
        return
    raise PermissionDenied


# Check service route permissions from user token groups (taking token from query parameters).
#
@handle_exceptions
async def verify_permission_for_service_route_query_params(
    request: Request, token: str = None
) -> Union[HTTPException, bool]:
    if token is None:
        raise PermissionDenied
    rtn = PERMISSIONS.authorise_route_for_service(
        service=PERMISSIONS_SERVICE_NAME,
        version=PERMISSIONS_SERVICE_VERSION,
        route=request.scope["route"].path,
        method=request.method,
        token=token,
        body=request.path_params,
    ).json()
    if rtn.get("is_authorised", False):
        return
    raise PermissionDenied


# Routes
# ------
#
@api_version(1)
@app.get(
    "/www/docs/oper",
    include_in_schema=False,
    dependencies=[Depends(increment_request_counter)]
    if DEBUG
    else [Depends(increment_request_counter)],
)
@handle_exceptions
async def oper_docs(request: Request) -> TEMPLATES.TemplateResponse:
    # Read and parse README.md, omitting excluded sections.
    if not DEBUG:
        readme_text_md = os.environ.get("README_MD", "")
    else:
        with open("../../../README.md") as f:
            readme_text_md = f.read()
    readme_text_html = convert_readme_to_html_docs(
        readme_text_md,
        exclude_sections=["Development", "Deployment", "Prototype", "References"],
    )

    openapi_schema = request.scope.get("app").openapi_schema
    openapi_schema_template = Template(json.dumps(openapi_schema))
    return TEMPLATES.TemplateResponse(
        "docs.html",
        {
            "request": request,
            "base_url": get_base_url_from_request(
                request, config.get("API_SCHEME", default="http")
            ),
            "page_title": "Compute API Operator Documentation",
            "openapi_schema": openapi_schema_template.render(
                {
                    "api_server_url": get_api_server_url_from_request(
                        request, config.get("API_SCHEME", default="http")
                    )
                }
            ),
            "readme_text_md": readme_text_html,
        },
    )


@api_version(1)
@app.get(
    "/www/docs/user",
    include_in_schema=False,
    dependencies=[Depends(increment_request_counter)]
    if DEBUG
    else [Depends(increment_request_counter)],
)
@handle_exceptions
async def user_docs(request: Request) -> TEMPLATES.TemplateResponse:
    # Read and parse README.md, omitting excluded sections.
    if not DEBUG:
        readme_text_md = os.environ.get("README_MD", "")
    else:
        with open("../../../README.md") as f:
            readme_text_md = f.read()
    readme_text_html = convert_readme_to_html_docs(
        readme_text_md,
        exclude_sections=[
            "Authorisation",
            "Workflows",
            "Schemas",
            "Development",
            "Deployment",
            "Prototype",
            "References",
        ],
    )

    # Exclude unnecessary paths.
    paths_to_include = {"/ping": ["get"], "/health": ["get"]}
    openapi_schema = copy.deepcopy(request.scope.get("app").openapi_schema)
    included_paths = {}
    for path, methods in openapi_schema.get("paths", {}).items():
        for method, attr in methods.items():
            if method in paths_to_include.get(path, []):
                if path not in included_paths:
                    included_paths[path] = {}
                included_paths[path][method] = attr
    openapi_schema.update({"paths": included_paths})

    openapi_schema_template = Template(json.dumps(openapi_schema))
    return TEMPLATES.TemplateResponse(
        "docs.html",
        {
            "request": request,
            "base_url": get_base_url_from_request(
                request, config.get("API_SCHEME", default="http")
            ),
            "page_title": "Compute API User Documentation",
            "openapi_schema": openapi_schema_template.render(
                {
                    "api_server_url": get_api_server_url_from_request(
                        request, config.get("API_SCHEME", default="http")
                    )
                }
            ),
            "readme_text_md": readme_text_html,
        },
    )


@api_version(1)
@app.get(
    "/ping",
    responses={200: {"model": models.response.PingResponse}},
    tags=["Status"],
    summary="Check API status",
)
@handle_exceptions
async def ping(request: Request):
    """Service aliveness."""
    return JSONResponse(
        {
            "status": "UP",
            "version": os.environ.get("SERVICE_VERSION"),
        }
    )


@api_version(1)
@app.get(
    "/health",
    responses={
        200: {"model": models.response.HealthResponse},
        500: {"model": models.response.HealthResponse},
    },
    tags=["Status"],
    summary="Check API health",
)
@handle_exceptions
async def health(request: Request):
    """Service health.

    This endpoint will return a 500 if any of the dependent services are down.
    """

    # Dependent services.
    #
    # Permissions API
    #
    permissions_api_response = PERMISSIONS.ping()

    # Set return code dependent on criteria e.g. dependent service statuses
    #
    healthy_criteria = [permissions_api_response.status_code == 200]
    return JSONResponse(
        status_code=status.HTTP_200_OK
        if all(healthy_criteria)
        else status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "uptime": round(time.time() - SERVICE_START_TIME),
            "number_of_managed_requests": REQUESTS_COUNTER,
            "dependent_services": {
                "permissions-api": {
                    "status": "UP"
                    if permissions_api_response.status_code == 200
                    else "DOWN",
                }
            },
        },
    )


@api_version(1)
@app.post(
    "/query",
    responses={200: {"model": models.QueryResponse}},
    tags=["Query"],
    summary="Query for general compute availability.",
)
@handle_exceptions
async def query(query_input: models.QueryInput):
    """Query for availability"""
    return query_resources(query_input)


@api_version(1)
@app.put(
    "/provision",
    responses={200: {"model": models.response.ProvisionResponse}},
    tags=["Submit"],
    summary="Query for general compute availability and provision resources.",
)
@handle_exceptions
async def provision(provision_input: models.QueryInput, db: Session = Depends(get_db)):
    """Query for availability and provision resources."""
    return provision_resources(provision_input, db)


@api_version(1)
@app.put(
    "/provision/{provision_id}/submit",
    responses={200: {"model": models.response.JobSubmissionResponse}},
    tags=["Submit"],
    summary="Submit job for the provision.",
)
@handle_exceptions
async def submit(
    job_input: models.JobInput, provision_id: str, db: Session = Depends(get_db)
):
    """Submit job to be executed using the provision."""
    return submit_job(job_input=job_input, provision_id=provision_id, db=db)


@api_version(1)
@app.get(
    "/provision/{provision_id}/status",
    responses={200: {"model": models.response.JobStatusResponse}},
    tags=["Submit"],
    summary="Status information for a submitted job.",
)
@handle_exceptions
async def get_job_status(provision_id: str, db: Session = Depends(get_db)):
    """See the satus of a submitted job."""
    return job_status(provision_id=provision_id, db=db)


# Versionise the API.
#
versions = versionize(app=app, prefix_format="/v{major}", docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Customise openapi.json.
#
# - Add schema server, title and tags.
# - Add request code samples to routes.
# - Remove 422 responses.
#
for route in app.routes:
    if isinstance(
        route.app, FastAPI
    ):  # find any FastAPI subapplications (e.g. /v1/, /v2/, ...)
        subapp = route.app
        subapp_base_path = "{}{}".format(
            os.environ.get("API_ROOT_PATH", default=""), route.path
        )
        subapp.openapi()
        subapp.openapi_schema["servers"] = [{"url": subapp_base_path}]
        subapp.openapi_schema["info"]["title"] = "Compute API Overview"
        subapp.openapi_schema["tags"] = [
            {
                "name": "Status",
                "description": "Operations describing the status of the API.",
                "x-tag-expanded": False,
            },
        ]
        # add request code samples and strip out 422s
        for language in ["shell", "python", "go", "js"]:
            for path, methods in subapp.openapi_schema["paths"].items():
                path = path.strip("/")
                for method, attr in methods.items():
                    if attr.get("responses", {}).get("422"):
                        del attr.get("responses")["422"]
                    method = method.strip("/")
                    sample_template_filename = "{}-{}-{}.j2".format(
                        language, path, method
                    ).replace("/", "-")
                    sample_template_path = os.path.join(
                        "request-code-samples", sample_template_filename
                    )
                    if os.path.exists(sample_template_path):
                        with open(sample_template_path, "r") as f:
                            sample_source_template = f.read()
                        code_samples = attr.get("x-code-samples", [])
                        code_samples.append(
                            {
                                "lang": language,
                                "source": str(
                                    sample_source_template
                                ),  # rendered later in route
                            }
                        )
                        attr["x-code-samples"] = code_samples
