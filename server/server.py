import cryptography
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from flask import Flask, request,send_file, send_from_directory, safe_join, abort,jsonify
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
import os, json
app = Flask(__name__)


@app.route("/shareData",methods=['POST'])
def shareData():
    data = request.data
    print(type(data), data)
    file = open('nithin.key', 'rb')  # Open the file as wb to read bytes
    key = file.read()  # The key will be type bytes
    file.close()
    f = Fernet(key)
    decrypted = f.decrypt(data)
    print(decrypted.decode())
    return "Hello World!"



@app.route("/generateKeys",methods=['POST'])
def generateKeys():
    try:
        data = request.get_json()
        print(data['_id'])
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

        with open('pr1-{}.pem'.format(data['_id']), 'wb') as f:
            f.write(pem)

        pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        app.config['keys_dir'] = os.getcwd()
        with open('pu1-{}.pem'.format(data['_id']), 'wb') as f:
            f.write(pem)
        try:
            return send_from_directory(app.config["keys_dir"], filename='pu1-{}.pem'.format(data['_id']), as_attachment=True)
        except FileNotFoundError:
            abort(404)
    except  Exception as ex:
        print(ex)
        return "Hello World!"

@app.route("/receivePubKey",methods=['POST'])
def receivePubKey():
    # try:
    data = request.data

    my_json = data.decode('utf8').replace("'", '"')
    print(my_json)
    data = json.loads(my_json)

    print("Format is ")
    print(type(data))
    decrypt_message(data)
    symetricKey_generation()
    response_payload = transmit_symetricKey()
    return jsonify(response_payload), 200

    # return "TRUE"
    # except  Exception as ex:
    #     print(ex)
    #     return "True"



def symetricKey_generation():
    key = Fernet.generate_key()
    file = open('nithin.key', 'wb')  # Open the file as wb to write bytes
    file.write(key)  # The key is type bytes still
    file.close()

def transmit_symetricKey():
    with open('pu2-{}.pem'.format('nithin'), "rb") as key_file:
        public_key = serialization.load_pem_public_key(
            key_file.read(),
            backend=default_backend()
        )
    CHUNK_SIZE = 150
    msg_contents= []
    f = open('{}.key'.format('nithin'), 'rb')
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

    return request_payload

def decrypt_message(encypted_msg):
    orginal_msg = []
    for each_chunk in encypted_msg['msg']:
        with open('pr1-{}.pem'.format('Nithin'), "rb") as key_file:
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
    # print(original_message)
    print(orginal_msg)
    f = open('pu2-{}.pem'.format('Nithin'), 'w+b')
    for each_ in orginal_msg:
        f.write(each_)
    # binary_format = bytearray(orginal_msg)
    # f.write(orginal_msg)
    f.close()


def generate_initial_key(_id):

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

    with open('private_key.pem', 'wb') as f:
        f.write(pem)

    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    with open('public_key.pem', 'wb') as f:
        f.write(pem)
    return

if __name__ == "__main__":
    app.run()