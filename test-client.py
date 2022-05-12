import requests

res = requests.post('http://0.0.0.0:5000/api/search_connect', json={ 'mac': '0000000000000000' })
print(res.content)
