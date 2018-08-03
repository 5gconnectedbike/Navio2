import urllib.parse
import urllib.request
import json

def get_token():
    params = urllib.parse.urlencode({"username": "eric", "password":"ctc123"}).encode()
    contents = urllib.request.urlopen('http://democut3.canadaeast.cloudapp.azure.com/rest/ctcapi/v3/auth/login?' ,data=params)

    data = json.loads(contents.read().decode(contents.info().get_param('charset') or 'utf-8'))

    return data['token']

def create_Device():
    url = 'http://democut3.canadaeast.cloudapp.azure.com/rest/ctcapi/v3/devices'

    data = urllib.parse.urlencode({"deviceTypeKey": 113001, "externalId": "Test05", "name": "Test05", "serviceId": "db39fd3e-7ad5-44be-a817-01fcb608efbb", "smartObjects": [], "metas": {}}).encode()
    
    headers = {
        'x-access-token': 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiZXJpYyIsInVzZXJJZCI6IjM2YmE5ZWIzLTU1NDYtNGI2Mi1hNjI2LTlkZWIyYTZkYTg2YiIsInJvbGVJZHMiOlsiMSIsImVjNDg1MGRmLWM5ZTItNGRkYy05ODMyLTRhZjEyYTEyY2ExMiJdLCJvcmdhbml6YXRpb25JZHMiOlsiYWFkZTBmZDQtMjQ3OS00OTM4LThjMjgtNmI3NzhmZGI5ZTE1Il0sIm9yZ2FuaXphdGlvbklkIjoiYWFkZTBmZDQtMjQ3OS00OTM4LThjMjgtNmI3NzhmZGI5ZTE1IiwiaWF0IjoxNTMzMjQ4MDIxLCJleHAiOjE1MzMyNTE2MjF9.ZNDG2KTAgGVDWgnhExR3D4BOoQ8hz1_akamAfOw4R8-yelv-rWtRK0MX_kPL4nFdl0_Kgh28lbLsyPGcOA6Q4izvtSCW9JYK3HKXdo2kTiP_IFMyJrMGoB6Ih6lD5bhQ8RLHjHovhMywy7YDhnX_j3EIeu8vXuursU2bv8nc_0IlgOk63MRDqkBIz612c0LQf5mfySxmLli6uUkCSdrSuT5l2PYl3H6z3Xelqh2svRzW9ZV4Mk5XZvLqLi0C9DfJB8l_HJz5jxN5QEVkr8m8a5ciZrp1e7rXU3vW0maaQH81I3f996usURc8LUPCA8EvFQmXAlTYbdzYilA_qaSXoA'
        }
    
    req = urllib.request.Request(url, data=data)
    req.add_header('x-access-token', 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiZXJpYyIsInVzZXJJZCI6IjM2YmE5ZWIzLTU1NDYtNGI2Mi1hNjI2LTlkZWIyYTZkYTg2YiIsInJvbGVJZHMiOlsiMSIsImVjNDg1MGRmLWM5ZTItNGRkYy05ODMyLTRhZjEyYTEyY2ExMiJdLCJvcmdhbml6YXRpb25JZHMiOlsiYWFkZTBmZDQtMjQ3OS00OTM4LThjMjgtNmI3NzhmZGI5ZTE1Il0sIm9yZ2FuaXphdGlvbklkIjoiYWFkZTBmZDQtMjQ3OS00OTM4LThjMjgtNmI3NzhmZGI5ZTE1IiwiaWF0IjoxNTMzMjQ4ODE0LCJleHAiOjE1MzMyNTI0MTR9.jXJzIb9xUjGJ83OF0cM3f5oUQDuyox7kq-fdv79O91iHh4v0AuN6HUoONzwQvnDfwSL0zwZUGgd6B51bUcqcNo-LC5qDtWxoxz0vdPhn39YimKhrmmmXMkAx713MrDoGmAGFa5eFR0PRknWfE2oexwgrZNwSnFfMju56ionybJV_KQJXpUyfN8ju-r_-9PyAM8JYaeqznpHwvylv0w0iAosXPWZJsWx5nGN23JrLwZm9K3K_bt9UthJYIrUS2tfDq505w1n-0n8A5W28FtGaJCLf2MvLUiM9QCGRbNMFO55bDPE6yvFXL3mcIkMtl5yONydVUnLjfgWXlJghk4oZkw')
    response = urllib.request.urlopen(req)
    the_page = response.read()

    # req = urllib.request.Request('http://democut3.canadaeast.cloudapp.azure.com/rest/ctcapi/v3/devices?')
    # token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiZXJpYyIsInVzZXJJZCI6IjM2YmE5ZWIzLTU1NDYtNGI2Mi1hNjI2LTlkZWIyYTZkYTg2YiIsInJvbGVJZHMiOlsiMSIsImVjNDg1MGRmLWM5ZTItNGRkYy05ODMyLTRhZjEyYTEyY2ExMiJdLCJvcmdhbml6YXRpb25JZHMiOlsiYWFkZTBmZDQtMjQ3OS00OTM4LThjMjgtNmI3NzhmZGI5ZTE1Il0sIm9yZ2FuaXphdGlvbklkIjoiYWFkZTBmZDQtMjQ3OS00OTM4LThjMjgtNmI3NzhmZGI5ZTE1IiwiaWF0IjoxNTMzMjQ3MzA3LCJleHAiOjE1MzMyNTA5MDd9.WCuNj8Q_rDcQUWaKymule9hw1mHMrrme7Mzpkf6fpTF17lhmCaZ06B-jpTRWz_qKpsZ1c6dStoLU2DQGCAx6swYkqdzG63cpWiduk0UnEj0F56CxixRL2H7Cvqv58ega7Rs6F0KuTyLQ_QqoUzWRPK-KQ5WVBpRVuMBMRfgwinUt9d141Q8Wi6QzKjj_c1jLFcEIyMK_jwanHDmKi6wSJkmmvmTgtfM9Tb2d2qXD1yvaNT0ZuWey43bkyLirH_UxENsJtZfvMxqxUzGTsBKjq79VJkMj3045Cej3bCKCSlDsE9o7CCA6keoABviLsB_igQ5z39ZAJqd3hJherUHyNA"
    # req.add_header('x-access-token', 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiZXJpYyIsInVzZXJJZCI6IjM2YmE5ZWIzLTU1NDYtNGI2Mi1hNjI2LTlkZWIyYTZkYTg2YiIsInJvbGVJZHMiOlsiMSIsImVjNDg1MGRmLWM5ZTItNGRkYy05ODMyLTRhZjEyYTEyY2ExMiJdLCJvcmdhbml6YXRpb25JZHMiOlsiYWFkZTBmZDQtMjQ3OS00OTM4LThjMjgtNmI3NzhmZGI5ZTE1Il0sIm9yZ2FuaXphdGlvbklkIjoiYWFkZTBmZDQtMjQ3OS00OTM4LThjMjgtNmI3NzhmZGI5ZTE1IiwiaWF0IjoxNTMzMjQ3MzA3LCJleHAiOjE1MzMyNTA5MDd9.WCuNj8Q_rDcQUWaKymule9hw1mHMrrme7Mzpkf6fpTF17lhmCaZ06B-jpTRWz_qKpsZ1c6dStoLU2DQGCAx6swYkqdzG63cpWiduk0UnEj0F56CxixRL2H7Cvqv58ega7Rs6F0KuTyLQ_QqoUzWRPK-KQ5WVBpRVuMBMRfgwinUt9d141Q8Wi6QzKjj_c1jLFcEIyMK_jwanHDmKi6wSJkmmvmTgtfM9Tb2d2qXD1yvaNT0ZuWey43bkyLirH_UxENsJtZfvMxqxUzGTsBKjq79VJkMj3045Cej3bCKCSlDsE9o7CCA6keoABviLsB_igQ5z39ZAJqd3hJherUHyNA')

    # contents = urllib.request.urlopen(req, data=params)
    # import requests
    # from requests.auth import HTTPBasicAuth
    # # import json
    # # # request = Request
    # params = {
    #     "deviceTypeKey": 113001,
    #     "externalId": "Test01",
    #     "name": "Test01",
    #     "serviceId": "db39fd3e-7ad5-44be-a817-01fcb608efbb",
    #     "smartObjects": [],
    #     "metas": {}
    #     }

    # # # headers = 
    # response = requests.post(
    #     url, 
    #     data = params,
    #     header=('x-access-token','eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiZXJpYyIsInVzZXJJZCI6IjM2YmE5ZWIzLTU1NDYtNGI2Mi1hNjI2LTlkZWIyYTZkYTg2YiIsInJvbGVJZHMiOlsiMSIsImVjNDg1MGRmLWM5ZTItNGRkYy05ODMyLTRhZjEyYTEyY2ExMiJdLCJvcmdhbml6YXRpb25JZHMiOlsiYWFkZTBmZDQtMjQ3OS00OTM4LThjMjgtNmI3NzhmZGI5ZTE1Il0sIm9yZ2FuaXphdGlvbklkIjoiYWFkZTBmZDQtMjQ3OS00OTM4LThjMjgtNmI3NzhmZGI5ZTE1IiwiaWF0IjoxNTMzMjQ3MzA3LCJleHAiOjE1MzMyNTA5MDd9.WCuNj8Q_rDcQUWaKymule9hw1mHMrrme7Mzpkf6fpTF17lhmCaZ06B-jpTRWz_qKpsZ1c6dStoLU2DQGCAx6swYkqdzG63cpWiduk0UnEj0F56CxixRL2H7Cvqv58ega7Rs6F0KuTyLQ_QqoUzWRPK-KQ5WVBpRVuMBMRfgwinUt9d141Q8Wi6QzKjj_c1jLFcEIyMK_jwanHDmKi6wSJkmmvmTgtfM9Tb2d2qXD1yvaNT0ZuWey43bkyLirH_UxENsJtZfvMxqxUzGTsBKjq79VJkMj3045Cej3bCKCSlDsE9o7CCA6keoABviLsB_igQ5z39ZAJqd3hJherUHyNA'))

    # # params = urllib.parse.urlencode({
    # #     "deviceTypeKey": 126001,
    # #     "externalId": "Test01",
    # #     "name": "Test01",
    #     "serviceId": "db39fd3e-7ad5-44be-a817-01fcb608efbb",
    #     "smartObjects": [],
    #     "metas": {}
    #     }).encode()
    # contents = urllib.request.urlopen('http://democut3.canadaeast.cloudapp.azure.com/rest/ctcapi/v3/devices',  data=params)
    
    # data = json.loads(contents.read().decode(contents.info().get_param('charset') or 'utf-8'))
    return the_page

if __name__ == '__main__':
    # token = get_token()
    # print(token)

    data = create_Device()
    print(data.content)
    print(data.text)
    print(data.status_code)
    print(data['id'])
