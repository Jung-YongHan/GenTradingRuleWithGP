import requests

# url = "https://api.upbit.com/v1/orderbook"
#
# querystring = {"markets":"KRW-BTC"}
# headers = {"Accept": "application/json"}
# response = requests.request("GET", url, headers=headers, params=querystring)
# print(response.text)


import requests

# url = "https://api.upbit.com/v1/candles/days"
url = "https://api.upbit.com/v1/candles/minutes/1"
querystring = {"count":"1", "market": 'KRW-BTC', "to":'2018-10-03T09:00:00Z'}
headers = {"Accept": "application/json"}
response = requests.request("GET", url, headers=headers, params=querystring)
# 2018-10-03T09:00:00,,KRW-BTC,7369000.0,7393000.0,7299000.0,7386000.0
print(response.text)

url = "https://api.upbit.com/v1/candles/days"
querystring = {"count":"1", "market": 'KRW-BTC', "to":'2018-10-04T00:00:00Z'}
headers = {"Accept": "application/json"}
response = requests.request("GET", url, headers=headers, params=querystring)
# 2018-10-04T00:00:00,,KRW-BTC,7369000.0,7393000.0,7299000.0,7386000.0
print(response.text)



