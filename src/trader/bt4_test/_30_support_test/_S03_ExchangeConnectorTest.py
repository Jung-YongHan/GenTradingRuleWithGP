import importlib
import time
import unittest
from os.path import dirname

import ccxt

from bt4.Constants import ExType
from bt4.quote.QuoteConnector import UniversalQuoteConnector
from bt4.quote.QuoteSupport import Tick
from bt4.trade.ExchangeConnector import ExConnFactory

import pandas as pd
import numpy as np

from bt4.utils.exchange_filter import ExFilterFactory
from bt4.utils.exchange_utils import std_2_uniformed_mkt_id, std_2_uniformed_mkt_ids
from bt4.utils.python_utils import from_utc_int_timestamp, get_1min_before_dt, now_dt, create_dt_at

pd.set_option('display.max_columns', None)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('max_colwidth', None)


stkim_upbit_access_key = "kOzKkEnwOtxhVptCkxZE7UHlFvWzQWSBR8WpKENG"
stkim_upbit_secrete_key = "cPZvKf82vX2P2l8boxTPK1oDyO9Da2k6rMhcZfz8"

# Mingu's Upbit Account
mingu_upbit_access_key = 'o9Allf8TkPze10TpPrOOdhcigcxZVyGcFyxx9JqK'
mingu_upbit_secret_key = 'kptMZquyG0KIKoJVJakOFQOZKMxd0iJsxTciexDf'

## STKIM's Binance api key
stkim_binance_access_key = 'wBOpXQfBCVQkS1j5zEwE8uTJw1m3YIm1cU4UP4sIh3xMRoVTKZ3X4oH7Atn60J3M'
stkim_binance_secret_key = 'xQkwCJESpskPGJCwM6VuvlERGjfYh7MrKy2oIqCaNCtUENVDSP0PP89uKCu5ENf3'


# Mingu's Binance api key
mingu_binance_access_key = 'NjbQqYaSVwWSG0ZPfzKC5RwvNQutSVIYLJE10bYEG5vbRDbLpq4oupAK6xLpYLZg'
mingu_binance_secret_key = 'oIpo2OdG55I3iitaUCahwRO8pej532HgV0JY5IJHnaXSnpQTjhSVUpHsrn8tYBEh'

# stkim_bithumb_access_key = "b8b77894345de3f6bff25e61810d778d4dfe7fbaf9aa5a"
# stkim_bithumb_secrete_key = "OGQyZGFhMGFmMmM4YWFjNDdmOTAzZDUwZTZmZmM3ODI1ODY1ODcwZDc0ODM0MWZlN2RiZGZjYTk1NGMxOQ"

stkim_bithumb_access_key = "23523048106b109c7dc0692ca4eb2749"
stkim_bithumb_secrete_key = "5a3d7fff94f6fe1d083965ab495181d9"

def fetch_current_market_price(ex_type, tgt_market, return_tick=False):
    uqc = UniversalQuoteConnector.instance()
    markets = [tgt_market]
    markets = ExFilterFactory.instance().get(ex_type).filter_market_ids_before(markets)

    _1m_bf_dt = get_1min_before_dt(now_dt())
    _1m_before_dt = create_dt_at(_1m_bf_dt.year, _1m_bf_dt.month, _1m_bf_dt.day, _1m_bf_dt.hour, _1m_bf_dt.minute, 0)
    _1m_quote_dfs = uqc.fetch_quote_at(ex_type, markets, _1m_before_dt)

    df = _1m_quote_dfs.loc[_1m_quote_dfs["market"] == tgt_market]
    if return_tick:
        data_list = df.to_numpy()[0].tolist()
        data_list.insert(0, df.index[0].strftime('%Y-%m-%dT%H_%M_%S'))
        tick = Tick.from_list(data_list)
        return tick
    else:
        price = df["close"].item()
        return price

