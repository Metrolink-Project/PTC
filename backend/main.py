# Necessary Imports
from fastapi import FastAPI, File, UploadFile, HTTPException  # The main FastAPI import
from fastapi.responses import HTMLResponse  # Used for returning HTML responses
from fastapi.staticfiles import StaticFiles   # Used for serving static files
from fastapi.responses import JSONResponse
import uvicorn                                # Used for running the app
from pydantic import BaseModel

import paramiko
import time
import shutil
import webbrowser
import zipfile
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

def run_remote_command(ssh_client, command, timeout=15):
    try:
        stdin, stdout, stderr = ssh_client.exec_command(command, timeout=timeout)
        start_time = time.time()

        while not stdout.channel.exit_status_ready():
            if time.time() - start_time > timeout:
                print("Command timed out.")
                return None, None, None
            time.sleep(0.1)

        exit_status = stdout.channel.recv_exit_status()
        out = stdout.read().decode()
        err = stderr.read().decode()

        return exit_status, out, err

    except Exception as e:
        print(f"Error running command: {e}")
        return None, None, None

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):

    message = f"Python recieved the file: {file.filename} {file.content_type}"

    # Perfect place to stop non-fsa files from going through for non-root users
    if (username != "root"):
        if not file.filename.lower().endswith(".fsa"):
            return JSONResponse(status_code=400, content="ERROR: Only .fsa files are allowed.")

    # Temporary folder to put file in order to upload
    temp_folder = "Z:\\Onboard Team\\Marc Reta"
    os.makedirs(temp_folder, exist_ok=True)
    temp_file_path = os.path.join(temp_folder, file.filename)

    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # For zip files, unzip and upload each file individually
    if file.filename.lower().endswith(".zip"):
        extract_dir = os.path.join(temp_folder, "extracted")
        os.makedirs(extract_dir, exist_ok=True)

        with zipfile.ZipFile(temp_file_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir) # it extracts to a folder 

    buffer.close()
    
    uploaded_files = []

    # SSH credentials
    ssh_host = "10.255.255.20"
    ssh_port = 22
    ssh_user = username
    ssh_pass = password

    try:
        client = paramiko.SSHClient()
        client.load_system_host_keys() 
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        print("SSH Username: " + username)
        print("SSH Password: " + password)

        # Connecting into the slot 10
        client.connect(ssh_host, port=ssh_port, username=username, password=password,
         look_for_keys=False, allow_agent=False, disabled_algorithms=
         {'pubkeys': ['rsa-sha2-256', 'rsa-sha2-512']})

        # Execute a command
        stdin, stdout, stderr = client.exec_command("mkdir -p upload")
        output = stdout.read().decode()
        print(output)

        # Upload file to slot 10
        if (ssh_user == "root"):
            transport = paramiko.Transport((ssh_host, ssh_port))
            transport.connect(username=ssh_user, password=ssh_pass)
            sftp = paramiko.SFTPClient.from_transport(transport)
            remote_path = f"/{ssh_user}/upload/{file.filename}"

            # Put the zip functionality here
            if file.filename.lower().endswith(".zip"):
                for root, dirs, files in os.walk(extract_dir):
                    for name in files:
                        local_path = os.path.join(root, name)
                        print(local_path)
                        zip_path = f"/{ssh_user}/upload/{name}"
                        sftp.put(local_path, zip_path)
                        uploaded_files.append(zip_path)
            else:
                sftp.put(temp_file_path, remote_path)

            # Install new OS into Slot 10
            command = "ls -l"
            stdin, stdout, stderr = client.exec_command(command)
            output = stdout.read().decode()
            print(output)

            command = "cd upload && chmod u+x install.sh"
            stdin, stdout, stderr = client.exec_command(command)
            output = stdout.read().decode()
            print(output)
            
            print("running ./install.sh")
            command = "cd upload && ./install.sh" 
            run_remote_command(client, command)

            sftp.close()
            transport.close()
            os.remove(temp_file_path)

        else:
            transport = paramiko.Transport((ssh_host, ssh_port))
            transport.connect(username=ssh_user, password=ssh_pass)
            sftp = paramiko.SFTPClient.from_transport(transport)
            remote_path = f"/home/{ssh_user}/upload/{file.filename}"
            sftp.put(temp_file_path, remote_path)
            sftp.close()
            transport.close()
            os.remove(temp_file_path)

        client.close()

        if file.filename.lower().endswith(".zip"):
            # delete extracted folder
            if os.path.exists(extract_dir):
                try:
                    shutil.rmtree(extract_dir)
                    print(f"Directory '{extract_dir}' and its contents deleted successfully.")
                except OSError as e:
                    print(f"Error deleting directory '{extract_dir}': {e}")
            else:
                print(f"Directory '{extract_dir}' does not exist.")

            return f"OS installed successfully: {uploaded_files}"

        return f"Install Sucess! Uploaded to {remote_path}"

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    webbrowser.open("http://127.0.0.1:6543")
    print("\n \n \n Welcome to Metrolink: PTC OS Installer! By Marc Reta \n \n \n")
    uvicorn.run(app, host="127.0.0.1", port=6543)
