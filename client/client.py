import requests
from cryptography.fernet import Fernet
import subprocess
import client_config as cfg
import client_helper as helper
import os.path
import uuid

def send_msg(_id, data):
    # Check the Keys Directory
    curr_directory = os.getcwd()
    if not os.path.exists(cfg.keys_folder):
        dirPath = os.path.join(curr_directory, cfg.keys_folder)
        os.mkdir(dirPath)
        helper.get_keys(_id)
    file_path = os.path.join(curr_directory, cfg.keys_folder, '{}.key'.format(_id))
    if not os.path.isfile(file_path):
        helper.get_keys(_id)

    file = open('{}/{}.key'.format(cfg.keys_folder, _id), 'rb')  # Open the file as wb to read bytes
    key = file.read()  # The key will be type bytes
    file.close()
    message = data['msg'].encode()

    f = Fernet(key)
    encrypted = f.encrypt(message)
    response = requests.post(url='{}/shareData?_id={}'.format(cfg.server_url, _id), data=encrypted,
                             headers=cfg.post_octect_headers)
    print(response)


if __name__ == '__main__':
    current_machine_id = str(uuid.uuid4())
    data = {}
    data['msg'] = "I am from CU Boulder - Colorado"
    send_msg(current_machine_id, data)