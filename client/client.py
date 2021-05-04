import requests
from cryptography.fernet import Fernet
import subprocess
import client_config as cfg
import client_helper as helper
import os.path
import uuid
import json
import zlib
import sys
import time
from getmac import get_mac_address as gma

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

    print("encrypted request sent to the server")

    print(response)

    res = f.decrypt(response.text.encode())
    print(sys.getsizeof(res))
    res = zlib.decompress(res)
    res = res.decode()
    print(sys.getsizeof(res))
    res = json.loads(res)

    print(res)

if __name__ == '__main__':
    current_machine_id = str(gma())
    data = {}
    data['msg'] = "23456"

    start_time = time.time()

    send_msg(current_machine_id, data)

    end_time = time.time()

    print(end_time - start_time)