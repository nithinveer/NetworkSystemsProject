import requests
from flask import Flask, request

from utils import (
    get_healthy_server,
    healthcheck,
    load_configuration,
    transform_backends_from_config,
)

loadbalancer = Flask(__name__)

config = load_configuration('loadbalancer.yaml')
register = transform_backends_from_config(config)

@loadbalancer.route('/')
@loadbalancer.route('/<path>', methods=['POST', 'GET'])
def router(path='/'):
    updated_register = healthcheck(register)

    healthy_server = get_healthy_server(register)

    if not healthy_server:
        return 'No backend servers available.', 503

    data = request.data
    headers = request.headers
    args = request.args

    path = request.full_path
    url = 'http://' + healthy_server.endpoint + path

    print("sending request " + path + " to ", str(healthy_server.endpoint))

    if request.method == 'POST':
        response = requests.post(url, data = data, headers = headers)
    elif request.method == 'GET':
        response = requests.get(url, data = data, headers = headers)

    return response.content, response.status_code

if __name__ == '__main__':
    loadbalancer.run(host='0.0.0.0')