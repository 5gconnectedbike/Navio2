import urllib.parse
import urllib.request
import json

params = urllib.parse.urlencode({"username": "eric", "password":"ctc123"}).encode()
contents = urllib.request.urlopen('http://democut3.canadaeast.cloudapp.azure.com/rest/ctcapi/v3/auth/login?' ,data=params)

data = json.loads(contents.read().decode(contents.info().get_param('charset') or 'utf-8'))
print(data)

print(data['token'])
