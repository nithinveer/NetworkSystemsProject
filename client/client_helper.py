from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from requests import post
import client_config as cfg
import json


def create_keys(_id):
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()

    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    with open('{}/pr2-{}.pem'.format(cfg.keys_folder, _id), 'wb') as f:
        f.write(pem)

    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    with open('{}/pu2-{}.pem'.format(cfg.keys_folder, _id), 'wb') as f:
        f.write(pem)


def transmit_publicKey(_id):
    with open('{}/pu1-{}.pem'.format(cfg.keys_folder, _id), "rb") as key_file:
        public_key = serialization.load_pem_public_key(
            key_file.read(),
            backend=default_backend()
        )

    msg_contents = []
    f = open('{}/pu2-{}.pem'.format(cfg.keys_folder, _id), 'rb')
    while True:
        piece = f.read(cfg.CHUNK_SIZE)
        if not piece:
            break
        msg_contents.append(piece)
    f.close()

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
    request_payload = {}
    request_payload['msg'] = encrypted_contents
    request_payload['_id'] = _id
    response = post(url='{}/receivePubKey'.format(cfg.server_url), data=json.dumps(request_payload),
                    headers=cfg.post_octect_headers).json()

    decrypt_message(response['msg'], _id)


def decrypt_message(encypted_msg, _id):
    orginal_msg = []
    for each_chunk in encypted_msg:
        with open('{}/pr2-{}.pem'.format(cfg.keys_folder, _id), "rb") as key_file:
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
    f = open('{}/{}.key'.format(cfg.keys_folder, _id), 'w+b')
    for each_ in orginal_msg:
        f.write(each_)
    f.close()


def get_keys(_id):
    request_payload = '{"_id":"' + _id + '"}'
    response = post(url='{}/generateKeys'.format(cfg.server_url), data=request_payload, headers=cfg.post_json_headers)
    if response.status_code == 200:
        with open('{}/pu1-{}.pem'.format(cfg.keys_folder, _id), 'wb') as f:
            f.write(response.content)
    create_keys(_id)
    transmit_publicKey(_id)
