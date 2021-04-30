import requests
from cryptography.fernet import Fernet
import subprocess
import client_config as cfg
import client_helper as helper
import os.path


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
    response = requests.post(url='http://127.0.0.1:5000/shareData?_id={}'.format(_id), data=encrypted,
                             headers=cfg.post_octect_headers)
    print(response)


if __name__ == '__main__':
    current_machine_id = subprocess.check_output('wmic csproduct get uuid').decode().split('\n')[1].strip()
    data = {}
    data['msg'] = "I am from CU Boulder - Colorado"
    send_msg(current_machine_id, data)
