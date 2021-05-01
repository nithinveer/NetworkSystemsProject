import os
import time
import psutil
import sys
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify(
        message=f'This is the server application home page.',
        server=request.base_url,
    )

@app.route('/get')
def sample():
    return jsonify(
        message=f'This is the server application.',
        server=request.base_url,
    )

@app.route('/hello')
def helloworld():
    return jsonify(
        message=f'Hello from server application.',
        server=request.base_url,
    )

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