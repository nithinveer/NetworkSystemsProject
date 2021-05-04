import os
import time
import psutil
from flask import Flask, request, jsonify
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.asymmetric import rsa
from flask import Flask, request, send_file, send_from_directory, safe_join, abort, jsonify
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
import os, json
import server_helper as helper
import server_config as cfg
import sys
import redis
import zlib

app = Flask(__name__)
f = open('student_data.json',)
student_data = json.load(f)
store = redis.Redis(host='35.224.22.211', port=6379, password='networksystems')

@app.route('/')
def home():
    return jsonify(
        message=f'This is the server application home page.',
        server=request.base_url,
    )

@app.route("/shareData", methods=['POST'])
def shareData():
    data = request.data
    print(type(data), data)
    _id = request.args.get('_id')

    helper.redis_to_file(store, '{}.key'.format(_id))
    file = open('{}/{}.key'.format(cfg.keys_folder, _id), 'rb')  # Open the file as wb to read bytes
    key = file.read()  # The key will be type bytes
    file.close()
    f = Fernet(key)
    decrypted = f.decrypt(data)
    arg = decrypted.decode()

    message = None

    for student in student_data['student_details']:
        if student['student_id'] == arg:
            message = student
    
    if message == None:
        message = jsonify({'name': 'NA', 'major': 'NA', 'email': 'NA'})

    response = json.dumps(message).encode()
    response = zlib.compress(response)

    encrypted = f.encrypt(response)

    return encrypted

@app.route("/generateKeys", methods=['POST'])
def generateKeys():
    try:
        data = request.get_json()
        print('Received Request for the _id {} to generate keys'.format(data['_id']))
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
        curr_directory = os.getcwd()
        if not os.path.exists(cfg.keys_folder):
            dirPath = os.path.join(curr_directory, cfg.keys_folder)
            os.mkdir(dirPath)
        with open('{}/pr1-{}.pem'.format(cfg.keys_folder, data['_id']), 'wb') as f:
            f.write(pem)

        print("generated private key 1")

        helper.file_to_redis(store, 'pr1-{}.pem'.format(data['_id']))

        pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        app.config['keys_dir'] = os.getcwd()
        with open('{}/pu1-{}.pem'.format(cfg.keys_folder, data['_id']), 'wb') as f:
            f.write(pem)

        print("generated public key 1")

        helper.file_to_redis(store, 'pu1-{}.pem'.format(data['_id']))

        try:
            print("sharing public key 1 to client")
            return send_from_directory(app.config["keys_dir"],
                                       filename='{}/pu1-{}.pem'.format(cfg.keys_folder, data['_id']),
                                       as_attachment=True)
        except FileNotFoundError:
            abort(404)
    except Exception as ex:
        print(ex)
        return "Hello World!"


@app.route("/receivePubKey", methods=['POST'])
def receivePubKey():
    data = request.data
    my_json = data.decode('utf8').replace("'", '"')
    print("received encrypted public key 2")
    data = json.loads(my_json)
    helper.decrypt_message(store, data)
    print("decryted public key 2 using private key 1")
    helper.symetricKey_generation(store, data['_id'])
    response_payload = helper.transmit_symetricKey(store, data['_id'])
    return jsonify(response_payload), 200

@app.route('/cpuUsage')
def cpu():
    cpu_usage = psutil.cpu_percent()
    return str(cpu_usage)

@app.route('/memoryUsage')
def memory():
    memory_usage = psutil.virtual_memory().percent/100
    return str(memory_usage)

@app.route('/healthcheck')
def healthcheck():
    return 'OK'

if __name__ == '__main__':
    port = sys.argv[1]
    app.run(host='0.0.0.0', port=port)