from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.fernet import Fernet
import server_config as cfg
import os


def redis_to_file(store, key):
    content = store.get(key)

    curr_directory = os.getcwd()
    if not os.path.exists(cfg.keys_folder):
        dirPath = os.path.join(curr_directory, cfg.keys_folder)
        os.mkdir(dirPath)

    f = open('{}/{}'.format(cfg.keys_folder, key), "wb")
    f.write(content)
    f.close()


def file_to_redis(store, key):
    curr_directory = os.getcwd()
    if not os.path.exists(cfg.keys_folder):
        dirPath = os.path.join(curr_directory, cfg.keys_folder)
        os.mkdir(dirPath)

    f = open('{}/{}'.format(cfg.keys_folder, key), "rb")
    content = f.read()
    f.close()
    store.set(key, content)


def transmit_symetricKey(store, _id):
    print("encrypting symmetric key using public key 2")

    redis_to_file(store, 'pu2-{}.pem'.format(_id))

    with open('{}/pu2-{}.pem'.format(cfg.keys_folder, _id), "rb") as key_file:
        public_key = serialization.load_pem_public_key(
            key_file.read(),
            backend=default_backend()
        )

    redis_to_file(store, '{}.key'.format(_id))
    msg_contents = []
    f = open('{}/{}.key'.format(cfg.keys_folder, _id), 'rb')
    while True:
        piece = f.read(cfg.CHUNK_SIZE)
        if not piece:
            break
        msg_contents.append(piece)
    f.close()

    print(msg_contents)
    encrypted_contents = []
    for each_chunk in msg_contents:
        encrypted = public_key.encrypt(
            each_chunk,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        encrypted_contents.append(encrypted.hex())
    print((encrypted_contents))
    request_payload = {}
    request_payload['msg'] = encrypted_contents

    return request_payload


def decrypt_message(store, encypted_msg):
    orginal_msg = []

    redis_to_file(store, 'pr1-{}.pem'.format(encypted_msg['_id']))
    for each_chunk in encypted_msg['msg']:
        with open('{}/pr1-{}.pem'.format(cfg.keys_folder, encypted_msg['_id']), "rb") as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=None,
                backend=default_backend()
            )
            original_message = private_key.decrypt(
                bytes.fromhex(each_chunk),
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            orginal_msg.append(original_message)

    print("request decrypted")

    f = open('{}/pu2-{}.pem'.format(cfg.keys_folder, encypted_msg['_id']), 'w+b')
    for each_ in orginal_msg:
        f.write(each_)
    f.close()

    file_to_redis(store, 'pu2-{}.pem'.format(encypted_msg['_id']))


def symetricKey_generation(store, _id):
    print("generating symmetric key")
    key = Fernet.generate_key()
    file = open('{}/{}.key'.format(cfg.keys_folder, _id), 'wb')  # Open the file as wb to write bytes
    file.write(key)  # The key is type bytes still
    file.close()

    file_to_redis(store, '{}.key'.format(_id))
