# Necessary Imports
from fastapi import FastAPI, File, UploadFile, HTTPException, Request  # The main FastAPI import
from fastapi.responses import HTMLResponse  # Used for returning HTML responses
from fastapi.staticfiles import StaticFiles   # Used for serving static files
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
import uvicorn                                # Used for running the app
from pydantic import BaseModel
from pathlib import Path
from glob import glob

import paramiko
import time
import shutil
import zipfile
import webbrowser
import os

# Configuration
app = FastAPI()                   # Specify the "app" that will run the routing

username = ""
password = ""

# Mount the static directory
app.mount('/static', StaticFiles(directory=str(Path(__file__).with_name('static')), html=True), name='static')
frontend = Jinja2Templates(directory=str(Path(__file__).with_name("frontend")))

@app.get("/")
def get_login_html(request: Request):
    return frontend.TemplateResponse("login.html", {"request": request})

@app.get("/index")
def get_index_html(request: Request):
    return frontend.TemplateResponse("index.html", {"request": request})
    
class LoginData(BaseModel):
    username: str
    password: str

@app.post("/login")
def login(data: LoginData):
    print("Username:" + data.username)
    print("Password:" + data.password)

    if (data.username == "tech" and data.password == ""):
        print("Login successful")
        global username 
        username = "root"
        global password 
        password = ""
        return {data.username, data.password}
    else:
        print("Wrong password")

    return 'Wrong password'

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
async def upload_file():

    your_folder_path = "C:\\Slot10_OS"

    if not os.path.exists(your_folder_path):
        os.makedirs(your_folder_path)

    extract_dir = "C:\\Slot10_OS\\extracted"
    os.makedirs(extract_dir, exist_ok=True)

    zip_files = glob(os.path.join(your_folder_path, '*.zip'))

    if zip_files:
        temp_file_path = zip_files[0]
        print(f"Found zip file at: {temp_file_path}")

        with zipfile.ZipFile(temp_file_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
            print(f"Extracted contents of {temp_file_path} to {extract_dir}")
    else:
        os.rmdir(extract_dir)
        return f"No OS file found in {your_folder_path}"
    
    uploaded_files = []

    # Delete below when testing Slot 10
    os.remove(temp_file_path)
    return 'Files were extracted successfully.'

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

            # Put the zip functionality here
            for root, dirs, files in os.walk(extract_dir):
                for name in files:
                    local_path = os.path.join(root, name)
                    print(local_path)
                    zip_path = f"/{ssh_user}/upload/{name}"
                    sftp.put(local_path, zip_path)
                    uploaded_files.append(zip_path)

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

        client.close()

        if os.path.exists(extract_dir):
            try:
                shutil.rmtree(extract_dir)
                print(f"Directory '{extract_dir}' and its contents deleted successfully.")
            except OSError as e:
                print(f"Error deleting directory '{extract_dir}': {e}")
        else:
            print(f"Directory '{extract_dir}' does not exist.")

        return f"OS installed successfully: {uploaded_files}"

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    webbrowser.open("http://127.0.0.1:6543")
    print("\n \n \n Welcome to Metrolink: PTC OS Installer! By Marc Reta \n \n \n")
    uvicorn.run(app, host="127.0.0.1", port=6543)
