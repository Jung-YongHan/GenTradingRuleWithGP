import copy
import datetime
import gc
import json
import os
import time
import unittest
from os.path import dirname, join

import pandas as pd

from bt4.Constants import CandleType, ExType
from bt4.quote.LocalQuoteDispatcher import LocalQuoteDispatcher
from bt4.quote.QuoteListener import QuoteListener
from bt4.quote.QuoteMgr import QuoteStorageMgr
from bt4.quote.QuoteSupport import Quote, Tick
from bt4.utils.memory_profiler import MemoryProfiler
from bt4.utils.mylog import init_log
import bt4.utils.mylog as log_module
from bt4.utils.python_utils import now_dt, str2dt, load_class_from_module, create_dt_at, TIME_FORMAT
from bt4.utils.stopwatch import StopWatch
from bt4_cfg.quote_conf import QUOTE_PARAMS

import redis
import bt4.GlobalProperties as global_prop

import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

pd.set_option('display.max_columns', None)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('max_colwidth', None)

log_module.log_mode = 'quote'
log = init_log()

pd.set_option('display.max_columns', None)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('max_colwidth', None)

class TestQuoteReceiver(QuoteListener):
    def __init__(self, ex_type):
        self.ex_type = ex_type

    def get_target_markets(self):
        pass

    def quote_tai_received(self, time_dt, market_ticks, market_tais):
        pass

    def quote_received(self, quote):
        market_ticks = quote.get_market_ticks(self.ex_type)
        print(f'## Exchange: {self.ex_type}')
        print(f'##' * 20)
        for market in market_ticks:
            market_tick = market_ticks[market]
            print(f'{quote.time_dt}-{self.ex_type.name} - {market} : {market_tick.close}')
        cdl_types = quote.get_candle_types(self.ex_type)

        cdl_type_str = ''
        for cdl_type in cdl_types:
            cdl_type_str = cdl_type_str + ',' +cdl_type.name
        print(f'## Exchange: {self.ex_type} - cdltype:{cdl_type_str}')



