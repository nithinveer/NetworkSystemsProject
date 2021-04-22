import cryptography
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from flask import Flask, request,send_file, send_from_directory, safe_join, abort
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
import os
app = Flask(__name__)

@app.route("/generateKeys",methods=['POST'])
def generateKeys():
    print('Hi')
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
    data = request.get_json()
    decrypt_message(data['msg'])


def decrypt_message(encypted_msg):
    orginal_msg = []
    for each_chunk in encypted_msg:
        with open('pr1-{}.pem'.format('Nithin'), "rb") as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=None,
                backend=default_backend()
            )
            original_message = private_key.decrypt(
                each_chunk,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
        orginal_msg.append(original_message)
        print(original_message)
    print(orginal_msg)


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