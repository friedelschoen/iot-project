from http.client import HTTPConnection
from typing import Optional

import serial
import sys
import json

if len(sys.argv) < 2:
	print(f'{sys.argv[0]} <port>')

serial_port = serial.Serial(port=sys.argv[1], baudrate=115200)

client: Optional[HTTPConnection] = None

def handle(req):
	global client

	if 'command' not in req:
		return 'command ommitted'
	elif req['command'] == 'hello':
		return None
	elif req['command'] == 'connect':
		client = HTTPConnection(req['host'], req['port'])
	elif req['command'] == 'send':
		if client is None:
			return 'not connected'
		client.request(req['method'], req['endpoint'], json.dumps(req['body']), req['headers'] or {})
		res = client.getresponse()
		return { 'code': res.status, 'headers': dict(res.headers), 'body': json.load(res) }
	else:
		return 'unknown command'

while serial_port.is_open:
	req = json.loads(serial_port.readline())

	print('-> ' + repr(req))
	res = handle(req)

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
