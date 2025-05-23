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
    global username 
    username = data.username 
    global password 
    password = data.password
    return {username, password}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):

    message = f"Python recieved the file: {file.filename} {file.content_type}"

    # Perfect place to stop non-fsa files from going through
    file.content_type

   # return message

    # SSH credentials
    ssh_host = "10.255.255.20"
    ssh_port = 22
    ssh_user = username
    ssh_pass = password

    try:
        client = paramiko.SSHClient()
        client.load_system_host_keys() 
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # BUG: not connecting even when pass and user is correct

        print("SSH Username: " + username)
        print("SSH Password: " + password)

        client.connect(ssh_host, port=ssh_port, username=username, password=password,
         look_for_keys=False, allow_agent=False, disabled_algorithms=
         {'pubkeys': ['rsa-sha2-256', 'rsa-sha2-512']})

        # Execute a command
        stdin, stdout, stderr = client.exec_command("ls -l")
        output = stdout.read().decode()
        print(output)

        client.close()

    except Exception as e:
        print(f"An error occurred: {e}")

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
