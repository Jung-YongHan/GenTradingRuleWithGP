import importlib
import time
from abc import *

import ccxt
import pandas as pd
from ccxt import ExchangeError

from bt4.Constants import ExType
from bt4.trade.ExConnectorResponse import ExResponseHandlerFactory
from bt4.utils.exchange_filter import ExFilterFactory
from bt4.utils.mylog import init_log
from bt4.utils.pandas_utils import sort_df
from bt4.utils.python_utils import SingletonInstance, load_class_from_module
from bt4.utils.pyupbit_ex import Upbit_Ex

'''
check the following web site
## https://github.com/sharebook-kr/pyupbit
'''
log = init_log()

class AbstractExConnector(metaclass=ABCMeta):
    def __init__(self):
        self.min_rebalance_limit = self.get_minimum_base_amount_for_rebalance()

    def get_min_rebalance_limit(self):
        return self.min_rebalance_limit

    def set_min_rebalance_limit(self, rebal_limit):
        self.min_rebalance_limit = rebal_limit

    @abstractmethod
    def get_base_currency(self):
        pass

    @abstractmethod
    def get_post_market(self):
        pass

    @abstractmethod
    def get_post_amount(self):
        pass

    @abstractmethod
    def fetch_balances(self):
        pass

    @abstractmethod
    def get_balance(self, currency):
        pass

    @abstractmethod
    def get_fee_ratio(self):
        pass

    @abstractmethod
    def get_minimum_base_amount_for_rebalance(self):
        pass

    @abstractmethod
    def enter_long(self, market, price, volume):
        pass

    @abstractmethod
    def exit_long(self, market, volume, price=0):
        pass

    def enter_short(self, market, price, volume):
        pass

    def exit_short(self, market, volume, price=0):
        pass

    def get_settled_orders(self, markets):
        pass

    def get_order(self, uuid):
        pass

    def cancel_order(self, uuid):
        pass




class ExConnFactory(SingletonInstance):
    def __init__(self):
        self.ex_connectors = {}

    def get_ex_conn(self, ex_type, access_key = None, secrete_key = None, feature_markets = None,
                    admin_params = None):
        ex_conn_key = (ex_type, access_key, secrete_key)

        if ex_conn_key in self.ex_connectors:
            return self.ex_connectors[ex_conn_key]
        else:
            if ex_type.name.startswith('dummy'):
                core_package_name = "bt4.trade."
                ex_connector = load_class_from_module(core_package_name + "DummyExConnector",
                                        ex_type.value + 'ExConnector')
                self.ex_connectors[ex_conn_key] = ex_connector
            else:
                if access_key is None and secrete_key is None:
                    log.error('Access and Secrete keys should be delivered to create ExchangeConnector for live trading.')
                    return None

                config = {
                    'apiKey': access_key,
                    'secret': secrete_key
                }

                for_ccxt_creation_ex_type = ex_type
                if ex_type == ExType.binanceusdm:
                    config['enableRateLimit'] = True
                    config['options'] = {'defaultType': 'future'}
                    for_ccxt_creation_ex_type = ExType.binance

                if admin_params is None:
                    exchange_class = getattr(ccxt, for_ccxt_creation_ex_type.value)
                    exchange = exchange_class(config)
                else:
                    mod = importlib.import_module(admin_params['module'])
                    exchange_class = getattr(mod, admin_params['conn_ex'])
                    exchange = exchange_class(config)

                if ex_type == ExType.binanceusdm :
                    try :
                        exchange.set_position_mode(hedged = True)
                    except ExchangeError as e :
                        print("Already in hedge mode, ", e)
                    if feature_markets is not None:
                        for f_market in feature_markets:
                            exchange.set_leverage(leverage = 1, symbol = f_market) ## TODO
                            exchange.set_margin_mode(marginMode = "ISOLATED", symbol = f_market) ## TODO

                ex_connector = CCXTWrapperExchange(ex_type, exchange)
                self.ex_connectors[ex_conn_key] = ex_connector

        return self.ex_connectors[ex_conn_key]