class MyTestCase(unittest.TestCase):


    def test_ex_connector_extension2(self):

        from_admin_params = {}
        from_admin_params['module'] = 'bt4.trade.upbit_ex'
        from_admin_params['conn_ex'] = 'upbit_ex'

        ccxt_wrapper = ExConnFactory.instance().get_ex_conn(ExType.upbit,
                                                            stkim_upbit_access_key,
                                                            stkim_upbit_secrete_key,
                                                            admin_params = from_admin_params)
        exchange = ccxt_wrapper.get_ccxt_ex()
        fetched_my_trade_df = exchange.fetch_my_trades()
        fetched_my_trade_df.to_csv("my_trade_history.csv")
        print(fetched_my_trade_df)


    def test_get_settled_orders_bithumb(self) :
        ccxt_wrapper = ExConnFactory.instance().get_ex_conn(ExType.bithumb,
                                                            stkim_bithumb_access_key,
                                                            stkim_bithumb_secrete_key,
                                                            admin_params = None)
        markets = ["KRW-BTC", "KRW-ETH", "KRW-XRP"]
        markets = std_2_uniformed_mkt_ids(markets)
        df = ccxt_wrapper.get_settled_orders(markets)
        print(df)

        balances = ccxt_wrapper.fetch_balances()
        print(balances)

    def test_get_settled_orders_upbit(self) :
        ccxt_wrapper = ExConnFactory.instance().get_ex_conn(ExType.upbit,
                                                            stkim_upbit_access_key,
                                                            stkim_upbit_secrete_key,
                                                            admin_params = None)
        markets = ["KRW-BTC", "KRW-ETH", "KRW-XRP"]
        df = ccxt_wrapper.get_settled_orders(markets)
        print(df)

        balances = ccxt_wrapper.fetch_balances()
        print(balances)


    def test_ex_connector_cash(self):
        ccxt_wrapper = ExConnFactory.instance().get_ex_conn(ExType.upbit,
                                                            mingu_upbit_access_key,
                                                            mingu_upbit_secret_key,
                                                            admin_params = None)

        ccxt_wrapper2 = ExConnFactory.instance().get_ex_conn(ExType.upbit,
                                                            mingu_upbit_access_key,
                                                            mingu_upbit_secret_key,
                                                            admin_params = None)
        self.assertEqual(ccxt_wrapper, ccxt_wrapper2)

        ccxt_wrapper3 = ExConnFactory.instance().get_ex_conn(ExType.upbit,
                                                            'abc',
                                                            'def',
                                                            admin_params = None)

        ccxt_wrapper4 = ExConnFactory.instance().get_ex_conn(ExType.upbit,
                                                            mingu_upbit_access_key,
                                                            mingu_upbit_secret_key,
                                                            admin_params = None)
        self.assertNotEqual(ccxt_wrapper3, ccxt_wrapper4)

        ccxt_wrapper5 = ExConnFactory.instance().get_ex_conn(ExType.upbit,
                                                             'abc',
                                                             'def',
                                                             admin_params = None)
        self.assertEqual(ccxt_wrapper3, ccxt_wrapper5)





    def test_ex_connector_extension(self):

        from_admin_params = {}
        from_admin_params['module'] = 'bt4.trade.upbit_ex'
        from_admin_params['conn_ex'] = 'upbit_ex'

        ccxt_wrapper = ExConnFactory.instance().get_ex_conn(ExType.upbit,
                                                            mingu_upbit_access_key,
                                                            mingu_upbit_secret_key,
                                                            admin_params = from_admin_params)
        exchange = ccxt_wrapper.get_ccxt_ex()
        exchange.fetch_expiration_date()

        ccxt_wrapper2 = ExConnFactory.instance().get_ex_conn(ExType.upbit,
                                                            mingu_upbit_access_key,
                                                            mingu_upbit_secret_key)
        exchange2 = ccxt_wrapper2.get_ccxt_ex()
        exchange2.fetch_expiration_date()


    def test_upbit_extension(self):

        config = {
            'apiKey' : mingu_upbit_access_key,
            'secret' : mingu_upbit_secret_key
        }

        exchange_class = getattr(ccxt, 'upbit')
        exchange = exchange_class(config)

        ccxt_history = exchange.fetch_withdrawals('KRW')
        print(ccxt_history)
        #####################################################
        print(self.__module__)
        print(__file__)
        print(dirname(__file__))
        module_name = 'bt3_test.upbit_ex'
        class_name = 'upbit_ex'
        mod = importlib.import_module(module_name)
        exchange_class = getattr(mod, class_name)
        exchange = exchange_class(config)

        ccxt_history = exchange.fetch_withdrawals('KRW')
        print(ccxt_history)

        exchange.fetch_expiration_date()


    def test_enter_long_exit_long_binanceusdm_using_ccxt(self):
        tgt_market = 'BTC/USDT'
        price = fetch_current_market_price(ExType.binanceusdm, tgt_market)
        print(f'{price=}')

        min_usdt = 21  ## Be cautious, Minumum price should be bigger than 0.001.
        fee_ratio = 0.001
        enter_long_vol = min_usdt * (1 - fee_ratio) / price
        # enter_long_vol = np.round(enter_long_vol, decimals=5)
        ccxt_wrapper = ExConnFactory.instance().get_ex_conn(ExType.binanceusdm,
                                                            stkim_binance_access_key,
                                                            stkim_binance_secret_key)
        exchange = ccxt_wrapper.get_ccxt_ex()
        print(f'requested : {min_usdt=}, {fee_ratio=}, {price=}, {enter_long_vol=}')
        response_buy = exchange.create_order(symbol=tgt_market, type='market', side='buy', amount=enter_long_vol, price=price)
        print(response_buy)
        # Response
        # {'info': {'orderId': '106728401464', 'symbol': 'BTCUSDT', 'status': 'FILLED',
        #           'clientOrderId': 'x-xcKtGhcu3ddb89bfe302e4154a594c', 'price': '0', 'avgPrice': '18835.10000',
        #           'origQty': '0.001', 'executedQty': '0.001', 'cumQty': '0.001', 'cumQuote': '18.83510',
        #           'timeInForce': 'GTC', 'type': 'MARKET', 'reduceOnly': False, 'closePosition': False, 'side': 'BUY',
        #           'positionSide': 'BOTH', 'stopPrice': '0', 'workingType': 'CONTRACT_PRICE', 'priceProtect': False,
        #           'origType': 'MARKET', 'updateTime': '1673598790512'}, 'id': '106728401464',
        #  'clientOrderId': 'x-xcKtGhcu3ddb89bfe302e4154a594c', 'timestamp': None, 'datetime': None,
        #  'lastTradeTimestamp': None, 'symbol': 'BTC/USDT', 'type': 'market', 'timeInForce': 'GTC', 'postOnly': False,
        #  'reduceOnly': False, 'side': 'buy', 'price': 18835.1, 'stopPrice': None, 'amount': 0.001, 'cost': 18.8351,
        #  'average': 18835.1, 'filled': 0.001, 'remaining': 0.0, 'status': 'closed', 'fee': None, 'trades': [],
        #  'fees': []}

        print(f'requestd volume : {enter_long_vol}')
        market_vol_without_fee = enter_long_vol * (1 - fee_ratio)
        print(f'{market_vol_without_fee=}')
        response_sell = exchange.create_order(symbol=tgt_market, type='market', side='sell', amount=market_vol_without_fee, price=price)
        print(response_sell)

        # Response
        # {'info': {'orderId': '106728401981', 'symbol': 'BTCUSDT', 'status': 'FILLED',
        #           'clientOrderId': 'x-xcKtGhcuce9be9bb1e744b7243170b', 'price': '0', 'avgPrice': '18835.00000',
        #           'origQty': '0.001', 'executedQty': '0.001', 'cumQty': '0.001', 'cumQuote': '18.83500',
        #           'timeInForce': 'GTC', 'type': 'MARKET', 'reduceOnly': False, 'closePosition': False, 'side': 'SELL',
        #           'positionSide': 'BOTH', 'stopPrice': '0', 'workingType': 'CONTRACT_PRICE', 'priceProtect': False,
        #           'origType': 'MARKET', 'updateTime': '1673598790725'}, 'id': '106728401981',
        #  'clientOrderId': 'x-xcKtGhcuce9be9bb1e744b7243170b', 'timestamp': None, 'datetime': None,
        #  'lastTradeTimestamp': None, 'symbol': 'BTC/USDT', 'type': 'market', 'timeInForce': 'GTC', 'postOnly': False,
        #  'reduceOnly': False, 'side': 'sell', 'price': 18835.0, 'stopPrice': None, 'amount': 0.001, 'cost': 18.835,
        #  'average': 18835.0, 'filled': 0.001, 'remaining': 0.0, 'status': 'closed', 'fee': None, 'trades': [], 'fees': []}

    # @unittest.skip("Tested")
    def test_enter_long_exit_long_binance_using_ccxt(self):
        ## Fetch Price
        tgt_market = 'BTC/USDT'
        price = fetch_current_market_price(ExType.binance, tgt_market)
        print(f'{price=}')
        min_usdt = 25 ## Be cautious. Binance 10 USDT is minimum amount for trading, while upbit is 5000 KRW.
        fee_ratio = 0.001
        enter_long_vol = min_usdt * (1 - fee_ratio) / price

        ccxt_wrapper = ExConnFactory.instance().get_ex_conn(ExType.binance,
                                                            stkim_binance_access_key,
                                                            stkim_binance_secret_key)
        exchange = ccxt_wrapper.get_ccxt_ex()
        print(f'requested : {min_usdt=}, {fee_ratio=}, {price=}, {enter_long_vol=}')
        response_buy = exchange.create_order(symbol=tgt_market, type = 'market', side='buy', amount=enter_long_vol, price=price)
        print(response_buy)
        # Response
        # {'info': {'symbol': 'BTCUSDT', 'orderId': '17273552679', 'orderListId': '-1',
        #           'clientOrderId': 'x-R4BD3S82f39065cd5f04b5c8e0b572', 'transactTime': '1673594488130',
        #           'price': '0.00000000', 'origQty': '0.00058000', 'executedQty': '0.00058000',
        #           'cummulativeQuoteQty': '10.91424860', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'MARKET',
        #           'side': 'BUY', 'workingTime': '1673594488130', 'fills': [
        #         {'price': '18817.67000000', 'qty': '0.00058000', 'commission': '0.00000000', 'commissionAsset': 'BNB',
        #          'tradeId': '2472442201'}], 'selfTradePreventionMode': 'NONE'}, 'id': '17273552679',
        #  'clientOrderId': 'x-R4BD3S82f39065cd5f04b5c8e0b572', 'timestamp': 1673594488130,
        #  'datetime': '2023-01-13T07:21:28.130Z', 'lastTradeTimestamp': None, 'symbol': 'BTC/USDT', 'type': 'market',
        #  'timeInForce': 'GTC', 'postOnly': False, 'reduceOnly': None, 'side': 'buy', 'price': 18817.67,
        #  'stopPrice': None, 'amount': 0.00058, 'cost': 10.9142486, 'average': 18817.67, 'filled': 0.00058,
        #  'remaining': 0.0, 'status': 'closed', 'fee': None,
        #  'trades':
        #      [{'info': {'price': '18817.67000000',
        #        'qty': '0.00058000',
        #        'commission': '0.00000000',
        #        'commissionAsset': 'BNB',
        #        'tradeId': '2472442201'},
        #        'timestamp': None, 'datetime': None,
        #        'symbol': 'BTC/USDT', 'id': '2472442201',
        #        'order': '17273552679', 'type': 'market',
        #        'side': 'buy', 'takerOrMaker': None,
        #        'price': 18817.67, 'amount': 0.00058,
        #        'cost': 10.9142486,
        #        'fee': {'cost': 0.0, 'currency': 'BNB'},
        #        'fees': [{'cost': 0.0, 'currency': 'BNB'}]}],
        #  'fees': []}

        print(f'requestd volume : {enter_long_vol}')
        market_vol_without_fee = enter_long_vol * (1 - fee_ratio)
        print(f'{market_vol_without_fee=}')
        response_sell = exchange.create_order(symbol=tgt_market, type='market', side='sell', amount=market_vol_without_fee, price=price)
        print(response_sell)
        # Response
        # {'info': {'symbol': 'BTCUSDT', 'orderId': '17273552707', 'orderListId': '-1',
        #           'clientOrderId': 'x-R4BD3S82ba62721f4ed91f541031de', 'transactTime': '1673594488180',
        #           'price': '0.00000000', 'origQty': '0.00058000', 'executedQty': '0.00058000',
        #           'cummulativeQuoteQty': '10.91392380', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'MARKET',
        #           'side': 'SELL', 'workingTime': '1673594488180', 'fills': [
        #         {'price': '18817.11000000', 'qty': '0.00058000', 'commission': '0.00000000', 'commissionAsset': 'BNB',
        #          'tradeId': '2472442211'}], 'selfTradePreventionMode': 'NONE'}, 'id': '17273552707',
        #  'clientOrderId': 'x-R4BD3S82ba62721f4ed91f541031de', 'timestamp': 1673594488180,
        #  'datetime': '2023-01-13T07:21:28.180Z', 'lastTradeTimestamp': None, 'symbol': 'BTC/USDT', 'type': 'market',
        #  'timeInForce': 'GTC', 'postOnly': False, 'reduceOnly': None, 'side': 'sell', 'price': 18817.11,
        #  'stopPrice': None, 'amount': 0.00058, 'cost': 10.9139238, 'average': 18817.11, 'filled': 0.00058,
        #  'remaining': 0.0, 'status': 'closed', 'fee': None,
        #  'trades': [{'info': {'price': '18817.11000000',
        #     'qty': '0.00058000',
        #     'commission': '0.00000000',
        #     'commissionAsset': 'BNB',
        #     'tradeId': '2472442211'},
        #     'timestamp': None, 'datetime': None,
        #     'symbol': 'BTC/USDT', 'id': '2472442211',
        #     'order': '17273552707', 'type': 'market',
        #     'side': 'sell', 'takerOrMaker': None,
        #     'price': 18817.11, 'amount': 0.00058,
        #     'cost': 10.9139238,
        #     'fee': {'cost': 0.0, 'currency': 'BNB'},
        #     'fees': [{'cost': 0.0, 'currency': 'BNB'}]}],
        #  'fees': []}


    def test_enter_long_exit_long_bithumb_using_ccxt(self):
        ## Fetch Price
        tgt_market = 'KRW-ETH'
        price = fetch_current_market_price(ExType.bithumb, tgt_market)
        min_krw = 5100
        fee_ratio = 0.0004
        enter_long_vol = round(min_krw * (1 - fee_ratio) / price, 8)
        print(f"{enter_long_vol=}")

        ccxt_wrapper = ExConnFactory.instance().get_ex_conn(ExType.bithumb, stkim_bithumb_access_key, stkim_bithumb_secrete_key)
        exchange = ccxt_wrapper.get_ccxt_ex()
        print(f'requested price : {price}')
        uniformed_tgt_mkt = std_2_uniformed_mkt_id(tgt_market)
        # response_buy = exchange.create_order(symbol=uniformed_tgt_mkt, type = 'market', side='buy', amount=enter_long_vol, price=price)
        response_buy = exchange.create_order(symbol = uniformed_tgt_mkt, type = 'market', side = 'buy',amount = enter_long_vol)
        print(f'## ccxt enter_long: {uniformed_tgt_mkt=}, {price=}, {enter_long_vol=}')

        print(response_buy)
        # Response
        # {'info'                :
        #   {'status' : '0000', 'order_id' : 'C0101000002054035018'},
        #       'symbol' : 'BTC/KRW',
        #       'type'   : 'market', 'side' : 'buy', 'id' : 'C0101000002054035018', 'fees' : [],
        #  'clientOrderId'       : None, 'timestamp' : None, 'datetime' : None, 'lastTradeTimestamp' : None,
        #  'lastUpdateTimestamp' : None, 'price' : None, 'amount' : None, 'cost' : None, 'average' : None,
        #  'filled'              : None, 'remaining' : None, 'timeInForce' : 'IOC', 'postOnly' : None, 'trades' : [],
        #  'reduceOnly'          : None, 'stopPrice' : None, 'triggerPrice' : None, 'takeProfitPrice' : None,
        #  'stopLossPrice'       : None, 'status' : None, 'fee' : None}

        print(f'requestd volume : {enter_long_vol}')
        market_vol_without_fee = round(enter_long_vol * (1 - fee_ratio), 8)
        print(f'{market_vol_without_fee=}')
        response_sell = exchange.create_order(symbol=uniformed_tgt_mkt, type='market', side='sell', amount=market_vol_without_fee, price=price)
        print(f'## ccxt exit_long: {tgt_market=}, {price=}, {market_vol_without_fee=}')
        print(response_sell)
        # Response
        # {'info'                :
        #   {'status' : '0000', 'order_id' : 'C0101000002054039402'},
        #   'symbol' : 'BTC/KRW',
        #  'type'                : 'market', 'side' : 'sell',
        #  'id' : 'C0101000002054039402', 'fees' : [],
        #  'clientOrderId'       : None, 'timestamp' : None, 'datetime' : None, 'lastTradeTimestamp' : None,
        #  'lastUpdateTimestamp' : None, 'price' : None, 'amount' : None, 'cost' : None, 'average' : None,
        #  'filled'              : None, 'remaining' : None, 'timeInForce' : 'IOC', 'postOnly' : None, 'trades' : [],
        #  'reduceOnly'          : None, 'stopPrice' : None, 'triggerPrice' : None, 'takeProfitPrice' : None,
        #  'stopLossPrice'       : None, 'status' : None, 'fee' : None}

    @unittest.skip("Tested")
    def test_enter_long_exit_long_upbit_using_ccxt(self):
        ## Fetch Price
        tgt_market = 'KRW-BTC'
        price = fetch_current_market_price(ExType.upbit, tgt_market)
        min_krw = 5100
        fee_ratio = 0.001
        enter_long_vol = min_krw * (1 - fee_ratio) / price

        ccxt_wrapper = ExConnFactory.instance().get_ex_conn(ExType.upbit,
                                                            mingu_upbit_access_key, mingu_upbit_secret_key)
        exchange = ccxt_wrapper.get_ccxt_ex()
        print(f'requested price : {price}')
        response_buy = exchange.create_order(symbol=tgt_market, type = 'market', side='buy', amount=enter_long_vol, price=price)
        print(f'## ccxt enter_long: {tgt_market=}, {price=}, {enter_long_vol=}')

        print(response_buy)
        # Response
        # {'info': {'uuid': '57af968a-ce17-4a60-b92f-e7bd7b217c99', 'side': 'bid', 'ord_type': 'price', 'price': '5094.9',
        #           'state': 'wait', 'market': 'KRW-BTC', 'created_at': '2023-01-13T14:31:15.704547+09:00',
        #           'reserved_fee': '2.54745', 'remaining_fee': '2.54745', 'paid_fee': '0', 'locked': '5097.44745',
        #           'executed_volume': '0', 'trades_count': '0'}, 'id': '57af968a-ce17-4a60-b92f-e7bd7b217c99',
        #  'clientOrderId': None, 'timestamp': 1673620275704, 'datetime': '2023-01-13T14:31:15.704Z',
        #  'lastTradeTimestamp': None, 'symbol': 'BTC/KRW', 'type': 'market', 'timeInForce': None, 'postOnly': None,
        #  'side': 'buy', 'price': None, 'stopPrice': None, 'cost': 5094.9, 'average': None, 'amount': None,
        #  'filled': 0.0, 'remaining': None, 'status': 'open', 'fee': {'currency': 'KRW', 'cost': 0.0}, 'trades': []}

        print(f'requestd volume : {enter_long_vol}')
        market_vol_without_fee = enter_long_vol * (1 - fee_ratio)
        print(f'{market_vol_without_fee=}')
        response_sell = exchange.create_order(symbol=tgt_market, type='market', side='sell', amount=market_vol_without_fee, price=price)
        print(f'## ccxt exit_long: {tgt_market=}, {price=}, {market_vol_without_fee=}')

        print(response_sell)
        # Response
        # {'info': {'uuid': '6bf1042c-207e-43d1-8327-af7c078d7c4b', 'side': 'ask', 'ord_type': 'market', 'state': 'wait',
        #           'market': 'KRW-BTC', 'created_at': '2023-01-13T14:35:18.585868+09:00', 'volume': '0.00021558',
        #           'remaining_volume': '0.00021558', 'reserved_fee': '0', 'remaining_fee': '0', 'paid_fee': '0',
        #           'locked': '0.00021558', 'executed_volume': '0', 'trades_count': '0'},
        #  'id': '6bf1042c-207e-43d1-8327-af7c078d7c4b', 'clientOrderId': None, 'timestamp': 1673620518585,
        #  'datetime': '2023-01-13T14:35:18.585Z', 'lastTradeTimestamp': None, 'symbol': 'BTC/KRW', 'type': 'market',
        #  'timeInForce': None, 'postOnly': None, 'side': 'sell', 'price': None, 'stopPrice': None, 'cost': None,
        #  'average': None, 'amount': 0.00021558, 'filled': 0.0, 'remaining': 0.00021558, 'status': 'open',
        #  'fee': {'currency': 'KRW', 'cost': 0.0}, 'trades': []}

    @unittest.skip("Tested")
    def test_binance_fetch_trading_fees(self):
        ccxt_wrapper = ExConnFactory.instance().get_ex_conn(ExType.binance,
                                                            stkim_binance_access_key, stkim_binance_secret_key)
        exchange = ccxt_wrapper.get_ccxt_ex()
        trading_fees = exchange.fetchTradingFees()
        print(trading_fees)

        ## Response
        ## TODO: The followings can be used for making DummyBinanceExchange()
        # {
        #  'BTC/USDT': {'info': {'symbol': 'BTCUSDT', 'makerCommission': '0', 'takerCommission': '0'},
        #               'symbol': 'BTC/USDT', 'maker': 0.0, 'taker': 0.0},
        #  'ETH/USDT': {'info': {'symbol': 'ETHUSDT', 'makerCommission': '0.001', 'takerCommission': '0.001'},
        #               'symbol': 'ETH/USDT', 'maker': 0.001, 'taker': 0.001},
        #  'XRP/USDT': {'info': {'symbol': 'XRPUSDT', 'makerCommission': '0.001', 'takerCommission': '0.001'},
        #               'symbol': 'XRP/USDT', 'maker': 0.001, 'taker': 0.001},
        # }


    def test_fetch_balances_bithumb(self):

        ex_conn = ExConnFactory.instance().get_ex_conn(ExType.bithumb,
                                                       stkim_bithumb_access_key, stkim_bithumb_secrete_key)
        ex_conn.fetch_balances()
        print(ex_conn.balances)


    # @unittest.skip("Tested")
    def test_fetch_balances_binance2(self):

        ex_conn = ExConnFactory.instance().get_ex_conn(ExType.binance,
                                                       stkim_binance_access_key, stkim_binance_secret_key)
        ex_conn.fetch_balances()
        print(f'USDT:', ex_conn.get_balance('USDT'))
        print(f'BTC:', ex_conn.get_balance('BTC'))
        print(f'ETH:', ex_conn.get_balance('ETH'))
        print(f'XRP:', ex_conn.get_balance('XRP'))

    @unittest.skip("Tested")
    def test_fetch_balances_binance(self):

        binance = ccxt.binance({
            'apiKey': stkim_binance_access_key,
            'secret': stkim_binance_secret_key
        })

        print('fetch_balance')
        print(binance.fetch_balance())

        # {'info': {'makerCommission': '10', 'takerCommission': '10', 'buyerCommission': '0', 'sellerCommission': '0',
        #           'commissionRates': {'maker': '0.00100000', 'taker': '0.00100000', 'buyer': '0.00000000',
        #                               'seller': '0.00000000'}, 'canTrade': True, 'canWithdraw': True,
        #           'canDeposit': True, 'brokered': False, 'requireSelfTradePrevention': False,
        #           'updateTime': '1673400368771', 'accountType': 'SPOT',
        #           'balances': [{'asset': 'BTC', 'free': '0.00000000', 'locked': '0.00000000'},
        #                        {'asset': 'ETH', 'free': '0.00000000', 'locked': '0.00000000'},
        #                        {'asset': 'USDT', 'free': '0.00000000', 'locked': '0.00000000'},
        #                        {'asset': 'HIFI', 'free': '0.00000000', 'locked': '0.00000000'}],
        #           'permissions': ['SPOT']},
        #  'BTC': {'free': 0.0, 'used': 0.0, 'total': 0.0},
        #  'ETH': {'free': 0.0, 'used': 0.0, 'total': 0.0},
        #  'USDT': {'free': 0.0, 'used': 0.0, 'total': 0.0},
        #  'timestamp': 1673400368771, 'datetime': '2023-01-11T01:26:08.771Z',
        #  'free': {'BTC': 0.0, 'ETH': 0.0, 'USDT': 0.0, 'XRP': 21.288549, 'MOD': 0.0, ...},
        #  'used': {'BTC': 0.0, 'ETH': 0.0, 'USDT': 0.0, 'XRP': 0.0,  ...},
        #  'total': {'BTC': 0.0, 'ETH': 0.0, 'USDT': 0.0, 'XRP': 21.288549, 'MOD': 0.0,}}


    if __name__ == '__main__':
        unittest.main()


