from http.client import HTTPConnection

import serial
import random
import sys
import json

if len(sys.argv) < 2:
	print(f'{sys.argv[0]} <serial>')

server_address = 'localhost', 5000
serial_port = serial.Serial(port=sys.argv[1], baudrate=115200)
debug_chars = '0123456789abcdefghijklmnopqrstuvwxyz'

client = HTTPConnection(server_address[0], server_address[1])

debug_token = ''.join(random.choice(debug_chars) for _ in range(16))

while serial_port.is_open:
	try:
		command, params_raw = serial_port.readline().decode().split(' ', 1)
		params = json.loads(params_raw)

		if command == 'hello':
			serial_port.write(f'ok {json.dumps(dict(debugToken=debug_token))}\n'.encode())
		elif command == 'send':
			method, endpoint, body = params["method"], params["endpoint"], params["body"]
			print(f'-> {method} {endpoint} {body}')

			client.request(method, endpoint, json.dumps(body))
			res = client.getresponse()
			response = res.read().decode()
			print(f'<- {res.status} {response}')

			serial_port.write(f'ok {json.dumps(dict(code=res.status, body=response))}\n'.encode())
	except:
		serial_port.write(b'0 {}\n')
