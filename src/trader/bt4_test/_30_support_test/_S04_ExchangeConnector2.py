import unittest
import pandas as pd

from bt4.Constants import ExType
from bt4.trade.ExchangeConnector import ExConnFactory
from bt4.utils.pyupbit_ex import Upbit_Ex
from bt4_test._30_support_test._S03_ExchangeConnectorTest import (
    stkim_binance_access_key,
    stkim_binance_secret_key,
    fetch_current_market_price,
    mingu_upbit_access_key,
    mingu_upbit_secret_key,
    mingu_binance_access_key,
    mingu_binance_secret_key, stkim_upbit_access_key, stkim_upbit_secrete_key,
)

pd.set_option('display.max_columns', None)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('max_colwidth', None)


class MyTestCase(unittest.TestCase):
    @unittest.skip("Tested")
    def test_withdraw(self):
        # 바이낸스 거래소에서 업비트 거래소로 ETH 이동
        trade_ex_type = ExType.upbit
        trade_ccxt_wrapper1 = ExConnFactory.instance().get_ex_conn(trade_ex_type, mingu_upbit_access_key, mingu_upbit_secret_key)
        upbit_exchange = trade_ccxt_wrapper1.get_ccxt_ex()
        deposit = upbit_exchange.fetch_deposit_address('ETH')
        upbit_eth_address = deposit['address']
        upbit_eth_tag = deposit['tag']

        trade_ex_type = ExType.binance
        trade_ccxt_wrapper2 = ExConnFactory.instance().get_ex_conn(trade_ex_type, mingu_binance_access_key, mingu_binance_secret_key)
        binance_exchange = trade_ccxt_wrapper2.get_ccxt_ex()

        result = binance_exchange.withdraw('ETH', 0.0099, upbit_eth_address, {'tag': upbit_eth_tag, 'network': 'ETH'})

        print(result)
        # {
        #     'info': {'id': '5456bc107a804a408130a3d753f15692'},
        #     'id': '5456bc107a804a408130a3d753f15692',
        #     'txid': None,
        #     'timestamp': None,
        #     'datetime': None,
        #     'network': None,
        #     'address': None,
        #     'addressTo': None,
        #     'addressFrom': None,
        #     'tag': None,
        #     'tagTo': None,
        #     'tagFrom': None,
        #     'type': None,
        #     'amount': None,
        #     'currency': 'ETH',
        #     'status': None,
        #     'updated': None,
        #     'internal': None,
        #     'fee': None,
        # }
    
    def test_withdraw_history(self):
        ############# withdraw history #############################
        ## pyupbit
        pyupbit = Upbit_Ex(mingu_upbit_access_key, mingu_upbit_secret_key, False)
        currency = 'KRW'
        pyubit_history = pyupbit.get_withdraw_history(currency)
        print(pyubit_history)
        # created_at done_at amount fee state
        # 2023-01-09T16:19:10 2023-01-09T16:19:39 59000.0 1000.0 Done
        
        ##############################################################
        print("@" * 50)
        
        ## ccxt upbit
        trade_ex_type = ExType.upbit
        trade_ccxt_wrapper = ExConnFactory.instance().get_ex_conn(trade_ex_type, mingu_upbit_access_key, mingu_upbit_secret_key)
        exchange = trade_ccxt_wrapper.get_ccxt_ex()
        ccxt_history = exchange.fetch_withdrawals(currency)
        print(ccxt_history)
        # [
        #     {
        #         'info': {
        #             'type': 'withdraw',
        #             'uuid': '7de124cb-f009-4486-9a87-edbbbf0bcae9',
        #             'currency': 'KRW',
        #             'txid': 'BKW-2023-01-09-a7b759a499dc5d07083c35d9b9',
        #             'state': 'DONE',
        #             'created_at': '2023-01-09T16:19:10+09:00',
        #             'done_at': '2023-01-09T16:19:39+09:00',
        #             'amount': '59000.0',
        #             'fee': '1000.0',
        #             'transaction_type': 'default',
        #         },
        #         'id': '7de124cb-f009-4486-9a87-edbbbf0bcae9',
        #         'currency': 'KRW',
        #         'amount': 59000.0,
        #         'network': None,
        #         'address': None,
        #         'addressTo': None,
        #         'addressFrom': None,
        #         'tag': None,
        #         'tagTo': None,
        #         'tagFrom': None,
        #         'status': 'ok',
        #         'type': 'withdrawal',
        #         'updated': 1673248779000,
        #         'txid': 'BKW-2023-01-09-a7b759a499dc5d07083c35d9b9',
        #         'timestamp': 1673248750000,
        #         'datetime': '2023-01-09T07:19:10.000Z',
        #         'fee': {'currency': 'KRW', 'cost': 1000.0},
        #     },
        # ]

    def test_withdraw_security_info(self):
        ############# withdraw account info #############################
        ## pyupbit
        pyupbit = Upbit_Ex(mingu_upbit_access_key, mingu_upbit_secret_key, False)
        currency = 'KRW'

        print(pyupbit.get_withdraw_account_info(currency))
        # (
        #     {
        #         'security_level': 0,
        #         'fee_level': 0,
        #         'email_verified': True,
        #         'identity_auth_verified': True,
        #         'bank_account_verified': True,
        #         'kakao_pay_auth_verified': True,
        #         'two_factor_auth_verified': True,
        #         'locked': False,
        #         'wallet_locked': False,
        #     },
        #     {
        #         'currency': 'KRW',
        #         'balance': '13242.81119599',
        #         'locked': '0.0',
        #         'avg_buy_price': '0',
        #         'avg_buy_price_modified': True,
        #         'unit_currency': 'KRW',
        #     },
        #     {
        #         'currency': 'KRW',
        #         'onetime': '50000000.0',
        #         'daily': '200000000.0',
        #         'remaining_daily': '200000000.0',
        #         'remaining_daily_fiat': '200000000.0',
        #         'fiat_currency': 'KRW',
        #         'minimum': '5000.0',
        #         'fixed': 0,
        #         'withdraw_delayed_fiat': '0.0',
        #         'can_withdraw': True,
        #         'remaining_daily_krw': '200000000.0',
        #     },
        # )

        ##############################################################
        print("@" * 50)
        ## ccxt upbit
        trade_ex_type = ExType.upbit
        trade_ccxt_wrapper = ExConnFactory.instance().get_ex_conn(trade_ex_type, mingu_upbit_access_key, mingu_upbit_secret_key)
        exchange = trade_ccxt_wrapper.get_ccxt_ex()
        print(exchange.fetch_currency_by_id('KRW'))
        # {
        #     'info': {
        #         'member_level': {
        #             'security_level': '0',
        #             'fee_level': '0',
        #             'email_verified': True,
        #             'identity_auth_verified': True,
        #             'bank_account_verified': True,
        #             'kakao_pay_auth_verified': True,
        #             'two_factor_auth_verified': True,
        #             'locked': False,
        #             'wallet_locked': False,
        #         },
        #         'currency': {
        #             'code': 'KRW',
        #             'withdraw_fee': '1000.0',
        #             'is_coin': False,
        #             'wallet_state': 'working',
        #             'wallet_support': ['deposit', 'withdraw'],
        #         },
        #         'account': {
        #             'currency': 'KRW',
        #             'balance': '13242.81119599',
        #             'locked': '0.0',
        #             'avg_buy_price': '0',
        #             'avg_buy_price_modified': True,
        #             'unit_currency': 'KRW',
        #         },
        #         'withdraw_limit': {
        #             'currency': 'KRW',
        #             'onetime': '50000000.0',
        #             'daily': '200000000.0',
        #             'remaining_daily': '200000000.0',
        #             'remaining_daily_fiat': '200000000.0',
        #             'fiat_currency': 'KRW',
        #             'minimum': '5000.0',
        #             'fixed': '0',
        #             'withdraw_delayed_fiat': '0.0',
        #             'can_withdraw': True,
        #             'remaining_daily_krw': '200000000.0',
        #         },
        #     },
        #     'id': 'KRW',
        #     'code': 'KRW',
        #     'name': 'KRW',
        #     'active': True,
        #     'fee': 1000.0,
        #     'precision': None,
        #     'limits': {'withdraw': {'min': 5000.0, 'max': 200000000.0}},
        # }


    def test_order_exit_long_upbit(self):
        quote_ex_type = ExType.upbit
        trade_ex_type = ExType.upbit
        tgt_market = 'KRW-BTC'
        min_krw = 5100
        fee_ratio = 0.001
        upbit_ex_etr_long_resp, enter_long_vol = self.__execute_enter_long_minimum_call__(
            quote_ex_type, trade_ex_type, mingu_upbit_access_key, mingu_upbit_secret_key, tgt_market, min_krw, fee_ratio
        )

        print(upbit_ex_etr_long_resp.__dict__)
        upbit_ex_exit_long_resp, market_vol_wo_fee = self.__execute_exit_long_minimum_call__(
            trade_ex_type, mingu_upbit_access_key, mingu_upbit_secret_key, tgt_market, enter_long_vol, fee_ratio
        )
        print(upbit_ex_exit_long_resp.__dict__)

    def __execute_enter_long_minimum_call__(
        self, quote_ex_type, trade_ex_type, access_key, secrete_key, tgt_market, min_amount_in_fiat, fee_ratio
    ):
        price = fetch_current_market_price(quote_ex_type, tgt_market)

        trade_ccxt_wrapper = ExConnFactory.instance().get_ex_conn(trade_ex_type, access_key, secrete_key)
        enter_long_vol = min_amount_in_fiat * (1 - fee_ratio) / price
        return trade_ccxt_wrapper.execute_enter_long(tgt_market, price, enter_long_vol), enter_long_vol

    def __execute_exit_long_minimum_call__(self, trade_ex_type, access_key, secrete_key, tgt_market, enter_long_vol, fee_ratio):
        ccxt_wrapper = ExConnFactory.instance().get_ex_conn(trade_ex_type, access_key, secrete_key)
        market_vol_without_fee = enter_long_vol * (1 - fee_ratio)
        return ccxt_wrapper.execute_exit_long(tgt_market, market_vol_without_fee), market_vol_without_fee

    @unittest.skip("Tested")
    def test_order_integrated(self):
        ex_type = ExType.upbit
        tgt_market = 'KRW-BTC'
        min_krw = 5100
        fee_ratio = 0.0005
        upbit_ex_resp = self.__execute_enter_long_minimum_call__(
            ex_type, stkim_binance_access_key, stkim_binance_secret_key, tgt_market, min_krw, fee_ratio
        )
        print(upbit_ex_resp.__dict__)
        #####################################################################
        ex_type = ExType.binance
        tgt_market = 'BTC/USDT'
        min_krw = 5100
        fee_ratio = 0.0005
        binance_ex_resp = self.__execute_enter_long_minimum_call__(
            ex_type, stkim_binance_access_key, stkim_binance_secret_key, tgt_market, min_krw, fee_ratio
        )
        print(binance_ex_resp.__dict__)

        #####################################################################
        ex_type = ExType.binanceusdm
        tgt_market = 'BTC/USDT'
        min_krw = 10
        fee_ratio = 0.0005
        usdm_ex_resp = self.__execute_enter_long_minimum_call__(
            ex_type, stkim_binance_access_key, stkim_binance_secret_key, tgt_market, min_krw, fee_ratio
        )
        print(usdm_ex_resp.__dict__)

    @unittest.skip("Tested")
    def test_order_result_binanceusdm(self):
        ex_type = ExType.binanceusdm
        ccxt_wrapper = ExConnFactory.instance().get_ex_conn(ex_type, stkim_binance_access_key, stkim_binance_secret_key)
        tgt_market = 'BTC/USDT'
        price = fetch_current_market_price(ex_type, tgt_market)
        min_krw = 5100
        fee_ratio = 0.0005
        enter_long_vol = min_krw * (1 - fee_ratio) / price

        ex_resp = ccxt_wrapper.execute_enter_long(tgt_market, min_krw, enter_long_vol)
        print(ex_resp.__dict__)

    @unittest.skip("Tested")
    def test_order_result_binance(self):
        ex_type = ExType.binance
        ccxt_wrapper = ExConnFactory.instance().get_ex_conn(ex_type, stkim_binance_access_key, stkim_binance_secret_key)
        tgt_market = 'BTC/USDT'
        price = fetch_current_market_price(ex_type, tgt_market)
        min_krw = 5100
        fee_ratio = 0.0005
        enter_long_vol = min_krw * (1 - fee_ratio) / price

        ex_resp = ccxt_wrapper.execute_enter_long(tgt_market, min_krw, enter_long_vol)
        print(ex_resp.__dict__)

    @unittest.skip("Tested")
    def test_order_result_upbit(self):
        ex_type = ExType.upbit
        ccxt_wrapper = ExConnFactory.instance().get_ex_conn(ex_type, stkim_binance_access_key, stkim_binance_secret_key)
        tgt_market = 'KRW-BTC'
        price = fetch_current_market_price(ex_type, tgt_market)
        min_krw = 5100
        fee_ratio = 0.0005
        enter_long_vol = min_krw * (1 - fee_ratio) / price

        ex_resp = ccxt_wrapper.execute_enter_long(tgt_market, min_krw, enter_long_vol)
        print(ex_resp.__dict__)


if __name__ == '__main__':
    unittest.main()
