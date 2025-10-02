import json
from bulltrader.ui.monitor.message import Adm_Ctrl_Msg

import datetime as dt
# my_json_string = """[
#     {"market":"KRW-BTC","candle_date_time_utc":"2021-09-30T12:37:00","candle_date_time_kst":"2021-09-30T21:37:00","opening_price":52976000.00000000,"high_price":52976000.00000000,"low_price":52910000.00000000,"trade_price":52976000.00000000,"timestamp":1633005460406,"candle_acc_trade_price":91081484.20203000,"candle_acc_trade_volume":1.71978770,"unit":1},{"market":"KRW-ETH","candle_date_time_utc":"2021-09-30T12:37:00","candle_date_time_kst":"2021-09-30T21:37:00","opening_price":3658000.00000000,"high_price":3660000.00000000,"low_price":3658000.00000000,"trade_price":3659000.00000000,"timestamp":1633005461222,"candle_acc_trade_price":108822345.24824000,"candle_acc_trade_volume":29.74487900,"unit":1},{"market":"KRW-MTL","candle_date_time_utc":"2021-09-30T12:37:00","candle_date_time_kst":"2021-09-30T21:37:00","opening_price":3480.00000000,"high_price":3485.00000000,"low_price":3480.00000000,"trade_price":3485.00000000,"timestamp":1633005448692,"candle_acc_trade_price":6712139.64011040,"candle_acc_trade_volume":1928.58387719,"unit":1},{"market":"KRW-XRP","candle_date_time_utc":"2021-09-30T12:37:00","candle_date_time_kst":"2021-09-30T21:37:00","opening_price":1155.00000000,"high_price":1160.00000000,"low_price":1155.00000000,"trade_price":1160.00000000,"timestamp":1633005457376,"candle_acc_trade_price":103938588.76842995,"candle_acc_trade_volume":89923.93745027,"unit":1},{"market":"KRW-SRM","candle_date_time_utc":"2021-09-30T12:37:00","candle_date_time_kst":"2021-09-30T21:37:00","opening_price":8780.00000000,"high_price":8785.00000000,"low_price":8780.00000000,"trade_price":8780.00000000,"timestamp":1633005462150,"candle_acc_trade_price":73294167.82769710,"candle_acc_trade_volume":8345.97705822,"unit":1},{"market":"KRW-SAND","candle_date_time_utc":"2021-09-30T12:37:00","candle_date_time_kst":"2021-09-30T21:37:00","opening_price":792.00000000,"high_price":794.00000000,"low_price":792.00000000,"trade_price":794.00000000,"timestamp":1633005455125,"candle_acc_trade_price":17387214.51268126,"candle_acc_trade_volume":21926.43628436,"unit":1},
#     "error":{"name":404,"message":"Code not found"},
#     {"market":"KRW-DOT","candle_date_time_utc":"2021-09-30T12:37:00","candle_date_time_kst":"2021-09-30T21:37:00","opening_price":34300.00000000,"high_price":34300.00000000,"low_price":34290.00000000,"trade_price":34290.00000000,"timestamp":1633005462888,"candle_acc_trade_price":5772880.78992870,"candle_acc_trade_volume":168.31874676,"unit":1},{"market":"KRW-ETC","candle_date_time_utc":"2021-09-30T12:37:00","candle_date_time_kst":"2021-09-30T21:37:00","opening_price":57120.00000000,"high_price":57150.00000000,"low_price":57120.00000000,"trade_price":57150.00000000,"timestamp":1633005461901,"candle_acc_trade_price":16812820.74934100,"candle_acc_trade_volume":294.22342736,"unit":1},{"market":"KRW-PLA","candle_date_time_utc":"2021-09-30T12:37:00","candle_date_time_kst":"2021-09-30T21:37:00","opening_price":853.00000000,"high_price":855.00000000,"low_price":853.00000000,"trade_price":853.00000000,"timestamp":1633005462915,"candle_acc_trade_price":35536540.53422309,"candle_acc_trade_volume":41649.92732677,"unit":1},{"market":"KRW-DOGE","candle_date_time_utc":"2021-09-30T12:37:00","candle_date_time_kst":"2021-09-30T21:37:00","opening_price":247.00000000,"high_price":247.00000000,"low_price":247.00000000,"trade_price":247.00000000,"timestamp":1633005463027,"candle_acc_trade_price":44454167.96670993,"candle_acc_trade_volume":179976.38852919,"unit":1},{"market":"KRW-ADA","candle_date_time_utc":"2021-09-30T12:37:00","candle_date_time_kst":"2021-09-30T21:37:00","opening_price":2570.00000000,"high_price":2575.00000000,"low_price":2570.00000000,"trade_price":2575.00000000,"timestamp":1633005463803,"candle_acc_trade_price":103071918.07471640,"candle_acc_trade_volume":40094.19217634,"unit":1},{"market":"KRW-AHT","candle_date_time_utc":"2021-09-30T12:37:00","candle_date_time_kst":"2021-09-30T21:37:00","opening_price":11.90000000,"high_price":11.90000000,"low_price":11.80000000,"trade_price":11.90000000,"timestamp":1633005461862,"candle_acc_trade_price":6705032.49248221,"candle_acc_trade_volume":563490.83756794,"unit":1},{"market":"KRW-KAVA","candle_date_time_utc":"2021-09-30T12:37:00","candle_date_time_kst":"2021-09-30T21:37:00","opening_price":6425.00000000,"high_price":6465.00000000,"low_price":6425.00000000,"trade_price":6430.00000000,"timestamp":1633005463867,"candle_acc_trade_price":30743738.27317980,"candle_acc_trade_volume":4775.35534324,"unit":1},{"market":"KRW-LSK","candle_date_time_utc":"2021-09-30T12:37:00","candle_date_time_kst":"2021-09-30T21:37:00","opening_price":3895.00000000,"high_price":3895.00000000,"low_price":3895.00000000,"trade_price":3895.00000000,"timestamp":1633005464084,"candle_acc_trade_price":3054976.49978805,"candle_acc_trade_volume":784.33286259,"unit":1},{"market":"KRW-QTUM","candle_date_time_utc":"2021-09-30T12:37:00","candle_date_time_kst":"2021-09-30T21:37:00","opening_price":12260.00000000,"high_price":12280.00000000,"low_price":12250.00000000,"trade_price":12270.00000000,"timestamp":1633005460382,"candle_acc_trade_price":23800620.03063670,"candle_acc_trade_volume":1939.78482430,"unit":1},{"market":"KRW-BTG","candle_date_time_utc":"2021-09-30T12:37:00","candle_date_time_kst":"2021-09-30T21:37:00","opening_price":61710.00000000,"high_price":61710.00000000,"low_price":61710.00000000,"trade_price":61710.00000000,"timestamp":1633005453637,"candle_acc_trade_price":534135.04142130,"candle_acc_trade_volume":8.65556703,"unit":1},{"market":"KRW-EOS","candle_date_time_utc":"2021-09-30T12:37:00","candle_date_time_kst":"2021-09-30T21:37:00","opening_price":4750.00000000,"high_price":4755.00000000,"low_price":4750.00000000,"trade_price":4755.00000000,"timestamp":1633005463893,"candle_acc_trade_price":56028409.05784365,"candle_acc_trade_volume":11783.53564785,"unit":1},{"market":"KRW-TRX","candle_date_time_utc":"2021-09-30T12:37:00","candle_date_time_kst":"2021-09-30T21:37:00","opening_price":108.00000000,"high_price":109.00000000,"low_price":108.00000000,"trade_price":109.00000000,"timestamp":1633005464441,"candle_acc_trade_price":19083835.61216738,"candle_acc_trade_volume":176640.40364647,"unit":1},{"market":"KRW-XTZ","candle_date_time_utc":"2021-09-30T12:37:00","candle_date_time_kst":"2021-09-30T21:37:00","opening_price":7295.00000000,"high_price":7300.00000000,"low_price":7290.00000000,"trade_price":7290.00000000,"timestamp":1633005464519,"candle_acc_trade_price":26192662.59828915,"candle_acc_trade_volume":3590.43218509,"unit":1},{"market":"KRW-BCH","candle_date_time_utc":"2021-09-30T12:37:00","candle_date_time_kst":"2021-09-30T21:37:00","opening_price":611000.00000000,"high_price":611000.00000000,"low_price":610900.00000000,"trade_price":610900.00000000,"timestamp":1633005465219,"candle_acc_trade_price":4769722.58571000,"candle_acc_trade_volume":7.80658361,"unit":1}]"""
#
# to_python = json.loads(my_json_string)
# print(to_python)

