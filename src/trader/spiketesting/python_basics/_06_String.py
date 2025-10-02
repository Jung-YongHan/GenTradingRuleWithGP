
# mass = ['1','2','3','4','5']
#
# mas = ''.join(ma for ma in mass)
# print(mas)

def split_source_target_markets(market):
    result = market.split('-')
    return result[0], result[1]

source, target = split_source_target_markets('KRW-BTC')
print(source, target)

import json
response_body = '''
[
  {
    "market": "KRW-BTC",
    "candle_date_time_utc": "2021-11-15T08:37:00",
    "candle_date_time_kst": "2021-11-15T17:37:00",
    "opening_price": 79008000,
    "high_price": 79080000,
    "low_price": 79000000,
    "trade_price": 79008000,
    "timestamp": 1636965434322,
    "candle_acc_trade_price": 191041747.42501,
    "candle_acc_trade_volume": 2.4178989,
    "unit": 1
  }
]
'''

a_json = json.loads(response_body)
for key in a_json:
    print(key['candle_date_time_kst'])

print(a_json[0]['candle_date_time_kst'])

# kst_value = a_json('candle_date_time_kst')
# print(f'candle_date_time_kst : {kst_value}')