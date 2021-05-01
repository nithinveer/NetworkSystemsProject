from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.fernet import Fernet
import server_config as cfg


def transmit_symetricKey(_id):
    with open('{}/pu2-{}.pem'.format(cfg.keys_folder, _id), "rb") as key_file:
        public_key = serialization.load_pem_public_key(
            key_file.read(),
            backend=default_backend()
        )
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


def decrypt_message(encypted_msg):
    orginal_msg = []
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
    print(orginal_msg)
    f = open('{}/pu2-{}.pem'.format(cfg.keys_folder, encypted_msg['_id']), 'w+b')
    for each_ in orginal_msg:
        f.write(each_)
    f.close()


def symetricKey_generation(_id):
    key = Fernet.generate_key()
    file = open('{}/{}.key'.format(cfg.keys_folder, _id), 'wb')  # Open the file as wb to write bytes
    file.write(key)  # The key is type bytes still
    file.close()
