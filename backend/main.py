# Necessary Imports
from fastapi import FastAPI, File, UploadFile  # The main FastAPI import
from fastapi.responses import HTMLResponse   # Used for returning HTML responses
from fastapi.staticfiles import StaticFiles   # Used for serving static files
from fastapi.responses import JSONResponse
import uvicorn                                # Used for running the app
from pydantic import BaseModel
import paramiko

# Configuration
app = FastAPI()                   # Specify the "app" that will run the routing

username = ""
password = ""

# Mount the static directory
app.mount("/static", StaticFiles(directory="backend/static"), name="static")

@app.get("/", response_class=HTMLResponse)
def get_index_html() -> HTMLResponse:
    with open("frontend/login.html") as html:
        return HTMLResponse(content=html.read())

@app.get("/index", response_class=HTMLResponse)
def get_index_html() -> HTMLResponse:
    with open("frontend/index.html") as html:
        return HTMLResponse(content=html.read())
    
class LoginData(BaseModel):
    username: str
    password: str

@app.post("/login")
def login(data: LoginData):
    print("Username:" + data.username)
    print("Password:" + data.password)
    username = data.username
    password = data.password
    return {username, password}

'''
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    return 0
'''

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=6543)
