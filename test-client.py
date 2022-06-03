import requests, random
from optparse import OptionParser

host = "muizenval.tk"
port = 80

parser = OptionParser()
parser.add_option('-c', '--connect', action="store_true", help='ready to connect')
parser.add_option('-s', '--status', type="choice", choices=[ "idle", "active" ], help='set status')
parser.add_option('-m', '--mac', type='string', help='mac-address to use, otherwise random')

opt, args = parser.parse_args()

if (opt.connect is None) == (opt.status is None):
	print("Error: either '--connect' or '--status' has to be specified")
	print()
	parser.print_help()
	exit()

if opt.mac:
	mac = opt.mac
else:
	mac = ''.join([ random.choice('0123456789ABCDEF') for _ in range(16) ])

print('using mac:', mac)

if opt.connect:
	res = requests.post(f'http://{host}:{port}/api/search_connect', json={ 'mac': mac })
	print('->', res.json()['error'])
elif opt.status == 'idle':
	res = requests.post(f'http://{host}:{port}/api/update_status', json={ 'mac': mac, 'status': False })
	print('->', res.json()['error'])
else:
	res = requests.post(f'http://{host}:{port}/api/update_status', json={ 'mac': mac, 'status': True })
	print('->', res.json()['error'])
