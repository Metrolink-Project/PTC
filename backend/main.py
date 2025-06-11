# Necessary Imports
from fastapi import FastAPI, File, UploadFile, HTTPException  # The main FastAPI import
from fastapi.responses import HTMLResponse  # Used for returning HTML responses
from fastapi.staticfiles import StaticFiles   # Used for serving static files
from fastapi.responses import JSONResponse
import uvicorn                                # Used for running the app
from pydantic import BaseModel

import paramiko
import tqdm
import shutil
import zipfile
import gzip
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

    # Perfect place to stop non-fsa files from going through for non-root users
    if (username != "root"):
        if not file.filename.lower().endswith(".fsa"):
            return JSONResponse(status_code=400, content="ERROR: Only .fsa files are allowed.")
        
    '''
    # Only allow .iso files to be uploaded to slot 10
    if not file.filename.lower().endswith(".iso"):
        return JSONResponse(status_code=400, content="ERROR: Only .iso files are allowed.")
    '''

    # Temporary folder to put file in order to upload
    temp_folder = "Z:\\Onboard Team\\Marc Reta"
    os.makedirs(temp_folder, exist_ok=True)
    temp_file_path = os.path.join(temp_folder, file.filename)
    gz_file_path = os.path.join(temp_folder, f'{file.filename}.gz')

    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    '''
    # create gzip
    with open(temp_file_path, 'rb') as temp_file:
        with gzip.open(gz_file_path, 'wb') as gz_file:
            shutil.copyfileobj(temp_file, gz_file)
    '''

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
        stdin, stdout, stderr = client.exec_command("ls -l")
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
                with tqdm.tqdm(desc='Uploading file', unit='iB', unit_scale=True, unit_divisor=1024) as pbar:
                    def progress(amt, tot):
                        pbar.total = tot
                        pbar.update(amt - pbar.n)  # Update with the incremental progress
                sftp.put(temp_file_path, remote_path, callback=progress)

            # Install files into Slot 10 (BUG: Crashed Slot 10)
            '''
            command = "cd upload && chmod +x install.sh && ./install.sh"
            stdin, stdout, stderr = client.exec_command(command)
            output = stdout.read().decode()
            print(output)
            '''

            '''
            command = "cd upload"
            stdin, stdout, stderr = client.exec_command(command)
            output = stdout.read().decode()
            print(output)

            command = "chmod +x install.sh"
            stdin, stdout, stderr = client.exec_command(command)
            output = stdout.read().decode()
            print(output)
            
            command = "ls -l"
            stdin, stdout, stderr = client.exec_command(command)
            output = stdout.read().decode()
            print(output)

            # Experiment with using dd for burning .iso file
            command = "sudo umount /boot"
            command = "sudo umount /home"
            command = f"sudo dd if={remote_path} of=/dev/sda bs=4M status=progress oflag=sync"
            command = "sudo mount /dev/sda1 /boot"
            command = "sudo mount /dev/sda3 /home"

                if=/path/to/your/filename.iso: Specifies the input file (your ISO image).
                of=/dev/sdX: Specifies the output device (your USB drive or CFast card).
                bs=4M: Sets the block size for faster copying (4 megabytes).
                status=progress: Displays the progress of the operation.
                oflag=sync: Ensures synchronous writes, meaning the command won't return until all data is written to the device. 


                Use lsblk or fdisk -l: The best way to determine the correct device path for your CFast card 
                is to use the lsblk or fdisk -l command in your terminal after inserting the card. This will show you a list of all 
                your block devices and their corresponding device names. Look for entries that correspond to your CFast card based on
                size, file system type, or mount point (if it's already mounted). 

                
                It's recommended to unmount the CFastCard before installing .iso file: (uses the mountpoint path)
                sudo umount /mnt/cfast

                Re-mount after installing .iso file: (use lsblk to find the original mount point before unmounting)
                sudo mount /dev/sdb1 /mnt/cfast
            '''

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
            # TODO: remove files that were extracted by zip

        '''
        # Running install.sh
        command = "cd 339bc94e1be405554a9107988b5535c0 &&" +
            " chmod +x install.sh && ./install.sh"
        '''

        client.close()

        if file.filename.lower().endswith(".zip"):
            return f"Files uploaded successfully: {uploaded_files}"

        return f"Upload Sucess! Uploaded to {remote_path}"

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=6543)
