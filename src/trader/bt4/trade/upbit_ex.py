import hashlib
import uuid
from urllib.parse import urlencode

import jwt
import requests
from ccxt import upbit
from ccxt.base.types import Int

from pyupbit import Upbit
import pandas as pd

from bt4.utils.mylog import init_log
from bt4.utils.pandas_utils import sort_df

log = init_log()
class upbit_ex(upbit):

    def __init__(self, config):
        self.access = config['apiKey']
        self.secrete = config['secret']

        super(upbit_ex, self).__init__(config)

    def fetch_my_trades(self, symbol: str = None, since: Int = None, limit: Int = None, params={}):
        sett_odr_df = pd.DataFrame()

        states = ['done', 'cancel']
        for state in states :
            state_df = self.__get_settled_order_in_state(state)
            sett_odr_df = pd.concat([sett_odr_df, state_df], ignore_index = True)

        sett_odr_df.set_index(['created_at'], drop = False, inplace = True)
        sort_df(sett_odr_df, 'created_at', ascending = False)
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


    def fetch_expiration_date(self):
        print('okay!!')