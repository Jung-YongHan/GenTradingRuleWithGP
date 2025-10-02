import datetime
import functools
import hashlib
import json
import unittest
from urllib.parse import urlencode

import jwt
import pandas as pd
import pyupbit
import redis
import requests
from ccxt import Exchange

from bt4.Constants import CandleType, ExType
from bt4.quote.QuoteConnector import UniversalQuoteConnector, UpbitQuoteConnector
from bt4.quote.QuoteSupport import Quote, Tick
from bt4.utils.pandas_utils import sort_df
from bt4.utils.python_utils import (
    TIME_FORMAT,
    create_dt_at,
    from_utc_int_timestamp,
    get_1min_before_dt,
    now_dt,
    str2dt,
    svr2local_dt,
    to_kst_time,
    to_utc_int_timestamp, start_timing, end_n_elapsed_time,
)

# from bt3_config.quote_conf import QUOTE_PARAMS
# from bt3_test._S03_ExchangeConnectorTest import stkim_upbit_access_key, stkim_upbit_secret_key

pd.set_option('display.max_columns', None)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('max_colwidth', None)

# from bulltrader_test.ExchangeGateway import UpbitExchangeGateway


class MyTestCase(unittest.TestCase):

    def test_binance_fetch_quote_num_candles(self):
        markets = ["USDT-BTC"]
        to_now_dt = datetime.datetime.now()
        uqc = UniversalQuoteConnector.instance()
        cdl_type = CandleType.MINUTES_1
        # _num_of_cdls = int(60 * 24 * 365 * 5 / cdl_type)
        _num_of_cdls = int(60 * 24 * 200 / cdl_type)
        print(f"download {_num_of_cdls} {cdl_type.name} candles")
        ccxt_dfs = uqc.fetch_quote_num_candles(ExType.binance, markets, _num_of_cdls, CandleType.MINUTES_1)
        for market in ccxt_dfs:
            market_df = ccxt_dfs[market]
            market_df.to_csv(f'{market}.csv')
            print(market_df.head(5))
            print(len(market_df))
            print(market_df.index.min())


    def test_bithumb_fetch_quote_num_candles(self):
        markets = ["KRW-BTC"]
        to_now_dt = datetime.datetime.now()
        uqc = UniversalQuoteConnector.instance()
        cdl_type = CandleType.MINUTES_1
        _num_of_cdls = int(60 * 24 * 365 * 5 / cdl_type)
        # _num_of_cdls = int(60 * 24 * 200 / cdl_type)
        print(f"download {_num_of_cdls} {cdl_type.name} candles")
        ccxt_dfs = uqc.fetch_quote_num_candles(ExType.bithumb, markets, _num_of_cdls, CandleType.MINUTES_1)
        for market in ccxt_dfs:
            market_df = ccxt_dfs[market]
            market_df.to_csv(f'{market}.csv')
            print(market_df.head(5))
            print(len(market_df))
            print(market_df.index.min())

    def test_upbit_fetch_quote_num_candles(self):
        markets = ["KRW-BTC"]
        to_now_dt = datetime.datetime.now()
        uqc = UniversalQuoteConnector.instance()
        cdl_type = CandleType.MINUTES_1
        # _num_of_cdls = int(60 * 24 * 365 * 5 / cdl_type)
        _num_of_cdls = int(60 * 24 * 200 / cdl_type)
        upbit_ccxt_dfs = uqc.fetch_quote_num_candles(ExType.upbit, markets, _num_of_cdls, CandleType.MINUTES_1)
        for market in upbit_ccxt_dfs:
            market_df = upbit_ccxt_dfs[market]
            market_df.to_csv(f'{market}.csv')
            print(market_df.head(5))
            print(len(market_df))
            print(market_df.index.min())

    @unittest.skip("Tested")
    def test_binance_fetch_tick_quote(self):
        market = 'KRW-BTC'
        to_now_dt = datetime.datetime.now()
        uqc = UniversalQuoteConnector.instance()
        upbit_ccxt_df = uqc.fetch_tick_quote(ExType.upbit, market, 400, to_now_dt, CandleType.DAYS)
        print(upbit_ccxt_df.head(5))
        print(len(upbit_ccxt_df))
        print(upbit_ccxt_df.index.min())

        market = 'BTC/USDT'
        binance_ccxt_df = uqc.fetch_tick_quote(ExType.binance, market, 400, to_now_dt, CandleType.DAYS)
        print(binance_ccxt_df.head(5))
        print(len(binance_ccxt_df))
        print(binance_ccxt_df.index.min())

    @unittest.skip("Tested")
    def test_binance_quote(self):

        markets = QUOTE_PARAMS[ExType.binance]['markets']
        ##########################################
        uqc = UniversalQuoteConnector.instance()

        now = now_dt()
        desired_dt = create_dt_at(now.year, now.month, now.day, now.hour, now.minute, 0)
        ccxt_market_dfs = UniversalQuoteConnector.instance().fetch_quote_at(ExType.binance, markets, desired_dt)
        print(ccxt_market_dfs.tail(3))

        market_ticks = {}
        if ccxt_market_dfs is not None:
            for market in ccxt_market_dfs['market'].unique():
                market_df = ccxt_market_dfs[ccxt_market_dfs['market'] == market]
                data_list = [market_df.index[0].to_pydatetime().strftime(TIME_FORMAT)]
                data_list.extend(market_df.to_numpy()[0])
                tick2 = Tick.from_list(data_list)
                market_ticks[market] = tick2

        ##########################################
        cdl_types_needed = [CandleType.DAYS, CandleType.HOUR]
        num_of_candles = 100
        cdl_runtime_dfs = {}
        for cdl_type in cdl_types_needed:
            ccxt_market_dfs = UniversalQuoteConnector.instance().fetch_quote_num_candles(ExType.upbit, markets,
                                                                                         num_of_candles, cdl_type)
            cdl_runtime_dfs[cdl_type] = ccxt_market_dfs

        time_dt = now_dt()
        quote = Quote(time_dt)
        quote.add_quote(ExType.upbit, cdl_runtime_dfs, market_ticks)

        encoded_json = quote.marshal()
        print(encoded_json)
        quote = Quote.unmarshal(encoded_json)
        cdl_returned_dfs = quote.get_candle_types(ExType.upbit)
        print(f'##' * 30 + f' Unmarshal')
        for cdl_type in cdl_returned_dfs:
            market_dfs = cdl_returned_dfs[cdl_type]
            for market in market_dfs:
                print(f'################### {cdl_type} - {market}')
                print(market_dfs[market].head(3))

        market_ticks = quote.get_market_ticks(ExType.upbit)
        for market in market_ticks:
            print(f'{market} - {market_ticks[market].close}')

    # @unittest.skip("Tested")
    def test_marshal_quote(self):
        markets = ('KRW-BTC', 'KRW-ETH', 'KRW-XRP')
        ##########################################
        uqc = UniversalQuoteConnector.instance()

        now = now_dt()
        desired_dt = create_dt_at(now.year, now.month, now.day, now.hour, now.minute, 0)
        ccxt_market_dfs = UniversalQuoteConnector.instance().fetch_quote_at(ExType.upbit, markets, desired_dt)
        print(ccxt_market_dfs.tail(3))

        market_ticks = {}
        if ccxt_market_dfs is not None:
            for market in ccxt_market_dfs['market'].unique():
                market_df = ccxt_market_dfs[ccxt_market_dfs['market'] == market]
                data_list = [market_df.index[0].to_pydatetime().strftime(TIME_FORMAT)]
                data_list.extend(market_df.to_numpy()[0])
                tick2 = Tick.from_list(data_list)
                market_ticks[market] = tick2


        ##########################################
        cdl_types_needed = [CandleType.DAYS, CandleType.HOUR]
        num_of_candles = 100
        cdl_runtime_dfs = {}
        for cdl_type in cdl_types_needed:
            ccxt_market_dfs = UniversalQuoteConnector.instance().fetch_quote_num_candles(ExType.upbit, markets,
                                                                                     num_of_candles, cdl_type)
            cdl_runtime_dfs[cdl_type] = ccxt_market_dfs

        time_dt = now_dt()
        quote = Quote(time_dt)
        quote.add_quote(ExType.upbit, cdl_runtime_dfs, market_ticks)

        encoded_json = quote.marshal()
        print(encoded_json)
        quote = Quote.unmarshal(encoded_json)
        cdl_returned_dfs = quote.get_candle_types(ExType.upbit)
        print(f'##' * 30 + f' Unmarshal')
        for cdl_type in cdl_returned_dfs:
            market_dfs = cdl_returned_dfs[cdl_type]
            for market in market_dfs:
                print(f'################### {cdl_type} - {market}')
                print(market_dfs[market].head(3))

        market_ticks = quote.get_market_ticks(ExType.upbit)
        for market in market_ticks:
            print(f'{market} - {market_ticks[market].close}')
            
    @unittest.skip("Tested")
    def test_make_market_tick(self):
        markets = ['KRW-BTC', 'KRW-ETH', 'KRW-XRP']
        uqc = UpbitQuoteConnector()
        _, last_svr_time = uqc.fetch_quote(markets)
        print(f'last_svr_time : {last_svr_time}')
        svr_korea_dt = svr2local_dt(last_svr_time)
        desired_at = get_1min_before_dt(svr_korea_dt, True)

        ccxt_market_dfs = UniversalQuoteConnector.instance().fetch_quote_at(ExType.upbit, markets, desired_at)
        print(ccxt_market_dfs.tail(3))
        market_df = ccxt_market_dfs.loc[ccxt_market_dfs['market'] == 'KRW-BTC']
        print(market_df)
        data_list = [market_df.index[0].to_pydatetime().strftime(TIME_FORMAT)]
        data_list.extend(market_df.to_numpy()[0])
        tick2 = Tick.from_list(data_list)
        print(tick2)

    @unittest.skip("Tested")
    def test_fetch_quote_at(self):
        ##################################################
        ## UpbitQuoteConnector
        markets = ['KRW-BTC','KRW-ETH', 'KRW-XRP']
        uqc = UpbitQuoteConnector()
        _, last_svr_time = uqc.fetch_quote(markets)
        print(f'last_svr_time : {last_svr_time}')
        svr_korea_dt = svr2local_dt(last_svr_time)
        desired_at = get_1min_before_dt(svr_korea_dt, True)
        json_string, last_svr_time = uqc.fetch_quote_at(markets, desired_at)
        a_json = json.loads(json_string)
        print(last_svr_time)
        _1_quote_df = pd.DataFrame.from_records(a_json)
        print(_1_quote_df.tail(3))

        ##################################################
        ## UpbitQuoteConnector
        print(f'###' * 100)
        ccxt_market_dfs = UniversalQuoteConnector.instance().fetch_quote_at(ExType.upbit, markets, desired_at)
        print(ccxt_market_dfs.tail(3))


    @unittest.skip("Tested")
    def test_fetch_quote_num_candles(self):
        num_of_candles = 1000
        uqc = UpbitQuoteConnector()
        markets = ['KRW-BTC', 'KRW-ETH', 'KRW-XRP']
        market_dfs = uqc.fetch_quote_num_candles(markets, num_of_candles, CandleType.DAYS)
        print('##' * 100)
        for market in market_dfs:
            print(market_dfs[market].head(5))

        ############################################################################
        print('##' * 100)
        ccxt_market_dfs = UniversalQuoteConnector.instance().fetch_quote_num_candles(ExType.upbit, markets, num_of_candles, CandleType.DAYS)
        for market in ccxt_market_dfs:
            print(ccxt_market_dfs[market].head(5))

        for market in ccxt_market_dfs:
            market_df = market_dfs[market]
            ccxt_df = ccxt_market_dfs[market]

            ser_upbit_trade_price = market_df['trade_price'].values
            ser_ccxt_close = ccxt_df['close'].values
            if functools.reduce(lambda x, y: x and y, map(lambda p, q: p == q, ser_upbit_trade_price, ser_ccxt_close),
                                True):
                print(f'{market} - The lists l1 and l2 are the same')
            else:
                print(f'{market} - The lists l1 and l2 are not the same')

    @unittest.skip("Tested")
    def test_server_time(self):

        uqc = UpbitQuoteConnector()
        markets = ['KRW-BTC', 'KRW-ETH', 'KRW-XRP']
        _, last_svr_time = uqc.fetch_quote(markets)
        print(f'last_svr_time : {last_svr_time}')

        svr_time = UniversalQuoteConnector.instance().fetch_time(ExType.binance)
        print(f'binance : {svr_time}')
        kor_dt = from_utc_int_timestamp(svr_time)
        print(f'binance : {kor_dt}')

        svr_time = UniversalQuoteConnector.instance().fetch_time(ExType.binanceusdm)
        print(f'binanceusdm : {svr_time}')
        kor_dt = from_utc_int_timestamp(svr_time)
        print(f'binanceusdm : {kor_dt}')

        svr_time = UniversalQuoteConnector.instance().fetch_time(ExType.upbit)
        print(f'upbit : {svr_time}')
        kor_dt = from_utc_int_timestamp(svr_time, True)
        print(f'upbit : {kor_dt}')


    @unittest.skip("Tested")
    def test_timestamp(self):
        to_now_dt = datetime.datetime.now()
        print(to_now_dt)
        utc_int_tp = to_utc_int_timestamp(to_now_dt)
        print(utc_int_tp)

        kor_dt = from_utc_int_timestamp(utc_int_tp)
        print(kor_dt)

        ################################################
        print('########################')
        kor_dt = create_dt_at(2023, 1, 1, 15, 0, 0)
        print(kor_dt)
        utc_int_tp = to_utc_int_timestamp(kor_dt)
        print(utc_int_tp)

        kor_dt = from_utc_int_timestamp(utc_int_tp)
        print(f'kor time: {kor_dt}')
        ust_dt = from_utc_int_timestamp(utc_int_tp, False)
        print(f'ust time: {ust_dt}')

        uqc = UpbitQuoteConnector()
        markets = ['KRW-BTC', 'KRW-ETH', 'KRW-XRP']
        _, last_svr_time = uqc.fetch_quote(markets)
        print(f'{last_svr_time=}')

        svr_time = UniversalQuoteConnector.instance().fetch_time(ExType.upbit)
        print(f'{svr_time=}')


        # ccxt_ex = Exchange(None)
        # Exchange.parse8601()

    def test_fetch_tick_quote_bithumb2(self) :
        pass

    def test_fetch_tick_quote_bithumb(self):
        market = 'KRW-BTC'
        to_now_dt = datetime.datetime.now()

        #####################################
        ### Bithumb
        uqc = UniversalQuoteConnector.instance()
        ccxt_df = uqc.fetch_tick_quote(ExType.bithumb, market, 180, to_now_dt, CandleType.DAYS)
        print(f"{to_now_dt=}")
        print(f"{len(ccxt_df)}")
        print(ccxt_df.tail(5))

        next_dt = str2dt(ccxt_df.tail(1).index[0].strftime('%Y-%m-%dT%H:%M:%S'))
        print(f"{next_dt=}")
        ccxt_df = uqc.fetch_tick_quote(ExType.bithumb, market, 180, next_dt, CandleType.DAYS)
        print(f"{len(ccxt_df)}")
        print(ccxt_df.tail(5))

        #####################################
        ### Upbit
        uqc = UniversalQuoteConnector.instance()
        ccxt_df = uqc.fetch_tick_quote(ExType.upbit, market, 180, to_now_dt, CandleType.DAYS)
        print(f"{to_now_dt=}")
        print(f"{len(ccxt_df)}")
        print(ccxt_df.tail(5))

        next_dt = str2dt(ccxt_df.tail(1).index[0].strftime('%Y-%m-%dT%H:%M:%S'))
        print(f"{next_dt=}")
        ccxt_df = uqc.fetch_tick_quote(ExType.upbit, market, 180, next_dt, CandleType.DAYS)
        print(f"{len(ccxt_df)}")
        print(ccxt_df.tail(5))

        #####################################
        ### Binance
        market = "BTC/USDT"
        ccxt_df = uqc.fetch_tick_quote(ExType.binance, market, 180, to_now_dt, CandleType.DAYS)
        print(f"{to_now_dt=}")
        print(f"{len(ccxt_df)}")
        print(ccxt_df.tail(5))

        next_dt = str2dt(ccxt_df.tail(1).index[0].strftime('%Y-%m-%dT%H:%M:%S'))
        print(f"{next_dt=}")
        ccxt_df = uqc.fetch_tick_quote(ExType.binance, market, 180, next_dt, CandleType.DAYS)
        print(f"{len(ccxt_df)}")
        print(ccxt_df.tail(5))


    @unittest.skip("Tested")
    def test_fetch_tick_quote(self):
        #####################################
        ### Upbit
        uqc = UpbitQuoteConnector()
        market = 'KRW-BTC'
        to_now_dt = datetime.datetime.now()
        _, _, market_df = uqc.fetch_tick_quote(market, 180, to_now_dt, CandleType.DAYS)
        print(market_df.head(5))

        #####################################
        ### UniversalQuoteConnector
        # since_dt = (pd.to_datetime(to_now_dt) - pd.Timedelta(days=180)).to_pydatetime()
        uqc = UniversalQuoteConnector.instance()
        ccxt_df = uqc.fetch_tick_quote(ExType.upbit, market, 180, to_now_dt, CandleType.DAYS)
        print(ccxt_df.head(5))

        ser_upbit_opening_price = market_df['opening_price'].values
        ser_ccxt_open = ccxt_df['open'].values
        if functools.reduce(lambda x, y: x and y, map(lambda p, q: p == q, ser_upbit_opening_price, ser_ccxt_open), True):
            print("The lists l1 and l2 are the same")
        else:
            print("The lists l1 and l2 are not the same")

    @unittest.skip("Tested")
    def test_fetch_tick_quote2(self):
        #####################################
        ### Upbit
        uqc = UpbitQuoteConnector()
        market = 'KRW-BTC'
        to_now_dt = datetime.datetime.now()
        _, _, market_df = uqc.fetch_tick_quote(market, 180, to_now_dt, CandleType.MINUTES_1)
        print(market_df.head(5))

        #####################################
        ### UniversalQuoteConnector
        # since_dt = (pd.to_datetime(to_now_dt) - pd.Timedelta(days=180)).to_pydatetime()
        uqc = UniversalQuoteConnector.instance()
        ccxt_df = uqc.fetch_tick_quote(ExType.upbit, market, 180, to_now_dt, CandleType.MINUTES_1)
        print(ccxt_df.head(5))

        ser_upbit_trade_price = market_df['trade_price'].values
        ser_ccxt_close = ccxt_df['close'].values
        if functools.reduce(lambda x, y: x and y, map(lambda p, q: p == q, ser_upbit_trade_price, ser_ccxt_close), True):
            print("The lists l1 and l2 are the same")
        else:
            print("The lists l1 and l2 are not the same")

    @unittest.skip("Tested")
    def test_fetch_tick_quote3(self):
        #####################################
        ### Upbit
        uqc = UpbitQuoteConnector()
        market = 'KRW-BTC'
        to_now_dt = datetime.datetime.now()
        _, _, market_df = uqc.fetch_tick_quote(market, 180, to_now_dt, CandleType.HOUR)
        print(market_df.head(5))

        #####################################
        ### UniversalQuoteConnector
        # since_dt = (pd.to_datetime(to_now_dt) - pd.Timedelta(days=180)).to_pydatetime()
        uqc = UniversalQuoteConnector.instance()
        ccxt_df = uqc.fetch_tick_quote(ExType.upbit, market, 180, to_now_dt, CandleType.HOUR)
        print(ccxt_df.head(5))

        ser_upbit_trade_price = market_df['trade_price'].values
        ser_ccxt_close = ccxt_df['close'].values
        if functools.reduce(lambda x, y: x and y, map(lambda p, q: p == q, ser_upbit_trade_price, ser_ccxt_close), True):
            print("The lists l1 and l2 are the same")
        else:
            print("The lists l1 and l2 are not the same")

    @unittest.skip("Tested")
    def test_fetch_ohldv_from_multiple_exchange(self):
        uqc = UpbitQuoteConnector()
        markets = ['KRW-BTC', 'KRW-ETH', 'KRW-XRP']
        market_dfs = uqc.fetch_quote_num_candles(markets, 600, CandleType.DAYS)
        for market in market_dfs:
            print(f'{market}==========================')
            print(market_dfs[market].tail(3))

    @unittest.skip("Tested")
    def test_fetch_market_data(self):
        qc = UpbitQuoteConnector()
        krw_btc = 'KRW-XRP'
        markets = [krw_btc]

        days = (now_dt() - str2dt('2022-08-01T00:00:00')).days
        market_dfs = qc.fetch_quote_num_candles(markets, 12 * 24 * days, CandleType.MINUTES_5)
        market_dfs[krw_btc].to_csv(krw_btc + "_" + CandleType.MINUTES_5.name + ".csv")

        market_dfs = qc.fetch_quote_num_candles(markets, 4 * 24 * days, CandleType.MINUTES_15)
        market_dfs[krw_btc].to_csv(krw_btc + "_" + CandleType.MINUTES_15.name + ".csv")

        market_dfs = qc.fetch_quote_num_candles(markets, 2 * 24 * days, CandleType.MINUTES_30)
        market_dfs[krw_btc].to_csv(krw_btc + "_" + CandleType.MINUTES_30.name + ".csv")

        market_dfs = qc.fetch_quote_num_candles(markets, 24 * days, CandleType.HOUR)
        market_dfs[krw_btc].to_csv(krw_btc + "_" + CandleType.HOUR.name + ".csv")

        market_dfs = qc.fetch_quote_num_candles(markets, 6 * days, CandleType.HOUR4)
        market_dfs[krw_btc].to_csv(krw_btc + "_" + CandleType.HOUR4.name + ".csv")

        market_dfs = qc.fetch_quote_num_candles(markets, days, CandleType.DAYS)
        market_dfs[krw_btc].to_csv(krw_btc + "_" + CandleType.DAYS.name + ".csv")


    @unittest.skip("Tested")
    def test_get_current_price(self):
        qc = UpbitQuoteConnector()
        markets = ['KRW-BTC', 'KRW-ETH', 'KRW-XRP']
        json_string, last_svr_time = qc.fetch_quote(markets)
        print(json_string)
        a_json = json.loads(json_string)
        _1m_quote_dfs = pd.DataFrame.from_records(a_json)

        print(_1m_quote_dfs.head(5))

        for market in markets:
            trade_price = _1m_quote_dfs[_1m_quote_dfs.market == market].iloc[-1]['trade_price']
            print(f'{market}-{trade_price}')



    @unittest.skip("Tested")
    def test_get_settled_orders_using_exchange_connector2(self):
        # am = AccountMgmt('stkim')
        # access_key = am.get_account().access_key
        # secret_key = am.get_account().secrete_key
        # print(f's_key : {secret_key} , a_key : {access_key}')
        #
        # upbit_ex = UpbitExchangeGateway()
        # upbit_ex.set_params(access_key, secret_key)
        # btc_sett_orders, df = upbit_ex.get_settled_orders('KRW-BTC')
        # df.to_csv('krw-btc_settle_stkim.csv')

        df = pd.read_csv('krw-btc_settle_stkim.csv')
        print(df.head(20))
        print(f'before removing limits: {len(df)}')

        df.drop(df[df['ord_type'] == 'limit'].index, inplace=True)
        print(f'after removing limits: {len(df)}')

        target_time_str = '07:59'
        svr_time_str    = '08:00' # plus one minute
        query_str1      = f'T{svr_time_str}:'
        svr_time_str2   = '08:01'  # plus one minute
        query_str2      = f'T{svr_time_str2}:'
        df = df[ (df['created_at'].str.contains(query_str1)) | (df['created_at'].str.contains(query_str2))]
        print(f'extracting the target hour data: {len(df)}')
        print(df.head(20))
        print('target data')
        print(df.head(1))

    # @unittest.skip("Tested")
    # def test_get_settled_orders_using_exchange_connector_with_multiple_states(self):
    #     access_key = stkim_upbit_access_key
    #     secret_key = stkim_upbit_secret_key
    #
    #     print(f's_key : {secret_key} , a_key : {access_key}')
    #
    #     upbit_ex = UpbitExchangeGateway()
    #     upbit_ex.set_params(access_key, secret_key)
    #
    #     markets = ['KRW-BTC', 'KRW-ETH', 'KRW-XRP']
    #     df = upbit_ex.get_settled_orders_as_df(markets)
    #     print(f'btc_sett_orders : {df}')
    #     print(df.columns)
    #     df.to_csv('settle_list.csv')
    #     df.set_index(['uuid'], drop=False, inplace=True)
    #     print(df.head(20))

    @unittest.skip("Tested")
    def test_get_settled_orders_using_pyupbit(self):
        access_key = stkim_upbit_access_key
        secret_key = stkim_upbit_secret_key

        server_url = 'https://api.upbit.com'
        print(f's_key : {secret_key} , a_key : {access_key}')

        upbit = pyupbit.Upbit(access_key, secret_key)
        results = upbit.get_order('KRW-BTC', state='done')
        done_df = pd.DataFrame.from_records(results)
        # done_df.set_index(['uuid'], drop=False, inplace=True)
        # done_df.to_csv('done_settle.csv')

        results = upbit.get_order('KRW-BTC', state='cancel')
        cancel_df = pd.DataFrame.from_records(results)
        # cancel_df.set_index(['uuid'], drop=False, inplace=True)
        # wait_df.to_csv('cancel_settle.csv')
        dataframe = pd.concat([done_df, cancel_df], ignore_index=True)
        dataframe.set_index(['created_at'], drop=False, inplace=True)
        sort_df(dataframe, 'created_at', ascending=False)
        dataframe.to_csv('done_cancel_settle.csv')

    @unittest.skip("Tested")
    def test_get_settled_orders_using_requests(self):
        access_key = stkim_upbit_access_key
        secret_key = stkim_upbit_secret_key

        server_url = 'https://api.upbit.com'
        print(f's_key : {secret_key} , a_key : {access_key}')

        market = 'KRW_BTC'
        # bulltrader_states = ['done','cancel']  ## cancel만 나옴
        # bulltrader_states = ['cancel','done'] ## 'done'만 나옴  ==> 마지막 것만 나오고 있음.
        # wait, cancel을
        # bulltrader_states = ['wait', 'cancel']  ## cancel만 나옴
        # bulltrader_states = ['wait', 'done']  ## done만 나옴 ==>
        # bulltrader_states = ['wait', 'watch']   ## 이 두 데이터는 현재 존재 하지 않아서 테스트 힘듬
        states = ['done','cancel']

        query = {
            # 'market': market,
            'bulltrader_states': states,
            'order_by': 'desc'
        }

        query_string = urlencode(query)

        # uuids = [
        #     '9ca023a5-851b-4fec-9f0a-48cd83c2eaae',
        # ]
        # uuids_query_string = '&'.join(["uuids[]={}".format(uuid) for uuid in uuids])
        #
        # query['uuids[]'] = uuids
        # query_string = "{0}&{1}".format(query_string, uuids_query_string).encode()

        m = hashlib.sha512()
        m.update(urlencode(query, doseq=True).replace("%5B%5D=", "[]=").encode())
        query_hash = m.hexdigest()

        # hash_object = hashlib.sha512(str(query_string).encode())
        # m = hashlib.sha512()
        # m.update(query_string)
        # query_hash = hash_object.hexdigest()
        import uuid
        payload = {
            'access_key': access_key,
            'nonce': str(uuid.uuid4()),
            'query_hash': query_hash,
            'query_hash_alg': 'SHA512',
        }

        jwt_token = jwt.encode(payload, secret_key)
        authorize_token = 'Bearer {}'.format(jwt_token)
        print(f'authorize_token:{authorize_token}')
        headers = {"Authorization": authorize_token}

        res = requests.get(server_url + "/v1/orders", params=query, headers=headers)

        print(res.json())

    def test_fetch_all_markets_upbit(self):
        uqc = UniversalQuoteConnector()
        universal_mkt_id = uqc.get_available_markets(ExType.upbit)
        print(universal_mkt_id)
        print(len(universal_mkt_id))

    def test_fetch_all_markets_bithumb(self):
        uqc = UniversalQuoteConnector()
        universal_mkt_id = uqc.get_available_markets(ExType.bithumb)
        print(universal_mkt_id)
        print(len(universal_mkt_id))

    def test_fetch_all_markets_binance(self):
        uqc = UniversalQuoteConnector()
        universal_mkt_id = uqc.get_available_markets(ExType.binance)
        print(universal_mkt_id)
        print(len(universal_mkt_id))


    def test_store_load_quote(self):
        uqc = UniversalQuoteConnector()
        markets = uqc.get_available_markets(ExType.upbit)
        # markets = ('KRW-BTC', 'KRW-ETH', 'KRW-XRP')
        ##########################################
        uqc = UniversalQuoteConnector.instance()

        now = now_dt()
        desired_dt = create_dt_at(now.year, now.month, now.day, now.hour, now.minute, 0)
        ccxt_market_dfs = UniversalQuoteConnector.instance().fetch_quote_at(ExType.upbit, markets, desired_dt)
        print(ccxt_market_dfs.tail(3))

        market_ticks = {}
        if ccxt_market_dfs is not None :
            for market in ccxt_market_dfs['market'].unique() :
                market_df = ccxt_market_dfs[ccxt_market_dfs['market'] == market]
                data_list = [market_df.index[0].to_pydatetime().strftime(TIME_FORMAT)]
                data_list.extend(market_df.to_numpy()[0])
                tick2 = Tick.from_list(data_list)
                market_ticks[market] = tick2

        ##########################################
        cdl_types_needed = [CandleType.DAYS, CandleType.HOUR]
        num_of_candles = 100
        cdl_runtime_dfs = {}
        for cdl_type in cdl_types_needed :
            ccxt_market_dfs = UniversalQuoteConnector.instance().fetch_quote_num_candles(ExType.upbit, markets,
                                                                                         num_of_candles, cdl_type)
            cdl_runtime_dfs[cdl_type] = ccxt_market_dfs

        time_dt = now_dt()
        quote = Quote(time_dt)
        quote.add_quote(ExType.upbit, cdl_runtime_dfs, market_ticks)

        encoded_json = quote.marshal()
        print(encoded_json)

        ## Store Redis
        self.rds = redis.StrictRedis(host = 'localhost', port = 6379, db = 0)
        self.rds.set("quote", encoded_json)  # todo 추후 월별로 변경되도록 구성

        ## Load Redis
        loaded_json = self.rds.get("quote")

        quote = Quote.unmarshal(loaded_json)
        cdl_returned_dfs = quote.get_candle_types(ExType.upbit)
        print(f'##' * 30 + f' Unmarshal')
        for cdl_type in cdl_returned_dfs :
            market_dfs = cdl_returned_dfs[cdl_type]
            for market in market_dfs :
                print(f'################### {cdl_type} - {market}')
                print(market_dfs[market].head(3))

        market_ticks = quote.get_market_ticks(ExType.upbit)
        for market in market_ticks :
            print(f'{market} - {market_ticks[market].close}')

    def test_fetch_1m_of_all_markets(self):
        uqc = UniversalQuoteConnector()
        markets = uqc.get_available_markets(ExType.upbit)
        print(markets)
        print(len(markets))

        __time_all_process = start_timing()
        ccxt_market_dfs = UniversalQuoteConnector.instance().fetch_quote_num_candles(ExType.upbit, markets,
                                                                                     200, CandleType.MINUTES_1)
        print(f"all markets: {ccxt_market_dfs.keys()}")
        print(end_n_elapsed_time(__time_all_process, 'fetching all quotes'))

if __name__ == '__main__':
    unittest.main()
