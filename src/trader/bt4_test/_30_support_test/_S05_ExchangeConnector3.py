import hashlib
import unittest
import uuid
from urllib.parse import urlencode, unquote
import jwt
import requests
import pandas as pd

from bt4_test._30_support_test._S03_ExchangeConnectorTest import stkim_upbit_access_key, stkim_upbit_secret_key

pd.set_option('display.max_columns', None)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('max_colwidth', None)

from bt4.utils.pyupbit_ex import Upbit_Ex

access_key = stkim_upbit_access_key
secret_key = stkim_upbit_secret_key

class MyTestCase(unittest.TestCase):



    def test_deposit_cash(self):
        amount = 10000
        pyupbit = Upbit_Ex(access_key, secret_key)
        result = pyupbit.deposit_cash(amount)

        print(result)


    def test_deposit_list(self):

        pyupbit = Upbit_Ex(access_key, secret_key)
        df, err_msg = pyupbit.get_deposite_history('KRW')

        print(df.head(5))
        print(err_msg)



    def test_api_key2(self):
        access_key = stkim_upbit_access_key
        secret_key = stkim_upbit_secret_key

        pyupbit = Upbit_Ex(access_key, secret_key)
        exp_date, remaining_days, err_msg = pyupbit.get_API_key_expire_date()
        print(f'{exp_date=}, {remaining_days=}, {err_msg=}')

        access_key = stkim_upbit_access_key
        secret_key = stkim_upbit_secret_key

        pyupbit = Upbit_Ex(access_key, secret_key)
        exp_date, remaining_days, err_msg = pyupbit.get_API_key_expire_date()
        print(f'{exp_date=}, {remaining_days=}, {err_msg=}')


    def test_api_keys(self):

        server_url = 'https://api.upbit.com/'

        payload = {
            'access_key': access_key,
            'nonce': str(uuid.uuid4()),
        }

        jwt_token = jwt.encode(payload, secret_key)
        authorization = 'Bearer {}'.format(jwt_token)
        headers = {
            'Authorization': authorization,
        }

        res = requests.get(server_url + '/v1/api_keys', params=None, headers=headers)
        print(res.json())

    ####################################################################
    ## Pyupbit
    def test_withdraw_krw(self):
        pyupbit = Upbit_Ex(access_key, secret_key, False)
        amount = 10000

        result = pyupbit.withdraw_cash(amount)
        print(result)

    def test_withdraw_history(self):
        pyupbit = Upbit_Ex(access_key, secret_key, False)
        df = pyupbit.get_withdraw_history('KRW')

        for row_dict in df.to_dict(orient="records"):
            print(row_dict['created_at'])
            print(row_dict['done_at'])

        print(df.head(5))

    def test_withdraw_security_info(self):
        pyupbit = Upbit_Ex(access_key, secret_key, False)
        currency = 'KRW'

        ml, account, wl = pyupbit.get_withdraw_account_info(currency)
        print(f'{ml=},{account=},{wl=}')

        ## {{'member_level': {'security_level': 4, 'fee_level': 0, 'email_verified': True,
        # 'identity_auth_verified': True, 'bank_account_verified': True,
        # 'kakao_pay_auth_verified': True, 'two_factor_auth_verified': True,
        # 'locked': False, 'wallet_locked': False},
        # 'currency': {'code': 'KRW', 'withdraw_fee': '1000.0', 'is_coin': False,
        # 'wallet_state': 'working', 'wallet_support': ['deposit', 'withdraw']},
        # 'account': {'currency': 'KRW', 'balance': '5064723.12050851', 'locked': '0.0',
        # 'avg_buy_price': '0', 'avg_buy_price_modified': True, 'unit_currency': 'KRW'},
        # 'withdraw_limit': {'currency': 'KRW', 'onetime': '50000000.0', 'daily': '200000000.0',
        # 'remaining_daily': '200000000.0', 'remaining_daily_fiat': '200000000.0',
        # 'fiat_currency': 'KRW', 'minimum': '5000.0', 'fixed': 0,
        # 'withdraw_delayed_fiat': '0.0', 'can_withdraw': True,
        # 'remaining_daily_krw': '200000000.0'}
        # }


    def test_list_individual_withdraw2(self):
        pyupbit = Upbit_Ex(access_key, secret_key)
        uuid = '956eed86-58e2-4b3a-a2dd-634680694f5d'
        currency = 'KRW'

        result = pyupbit.get_individual_withdraw_order(uuid, currency)
        print(result)

    ####################################################################
    ## Example of Upbit API
    def test_krw_withdraw(self):
        server_url = 'https://api.upbit.com/'

        params = {
            'amount': '10000'
        }
        query_string = unquote(urlencode(params, doseq=True)).encode("utf-8")

        m = hashlib.sha512()
        m.update(query_string)
        query_hash = m.hexdigest()

        payload = {
            'access_key': access_key,
            'nonce': str(uuid.uuid4()),
            'query_hash': query_hash,
            'query_hash_alg': 'SHA512',
        }

        jwt_token = jwt.encode(payload, secret_key)
        authorization = 'Bearer {}'.format(jwt_token)
        headers = {
            'Authorization': authorization,
        }

        res = requests.post(server_url + '/v1/withdraws/krw', json=params, headers=headers)
        print(res.json())
        ##{'type': 'withdraw', 'uuid': '956eed86-58e2-4b3a-a2dd-634680694f5d', 'currency': 'KRW', 'txid': None, 'holder': None, 'confirmations': 0, 'blockchain_url': None, 'state': 'processing', 'state_i18n': '출금진행중', 'created_at': '2022-10-28T16:01:48+09:00', 'done_at': None, 'amount': '10000.0', 'fee': '1000.0', 'krw_amount': '10000.0', 'fiat_amount': '10000.0', 'fiat_currency': 'KRW', 'transaction_type': 'default', 'bank': '', 'address': '', 'memo': None, 'cancelable': False}
        ## 카카오 페이로 신청됨

        # 이 uuid로 test_list_individual_withdraw을 호출하면
        ## 진행중인 상태이면, [{'type': 'withdraw', 'uuid': '956eed86-58e2-4b3a-a2dd-634680694f5d',
        # 'currency': 'KRW', 'txid': 'BKW-2022-10-28-bac38d547bac1122ac959bb115',
        # 'state': 'PROCESSING', 'created_at': '2022-10-28T16:01:48+09:00',
        # 'done_at': None, 'amount': '10000.0',
        # 'fee': '1000.0', 'transaction_type': 'default'},
        # State가 "PROCESSING"임

        # # 실패시 State가 "FAILED"임
        # [{'type': 'withdraw', 'uuid': '956eed86-58e2-4b3a-a2dd-634680694f5d',
        # 'currency': 'KRW', 'txid': 'BKW-2022-10-28-bac38d547bac1122ac959bb115',
        # 'state': 'FAILED', 'created_at': '2022-10-28T16:01:48+09:00',
        # 'done_at': None, 'amount': '10000.0', 'fee': '1000.0', 'transaction_type': 'default'},

        ## 성공시에 State는 'DONE'임


    def test_withdraw_chance(self):
        server_url = 'https://api.upbit.com/'

        params = {
            'currency': 'KRW'
        }
        query_string = unquote(urlencode(params, doseq=True)).encode("utf-8")

        m = hashlib.sha512()
        m.update(query_string)
        query_hash = m.hexdigest()

        payload = {
            'access_key': access_key,
            'nonce': str(uuid.uuid4()),
            'query_hash': query_hash,
            'query_hash_alg': 'SHA512',
        }

        jwt_token = jwt.encode(payload, secret_key)
        authorization = 'Bearer {}'.format(jwt_token)
        headers = {
            'Authorization': authorization,
        }

        res = requests.get(server_url + '/v1/withdraws/chance', params=params, headers=headers)
        print(res.json())

       ## {'member_level': {'security_level': 4, 'fee_level': 0, 'email_verified': True,
            # 'identity_auth_verified': True, 'bank_account_verified': True,
            # 'kakao_pay_auth_verified': True, 'two_factor_auth_verified': True,
            # 'locked': False, 'wallet_locked': False},
            # 'currency': {'code': 'KRW', 'withdraw_fee': '1000.0', 'is_coin': False,
                # 'wallet_state': 'working', 'wallet_support': ['deposit', 'withdraw']},
            # 'account': {'currency': 'KRW', 'balance': '5064723.12050851', 'locked': '0.0',
                # 'avg_buy_price': '0', 'avg_buy_price_modified': True, 'unit_currency': 'KRW'},
            # 'withdraw_limit': {'currency': 'KRW', 'onetime': '50000000.0', 'daily': '200000000.0',
                # 'remaining_daily': '200000000.0', 'remaining_daily_fiat': '200000000.0',
                # 'fiat_currency': 'KRW', 'minimum': '5000.0', 'fixed': 0,
                # 'withdraw_delayed_fiat': '0.0', 'can_withdraw': True,
                # 'remaining_daily_krw': '200000000.0'}}


    def test_list_individual_withdraw(self):
        server_url = 'https://api.upbit.com/'

        params = {
            'uuid': '956eed86-58e2-4b3a-a2dd-634680694f5d',
        }

        query_string = unquote(urlencode(params, doseq=True)).encode("utf-8")

        m = hashlib.sha512()
        m.update(query_string)
        query_hash = m.hexdigest()

        payload = {
            'access_key': access_key,
            'nonce': str(uuid.uuid4()),
            'query_hash': query_hash,
            'query_hash_alg': 'SHA512',
        }

        jwt_token = jwt.encode(payload, secret_key)
        authorization = 'Bearer {}'.format(jwt_token)
        headers = {
            'Authorization': authorization,
        }

        res = requests.get(server_url + '/v1/withdraws', params=params, headers=headers)
        print(res.json())
        ## [{'type': 'withdraw', 'uuid': '78a292ee-8dae-4bb0-88b1-0a6fb10b9614', 'currency': 'FIL', 'txid': 'bafy2bzacecwf4pyfwpxml6g2nnky2zrhnb4gylck5wspyzs2u254mwht4vgoq', 'state': 'DONE',
        # 'created_at': '2022-08-19T17:12:43+09:00', 'done_at': '2022-08-19T17:43:57+09:00', 'amount': '1.46995788', 'fee': '0.15', 'transaction_type': 'default'},
        #
        # {'type': 'withdraw', 'uuid': '46465946-a4e6-46da-87e0-f310c125492f', 'currency': 'BTT', 'txid': 'swap_17-1b1f61ec-39e6-4f6f-8738-32b21d67216f', 'state': 'DONE',
        # 'created_at': '2022-01-04T15:44:26+09:00', 'done_at': '2022-01-04T15:44:27+09:00', 'amount': '0.0', 'fee': '0.0', 'transaction_type': 'internal'},
        #
        # {'type': 'withdraw', 'uuid': 'c427a984-dbf7-46df-8493-446848d81eda', 'currency': 'KRW', 'txid': 'CooconKrwWithdrawTx-2020-01-15-0344cfc9-7d83-49b3-a651-a94ac85c3663', 'state': 'DONE',
        # 'created_at': '2020-01-15T17:59:39+09:00', 'done_at': '2020-01-15T18:04:49+09:00', 'amount': '6256923.0', 'fee': '1000.0', 'transaction_type': 'default'},
        #
        # {'type': 'withdraw', 'uuid': '3151e136-481e-458a-a879-2811ad9f7635', 'currency': 'KRW', 'txid': 'CooconKrwWithdrawTx-2020-01-08-6051b9ae-6eb1-4c68-832d-3be29db080b5', 'state': 'DONE',
        # 'created_at': '2020-01-08T14:10:12+09:00', 'done_at': '2020-01-08T14:15:29+09:00', 'amount': '8182844.0', 'fee': '1000.0', 'transaction_type': 'default'},
        #
        # {'type': 'withdraw', 'uuid': '204b26f6-045c-4d96-a014-6760b1368d11', 'currency': 'BTC', 'txid': 'upbit4c0a03b080d24375a3330739929e89c81d26380f5bce4ec3b949cab299e', 'state': 'DONE',
        # 'created_at': '2019-07-21T07:46:12+09:00', 'done_at': '2019-07-21T07:47:10+09:00', 'amount': '0.0888888', 'fee': '0.0', 'transaction_type': 'internal'},
        #
        # {'type': 'withdraw', 'uuid': '6b7fd658-b50c-44f6-bd5c-7d686219780e', 'currency': 'TRX', 'txid': 'upbit54fbb244b20846aba99d802385eb26820963e9aaac2842cba581ce241b2', 'state': 'DONE',
        # 'created_at': '2019-07-20T08:14:25+09:00', 'done_at': '2019-07-20T08:14:44+09:00', 'amount': '30580.0', 'fee': '0.0', 'transaction_type': 'internal'},
        #
        # {'type': 'withdraw', 'uuid': 'eeda6d6b-d529-452b-aa1f-34ae91ab67fa', 'currency': 'BTC', 'txid': 'de040ec60058837414619dadaf402d6d70c5d07917eded8c669febd7c99c8aa5', 'state': 'DONE',
        # 'created_at': '2018-10-19T11:01:08+09:00', 'done_at': '2018-10-19T11:17:57+09:00', 'amount': '0.14359815', 'fee': '0.0005', 'transaction_type': 'default'},
        #
        # {'type': 'withdraw', 'uuid': '53b93c8d-d167-4e93-8ffb-1d43ce76b932', 'currency': 'ETH', 'txid': '0xf09a16b9c0a5ae229921376b5fb8dc02146f91c89d582a80de857fa3d8ed8074', 'state': 'DONE',
        # 'created_at': '2018-09-23T07:29:06+09:00', 'done_at': '2018-09-23T07:38:53+09:00', 'amount': '0.03', 'fee': '0.01', 'transaction_type': 'default'},
        #
        # {'type': 'withdraw', 'uuid': 'c3b902c2-bb5c-4c45-85a8-6615ecea88e9', 'currency': 'BTC', 'txid': '261f30467a6b5e8a0dd1da1827f7401ae22417301876123fbcaa8afe188c1c14', 'state': 'DONE',
        # 'created_at': '2018-08-27T13:23:04+09:00', 'done_at': '2018-08-27T13:29:18+09:00', 'amount': '0.10260848', 'fee': '0.0005', 'transaction_type': 'default'},
        #
        # {'type': 'withdraw', 'uuid': '0ed72bf8-42b2-48ec-8cd3-446282a5dc27', 'currency': 'BTC', 'txid': '8a202d477e64d5710d39feb7022c5e363d887c209b299e6ef0c92fd13c54e424', 'state': 'DONE',
        # 'created_at': '2018-08-27T13:19:11+09:00', 'done_at': '2018-08-27T13:29:16+09:00', 'amount': '0.24741718', 'fee': '0.0005', 'transaction_type': 'default'},
        #
        # {'type': 'withdraw', 'uuid': '3437cc94-0eed-4437-80af-816e7f366c4a', 'currency': 'BTC', 'txid': '942dfed51d83985f3b29574ba1ccb2cb553506f2aada8da325588c49010a4c25', 'state': 'DONE',
        # 'created_at': '2018-08-26T03:15:39+09:00', 'done_at': '2018-08-26T03:27:51+09:00', 'amount': '0.0845992', 'fee': '0.0005', 'transaction_type': 'default'},
        #
        # {'type': 'withdraw', 'uuid': '0dc2189f-6e92-4248-9462-c3dc04ff87f2', 'currency': 'TRX', 'txid': 'dc28ae429cc01c975eb4953210b756ca90f5253c6d2c84799204c9f778a642a2', 'state': 'DONE',
        # 'created_at': '2018-08-24T21:09:18+09:00', 'done_at': '2018-08-24T21:12:13+09:00', 'amount': '169850.0', 'fee': '0.0', 'transaction_type': 'default'},
        #
        # {'type': 'withdraw', 'uuid': 'ef9eb38a-627c-41fc-8a06-2da4b52d3dc4', 'currency': 'BTC', 'txid': '0a82824e2b68a1c0d7e9a0d6e362d92103736e924b9522b10bac6618748d6fc5', 'state': 'DONE',
        # 'created_at': '2018-08-24T16:42:51+09:00', 'done_at': '2018-08-24T17:01:27+09:00', 'amount': '0.8848039', 'fee': '0.0005', 'transaction_type': 'default'},
        #
        # {'type': 'withdraw', 'uuid': '60e4fdb0-eec9-4852-8e67-862e9c3b720e', 'currency': 'TRX', 'txid': '6cd56d01852daf4a77f81c3f747b5940f1e3f5b17fbf748fe77c1aca77ce239d', 'state': 'DONE',
        # 'created_at': '2018-08-10T18:29:24+09:00', 'done_at': '2018-08-10T18:30:59+09:00', 'amount': '5000.0', 'fee': '0.0', 'transaction_type': 'default'}]


    # @unittest.skip("Tested")
    def test_list_withdraw_history(self):
        server_url = 'https://api.upbit.com/'

        params = {
          'currency': 'KRW',
          'state': 'done'
        }

        query_string = unquote(urlencode(params, doseq=True)).encode("utf-8")

        m = hashlib.sha512()
        m.update(query_string)
        query_hash = m.hexdigest()

        payload = {
            'access_key': access_key,
            'nonce': str(uuid.uuid4()),
            'query_hash': query_hash,
            'query_hash_alg': 'SHA512',
        }

        jwt_token = jwt.encode(payload, secret_key)
        authorization = 'Bearer {}'.format(jwt_token)
        headers = {
          'Authorization': authorization,
        }

        res = requests.get(server_url + '/v1/withdraws', params=params, headers=headers)
        print(res.json())
        ## returns:
        ## [
        # {'type': 'withdraw', 'uuid': 'c427a984-dbf7-46df-8493-446848d81eda', 'currency': 'KRW', 'txid': 'CooconKrwWithdrawTx-2020-01-15-0344cfc9-7d83-49b3-a651-a94ac85c3663', 'state': 'DONE', 'created_at': '2020-01-15T17:59:39+09:00', 'done_at': '2020-01-15T18:04:49+09:00', 'amount': '6256923.0', 'fee': '1000.0', 'transaction_type': 'default'},
        # {'type': 'withdraw', 'uuid': '3151e136-481e-458a-a879-2811ad9f7635', 'currency': 'KRW', 'txid': 'CooconKrwWithdrawTx-2020-01-08-6051b9ae-6eb1-4c68-832d-3be29db080b5', 'state': 'DONE', 'created_at': '2020-01-08T14:10:12+09:00', 'done_at': '2020-01-08T14:15:29+09:00', 'amount': '8182844.0', 'fee': '1000.0', 'transaction_type': 'default'}]



if __name__ == '__main__':
    unittest.main()
