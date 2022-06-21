from http.client import HTTPConnection

import serial
import sys
import json

if len(sys.argv) < 2:
	print(f'{sys.argv[0]} <serial>')

server_address = 'localhost', 5000
serial_port = serial.Serial(port=sys.argv[1], baudrate=115200)

client = HTTPConnection(server_address[0], server_address[1])

while serial_port.is_open:
	try:
		method, endpoint, body = serial_port.readline().decode().split(' ', 2)
		print(f'-> {method} {endpoint} {body}')

		client.request(method, endpoint, body)
		res = client.getresponse()
		response = res.read().decode()
		print(f'<- {res.status} {response}')

		serial_port.write(f'{res.status} {response}'.encode())
	except:
		serial_port.write(b'0 {}\n')
