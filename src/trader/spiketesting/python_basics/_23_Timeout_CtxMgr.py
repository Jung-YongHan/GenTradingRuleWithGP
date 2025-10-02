import requests
import eventlet

eventlet.monkey_patch()

# def request2(method, url, strict_timeout, **kwargs):
#     try:
#         with eventlet.Timeout(strict_timeout) as t:
#             return requests.request("GET", url, **kwargs)
#     except eventlet.Timeout as te:
#         raise te
#     except Exception as exp:
#         raise exp

from bulltrader.utils.net_utils import request2

try:
    # headers = {"Accept": "application/json"}
    # querystring = {"count": 1, "market": 'KRW-BTC'}
    headers = None
    querystring = None

    # timeout = 3
    strict_timeout = 2.5
    url = "http://ipv4.download.thinkbroadband.com/1MB.zip"

    response = request2("GET", url, strict_timeout = strict_timeout, headers=headers, params = querystring, verify=False)
    print(response.text)
except eventlet.Timeout as te:
    print(f'Eventlet.Timeout Exception: the request does not executed within {str(te)} sec.')
except requests.exceptions.Timeout as tout:
    print(f'Timeout Exception:{str(tout)}')
except Exception as exp:
    print(f'Exception:{str(exp)}')


# def request_wh_timeout(timeout_sec, url, error_callback_mtd):
#     try:
#         with eventlet.Timeout(timeout_sec) as t:
#             start_t = start_timing()
#             print(f'processing: {url}')
#             response = requests.get(url, verify=False)
#             end_n_elapsed_time(start_t, 'processing done..')
#     except eventlet.Timeout as te:
#         if te != t:
#             raise
#         print(f'TIMEOUT!! It passed {timeout_sec} sec..')
#         error_callback_mtd()
#
# def error_call_back_m1():
#     print('call backed!!')
#
# request_wh_timeout(5, "http://ipv4.download.thinkbroadband.com/1MB.zip", error_call_back_m1)
# request_wh_timeout(3, "http://ipv4.download.thinkbroadband.com/1MB.zip", error_call_back_m1)
# request_wh_timeout(2, "http://ipv4.download.thinkbroadband.com/1MB.zip", error_call_back_m1)
# request_wh_timeout(1, "http://ipv4.download.thinkbroadband.com/1MB.zip", error_call_back_m1)
# request_wh_timeout(0.5, "http://ipv4.download.thinkbroadband.com/1MB.zip", error_call_back_m1)
# request_wh_timeout(0.3, "http://ipv4.download.thinkbroadband.com/1MB.zip", error_call_back_m1)
#

