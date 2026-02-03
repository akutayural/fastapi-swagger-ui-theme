from fastapi import FastAPI, Depends
from pydantic import BaseModel

from fastapi_swagger_ui_theme import setup_swagger_ui_theme
from test.auth import authenticate_user, require_token, DEMO_TOKEN
from api_exception import ResponseModel

app = FastAPI(docs_url=None)  # Close the docs_url here.

setup_swagger_ui_theme(app, docs_path="/docs")


class LoginRequest(BaseModel):
    username: str
    password: str


@app.post("/login", response_model=ResponseModel)
def login(body: LoginRequest):
    '''

    {
  "username": "admin",
  "password": "admin"
} is for the successful request. Anything except than that can be used for error cases.
    :return:
    '''
    if not authenticate_user(body.username, body.password):
        return {"ok": False, "message": "Invalid credentials"}

    return ResponseModel()


@app.get("/ping")
def ping(token: str = Depends(require_token)):
    return {"ok": True, "message": "pong", "token": token}
