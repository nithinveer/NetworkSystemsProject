import requests


class Server:
    def __init__(self, endpoint, path='/healthcheck'):
        self.endpoint = endpoint
        self.path = path
        self.healthy = True
        self.timeout = 1
        self.scheme = 'http://'
        self.status = 0

    def healthcheck_and_update_status(self):
        try:
            response = requests.get(self.scheme + self.endpoint + self.path, timeout=self.timeout)
            if response.ok:
                self.healthy = True

                cpu_usage = requests.get(self.scheme + self.endpoint + '/cpuUsage', timeout=self.timeout).content
                memory_usage = requests.get(self.scheme + self.endpoint + '/memoryUsage', timeout=self.timeout).content

                self.status = 0.5 * (float(cpu_usage) + float(memory_usage))
            else:
                self.healthy = False

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            self.healthy = False

    def __eq__(self, other):
        if isinstance(other, Server):
            return self.endpoint == other.endpoint
        return False

    def __repr__(self):
        return f'<Server: {self.endpoint} {self.healthy} {self.timeout}>'
