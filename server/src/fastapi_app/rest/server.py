import os
from typing import Union

import requests
from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi_app.rest.permissions import Permission
from starlette.config import Config
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, RedirectResponse

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
oauth = OAuth(config)
oauth.register(
    name=oauth.config.get('CLIENT_NAME'),
    server_metadata_url=oauth.config.get('CLIENT_CONF_URL'),
    client_kwargs={
        'scope': oauth.config.get('CLIENT_SCOPES')
    }
)
OAUTH_CLIENT = getattr(oauth, oauth.config.get('CLIENT_NAME'))

## Instantiate permissions and roles modules to check authZ for routes.
#
permission_definition_abspath = os.path.join(oauth.config.get('PERMISSIONS_RELPATH'),
                                             oauth.config.get('PERMISSIONS_NAME'))
roles_definition_abspath = os.path.join(oauth.config.get('ROLES_RELPATH'),
                                        oauth.config.get('ROLES_NAME'))
PERMISSION = Permission(permissions_definition_path=permission_definition_abspath,
                        roles_definition_path=roles_definition_abspath,
                        root_group=oauth.config.get('PERMISSIONS_ROOT_GROUP'))


## Function to validate (and return) a token using the introspection endpoint.
#
async def validate_token_by_remote_introspection(request: Request) -> Union[dict, bool]:
    print(request.session.get('user'))
    if request.session.get('user') and request.session.get('access_token'):
        if 'introspection_endpoint' not in OAUTH_CLIENT.server_metadata:
            await OAUTH_CLIENT.load_server_metadata()
        url = OAUTH_CLIENT.server_metadata['introspection_endpoint']
        data = {'token': request.session.get('access_token'), 'token_type_hint': 'access_token'}
        auth = (OAUTH_CLIENT.client_id, OAUTH_CLIENT.client_secret)
        resp = requests.post(url, data=data, auth=auth)
        resp.raise_for_status()
        resp_json = resp.json()
        if resp_json['active'] is not True:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token is invalid, please try logging in.")
        return resp_json
    return False


## Function to check permissions from user token groups.
#
async def verify_permission_for_route(request: Request) -> Union[HTTPException, RedirectResponse]:
    introspected_token = await validate_token_by_remote_introspection(request)
    print("Token is: {}".format(introspected_token))
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
    redirect_uri = request.url_for('code')
    authorization_url = await OAUTH_CLIENT.create_authorization_url()
    return HTMLResponse("Please go to: {}&redirect_uri={}".format(authorization_url['url'], redirect_uri))


@app.get('/code')
async def code(request: Request):
    '''
    Strip the authorization code from the URL provided by IAM
    '''
    code = request.query_params.get('code')
    return HTMLResponse('Authorization code is: {}'.format(code))


@app.get('/token')
async def token(request: Request, code: str) -> RedirectResponse:
    '''
    Use auth code (required as query param 'code') to retrieve token from IAM
    '''
    redirect_uri = request.url_for('code')
    await OAUTH_CLIENT.load_server_metadata()
    token_endpoint = OAUTH_CLIENT.server_metadata['token_endpoint']
    params = {'grant_type': 'authorization_code', 'code': code, 'redirect_uri': redirect_uri,
              'client_id': OAUTH_CLIENT.client_id, 'client_secret': OAUTH_CLIENT.client_secret}
    token = requests.post(token_endpoint, params=params)
    return JSONResponse(token.json())


## TODO: Fix, currently cannot validate Bearer token retrieved above
#
@app.get("/test_auth")
async def read_test_auth(request: Request):
    token = await OAUTH_CLIENT.authorize_access_token(request)
    print(token)
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