class MyTestCase(unittest.TestCase):

    def test_local_quote_dispatcher_for_multi_quote_provider22(self):
        # exchanges = QUOTE_PARAMS['exchanges']
        exchanges = [ExType.upbit, ExType.binance]
        start_pdt = datetime.datetime(2018, 10, 1, 8, 59, 0)
        end_pdt = datetime.datetime(2023, 1, 1, 8, 59, 0)
        cld_type_needed = [CandleType.DAYS, CandleType.DAYS_TF, CandleType.HOUR]
        # cld_type_needed = [CandleType.HOUR]
        bt_times = ['8:59']
        local_quote_dispatcher = LocalQuoteDispatcher(start_pdt, end_pdt, exchanges, cld_type_needed)
        for ex_type in exchanges:
            local_quote_dispatcher.addQuoteListener(TestQuoteReceiver(ex_type))
        local_quote_dispatcher.process_quote(bt_times, CandleType.HOUR)

    def create_binance_1m_from_1h(self, _1h_file_path, _1m_file_path):
        btc_usdt_hour_df = pd.read_csv(_1h_file_path, index_col='datetime', parse_dates=True)
        print('1H-가장 오래된 날짜:', btc_usdt_hour_df.index.min())
        print('1H-가장 최근 날짜:', btc_usdt_hour_df.index.max())

        btc_usdt_1min_df = pd.read_csv(_1m_file_path, index_col='datetime', parse_dates=True)
        print('1 MIN-가장 오래된 날짜:', btc_usdt_1min_df.index.min())
        print('1 MIN-가장 최근 날짜:', btc_usdt_1min_df.index.max())

        _1h_of_missed_min = btc_usdt_hour_df[btc_usdt_hour_df.index.min(): btc_usdt_1min_df.index.min()]
        missed_minutes = pd.date_range(btc_usdt_hour_df.index.min(), btc_usdt_1min_df.index.min(), freq='min')
        date_df = pd.DataFrame(index=missed_minutes)
        tgt_df = pd.concat([date_df, _1h_of_missed_min], axis=1)
        tgt_df = tgt_df.fillna(method='ffill')
        print(tgt_df.head(20))

        result_df = pd.concat([tgt_df, btc_usdt_1min_df], axis=0)
        result_df = result_df.loc[~result_df.index.duplicated(keep='first')]
        result_df = result_df.sort_index(ascending=True)
        result_df.index.name = 'datetime'
        return result_df

    def test_create_binance_1m_from_1h(self):

        root_dir = dirname(dirname(__file__))  ## parent of parent of directory of simulator.py
        btc_usdt_hour_file_name = join(root_dir, f'data{os.sep}binance{os.sep}BTC_USDT_HOUR.csv')
        btc_usdt_1min_file_name = join(root_dir, f'data{os.sep}binance{os.sep}BTC_USDT_MINUTES_1.csv')
        result_df = self.create_binance_1m_from_1h(btc_usdt_hour_file_name, btc_usdt_1min_file_name)
        result_df.to_csv(btc_usdt_1min_file_name + '_gen')

        eth_usdt_hour_file_name = join(root_dir, f'data{os.sep}binance{os.sep}ETH_USDT_HOUR.csv')
        eth_usdt_1min_file_name = join(root_dir, f'data{os.sep}binance{os.sep}ETH_USDT_MINUTES_1.csv')
        result_df = self.create_binance_1m_from_1h(eth_usdt_hour_file_name, eth_usdt_1min_file_name)
        result_df.to_csv(eth_usdt_1min_file_name + '_gen')

        xrp_usdt_hour_file_name = join(root_dir, f'data{os.sep}binance{os.sep}XRP_USDT_HOUR.csv')
        xrp_usdt_1min_file_name = join(root_dir, f'data{os.sep}binance{os.sep}XRP_USDT_MINUTES_1.csv')
        result_df = self.create_binance_1m_from_1h(xrp_usdt_hour_file_name, xrp_usdt_1min_file_name)
        result_df.to_csv(xrp_usdt_1min_file_name + '_gen')


    def test_binance_local_quote_dispatcher(self):
        ex_type = ExType.binance
        start_pdt = datetime.datetime(2018, 10, 1, 8, 59, 0)
        end_pdt = datetime.datetime(2023, 1, 1, 8, 59, 0)
        cld_type_needed = [CandleType.DAYS, CandleType.DAYS_TF, CandleType.HOUR]
        # cld_type_needed = [CandleType.HOUR]
        bt_times = []
        quote_providers = QUOTE_PARAMS['exchanges']
        local_quote_dispatcher = LocalQuoteDispatcher(start_pdt, end_pdt, quote_providers, cld_type_needed)
        local_quote_dispatcher.addQuoteListener(TestQuoteReceiver(ex_type))
        local_quote_dispatcher.process_quote(bt_times, CandleType.MINUTES_1)

    def test_1m_quote_dispatch(self):

        markets = ['KRW-BTC', 'KRW-ETH', 'KRW-XRP']
        start_pdt = pd.to_datetime('2023-01-01 00:00:00')
        end_pdt = pd.to_datetime('2023-01-30 00:00:00')
        cdl_types_needed = [CandleType.DAYS, CandleType.HOUR]
        ex_type = ExType.upbit
        quote_storage = QuoteStorageMgr(markets, cdl_types_needed, ex_type)

        _1m_simul_dfs = quote_storage.load_quote_in_range2(markets, start_pdt, end_pdt, CandleType.MINUTES_1)
        time_pdts = None
        for market in _1m_simul_dfs:
            time_pdts = _1m_simul_dfs[market].index
            break

        market_ticks = {}
        for time_pdt in time_pdts:
            _1m_dfs = pd.DataFrame()
            for market in _1m_simul_dfs:
                _1m_market_df = _1m_simul_dfs[market]
                _1m_market_sel_df = _1m_market_df.loc[_1m_market_df.index == time_pdt]
                _1m_dfs = pd.concat([_1m_dfs, _1m_market_sel_df], axis=0)
                # data_list = [idx.to_pydatetime().strftime(TIME_FORMAT)]
                if _1m_market_sel_df is not None and not _1m_market_sel_df.empty:
                    data_list = [time_pdt]
                    data_list.extend(_1m_market_sel_df.to_numpy()[0])
                    tick2 = Tick.from_list(data_list)
                    print(tick2)
                    market_ticks[market] = tick2

            print(f'###' * 40)
            print(_1m_dfs.head(3))



    def test_quote_storage_mgr(self):

        markets = ['KRW-BTC', 'KRW-ETH', 'KRW-XRP']
        start_pdt = pd.to_datetime('2023-01-01 00:00:00')
        end_pdt = pd.to_datetime('2023-01-30 00:00:00')
        cdl_types_needed = [CandleType.DAYS, CandleType.HOUR]
        ex_type = ExType.upbit

        quote_storage = QuoteStorageMgr(markets, cdl_types_needed, ex_type)

        cdl_runtime_dfs = {}
        for cdl_type in cdl_types_needed:
            cdl_runtime_dfs[cdl_type] = copy.deepcopy(
                quote_storage.load_quote_in_range(markets, start_pdt, 200, cdl_type))

        for cdl_type in cdl_runtime_dfs:
            print(f'{cdl_type.name}==================================================')
            cdl_dfs = cdl_runtime_dfs[cdl_type]
            for market in cdl_dfs:
                print(cdl_dfs[market].head(5))

        ############################################################################
        quote_storage.load_quote_in_range2(markets, start_pdt, end_pdt, CandleType.MINUTES_1)


    def test_marshal_quote(self):
        markets = ('KRW-BTC', 'KRW-ETH', 'KRW-XRP')
        ##########################################
        conn_module_name = 'bt4.quote' + '.QuoteConnector'
        conn_class_name = "UniversalQuoteConnector"
        self.q_connector = load_class_from_module(conn_module_name, conn_class_name)
        now = now_dt()
        desired_dt = create_dt_at(now.year, now.month, now.day, now.hour, now.minute, 0)
        market_dfs = self.q_connector.fetch_quote_at(ExType.upbit, markets, desired_dt)

        market_ticks = {}
        if market_dfs is not None:
            for market in market_dfs['market'].unique():
                market_df = market_dfs.loc[market_dfs['market'] == market]
                df_list = []
                df_list.append(market_df.index[0].strftime('%Y-%m-%dT%H_%M_%S'))
                df_list.extend(market_df.to_numpy()[0])
                tick2 = Tick.from_list(df_list)
                market_ticks[market] = tick2

        ##########################################
        cdl_types_needed = [CandleType.DAYS, CandleType.HOUR]
        start_dt = str2dt('2018-10-01T00:00:00')
        end_dt = str2dt('2018-12-01T00:00:00')
        simul_storage = QuoteStorageMgr(markets, cdl_types_needed)

        cdl_runtime_dfs = {}
        for cdl_type in cdl_types_needed:
            q_df = simul_storage.load_quote_in_range(ExType.upbit, markets, start_dt, 200, cdl_type)
            cdl_runtime_dfs[cdl_type] = copy.deepcopy(q_df)

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


    def test_fetch_bithumb(self):
        # markets = 'KRW-BTC KRW-ETH KRW-XRP KRW-SOL KRW-DOGE KRW-ADA KRW-SHIB KRW-AVAX KRW-TRX KRW-DOT KRW-BCH KRW-LINK KRW-NEAR KRW-MATIC KRW-ETC KRW-HBAR KRW-APT KRW-ATOM KRW-MNT KRW-CRO'.split()  # 정보를 읽어와 진행 필요
        markets = ["BTC/KRW", "ETH/KRW", "XRP/KRW"]
        # markets = ('KRW-BTC', 'KRW-ETH', 'KRW-XRP')
        ##########################################
        conn_module_name = 'bt4.quote' + '.QuoteConnector'
        conn_class_name = "UniversalQuoteConnector"
        self.q_connector = load_class_from_module(conn_module_name, conn_class_name)
        now = now_dt()
        desired_dt = create_dt_at(now.year, now.month, now.day, now.hour, now.minute, 0)
        market_dfs = self.q_connector.fetch_quote_at(ExType.bithumb, markets, desired_dt)
        print(f"{market_dfs=}")


    def test_to_from_redis_quote(self):
        markets = 'KRW-BTC KRW-ETH KRW-XRP KRW-SOL KRW-DOGE KRW-ADA KRW-SHIB KRW-AVAX KRW-TRX KRW-DOT KRW-BCH KRW-LINK KRW-NEAR KRW-MATIC KRW-ETC KRW-HBAR KRW-APT KRW-ATOM KRW-MNT KRW-CRO'.split() #정보를 읽어와 진행 필요
        # markets = ('KRW-BTC', 'KRW-ETH', 'KRW-XRP')
        ##########################################
        conn_module_name = 'bt4.quote' + '.QuoteConnector'
        conn_class_name = "UniversalQuoteConnector"
        self.q_connector = load_class_from_module(conn_module_name, conn_class_name)
        now = now_dt()
        desired_dt = create_dt_at(now.year, now.month, now.day, now.hour, now.minute, 0)
        market_dfs = self.q_connector.fetch_quote_at(ExType.upbit, markets, desired_dt)

        market_ticks = {}
        if market_dfs is not None:
            for market in market_dfs['market'].unique():
                market_df = market_dfs.loc[market_dfs['market'] == market]
                df_list = []
                df_list.append(market_df.index[0].strftime('%Y-%m-%dT%H_%M_%S'))
                df_list.extend(market_df.to_numpy()[0])
                tick2 = Tick.from_list(df_list)
                market_ticks[market] = tick2

        ##########################################
        cdl_types_needed = [CandleType.DAYS, CandleType.HOUR4, CandleType.HOUR, CandleType.MINUTES_30, CandleType.MINUTES_15, CandleType.MINUTES_5, CandleType.MINUTES_3, CandleType.MINUTES_1]
        start_dt = str2dt('2018-10-01T00:00:00')
        end_dt = str2dt('2019-12-01T00:00:00')
        simul_storage = QuoteStorageMgr(markets, cdl_types_needed)

        cdl_runtime_dfs = {}
        for cdl_type in cdl_types_needed:
            q_df = simul_storage.load_quote_in_range(ExType.upbit, markets, start_dt, 200, cdl_type)
            cdl_runtime_dfs[cdl_type] = copy.deepcopy(q_df)

        time_dt = now_dt()
        quote = Quote(time_dt)
        quote.add_quote(ExType.upbit, cdl_runtime_dfs, market_ticks)

        ##########################################
        ## marshal & unmarshal
        # encoded_json = quote.marshal()
        # print(encoded_json)
        # quote = Quote.unmarshal(encoded_json)

        ####################################################################################
        ## to_redis, from_redis
        _redis = redis.StrictRedis(host = global_prop.QUOTE_REDIS_IP_ADDR, port = global_prop.REDIS_PORT, db = 0)
        self.mem_profiler = MemoryProfiler()

        self.mem_profiler.take_1st_snapshot()
        sw = StopWatch()
        sw.start()
        count = 1
        for idx in range(0, count):
            print(f"### {idx}")
            is_stored_well = quote.to_redis()

        elapsed_time = sw.stop()
        print(f"{elapsed_time=}, avg elapsed time=> {elapsed_time/count}")

        if is_stored_well:
            print("Storing quote to redis has been successfully executed!")
        else:
            print("Something is wrong in storing quote to redis.")

        self.mem_profiler.take_2nd_snapshot_and_show_topN(40)
        self.mem_profiler.print_mem_usage()

        self.mem_profiler.take_1st_snapshot()
        sw = StopWatch()
        sw.start()

        count = 10
        for idx in range(0, count):
            includes = {}
            includes[ExType.upbit] = markets

            received_quote = Quote.from_redis(time_dt, _redis, includes)

            self.mem_profiler.take_2nd_snapshot_and_show_topN(40)
            self.mem_profiler.print_mem_usage()

            print(f"count : {idx}")
            gc.collect()

            # time.sleep(1)

        ####################################################################################
        cdl_returned_dfs = received_quote.get_candle_types(ExType.upbit)
        print(f'##' * 30 + f' Unmarshal')
        for cdl_type in cdl_returned_dfs:
            market_dfs = cdl_returned_dfs[cdl_type]
            for market in market_dfs:
                print(f"################### {cdl_type} - {market}, len : {len(market_dfs[market])}")

        market_ticks = received_quote.get_market_ticks(ExType.upbit)
        for market in market_ticks:
            print(f'{market} - {market_ticks[market].close}')

    def test_to_from_redis_quote_multi_exchange(self) :
        upbit_markets = 'KRW-BTC KRW-ETH KRW-XRP'.split()  # 정보를 읽어와 진행 필요
        bithumb_mkts = ["BTC/KRW", "ETH/KRW", "XRP/KRW"]
        # markets = ('KRW-BTC', 'KRW-ETH', 'KRW-XRP')
        ##########################################
        conn_module_name = 'bt4.quote' + '.QuoteConnector'
        conn_class_name = "UniversalQuoteConnector"
        self.q_connector = load_class_from_module(conn_module_name, conn_class_name)
        now = now_dt()
        desired_dt = create_dt_at(now.year, now.month, now.day, now.hour, now.minute, 0)
        upbit_market_dfs = self.q_connector.fetch_quote_at(ExType.upbit, upbit_markets, desired_dt)
        bithumb_market_dfs = self.q_connector.fetch_quote_at(ExType.bithumb, bithumb_mkts, desired_dt)

        upbit_market_ticks = {}
        if upbit_market_dfs is not None :
            for market in upbit_market_dfs['market'].unique() :
                market_df = upbit_market_dfs.loc[upbit_market_dfs['market'] == market]
                df_list = []
                df_list.append(market_df.index[0].strftime('%Y-%m-%dT%H_%M_%S'))
                df_list.extend(market_df.to_numpy()[0])
                tick2 = Tick.from_list(df_list)
                upbit_market_ticks[market] = tick2

        bithumb_market_ticks = {}
        if bithumb_market_dfs is not None :
            for market in bithumb_market_dfs['market'].unique() :
                market_df = bithumb_market_dfs.loc[bithumb_market_dfs['market'] == market]
                df_list = []
                df_list.append(market_df.index[0].strftime('%Y-%m-%dT%H_%M_%S'))
                df_list.extend(market_df.to_numpy()[0])
                tick2 = Tick.from_list(df_list)
                bithumb_market_ticks[market] = tick2

        ##########################################
        cdl_types_needed = [CandleType.DAYS, CandleType.HOUR4, CandleType.HOUR, CandleType.MINUTES_30,
                            CandleType.MINUTES_15, CandleType.MINUTES_5, CandleType.MINUTES_3, CandleType.MINUTES_1]
        start_dt = str2dt('2018-10-01T00:00:00')
        end_dt = str2dt('2019-12-01T00:00:00')
        simul_storage = QuoteStorageMgr(upbit_markets, cdl_types_needed)

        cdl_runtime_dfs = {}
        for cdl_type in cdl_types_needed :
            q_df = simul_storage.load_quote_in_range(ExType.upbit, upbit_markets, start_dt, 200, cdl_type)
            cdl_runtime_dfs[cdl_type] = copy.deepcopy(q_df)

        time_dt = now_dt()
        quote = Quote(time_dt)
        quote.add_quote(ExType.upbit, cdl_runtime_dfs, upbit_market_ticks)
        quote.add_quote(ExType.bithumb, cdl_runtime_dfs, bithumb_market_ticks)

        ##########################################
        ## marshal & unmarshal
        # encoded_json = quote.marshal()
        # print(encoded_json)
        # quote = Quote.unmarshal(encoded_json)

        ####################################################################################
        ## to_redis, from_redis
        _redis = redis.StrictRedis(host = global_prop.QUOTE_REDIS_IP_ADDR, port = global_prop.REDIS_PORT, db = 0)
        self.mem_profiler = MemoryProfiler()

        self.mem_profiler.take_1st_snapshot()
        sw = StopWatch()
        sw.start()
        count = 1
        for idx in range(0, count) :
            print(f"### {idx}")
            is_stored_well = quote.to_redis()

        elapsed_time = sw.stop()
        print(f"{elapsed_time=}, avg elapsed time=> {elapsed_time / count}")

        if is_stored_well :
            print("Storing quote to redis has been successfully executed!")
        else :
            print("Something is wrong in storing quote to redis.")

        self.mem_profiler.take_2nd_snapshot_and_show_topN(40)
        self.mem_profiler.print_mem_usage()

        self.mem_profiler.take_1st_snapshot()
        sw = StopWatch()
        sw.start()

        count = 10
        for idx in range(0, count) :
            includes = {}
            includes[ExType.upbit] = upbit_markets

            received_quote = Quote.from_redis(time_dt, _redis, includes)

            self.mem_profiler.take_2nd_snapshot_and_show_topN(40)
            self.mem_profiler.print_mem_usage()

            print(f"count : {idx}")
            gc.collect()

            # time.sleep(1)

        ####################################################################################
        cdl_returned_dfs = received_quote.get_candle_types(ExType.upbit)
        print(f'##' * 30 + f' Unmarshal')
        for cdl_type in cdl_returned_dfs :
            upbit_market_dfs = cdl_returned_dfs[cdl_type]
            for market in upbit_market_dfs :
                print(f"################### {cdl_type} - {market}, len : {len(upbit_market_dfs[market])}")

        market_ticks = received_quote.get_market_ticks(ExType.upbit)
        for market in market_ticks :
            print(f'{market} - {market_ticks[market].close}')



    def test_quote_market_ticks(self):
        markets = ('KRW-BTC', 'KRW-ETH', 'KRW-XRP')
        start_dt = str2dt('2018-10-01T00:00:00')
        end_dt = str2dt('2018-12-01T00:00:00')
        cdl_types_needed = [CandleType.DAYS, CandleType.HOUR]
        simul_storage = QuoteStorageMgr(markets, cdl_types_needed)

        cdl_runtime_dfs = {}
        for cdl_type in cdl_types_needed:
            q_df = simul_storage.load_quote_in_range(markets, start_dt, 200, cdl_type)
            cdl_runtime_dfs[cdl_type] = copy.deepcopy(q_df)

        time_dt = now_dt()
        quote = Quote(time_dt)
        quote.add_quote(ExType.upbit, cdl_runtime_dfs)

        market_ticks = quote.get_market_ticks(ExType.upbit, CandleType.DAYS)

        for market_tick in market_ticks:
            print(f'################### {market_tick} => {market_ticks[market_tick]}')



    # @unittest.skip("Tested")
    def test_execute_merge_df(self):
        # markets = ['KRW-BTC', 'KRW-ETH', 'KRW-XRP']
        # simul_start_dt = create_dt_at(2022, 1, 17, 4, 20, 0)
        # simul_end_dt = create_dt_at(2022, 1, 17, 4, 20, 0)
        # eqd = LocalQuoteDispatcher()

        _1m_simul_dfs = {}
        root_dir = dirname(dirname(__file__))
        btc_1m_csv = join(root_dir, './data/KRW-BTC_MINUTES_1.csv')
        btc_1m_df = pd.read_csv(btc_1m_csv, header=None)
        _1m_simul_dfs['KRW-BTC'] = btc_1m_df

        eth_1m_csv = join(root_dir, './data/KRW-ETH_MINUTES_1.csv')
        eth_1m_df = pd.read_csv(eth_1m_csv, header=None)
        _1m_simul_dfs['KRW-ETH'] = eth_1m_df

        # xrp_1m_csv = join(root_dir, './data/KRW-XRP_MINUTES_1.csv')
        # xrp_1m_df = pd.read_csv(xrp_1m_csv, header=None)
        # _1m_simul_dfs['KRW-XRP'] = xrp_1m_df
        #################################################################

        # df_all = None
        # for market in _1m_simul_dfs:
        #     market_df = _1m_simul_dfs[market]
        #
        #     market_df.set_index(market_df.columns[2], inplace=True, drop=False)
        #     market_df = market_df.fillna(0)
        #     if df_all is None:
        #         df_all = market_df
        #     else:
        #         df_all = df_all.join(market_df, how='outer', lsuffix='_left', rsuffix='_right')     ## Inner Product to remove the missing minute data in all markets
        #
        # df_all.to_csv('merged.csv')
        df_all_csv = join('merged.csv')
        df_all = pd.read_csv(df_all_csv, header=None)
        # df_all.fillna(method='ffill', inplace=True)
        # df_all.iloc[:, 3] = df_all.iloc[:, 0]
        # df_all.iloc[:, 14] = df_all.iloc[:, 0]
        print(f'num of na 1: {df_all.isna().any(axis=1).sum()}')
        print(f'num of na 2: {df_all.isna().sum(axis=1)}')

        print(f'num of na : {df_all.isna().tail(20)}')
        print('done!')


        # list_of_time, _1m_time_based_merged_dfs = eqd.merge_df(_1m_simul_dfs)
        #
        # listOfMarkets = [np.nan_to_num(x.to_numpy()) for x in _1m_time_based_merged_dfs]
        # listOfMarkets.insert(0, list_of_time)




if __name__ == '__main__':
    unittest.main()
    #
    # qd = QuoteDispatcher()
    # df = qd.process_quote()