class CCXTWrapperExchange(AbstractExConnector):

    def __init__(self, ex_type, ccxt_ex):
        self.ex_type = ex_type
        super(CCXTWrapperExchange, self).__init__()
        self.ccxt_ex = ccxt_ex
        self.balances = {}
        self.is_live_trading = True
        self.ex_filter = ExFilterFactory.instance().get(ex_type)
        self.ex_resp_handler = ExResponseHandlerFactory.instance().get(ex_type)

    def get_base_currency(self):
        if self.ex_type == ExType.upbit or self.ex_type == ExType.bithumb:
            return 'KRW'
        if self.ex_type == ExType.binance or self.ex_type == ExType.binanceusdm:
            return 'USDT'

    def get_ccxt_ex(self):
        return self.ccxt_ex

    def fetch_balances(self):
        bal_dic = self.ccxt_ex.fetch_balance()

        for bal_key in bal_dic:
            if isinstance(bal_dic[bal_key], dict):
                if len(bal_dic[bal_key]) == 3 and 'free' in bal_dic[bal_key] and 'used' in bal_dic[bal_key] and 'total' in bal_dic[bal_key]:
                    bal = bal_dic[bal_key]
                    cur_bal = CurrencyBalance(bal_key, float(bal['free']), float(bal['used']), bal['total'])
                    self.balances[cur_bal.currency] = cur_bal
                    amount = bal['free']
                    if amount > 0:
                        log.info(f'[{self.ex_type.value}] load - balance {cur_bal.currency}:{amount}')

    def get_balance(self, currency):
        if currency in self.balances:
            return self.balances[currency].free
        else:
            return 0

    def get_fee_ratio(self):
        if self.ex_type == ExType.upbit:
            return 0.0005
        if self.ex_type == ExType.bithumb:
            return 0.0004
        if self.ex_type == ExType.binance:
            return 0.001
        if self.ex_type == ExType.binanceusdm:
            return 0.0004

    def get_post_market(self):
        if self.ex_type == ExType.upbit:
            return "KRW-BTC"
        if self.ex_type == ExType.bithumb :
            return "KRW-ETH"
        if self.ex_type == ExType.binance:
            return "USDT-BTC"
        if self.ex_type == ExType.binanceusdm:
            return "USDT-BTC"


    def get_post_amount(self):
        if self.ex_type == ExType.upbit or self.ex_type == ExType.bithumb :
            return 5100 #KRW
        if self.ex_type == ExType.binance:
            return 11   #USDT
        if self.ex_type == ExType.binanceusdm:
            return 11   #USDT

    def get_minimum_base_amount_for_rebalance(self):
        if self.ex_type == ExType.upbit or self.ex_type == ExType.bithumb :
            return 50000
        if self.ex_type == ExType.binance:
            return 11
        if self.ex_type == ExType.binanceusdm:
            return 11

    def enter_long(self, market, price, volume):
        market = self.ex_filter.filter_market_id_before(market) # KRW-BTC -> BTC/KRW (bithumb)
        volume = self.ex_filter.filter_volume(volume)    # 소수 8자리에서 round (bithumb)
        is_processed = False

        order_price = price * volume ## order_price * vol = market_cash_bal * (1-fee)
        # log.info(f'{self.ex_type.name} ######## buy_position(try):{market}, price = {order_price}')
        log.info(f'{self.ex_type.name} ######## buy_position(try):{market}, price = {price}')
        buy_request_result = self.execute_enter_long(market, price, volume)
        print(f'initial order status : {buy_request_result.status}')
        if buy_request_result.status == 'open':
            while True:
                time.sleep(0.2)
                # time.sleep(5)
                # buy_order_state_result = self.get_order(buy_request_result.id, market)
                # log.info(f'sleep for waiting the market order({order_price} at {market}) to be settled. current status is \'{buy_order_state_result.status}\'')
                # if buy_order_state_result.status == 'closed' or buy_order_state_result.status == 'canceled':
                #     break

                order_status = self.get_order_status(buy_request_result.id, market)
                log.info(f'sleep for waiting the market order({order_price} at {market}) to be settled. current status is \'{order_status}\'')
                if order_status == 'closed' or order_status == 'canceled':
                    time.sleep(0.2)
                    buy_order_state_result = self.get_order(buy_request_result.id, market)
                    break

        avg_price = price
        total_vol = volume
        if buy_order_state_result is not None:
            paid_fee = 0 if buy_order_state_result.paid_fee is None else buy_order_state_result.paid_fee
            total_vol = buy_order_state_result.amount
            if buy_order_state_result.trades_count > 0:
                total_prices = 0
                total_vol = 0
                for trade in buy_order_state_result.trades:
                    total_prices += trade.price
                    total_vol += trade.amount
                avg_price = total_prices / buy_order_state_result.trades_count
            is_processed = True
        else:
            paid_fee = -1

        log.info(f'######## buy_position(result):{is_processed}, price = {avg_price}, vol={total_vol}, fee={paid_fee}')
        return is_processed, avg_price, total_vol, paid_fee

    def execute_enter_long(self, market, price, volume):
        if self.is_live_trading:
            log.info(f'## ccxt enter_long: {market=}, {price=}, {volume=}')
            result = self.ccxt_ex.create_order(symbol=market, type = 'market', side='buy', amount=volume, price=price)
        else:
            if self.ex_type == ExType.upbit:
                result = {'info': {'uuid': '57af968a-ce17-4a60-b92f-e7bd7b217c99', 'side': 'bid', 'ord_type': 'price', 'price': '5094.9', 'state': 'wait', 'market': 'KRW-BTC', 'created_at': '2023-01-13T14:31:15.704547+09:00', 'reserved_fee': '2.54745', 'remaining_fee': '2.54745', 'paid_fee': '0', 'locked': '5097.44745', 'executed_volume': '0', 'trades_count': '0'},
                          'id': '57af968a-ce17-4a60-b92f-e7bd7b217c99', 'clientOrderId': None, 'timestamp': 1673620275704, 'datetime': '2023-01-13T14:31:15.704Z', 'lastTradeTimestamp': None, 'symbol': 'BTC/KRW', 'type': 'market', 'timeInForce': None, 'postOnly': None,
                          'side': 'buy', 'price': None, 'stopPrice': None, 'cost': 5094.9, 'average': None, 'amount': None,'filled': 0.0, 'remaining': None, 'status': 'open','fee': {'currency': 'KRW', 'cost': 0.0}, 'trades': []}

            if self.ex_type == ExType.bithumb:
                result = {'info' : {'status' : '0000', 'order_id' : 'C0101000002054035018'}, 'symbol' : 'BTC/KRW', 'type'   : 'market', 'side' : 'buy',
                          'id' : 'C0101000002054035018', 'fees' : [], 'clientOrderId'  : None, 'timestamp' : None, 'datetime' : None, 'lastTradeTimestamp' : None,
                          'lastUpdateTimestamp' : None, 'price' : None, 'amount' : None, 'cost' : None, 'average' : None,
                          'filled'              : None, 'remaining' : None, 'timeInForce' : 'IOC', 'postOnly' : None, 'trades' : [],
                          'reduceOnly'          : None, 'stopPrice' : None, 'triggerPrice' : None, 'takeProfitPrice' : None,
                          'stopLossPrice'       : None, 'status' : None, 'fee' : None}

            if self.ex_type == ExType.binance:
                result = {'info': {'symbol': 'BTCUSDT', 'orderId': '17273552679', 'orderListId': '-1', 'clientOrderId': 'x-R4BD3S82f39065cd5f04b5c8e0b572', 'transactTime': '1673594488130', 'price': '0.00000000', 'origQty': '0.00058000', 'executedQty': '0.00058000','cummulativeQuoteQty': '10.91424860', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'MARKET','side': 'BUY', 'workingTime': '1673594488130','fills': [{'price': '18817.67000000', 'qty': '0.00058000', 'commission': '0.00000000','commissionAsset': 'BNB', 'tradeId': '2472442201'}],'selfTradePreventionMode': 'NONE'},
                        'id': '17273552679', 'clientOrderId': 'x-R4BD3S82f39065cd5f04b5c8e0b572', 'timestamp': 1673594488130,'datetime': '2023-01-13T07:21:28.130Z', 'lastTradeTimestamp': None, 'symbol': 'BTC/USDT', 'type': 'market','timeInForce': 'GTC', 'postOnly': False, 'reduceOnly': None, 'side': 'buy', 'price': 18817.67,
                        'stopPrice': None, 'amount': 0.00058, 'cost': 10.9142486, 'average': 18817.67, 'filled': 0.00058,'remaining': 0.0, 'status': 'closed', 'fee': None,'trades': [{'info': {'price': '18817.67000000', 'qty': '0.00058000', 'commission': '0.00000000', 'commissionAsset': 'BNB', 'tradeId': '2472442201'}, 'timestamp': None, 'datetime': None, 'symbol': 'BTC/USDT', 'id': '2472442201', 'order': '17273552679', 'type': 'market','side': 'buy', 'takerOrMaker': None, 'price': 18817.67, 'amount': 0.00058, 'cost': 10.9142486, 'fee': {'cost': 0.0, 'currency': 'BNB'},'fees': [{'cost': 0.0, 'currency': 'BNB'}]}],'fees': []}

            if self.ex_type == ExType.binanceusdm:
                result = {'info': {'orderId': '106728401464', 'symbol': 'BTCUSDT', 'status': 'FILLED','clientOrderId': 'x-xcKtGhcu3ddb89bfe302e4154a594c', 'price': '0', 'avgPrice': '18835.10000','origQty': '0.001', 'executedQty': '0.001', 'cumQty': '0.001', 'cumQuote': '18.83510','timeInForce': 'GTC', 'type': 'MARKET', 'reduceOnly': False, 'closePosition': False,
                          'side': 'BUY', 'positionSide': 'BOTH', 'stopPrice': '0', 'workingType': 'CONTRACT_PRICE','priceProtect': False, 'origType': 'MARKET', 'updateTime': '1673598790512'}, 'id': '106728401464', 'clientOrderId': 'x-xcKtGhcu3ddb89bfe302e4154a594c', 'timestamp': None,'datetime': None, 'lastTradeTimestamp': None, 'symbol': 'BTC/USDT', 'type': 'market','timeInForce': 'GTC', 'postOnly': False, 'reduceOnly': False, 'side': 'buy', 'price': 18835.1,
                         'stopPrice': None, 'amount': 0.001, 'cost': 18.8351, 'average': 18835.1, 'filled': 0.001,'remaining': 0.0, 'status': 'closed', 'fee': None, 'trades': [], 'fees': []}
        return self.ex_resp_handler.handle(result)

    def get_order(self, uuid, market):
        result = self.ccxt_ex.fetch_order(uuid, symbol = market)
        return self.ex_resp_handler.handle(result)

    def get_order_status(self, uuid, market):
        return self.ccxt_ex.fetch_order_status(id = uuid, symbol = market)

    def exit_long(self, market, volume, price=0):
        market = self.ex_filter.filter_market_id_before(market)  # KRW-BTC -> BTC/KRW (bithumb)
        volume = self.ex_filter.filter_volume(volume)  # 소수 8자리에서 round (bithumb)

        is_processed = False
        log.info(f'######## sell_position(try):{market}, volume = {volume}')

        sell_result = self.execute_exit_long(market, volume)
        if sell_result.status == 'open':
            while True:
                time.sleep(0.2)
                # order_state = self.get_order(sell_result.id, market)
                # log.info(f'sleep for waiting the market order({volume} at {market}) to be settled.')
                # if order_state.status == 'closed':
                #     break

                order_status = self.get_order_status(sell_result.id, market)
                log.info(f'sleep for waiting the market order({volume} at {market}) to be settled. current status is \'{order_status}\'')

                if order_status == 'closed' or order_status == 'canceled':
                    time.sleep(0.2)
                    sell_result = self.get_order(sell_result.id, market)
                    break

        avg_price = 0
        if sell_result is not None:
            paid_fee = 0 if sell_result.paid_fee is None else sell_result.paid_fee
            total_vol = sell_result.amount
            if sell_result.trades_count > 0:
                total_prices = 0
                total_vol = 0
                for trade in sell_result.trades:
                    total_prices += trade.price
                    total_vol += trade.amount
                avg_price = total_prices / sell_result.trades_count
            is_processed = True
        else:
            paid_fee = -1

        log.info(f'######## sell_position(result):{is_processed}, price = {avg_price}, vol={total_vol}, fee={paid_fee}')
        return is_processed, avg_price, total_vol, paid_fee


    def execute_exit_long(self, market, volume, price=0):
        if self.is_live_trading:
            log.info(f'## ccxt exit_long: {market=}, {price=}, {volume=}')
            result = self.ccxt_ex.create_order(symbol=market, type='market', side='sell', amount=volume)
        else:
            if self.ex_type == ExType.upbit:
                result = {'info': {'uuid': '6bf1042c-207e-43d1-8327-af7c078d7c4b', 'side': 'ask', 'ord_type': 'market', 'state': 'wait', 'market': 'KRW-BTC', 'created_at': '2023-01-13T14:35:18.585868+09:00', 'volume': '0.00021558','remaining_volume': '0.00021558', 'reserved_fee': '0', 'remaining_fee': '0', 'paid_fee': '0','locked': '0.00021558', 'executed_volume': '0', 'trades_count': '0'},
                 'id': '6bf1042c-207e-43d1-8327-af7c078d7c4b', 'clientOrderId': None, 'timestamp': 1673620518585, 'datetime': '2023-01-13T14:35:18.585Z', 'lastTradeTimestamp': None, 'symbol': 'BTC/KRW', 'type': 'market', 'timeInForce': None, 'postOnly': None, 'side': 'sell', 'price': None, 'stopPrice': None, 'cost': None,'average': None, 'amount': 0.00021558, 'filled': 0.0, 'remaining': 0.00021558, 'status': 'open','fee': {'currency': 'KRW', 'cost': 0.0}, 'trades': []}

            elif self.ex_type == ExType.bithumb:
                result = {'info' : {'status' : '0000', 'order_id' : 'C0101000002054039402'}, 'symbol' : 'BTC/KRW',  'type' : 'market', 'side' : 'sell',
                  'id' : 'C0101000002054039402', 'fees' : [], 'clientOrderId'       : None, 'timestamp' : None, 'datetime' : None, 'lastTradeTimestamp' : None, 'lastUpdateTimestamp' : None, 'price' : None, 'amount' : None, 'cost' : None, 'average' : None,
                 'filled'              : None, 'remaining' : None, 'timeInForce' : 'IOC', 'postOnly' : None, 'trades' : [], 'reduceOnly'          : None, 'stopPrice' : None, 'triggerPrice' : None, 'takeProfitPrice' : None, 'stopLossPrice'       : None, 'status' : None, 'fee' : None}

            elif self.ex_type == ExType.binance:
                result = {'info': {'symbol': 'BTCUSDT', 'orderId': '17273552707', 'orderListId': '-1', 'clientOrderId': 'x-R4BD3S82ba62721f4ed91f541031de', 'transactTime': '1673594488180', 'price': '0.00000000', 'origQty': '0.00058000', 'executedQty': '0.00058000',
                      'cummulativeQuoteQty': '10.91392380', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'MARKET', 'side': 'SELL', 'workingTime': '1673594488180', 'fills': [ {'price': '18817.11000000', 'qty': '0.00058000', 'commission': '0.00000000', 'commissionAsset': 'BNB', 'tradeId': '2472442211'}], 'selfTradePreventionMode': 'NONE'},
                     'id': '17273552707', 'clientOrderId': 'x-R4BD3S82ba62721f4ed91f541031de', 'timestamp': 1673594488180, 'datetime': '2023-01-13T07:21:28.180Z', 'lastTradeTimestamp': None, 'symbol': 'BTC/USDT', 'type': 'market', 'timeInForce': 'GTC', 'postOnly': False, 'reduceOnly': None, 'side': 'sell', 'price': 18817.11, 'stopPrice': None, 'amount': 0.00058, 'cost': 10.9139238, 'average': 18817.11, 'filled': 0.00058, 'remaining': 0.0, 'status': 'closed', 'fee': None,
                     'trades': [{'info': {'price': '18817.11000000', 'qty': '0.00058000', 'commission': '0.00000000', 'commissionAsset': 'BNB', 'tradeId': '2472442211'}, 'timestamp': None, 'datetime': None, 'symbol': 'BTC/USDT', 'id': '2472442211','order': '17273552707', 'type': 'market', 'side': 'sell', 'takerOrMaker': None,'price': 18817.11, 'amount': 0.00058,'cost': 10.9139238,'fee': {'cost': 0.0, 'currency': 'BNB'}, 'fees': [ {'cost': 0.0, 'currency': 'BNB'}]}],'fees': []}

            elif self.ex_type == ExType.binanceusdm:
                result = {'info': {'orderId': '106728401981', 'symbol': 'BTCUSDT', 'status': 'FILLED', 'clientOrderId': 'x-xcKtGhcuce9be9bb1e744b7243170b', 'price': '0', 'avgPrice': '18835.00000','origQty': '0.001', 'executedQty': '0.001', 'cumQty': '0.001', 'cumQuote': '18.83500','timeInForce': 'GTC', 'type': 'MARKET', 'reduceOnly': False, 'closePosition': False, 'side': 'SELL', 'positionSide': 'BOTH', 'stopPrice': '0', 'workingType': 'CONTRACT_PRICE',
                                'priceProtect': False, 'origType': 'MARKET', 'updateTime': '1673598790725'},'id': '106728401981', 'clientOrderId': 'x-xcKtGhcuce9be9bb1e744b7243170b', 'timestamp': None,'datetime': None, 'lastTradeTimestamp': None, 'symbol': 'BTC/USDT', 'type': 'market', 'timeInForce': 'GTC', 'postOnly': False, 'reduceOnly': False, 'side': 'sell', 'price': 18835.0,'stopPrice': None, 'amount': 0.001, 'cost': 18.835, 'average': 18835.0, 'filled': 0.001,'remaining': 0.0, 'status': 'closed', 'fee': None, 'trades': [], 'fees': []
                          }
        return self.ex_resp_handler.handle(result)

    def get_settled_orders(self, markets):
        df_data_dict = {}
        for market in markets:
            trade_list = self.ccxt_ex.fetch_trades(market)
            for trade in trade_list:
                id = trade.pop('id')
                trade.pop('info')
                trade.pop('fees')
                df_data_dict[id] = trade
        df = pd.DataFrame(df_data_dict)
        df.index.name = 'id'
        df = df.T
        df = df.sort_index(ascending=True)
        return df

    def fetch_my_trades(self):
        print("fetch_my_trades")
        return self.ccxt_ex.fetch_my_trades()

class CurrencyBalance:
    def __init__(self, currency, free, used, total):
        self.currency = currency
        self.free = free
        self.used = used
        self.total = total


class FutureBalance:
    def __init__(self, long, short, balance=0.0):
        self.long = long
        self.short = short
        self.balance = balance