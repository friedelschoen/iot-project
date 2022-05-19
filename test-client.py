import requests, random

mac = ''.join([ random.choice('0123456789ABCDEF') for _ in range(16) ])

res = requests.post('http://0.0.0.0:5000/api/search_connect', json={ 'mac': mac })
print('MAC:', mac)
print('Answer:', res.content)


#mac = '90FD852087386BE9'
#res = requests.post('http://0.0.0.0:5000/api/update_status', json={ 'mac': mac, 'status': False })
