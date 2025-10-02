import hashlib
import json
from urllib.parse import urlencode, unquote
import uuid
import jwt
import requests
from pyupbit import Upbit
import pandas as pd
from bt4.utils.pandas_utils import sort_df
from bt4.utils.mylog import init_log
from bt4.utils.python_utils import now_dt

log = init_log()

@DeprecationWarning
class Upbit_Ex(Upbit):
    def __init__(self, access, secret, test_mode = False):
        super(Upbit_Ex, self).__init__(access, secret)
        self.server_url = 'https://api.upbit.com/'
        self.test_mode = test_mode

    ## state를 하나의 변수만 받았는데, list로 받을수 있게함
    ## 2021년 3월 22일부터 미체결 주문(wait, watch)과 완료 주문(done, cancel)을 혼합하여 조회하실 수 없습니다.
    ## 예시1) done, cancel 주문을 한 번에 조회 => 가능 ==> 실제로 해보니 한꺼번에 조회되지 않음.
    ## 예시2) wait, done 주문을 한 번에 조회 => 불가능 (각각 API 호출 필요)
    def get_settled_orders(self, markets):
        sett_odr_df = pd.DataFrame()

        states = ['done', 'cancel']
        for state in states:
            state_df = self.__get_settled_order_in_state(state)
            sett_odr_df = pd.concat([sett_odr_df, state_df], ignore_index=True)

        sett_odr_df.set_index(['created_at'], drop=False, inplace=True)
        sort_df(sett_odr_df, 'created_at', ascending=False)
        return sett_odr_df

    def __get_settled_order_in_state(self, state):
        query = {
            'state': state,
            'order_by': 'desc'
        }
        m = hashlib.sha512()
        m.update(urlencode(query, doseq=True).replace("%5B%5D=", "[]=").encode())
        query_hash = m.hexdigest()
        payload = {
            'access_key': self.access,
            'nonce': str(uuid.uuid4()),
            'query_hash': query_hash,
            'query_hash_alg': 'SHA512',
        }
        jwt_token = jwt.encode(payload, self.secret)
        authorize_token = 'Bearer {}'.format(jwt_token)
        # print(f'authorize_token:{authorize_token}')
        headers = {"Authorization": authorize_token}
        res = requests.get('https://api.upbit.com/v1/orders', params=query, headers=headers)
        if res.status_code != 200:
            log.error(f'ERROR! Fetching settlement data of the access key({self.access}) has been failed!')
            return []
        return pd.DataFrame.from_records(res.json())

    #############################################################
    ### Withdraw Operations
    def withdraw_cash(self, amount):
        if self.test_mode:
            dummy_resp = {'type': 'withdraw', 'uuid': 'xxxxxxxx-58e2-4b3a-a2dd-634680694f5d', 'currency': 'KRW', 'txid': None, 'holder': None, 'confirmations': 0, 'blockchain_url': None, 'state': 'processing', 'state_i18n': '출금진행중', 'created_at': '2022-10-28T16:01:48+09:00', 'done_at': None, 'amount': '10000.0', 'fee': '1000.0', 'krw_amount': '10000.0', 'fiat_amount': '10000.0', 'fiat_currency': 'KRW', 'transaction_type': 'default', 'bank': '', 'address': '', 'memo': None, 'cancelable': False}
            return dummy_resp
        else:
            return super(Upbit_Ex, self).withdraw_cash(amount)

    def get_withdraw_account_info(self, currency):
        if self.test_mode:
            dummy_resp = {'member_level': {'security_level': 3, 'fee_level': 0, 'email_verified': True,
                              'identity_auth_verified': True, 'bank_account_verified': True,
                              'kakao_pay_auth_verified': False, 'two_factor_auth_verified': True, 'locked': False,
                              'wallet_locked': False},
             'currency': {'code': 'KRW', 'withdraw_fee': '1000.0', 'is_coin': False, 'wallet_state': 'working',
                          'wallet_support': ['deposit', 'withdraw']},
             'account': {'currency': 'KRW', 'balance': '8504199.86473706', 'locked': '0.0', 'avg_buy_price': '0',
                         'avg_buy_price_modified': True, 'unit_currency': 'KRW'},
             'withdraw_limit': {'currency': 'KRW', 'onetime': '50000000.0', 'daily': '200000000.0',
                                'remaining_daily': '200000000.0', 'remaining_daily_fiat': '200000000.0',
                                'fiat_currency': 'KRW', 'minimum': '5000.0', 'fixed': 0, 'withdraw_delayed_fiat': '0.0',
                                'can_withdraw': True, 'remaining_daily_krw': '3000.0'}}

            return dummy_resp['member_level'], dummy_resp['account'], dummy_resp['withdraw_limit']

        params = {
            'currency': currency
        }
        query_string = unquote(urlencode(params, doseq=True)).encode("utf-8")

        m = hashlib.sha512()
        m.update(query_string)
        query_hash = m.hexdigest()

        payload = {
            'access_key': self.access,
            'nonce': str(uuid.uuid4()),
            'query_hash': query_hash,
            'query_hash_alg': 'SHA512',
        }

        jwt_token = jwt.encode(payload, self.secret)
        authorization = 'Bearer {}'.format(jwt_token)
        headers = {
            'Authorization': authorization,
        }

        res = requests.get(self.server_url + '/v1/withdraws/chance', params=params, headers=headers)

        if res.status_code != 200:
            log.error(f'ERROR! Fetching withdraw account information of ({self.access}) has been failed!')
            return ''
        result_dic = res.json()
        return result_dic['member_level'], result_dic['account'], result_dic['withdraw_limit']

    def get_withdraw_history(self, currency):
        params = {
            'currency': currency
        }

        query_string = unquote(urlencode(params, doseq=True)).encode("utf-8")

        m = hashlib.sha512()
        m.update(query_string)
        query_hash = m.hexdigest()

        payload = {
            'access_key': self.access,
            'nonce': str(uuid.uuid4()),
            'query_hash': query_hash,
            'query_hash_alg': 'SHA512',
        }

        jwt_token = jwt.encode(payload, self.secret)
        authorization = 'Bearer {}'.format(jwt_token)
        headers = {
            'Authorization': authorization,
        }

        res = requests.get(self.server_url + '/v1/withdraws', params=params, headers=headers)
        df = pd.DataFrame.from_records(res.json())
        df = df.set_index(['created_at'], drop=False)
        df.index.name = 'created_at'
        df.index = pd.to_datetime(df.index)
        df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%dT%H:%M:%S')
        df['done_at'] = pd.to_datetime(df['done_at']).dt.strftime('%Y-%m-%dT%H:%M:%S')
        df = df.astype({'amount': 'float', 'fee': 'float'})
        col_list = ['created_at', 'done_at', 'amount', 'fee', 'state']
        return df[col_list]

    def get_API_key_expire_date(self):
        payload = {
            'access_key': self.access,
            'nonce': str(uuid.uuid4()),
        }

        jwt_token = jwt.encode(payload, self.secret)
        authorization = 'Bearer {}'.format(jwt_token)
        headers = {
            'Authorization': authorization,
        }

        res = requests.get(self.server_url + '/v1/api_keys', params=None, headers=headers)
        key_list = res.json()
        # print(key_list)
        if 'error' not in key_list:
            for key_ in key_list:
                if key_['access_key'] == self.access:
                    expired_at = key_['expire_at']
                    expired_at = pd.to_datetime(expired_at).tz_localize(None).strftime("%Y-%m-%dT%H:%M:%S")
                    remaining_days = (pd.to_datetime(expired_at) - pd.to_datetime(now_dt())).days
                    return expired_at, remaining_days, None
            return None, None, f'No API Key({self.access}) exists in the list.'
        else:
            err_msg = key_list['error']['message']
            return None, None, err_msg

    def get_deposite_history(self, currency):
        params = {
            'currency': currency
        }
        query_string = unquote(urlencode(params, doseq=True)).encode("utf-8")

        m = hashlib.sha512()
        m.update(query_string)
        query_hash = m.hexdigest()

        payload = {
            'access_key': self.access,
            'nonce': str(uuid.uuid4()),
            'query_hash': query_hash,
            'query_hash_alg': 'SHA512',
        }

        jwt_token = jwt.encode(payload, self.secret)
        authorization = 'Bearer {}'.format(jwt_token)
        headers = {
            'Authorization': authorization,
        }

        res = requests.get(self.server_url + '/v1/deposits', params=params, headers=headers)
        key_list = res.json()
        # print(key_list)
        if 'error' not in key_list:
            df = pd.DataFrame.from_records(res.json())
            df = df.set_index(['created_at'], drop=False)
            df.index.name = 'created_at'
            df.index = pd.to_datetime(df.index)
            df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%dT%H:%M:%S')
            df['done_at'] = pd.to_datetime(df['done_at']).dt.strftime('%Y-%m-%dT%H:%M:%S')
            df = df.astype({'amount': 'float', 'fee': 'float'})
            col_list = ['created_at', 'done_at', 'amount', 'fee', 'state']
            return df[col_list], None
        else:
            err_msg = key_list['error']['message']
            return None, err_msg

    def deposit_cash(self, amount):

        params = {
            'amount': amount
        }
        query_string = unquote(urlencode(params, doseq=True)).encode("utf-8")

        m = hashlib.sha512()
        m.update(query_string)
        query_hash = m.hexdigest()

        payload = {
            'access_key': self.access,
            'nonce': str(uuid.uuid4()),
            'query_hash': query_hash,
            'query_hash_alg': 'SHA512',
        }

        jwt_token = jwt.encode(payload, self.secret)
        authorization = 'Bearer {}'.format(jwt_token)
        headers = {
            'Authorization': authorization,
        }

        res = requests.post(self.server_url + '/v1/deposits/krw', json=params, headers=headers)
        return res.json()