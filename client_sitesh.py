import requests


def send_msg():
	response = requests.get('http://127.0.0.1:5000/23456')
	print(response.text)


if __name__ == '__main__':
	send_msg()