# print(to_python['article'][0]['id'])
# print(to_python['article'][1]['id'])

## print(to_python['blog'])
# blog = {'URL': 'datacamp.com', 'name': 'Datacamp'}
# to_json = json.dumps(blog)
# print(to_json)

# my_json_string = """
# {
#   "accounts":
#           [
#             {
#               "alias":"stkim",
#               "access_key": "a",
#               "secrete_key": "b"
#             },
#             {
#               "alias":"sohyun",
#               "access_key": "a",
#               "secrete_key": "b"
#             },
#             {
#               "alias":"jungi",
#               "access_key": "a",
#               "secrete_key": "b"
#             }
#           ]
# }
# """
from bulltrader.utils.python_utils import now_str

my_json_string = """
{
  "stkim": {
    "access_key": "a",
    "secrete_key": "b"
  },
  "sohyun": {
    "access_key": "c",
    "secrete_key": "d"
  },
  "jungi": {
    "access_key": "e",
    "secrete_key": "f"
  }
}
"""
to_python = json.loads(my_json_string)
for name in to_python:
    print(name)
    keys = to_python[name]
    print(keys['access_key'])
    print(keys['secrete_key'])


###########################################
# time = dt.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
msg_json = Adm_Ctrl_Msg('1.0', 'force_buy', 'stkim', '07:59', now_str()).to_json()
msg_obj = Adm_Ctrl_Msg.from_json(msg_json)
print(f'msg_obj : {msg_obj.account} {msg_obj.control}')
