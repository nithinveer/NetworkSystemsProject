from flask import Flask, jsonify
import json

app = Flask(__name__)


#@app.route("/<arg>")
#def home(arg):
#	person = {'name': 'Alice', 'birth-year': 1986}
#	return jsonify(person)

@app.route("/<arg>", methods=['POST', 'GET'])
def home(arg):
	f = open('student_data.json',)
	data = json.load(f)
	for i in data['student_details']:
		if i['student_id'] == arg:
			return jsonify(i)
	return  jsonify({'name': 'Alice', 'birth-year': 1986})

if __name__ == "__main__":
	app.run(debug=True)