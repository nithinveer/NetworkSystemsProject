import yaml
from models import Server
import random

def load_configuration(path):
    with open(path) as config_file:
        config = yaml.load(config_file, Loader=yaml.FullLoader)
    return config

def transform_backends_from_config(config):
    register = []
    for entry in config['servers']:
        register.append(Server(entry))
    return register

def get_healthy_server(register):
    try:
        return least_connections([server for server in register if server.healthy])
    except IndexError:
        return None

def healthcheck(register):
    print("healthcheck")
    for server in register:
        server.healthcheck_and_update_status()
    return register

def least_connections(servers):
    print("find server")
    if not servers:
        return None
    return min(servers, key=lambda x: x.status)