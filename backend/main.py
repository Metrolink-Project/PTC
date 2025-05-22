# Necessary Imports
from fastapi import FastAPI, File, UploadFile  # The main FastAPI import
from fastapi.responses import HTMLResponse   # Used for returning HTML responses
from fastapi.staticfiles import StaticFiles   # Used for serving static files
from fastapi.responses import JSONResponse
import uvicorn                                # Used for running the app
from pydantic import BaseModel

import paramiko
import shutil
import os

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

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):

    message = "Python recieved the file"

    return message
    '''
    temp_file_path = f"/tmp/{file.filename}"
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

        # SSH credentials
        ssh_host = "10.255.255.20"
        ssh_port = 22
        ssh_user = username
        ssh_pass = password

        try:
            transport = paramiko.Transport((ssh_host, ssh_port))
            transport.connect(username=ssh_user, password=ssh_pass)
            sftp = paramiko.SFTPClient.from_transport(transport)
            remote_path = f"/home/{ssh_user}/{file.filename}"
            sftp.put(temp_file_path, remote_path)
            sftp.close()
            transport.close()
            os.remove(temp_file_path)
            return {"message": f"Uploaded to {remote_path}"}
        except Exception as e:
            return {"message": f"Upload failed: {str(e)}"}
    '''

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=6543)
