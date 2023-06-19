from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = ["*"]     # non-public endpoints are only accessible via tokens.

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

def get_auth_token(token_info):
    return {}

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/login")
def login(username: str, password: str):
    return {"Login success", 200}


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
