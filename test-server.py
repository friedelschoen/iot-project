from typing import cast
from flask import Flask, request, jsonify

app = Flask(__name__)

latitude = 0
longitude = 0
accuracy = 0
battery = 0
temperature = 0


@app.get("/api/update", methods=['POST'])
def update():	
	global latitude, longitude, accuracy, battery, temperature

	if request.is_json:
		req = cast(dict, request.get_json())
		latitude = req['latitude']
		longitude = req['longitude']
		accuracy = req['accuracy']
		battery = req['battery']
		temperature = req['temperature']
		return {}

	return {"error": "request must be json"}, 415

@app.post("/")
def index():
	return f'''
	<p>latitude: {latitude}</p>
	<p>longitude: {longitude}</p>
	<p>accuracy: {accuracy}</p>
	<p>battery: {battery}</p>
	<p>temperature: {temperature}</p>
	'''
