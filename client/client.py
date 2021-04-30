from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import requests
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
import json
post_request_headers = {"Content-Type": "application/json"}
post_octect_headers = {'Content-Type': 'application/octet-stream'}
def get_keys():
    request_payload= '{"_id":"Nithin"}'
    # request_payload['_id'] = 'Nithin'
    response = requests.post(url='http://127.0.0.1:5000/generateKeys', data=request_payload, headers=post_request_headers)
    print(response.status_code)
    if response.status_code ==200:
        open('pu1-{}.pem'.format('nithin'), 'wb').write(response.content)
        with open('pu1-{}.pem'.format('nithin'), 'wb') as f:
            f.write(response.content)
    create_keys('Nithin')
    # time.sleep(10)
    transmit_publicKey()

def transmit_publicKey():
    with open('pu1-{}.pem'.format('nithin'), "rb") as key_file:
        public_key = serialization.load_pem_public_key(
            key_file.read(),
            backend=default_backend()
        )
    CHUNK_SIZE = 150
    msg_contents= []
    f = open('pu2-{}.pem'.format('nithin'), 'rb')
    while True:
        piece = f.read(CHUNK_SIZE)
        if not piece:
            break
        msg_contents.append(piece)
    f.close()

    print(msg_contents)
    encrypted_contents = []
    for each_chunk in msg_contents:
        print(type(each_chunk))
        encrypted = public_key.encrypt(
            each_chunk,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        print(type(encrypted))
        encrypted_contents.append(encrypted.hex())
    print((encrypted_contents))
    request_payload = {}
    request_payload['msg'] = encrypted_contents
    print(request_payload)
    response = requests.post(url='http://127.0.0.1:5000/receivePubKey', data=json.dumps(request_payload),
                             headers=post_octect_headers)

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

    with open('pr2-{}.pem'.format(_id), 'wb') as f:
        f.write(pem)

    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    with open('pu2-{}.pem'.format(_id), 'wb') as f:
        f.write(pem)
    
    
if __name__ == '__main__':
    get_keys()
    