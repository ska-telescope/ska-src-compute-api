import os
from typing import Union
import uuid 

import requests
from authlib.integrations.requests_client import OAuth2Session
from fastapi import Depends, FastAPI, HTTPException, status, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi_app.rest.permissions import Permission
from starlette.config import Config
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, RedirectResponse
import urllib.parse

config = Config('.env')

# Instantiate FastAPI() allowing CORS.
#
app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=config.get('SESSION_MIDDLEWARE_SECRET_KEY'))
origins = ["*"]     # Security risk if service is used externally

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Configure OAuth2 client.
#
# The <name> specified here must have a corresponding <name>_CLIENT_ID and <name>_CLIENT_SECRET
# environment variable.

client_name = config.get('CLIENT_NAME')
client_id = config.get("{}_CLIENT_ID".format(client_name))
client_secret = config.get("{}_CLIENT_SECRET".format(client_name))
client_scopes = config.get('CLIENT_SCOPES')

# Get endpoints from oidc well_known
client_well_known = requests.get(config.get('CLIENT_CONF_URL')).json()
authorization_endpoint = client_well_known['authorization_endpoint']
token_endpoint = client_well_known['token_endpoint']
introspection_endpoint = client_well_known['introspection_endpoint']

# Instantiate OAuth2 client
client = OAuth2Session(client_id, client_secret, scope=client_scopes)

## Instantiate permissions and roles modules to check authZ for routes.
#
permission_definition_abspath = os.path.join(config.get('PERMISSIONS_RELPATH'),
                                             config.get('PERMISSIONS_NAME'))
roles_definition_abspath = os.path.join(config.get('ROLES_RELPATH'),
                                        config.get('ROLES_NAME'))
PERMISSION = Permission(permissions_definition_path=permission_definition_abspath,
                        roles_definition_path=roles_definition_abspath,
                        root_group=config.get('PERMISSIONS_ROOT_GROUP'))

## Function to validate (and return) a token using the introspection endpoint.
#
async def validate_token_by_remote_introspection(access_token: str) -> Union[dict, bool]:
    if access_token:
        data = {'token': access_token, 'token_type_hint': 'access_token'}
        auth = (client_id, client_secret)
        resp = requests.post(introspection_endpoint, data=data, auth=auth)
        resp.raise_for_status()
        resp_json = resp.json()
        if resp_json['active'] is not True:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token is invalid, please try logging in.")
        return resp_json
    return False


## Function to check permissions from user token groups.
#
async def verify_permission_for_route(request: Request, Authorization: Union[str, None] = Header(default=None)) -> Union[HTTPException, RedirectResponse]:
    if Authorization is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "You are not authorised to view this resource.")
    access_token = Authorization.split('Bearer')[1].strip()
    introspected_token = await validate_token_by_remote_introspection(access_token)
    if not introspected_token:
        groups = []
    else:
        groups = introspected_token['groups']
    try:
        route = request.scope['root_path'] + request.scope['route'].path
        method = request.method

        if PERMISSION.check_role_membership_for_route(
                route=route, method=method, groups=groups, **request.path_params):
            return
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "You are not authorised to view this resource.")
    except Exception as e:
        if hasattr(e, "http_error_status"):
            raise HTTPException(e.http_error_status, e.message)
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, repr(e))


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get('/login')
async def login(request: Request):
    '''
    Construct a URL user can use to authenticate with IAM (auth code flow)
    '''
    authorization_uri, state = client.create_authorization_url(authorization_endpoint)
    authorization_uri = "{}&redirect_uri={}".format(authorization_uri, request.url_for("code"))
    return HTMLResponse("{}".format(authorization_uri))


@app.get('/code')
async def code(request: Request):
    '''
    Strip the authorization code from the URL provided by IAM
    '''
    code = request.query_params.get('code')
    return HTMLResponse('Authorization code is: {}'.format(code))


@app.get('/token')
async def token(request: Request, code: str) -> JSONResponse:
    '''
    Use auth code (required as query param 'code') to retrieve token from IAM
    '''
    url = "{}?".format(token_endpoint)
    params = {
        'code': code,
        'redirect_uri': request.url_for('code')
    }
    authorization_response = url + urllib.parse.urlencode(params)
    token = client.fetch_token(token_endpoint, authorization_response=authorization_response, redirect_uri=request.url_for('code'))
    #session_id = str(uuid.uuid4())
    #SESSIONS[session_id] = token['access_token']
    return JSONResponse(token['access_token'])

@app.get("/test_auth", dependencies=[Depends(verify_permission_for_route)])
async def read_test_auth(request: Request, Authorization: Union[str, None] = Header(default=None)) -> Union[JSONResponse, HTTPException]:
    return {"Authenticated successfully", 200}


@app.post("/resource", status_code=201)
def create_item(resource_name: str):
    return {"POST success", 201}


@app.get("/resources/{resource_id}")
def read_item():
    return {"GET success", 200}


@app.put("/resources/{resource_id}")
def update_item():
    return {"PUT success", 204}


@app.delete("/resources/{resource_id}")
def delete_item():
    return {"DELETE success", 204}
