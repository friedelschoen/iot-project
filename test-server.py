from flask import json
from werkzeug.exceptions import HTTPException
from flask import Flask, request

app = Flask(__name__)

status = {}

@app.post("/api/update")
def update():	
	global status

	req = request.get_json(True)
	if not req:
		return
	status = req
	return {}

@app.get("/")
def index():
	return f'''
	 <link rel="stylesheet" href="https://unpkg.com/leaflet@1.8.0/dist/leaflet.css"
   integrity="sha512-hoalWLoI8r4UszCkZ5kL8vayOGVae1oxXe/2A4AO6J9+580uKHDO3JdHb7NzwwzK5xr/Fs0W40kiNHxM9vyTtQ=="
   crossorigin=""/>
	<script src="https://unpkg.com/leaflet@1.8.0/dist/leaflet.js"
   integrity="sha512-BB3hKbKWOc9Ez/TAwyWxNXeoV9c1v6FIeYiBieIWkpLjauysF18NzgR1MBNBXf8/KABdlkX68nAhlwcDFLGPCQ=="
   crossorigin=""></script>

	<h1>Status update</h1>
	<p>latitude: <code>{status['']:.10f}</code></p>
	<p>longitude: <code>{longitude:.10f}</code></p>
	<p>accuracy: <code>{accuracy:.2f}%</code></p>
	<p>battery: <code>{battery}V</code></p>
	<p>temperature: <code>{temperature}&deg;c</code></p>

	<div id="map" style='height: 50%;'></div>

	<script type="text/javascript">
	var map = L.map('map').setView([52.283333, 5.666667], 7);
	L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
		maxZoom: 19,
		attribution: '© OpenStreetMap'
	}}).addTo(map);
	var marker = L.marker([{latitude}, {longitude}]).addTo(map);
	</script>
	'''

@app.errorhandler(HTTPException)
def handle_exception(e):
    response = e.get_response()
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"
    return response

app.run('0.0.0.0', 5000)
