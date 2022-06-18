from http.client import HTTPConnection

import serial
import sys
import json

if len(sys.argv) < 2:
	print(f'{sys.argv[0]} <serial>')

server_address = ''
serial_port = serial.Serial(port=sys.argv[2], baudrate=115200)

client = None

def handle(req):
	global client

	if 'command' not in req:
		return 'command ommitted'
	elif req['command'] == 'hello':
		return None
	elif req['command'] == 'connect':
		client = HTTPConnection(req['host'], req['port'])
	elif req['command'] == 'send':
		headers = req['headers'] or {}
		headers['Content-Type'] = 'application/json'
		if client is None:
			return 'not connected'
		client.request(req['method'], req['endpoint'], json.dumps(req['body']), headers)
		res = client.getresponse()
		return { 'code': res.status, 'headers': dict(res.headers), 'body': json.load(res) }
	else:
		return 'unknown command'

while serial_port.is_open:
	try:
		req = json.loads(serial_port.readline())
		res = handle(req)
	except Exception as e:
		req = '<error>'
		res = { 'error': 'internal', 'description': str(e) }
	print('-> ' + repr(req))

	if type(res) == str:
		res = { "error": res }
	elif res is None:
		res = { "error": None }
	elif type(res) == dict:
		if 'error' not in res:
			res['error'] = None
	else:
		res = { "error": None, "value": res }
	print('<- ' + repr(res))

	serial_port.write((json.dumps(res) + '\n').encode())
