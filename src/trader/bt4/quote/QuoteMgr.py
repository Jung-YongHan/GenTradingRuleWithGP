import datetime
import os
from datetime import timedelta, datetime as dt
from os.path import dirname, join

import pandas as pd

from bt4 import GlobalProperties
from bt4.Constants import CandleType, ExType, QItem
from bt4.quote.QuoteConnector import UniversalQuoteConnector
from bt4.utils.mylog import init_log
from bt4.utils.pandas_utils import rename_columns, sort_df
from bt4.utils.python_utils import SingletonInstance, load_class_from_module, start_timing, end_n_elapsed_time
from bulltrader_conf.quote import quote_config as QC
import pickle
import zlib
import redis
from multiprocessing.pool import ThreadPool
import math

log = init_log()

class QuoteStorageMgr:
    def __init__(self, markets: list, cdl_types_needed):
        log.info(f"connecting to Redis Server : {GlobalProperties.REDIS_HOST}:{GlobalProperties.REDIS_PORT}")
        self.rds = redis.StrictRedis(host=GlobalProperties.REDIS_HOST , port=GlobalProperties.REDIS_PORT, db=0)
        self.ex_cdl_dfs: dict = {}
        self.uq_connector = None
        self.cdl_types_needed: list = cdl_types_needed
        self.markets: list = markets
        self.uq_connector = UniversalQuoteConnector.instance()

    def initialize(self, ex_type: ExType) -> None:
        tmp_cdl_types_needed: list = self.cdl_types_needed.copy()
        if CandleType.MINUTES_1 not in tmp_cdl_types_needed:
            tmp_cdl_types_needed.append(CandleType.MINUTES_1)

        cdl_dfs = {}
        # cdl_dfs = self.load_past_quote_multi(ex_type, self.markets, tmp_cdl_types_needed)
        for cdl_type in tmp_cdl_types_needed:
            cdl_dfs[cdl_type.name] = self.load_past_quote(ex_type, cdl_type)
            if cdl_type == CandleType.HOUR:
                self.__set_timeframe(ex_type, cdl_dfs[cdl_type.name])
        self.ex_cdl_dfs[ex_type.name] = cdl_dfs

    def __set_timeframe(self, ex_type, dfs):
        root_dir: str = dirname(dirname(dirname(__file__)))  ## parent of parent of directory of simulator.py
        name_str = 'timeframe'
        sub_key = '201810'
        is_redis_none: int = 0

        cache_file_path = join(root_dir, f'./data/{ex_type.name}/{name_str}')
        if not os.path.exists(cache_file_path):
            os.makedirs(cache_file_path)

        _1h_timeframe_dfs = {}
        for timeframe_hour in range(24):
            key = f'{CandleType.DAYS.name}_{timeframe_hour}'
            _1d_quotes_for_timeframe = {}
            for market in self.markets:
                # key_market_redis = f'{ex_type}:{key}:{market}'
                key_market_redis = f'{ex_type}:{key}'
                if self.rds.hexists(key_market_redis, market) == is_redis_none:
                    log.info(f'key: {key_market_redis} 은/는 캐시 DB에 없습니다. 초기 데이터를 저장합니다.')
                    key_market_file = f'{market.replace("/","_")}_{key}'
                    file_name = f'{name_str}_{key_market_file}.csv'
                    file_path = join(root_dir, f'./data/{ex_type.name}/{name_str}/{file_name}')

                    if os.path.isfile(file_path):
                        log.info(f'{file_path}가 존재합니다. 파일을 읽어옵니다.')
                        _1d_quotes_for_timeframe[market] = pd.read_csv(file_path, index_col=QItem.time.value, parse_dates=True)
                        self.store_df_to_redis(_1d_quotes_for_timeframe[market], key_market_redis, market)
                    else:
                        log.info(f'{file_path}의 캐시 데이터가 없습니다. 데이터를 생성합니다.')
                        _1d_quotes_for_timeframe[market] = self.uq_connector.extract_1d_quote_for_timeframe(dfs[market], timeframe_hour)

                        log.info(f'{file_path}에 {key_market_file} 캐시 데이터를 저장합니다.')
                        _1d_quotes_for_timeframe[market].to_csv(file_path, index=True)

                        self.store_df_to_redis(_1d_quotes_for_timeframe[market], key_market_redis, market)
                else:
                    _1d_quotes_for_timeframe[market] = self.search_df_from_redis(key_market_redis, market)
            _1h_timeframe_dfs[key] = _1d_quotes_for_timeframe


        self.uq_connector.load_cache(ex_type, _1h_timeframe_dfs)

    def __set_timeframe2(self, ex_type, dfs):
        root_dir: str = dirname(dirname(dirname(__file__)))  ## parent of parent of directory of simulator.py
        name_str = 'timeframe'

        cache_file_path = join(root_dir, f'./data/{ex_type.name}/{name_str}')
        if not os.path.exists(cache_file_path):
            os.makedirs(cache_file_path)

        _1h_timeframe_dfs = {}
        for timeframe_hour in range(24):
            key = f'{CandleType.DAYS.name}_{timeframe_hour}'
            _1d_quotes_for_timeframe = {}
            for market in self.markets:
                # key_market_redis = f'{ex_type}:{key}:{market}'
                key_market_redis = f'{ex_type.name}:{key}'
                key_market_file = f'{market.replace("/","_")}_{key}'
                file_name = f'{name_str}_{key_market_file}.csv'
                file_path = join(root_dir, f'./data/{ex_type.name}/{name_str}/{file_name}')

                _1d_quotes_for_timeframe[market] = self.uq_connector.extract_1d_quote_for_timeframe(dfs[market], timeframe_hour)

                log.info(f'[CSV] {file_path}에 {key_market_file} 캐시 데이터를 저장합니다.')
                _1d_quotes_for_timeframe[market].to_csv(file_path, index=True)

                self.store_df_to_redis(_1d_quotes_for_timeframe[market], key_market_redis, market)
            _1h_timeframe_dfs[key] = _1d_quotes_for_timeframe

        self.uq_connector.load_cache(ex_type, _1h_timeframe_dfs)

    def extract_timeframe_quotes(self, ex_type: ExType, _1h_dfs: dict, timeframe_hours: list) -> dict:
        return self.uq_connector.extract_timeframe_quotes(ex_type, _1h_dfs, timeframe_hours)

    def store_df_to_redis(self, df, key: str, sub_key: str = '201810'):
        df.iloc(0)
        pickle_df: bytes = zlib.compress(pickle.dumps(df))
        self.rds.hset(key, sub_key, pickle_df)
        log.info(f'[Redis] {key}/{sub_key}에 데이터를 저장합니다.')

    def search_df_from_redis(self, key: str, sub_key: str = '201810'):
        return pickle.loads(zlib.decompress(self.rds.hget(key, sub_key)))

    def load_past_quote(self, ex_type: ExType, cdl_type: CandleType) -> dict:
        root_dir: str = dirname(dirname(dirname(__file__)))  ## parent of parent of directory of simulator.py
        missing_market_in_files: list = []
        dfs: dict = {}
        is_redis_none: int = 0

        for market in self.markets:  # 1.
            # key: str = f'{ex_type.name}:{cdl_type.name}:{market}'
            key: str = f'{ex_type.name}:{cdl_type.name}'
            if self.rds.hexists(key, market) == is_redis_none:
                # todo timeframe의 경우 존재하지 않을 때 전체 기간의 해당 타임프레임 데이터를 생성하고 저장하도록 구현
                log.info(f'key: {key} 은/는 캐시 DB에 없습니다. 초기 데이터를 저장합니다.')
                f_market = market.replace('/', '_')
                file_name: str = join(root_dir, f'data{os.sep}{ex_type.name}{os.sep}{f_market}_{cdl_type.name}.csv')
                if os.path.isfile(file_name):  # 1.1
                    log.info('fetching markets from ' + file_name)
                    tmp_df = pd.read_csv(file_name, parse_dates=True, index_col=QItem.time.value)
                    dfs[market] = self.__fill_empty_time(tmp_df, cdl_type)
                    self.store_df_to_redis(dfs[market], key, market)
                else:
                    missing_market_in_files.append(market)
            else:
                # log.info(f'key: {key} 이/가 존재합니다. 데이터를 캐시 DB에서 읽어옵니다.')
                dfs[market] = self.search_df_from_redis(key, market)

        if len(missing_market_in_files) != 0:
            missing_market_dfs: dict = self.uq_connector.fetch_quote_num_candles(ex_type, missing_market_in_files, int(60 * 24 * 365 * 20 / cdl_type), cdl_type)
            for m_market in missing_market_dfs:
                f_market = m_market.replace('/','_')
                file_name: str = join(root_dir, f'data{os.sep}{ex_type.name}{os.sep}{f_market}_{cdl_type.name}.csv')
                log.info(f'### write patched data {file_name}')
                missing_market_dfs[m_market].to_csv(file_name, index=True)

                # key: str = f'{ex_type.name}:{cdl_type.name}:{m_market}'
                key: str = f'{ex_type.name}:{cdl_type.name}'
                dfs[m_market] = self.__fill_empty_time(missing_market_dfs[m_market], cdl_type)
                self.store_df_to_redis(missing_market_dfs[m_market], key, m_market)
            dfs.update(missing_market_dfs)
        return dfs

    def fetch_candle(self, args):
        # print(args)
        ex_type = args[0]
        market = args[1]
        num_of_candle = args[2]
        now_dt = args[3]
        candle_type = args[4]
        end_dt = args[5]
        candle_df = args[6]
        root_dir = args[7]

        delta = now_dt - end_dt
        minute_diff = math.ceil(delta.total_seconds() / candle_type.value / 60)
        iter_num = math.ceil(minute_diff / num_of_candle)
        total_df = None
        for i in range(iter_num):
            # print(f'{market}의 {candle_type.name} - {i+1}번째 수집({200*(i+1)}/{minute_diff}, {200*(i+1)/minute_diff*100:.2f}%)')
            print(f' {market}의 {candle_type.name} - {i+1}번째 수집({200*(i+1)}/{minute_diff}, {200 * (i + 1) / minute_diff * 100:.2f}%)')
            df = self.uq_connector.fetch_tick_quote(ex_type, market, num_of_candle, now_dt,candle_type)
            # print(f'df is None === {df is None}')
            if df is None:
                break
            else:
                if total_df is not None:
                    total_df = pd.concat([total_df, df])
                else:
                    total_df = df
            now_dt = now_dt - datetime.timedelta(minutes = num_of_candle * candle_type.value)

        candle_df = pd.concat([candle_df, total_df]).sort_index()
        candle_df = candle_df[~candle_df.index.duplicated()]
        candle_df.index.name = 'datetime'
        candle_df.to_csv(f'{root_dir}/data/{ex_type.name}/{market}_{candle_type.name}.csv', index=True)

        # redis_key = f'{ex_type.value}:{candle_type.name}:{market}'
        redis_key = f'{ex_type.value}:{candle_type.name}'
        candle_df = self.__fill_empty_time(candle_df, candle_type)
        self.store_df_to_redis(candle_df, redis_key, market)
        return (market, candle_type, f'{root_dir}/data/{ex_type.name}/{market}_{candle_type.name}.csv', candle_df)

    def download_parallel(self, args, total_dfs) -> dict:
        # cpus = cpu_count()
        cpus = 5
        pool = ThreadPool(cpus)
        results = pool.imap_unordered(self.fetch_candle, args)
        pool.close()
        pool.join()

        for result in results:
            market = result[0]
            candle_type = result[1]
            total_dfs[candle_type.name][market] = result[3]
            print('[수집 완료] ::: Market ->', result[0], ', Candle Type ->', result[1].name, ', Path >', result[2])
        return total_dfs

    def load_stored_quote(self,
                          ex_type: ExType,
                          markets: list = [],
                          cdl_types_needed: list = [],
                          start_to: datetime.datetime = datetime.datetime.now() - timedelta(days=1),
                          from_to: datetime.datetime = datetime.datetime(2017, 1, 1, 0, 0, 0),
                          do_update: bool = False,
                          root_dir: str = dirname(dirname(dirname(__file__)))) -> dict:

        if ex_type is None:
            raise ValueError("The ex_type cannot be None")

        if not markets:
            if not self.markets:
                raise ValueError("The markets cannot be None")
            markets = self.markets

        if not cdl_types_needed:
            if not self.cdl_types_needed:
                raise ValueError("The cdl_types_needed cannot be None")
            cdl_types_needed = self.cdl_types_needed

        # root_dir: str = dirname(dirname(dirname(__file__)))  ## parent of parent of directory of simulator.py
        missing_market_in_files: list = []
        total_dfs: dict = {}
        is_redis_none: int = 0

        task = []
        num_of_candle_for_dispatching = 200
        data_dir_path = f'{root_dir}{os.sep}data{os.sep}{ex_type.name}'
        if not os.path.exists(data_dir_path):
            log.info(f'[dir] {data_dir_path}의 경로에 디렉터리가 없습니다. 디렉터리를 생성합니다.')
            os.makedirs(data_dir_path)

        for candle_type in cdl_types_needed:
            dfs: dict = {}
            for market in markets:
                # key: str = f'{ex_type.name}:{candle_type.name}:{market}'
                key: str = f'{ex_type.name}:{candle_type.name}'
                if self.rds.hexists(key, market) == is_redis_none:
                    # todo timeframe의 경우 존재하지 않을 때 전체 기간의 해당 타임프레임 데이터를 생성하고 저장하도록 구현
                    log.info(f'[Redis] key-{key}:{market}은/는 캐시 DB에 없습니다. 저장된 CSV 파일을 확인합니다.')
                    f_market = market.replace('/', '_')
                    file_name: str = join(root_dir, f'data{os.sep}{ex_type.name}{os.sep}{f_market}_{candle_type.name}.csv')
                    if os.path.isfile(file_name):  # 1.1
                        log.info(f'[CSV] key-{key}:{market}에 해당되는 CSV 파일이 존재합니다. ' + file_name + '로 부터 데이터를 읽어옵니다.')
                        tmp_df = pd.read_csv(file_name, parse_dates=True, index_col=QItem.time.value)
                        dfs[market] = self.__fill_empty_time(tmp_df, candle_type)
                        # self.store_df_to_redis(dfs[market], key)
                        end_dt = dfs[market].index[-1]
                        target_df = dfs[market]
                    else:
                        log.info(f'[CSV] key-{key}:{market}에 해당되는 CSV 파일이 {file_name}에 존재하지 않습니다. 전구간 데이터 수집을 진행합니다.')
                        missing_market_in_files.append(key)
                        end_dt = from_to
                        target_df = pd.DataFrame()

                else:
                    log.info(f'[Redis] key: key-{key}:{market}이/가 존재합니다. 데이터를 캐시 DB에서 읽어옵니다.')
                    dfs[market] = self.search_df_from_redis(key, market)
                    end_dt = dfs[market].index[-1]
                    target_df = dfs[market]
                task.append((ex_type, market, num_of_candle_for_dispatching, start_to, candle_type, end_dt, target_df, root_dir))
            total_dfs[candle_type.name] = dfs

        # todo 왜 이 로직을 작성했는지 기억이 나지 않음
        is_wait = True if len(missing_market_in_files) > 1 else False

        if do_update:
            total_dfs = self.download_parallel(task, total_dfs)
            self.__update_date(f'{ex_type.name}:Period', total_dfs['DAYS'])
            if CandleType.HOUR in cdl_types_needed:
                self.__set_timeframe2(ex_type, total_dfs['HOUR'])
        return total_dfs

    def __read_cache_timeframe(self, cache_name: str, root_dir: str) -> dict:
        _1d_quotes = {}
        for timeframe_hour in range(24):
            key = f'{CandleType.DAYS.name}_{timeframe_hour}'
            _1d_quotes_for_timeframe = {}
            for market in self.markets:
                cache_key = f'{market}_{key}'
                file_name = f'daily_{cache_name}_base_{cache_key}.csv'
                file_path = join(root_dir, f'./data/{cache_name}/{file_name}')
                if os.path.isfile(file_path):
                    log.info(f'{file_path}을/를 읽어옵니다.')
                    resampled_df = pd.read_csv(file_path, index_col=QItem.time.value)
                    _1d_quotes_for_timeframe[market] = resampled_df
                else:
                    log.info(f'{file_path}의 캐시 데이터가 없습니다.')
            _1d_quotes[key] = _1d_quotes_for_timeframe
        return _1d_quotes

    def __write_cache_timeframe(self, cache_name: str, root_dir: str, _1h_timeframe_dfs, ex_type: ExType, cdl_type: CandleType) -> None:
        for timeframe_hour in range(24):
            key = f'{CandleType.DAYS.name}_{timeframe_hour}'
            for market in self.markets:
                key_market = f'{market}_{key}'
                file_name = f'daily_{cache_name}_base_{key_market}.csv'
                file_path = join(root_dir, f'./data/{cache_name}/{file_name}')
                log.info(f'{file_path}에 {key_market} 캐시 데이터를 저장합니다.')
                _1h_timeframe_dfs[key][market].to_csv(file_path)

                # redis_key = f'{ex_type.value}:{key}:{market}'
                redis_key = f'{ex_type.value}:{key}'
                self.store_df_to_redis(_1h_timeframe_dfs[key][market], redis_key, market)

    def __fill_empty_time(self, df, cdl_type: CandleType):
        freq_str = f'{cdl_type.value}min'
        idx = pd.date_range(df.index.min(), df.index.max(), freq=freq_str)
        skelton_df = pd.DataFrame(index=idx)
        df = pd.concat([skelton_df, df], axis=1)
        df.ffill(inplace=True)
        return df

    def load_and_fill_quote_to_end(self, ex_type: ExType, runtime_dfs, start_pdt, cdl_type: CandleType) :
        if ex_type not in self.ex_cdl_dfs : self.initialize(ex_type)
        simul_range_end_pdt = start_pdt
        runtime_df = list(runtime_dfs.values())[0]
        simul_range_start_pdt = runtime_df.tail(1).index.item() + timedelta(minutes=1)
        return self.load_quote_in_range2(ex_type, runtime_dfs.keys(), simul_range_start_pdt, simul_range_end_pdt, cdl_type)

    def load_quote_in_range(self, ex_type: ExType, markets: list, start_pdt, num_back_candles: int, cdl_type: CandleType):
        if ex_type not in self.ex_cdl_dfs: self.initialize(ex_type)

        simul_range_end_pdt = start_pdt
        simul_range_start_pdt = self.get_candle_start_pdt(cdl_type, start_pdt, num_back_candles)
        return self.load_quote_in_range2(ex_type, markets, simul_range_start_pdt, simul_range_end_pdt, cdl_type)

    def get_candle_start_pdt(self, cdl_type, start_pdt, num_back_candles):
        simul_range_end_pdt = start_pdt

        days = 200
        simul_range_start_pdt = simul_range_end_pdt - timedelta(days = 200)

        # if cdl_type == CandleType.DAYS :
        #     # simul_range_end_dt = simul_range_end_dt - timedelta(days=1)
        #     simul_range_start_pdt = simul_range_end_pdt - timedelta(days = num_back_candles)
        # elif cdl_type == CandleType.HOUR4 :  # for DataType.HOUR4
        #     # simul_range_end_dt = simul_range_end_dt - timedelta(hours=4)
        #     simul_range_start_pdt = simul_range_end_pdt - timedelta(hours = num_back_candles * 4)
        # elif cdl_type == CandleType.HOUR :  # for DataType.HOUR
        #     # simul_range_end_dt = simul_range_end_dt - timedelta(hours=1)
        #     simul_range_start_pdt = simul_range_end_pdt - timedelta(hours = num_back_candles)
        # elif cdl_type == CandleType.MINUTES_1 :
        #     # simul_range_end_dt = simul_range_end_dt - timedelta(minutes=1)
        #     simul_range_start_pdt = simul_range_end_pdt - timedelta(minutes = num_back_candles * num_back_candles)
        # elif cdl_type == CandleType.MINUTES_3 :
        #     # simul_range_end_dt = simul_range_end_dt - timedelta(minutes=1)
        #     simul_range_start_pdt = simul_range_end_pdt - timedelta(minutes = num_back_candles * 3)
        # elif cdl_type == CandleType.MINUTES_5 :
        #     # simul_range_end_dt = simul_range_end_dt - timedelta(minutes=1)
        #     simul_range_start_pdt = simul_range_end_pdt - timedelta(minutes = num_back_candles * 5)
        # elif cdl_type == CandleType.MINUTES_10 :
        #     # simul_range_end_dt = simul_range_end_dt - timedelta(minutes=1)
        #     simul_range_start_pdt = simul_range_end_pdt - timedelta(minutes = num_back_candles * 10)
        # elif cdl_type == CandleType.MINUTES_15 :
        #     # simul_range_end_dt = simul_range_end_dt - timedelta(minutes=1)
        #     simul_range_start_pdt = simul_range_end_pdt - timedelta(minutes = num_back_candles * 15)
        # elif cdl_type == CandleType.MINUTES_30 :
        #     # simul_range_end_dt = simul_range_end_dt - timedelta(minutes=1)
        #     simul_range_start_pdt = simul_range_end_pdt - timedelta(minutes = num_back_candles * 30)
        return simul_range_start_pdt

    def load_quote_in_range2(self, ex_type: ExType, markets: list, start_pdt, end_pdt, cdl_type: CandleType) -> dict:
        if ex_type not in self.ex_cdl_dfs : self.initialize(ex_type)

        target_dfs: dict = self.ex_cdl_dfs[ex_type.name][cdl_type.name]
        ranged_dfs: dict = {}
        for market in markets:
            ranged_dfs[market] = target_dfs[market].loc[start_pdt:end_pdt]
        return ranged_dfs

    def __update_date(self, key, dfs):

        for market in self.markets:
            # Get the index of the first row
            first_index = dfs[market].index[0]
            print("Index of the first row:", first_index)
            self.rds.hset(f'{key}:{market}', 'start_date', first_index.strftime('%Y-%m-%d'))

            # Get the index of the last row
            last_index = dfs[market].index[-1]
            print("Index of the last row:", last_index)
            self.rds.hset(f'{key}:{market}', 'end_date', last_index.strftime('%Y-%m-%d'))

class QuoteMgr(SingletonInstance):
    def __init__(self, exchange):
        ## TODO : create all candle types for upbit_spot, binance_spot, binance_futures
        ## TODO : should support all markets
        ## TODO : should store them into redis
        ## TODO : load them into dataframe
        ## TODO : Marshel and Unmarshal Quote(exchange, market, candle_type) for sending Kafka
        ## TODO : Need to consider size for transfering them into network.
        self._1d_dfs = None
        self._4h_dfs = None
        self._1h_dfs = None
        self._1m_dfs = None
        self._3m_dfs = None
        self._5m_dfs = None
        self._10m_dfs = None
        self._15m_dfs = None
        self._30m_dfs = None
        self._1h_timeframe_dfs = {}
        self.q_connector = None
        self.initialize()

    def initialize(self):
        qd_params = QC.QUOTE_DISPATCHER_PARAMS
        self.q_connector_name = qd_params[QC.PARAM_QUOTE_CONNECTOR]
        self.markets = qd_params[QC.PARAM_MARKET]
        conn_module_name = __package__ + '.QuoteConnector'
        conn_class_name = self.q_connector_name + "QuoteConnector"
        self.q_connector = load_class_from_module(conn_module_name, conn_class_name)
        self.q_connector.on_cache = True

        if self._1d_dfs is None:
            self._1d_dfs = self.load_past_quote(data_type=CandleType.DAYS)
        if self._4h_dfs is None:
            self._4h_dfs = self.load_past_quote(data_type=CandleType.HOUR4)
        if self._1h_dfs is None:
            self._1h_dfs = self.load_past_quote(data_type=CandleType.HOUR)
        if self._1m_dfs is None:
            self._1m_dfs = self.load_past_quote(data_type=CandleType.MINUTES_1)
        if self._3m_dfs is None:
            self._3m_dfs = self.load_past_quote(data_type=CandleType.MINUTES_3)
        if self._5m_dfs is None:
            self._5m_dfs = self.load_past_quote(data_type=CandleType.MINUTES_5)
        if self._10m_dfs is None:
            self._10m_dfs = self.load_past_quote(data_type=CandleType.MINUTES_10)
        if self._15m_dfs is None:
            self._15m_dfs = self.load_past_quote(data_type=CandleType.MINUTES_15)
        if self._30m_dfs is None:
            self._30m_dfs = self.load_past_quote(data_type=CandleType.MINUTES_30)

        root_dir = dirname(dirname(dirname(__file__)))  ## parent of parent of directory of simulator.py
        self.timeframe_hours = qd_params[QC.PARAM_TIMEFRAME_HOURS]
        date_key = 'candle_date_time_kst'

        if len(self._1h_timeframe_dfs.keys()) == 0:
            '''
                캐시 절차
                * 모든 타임프레임 캐시 데이터(파일)가 있는지 확인한다.
                    O -> 모든 데이터를 읽는다.
                        a. cache_enable = True
                        b. 읽은 데이터를 리턴한다.
                    X -> 데이터 생성
                        a. extract_timeframe_quotes를 활용하여 전체 데이터 생성
                        b. 생성된 데이터 cache 폴더에 저장
                        c. 생성된 데이터 전달

                ----------------------------------------------------------
                데이터를 확인하기 위해서
                    1. 마켓 정보
                    2. 타임프레임 전체
                    3.
            '''

            def read_cache_timeframe(cache_name: str) -> dict:
                _1d_quotes = {}
                for timeframe_hour in self.timeframe_hours:
                    key = f'{CandleType.DAYS.name}_{timeframe_hour}'
                    _1d_quotes_for_timeframe = {}
                    for market in self.markets:
                        cache_key = f'{market}_{key}'
                        file_name = f'daily_{cache_name}_cache_base_{cache_key}.csv'
                        file_path = join(root_dir, f'./data/cache/{cache_name}/{file_name}')
                        if os.path.isfile(file_path):
                            resampled_df = pd.read_csv(file_path, index_col=date_key)
                            _1d_quotes_for_timeframe[market] = resampled_df
                        else:
                            log.info('캐시 데이터가 없습니다.')
                    _1d_quotes[key] = _1d_quotes_for_timeframe
                return _1d_quotes

            def write_cache_timeframe(cache_name: str) -> None:
                for timeframe_hour in self.timeframe_hours:
                    key = f'{CandleType.DAYS.name}_{timeframe_hour}'
                    for market in self.markets:
                        cache_key = f'{market}_{key}'
                        file_name = f'daily_{cache_name}_cache_base_{cache_key}.csv'
                        file_path = join(root_dir, f'./data/cache/{cache_name}/{file_name}')
                        self._1h_timeframe_dfs[key][market].to_csv(file_path)

            cache_name_str = 'timeframe'
            cache_file_path = join(root_dir, f'./data/cache/{cache_name_str}')
            if not os.path.exists(cache_file_path):
                os.makedirs(cache_file_path)

            if len(os.listdir(cache_file_path)) == 0:
                start = start_timing()
                self._1h_timeframe_dfs = self.q_connector.extract_timeframe_quotes(self._1h_dfs, self.timeframe_hours)
                write_cache_timeframe(cache_name_str)
                end_n_elapsed_time(start, 'q_connector.extract_timeframe_quotes')
            else:
                self._1h_timeframe_dfs = read_cache_timeframe('timeframe')

    def load_past_quote(self, data_type):
        root_dir = dirname(dirname(dirname(__file__)))  ## parent of parent of directory of simulator.py
        missing_market_in_files = []
        dfs = {}

        for market in self.markets:  # 1.
            file_name = join(root_dir, f'data{os.sep}{market}_{data_type.name}.csv')
            if os.path.isfile(file_name):  # 1.1
                df = pd.read_csv(file_name, header=None)
                log.info('fetching markets from ' + file_name)
                dfs[market] = df
            else:
                missing_market_in_files.append(market)

        if len(missing_market_in_files) != 0:
            missing_market_dfs = self.q_connector.fetch_quote_num_candles(missing_market_in_files, 60 * 24 * 365 * 20,
                                                                          data_type)
            for m_market in missing_market_dfs:
                file_name = join(root_dir, f'data{os.sep}{m_market}_{data_type.name}.csv')
                log.info(f'### write patched data {file_name}')
                missing_market_dfs[m_market].to_csv(file_name, header=None, index=False)

            dfs.update(missing_market_dfs)

        for market in self.markets:
            c_name_dic = {}
            # column_names = self.q_connector.get_column_names() # Why does not this work?
            column_names = ['market', 'candle_date_time_utc', 'candle_date_time_kst', 'opening_price', 'high_price',
                            'low_price', 'trade_price', 'timestamp', 'candle_acc_trade_price',
                            'candle_acc_trade_volume', 'unit']
            for i, cname in enumerate(column_names):
                c_name_dic[f'{i}'] = cname
                c_name_dic[i] = cname
            rename_columns(dfs[market], c_name_dic)
            sort_df(dfs[market], 'candle_date_time_kst')
            # shift_rows_of_columns(dfs[market], ['opening_price', 'high_price',
            #    'low_price', 'trade_price', 'timestamp', 'candle_acc_trade_price', 'candle_acc_trade_volume'], 1)

        return dfs

    def load_quote_in_range(self, markets, simul_start_dt, num_back_candles, data_type):
        simul_range_end_dt = simul_start_dt

        if data_type == CandleType.DAYS:
            # simul_range_end_dt = simul_range_end_dt - timedelta(days=1)
            simul_range_start_dt = simul_range_end_dt - timedelta(days=num_back_candles)
        elif data_type == CandleType.HOUR4:  # for DataType.HOUR4
            # simul_range_end_dt = simul_range_end_dt - timedelta(hours=4)
            simul_range_start_dt = simul_range_end_dt - timedelta(hours=num_back_candles * 4)
        elif data_type == CandleType.HOUR:  # for DataType.HOUR
            # simul_range_end_dt = simul_range_end_dt - timedelta(hours=1)
            simul_range_start_dt = simul_range_end_dt - timedelta(hours=num_back_candles)
        elif data_type == CandleType.MINUTES_1:
            # simul_range_end_dt = simul_range_end_dt - timedelta(minutes=1)
            simul_range_start_dt = simul_range_end_dt - timedelta(minutes=num_back_candles)
        elif data_type == CandleType.MINUTES_3:
            # simul_range_end_dt = simul_range_end_dt - timedelta(minutes=1)
            simul_range_start_dt = simul_range_end_dt - timedelta(minutes=num_back_candles * 3)
        elif data_type == CandleType.MINUTES_5:
            # simul_range_end_dt = simul_range_end_dt - timedelta(minutes=1)
            simul_range_start_dt = simul_range_end_dt - timedelta(minutes=num_back_candles * 5)
        elif data_type == CandleType.MINUTES_10:
            # simul_range_end_dt = simul_range_end_dt - timedelta(minutes=1)
            simul_range_start_dt = simul_range_end_dt - timedelta(minutes=num_back_candles * 10)
        elif data_type == CandleType.MINUTES_15:
            # simul_range_end_dt = simul_range_end_dt - timedelta(minutes=1)
            simul_range_start_dt = simul_range_end_dt - timedelta(minutes=num_back_candles * 15)
        elif data_type == CandleType.MINUTES_30:
            # simul_range_end_dt = simul_range_end_dt - timedelta(minutes=1)
            simul_range_start_dt = simul_range_end_dt - timedelta(minutes=num_back_candles * 30)

        return self.load_quote_in_range2(markets, simul_range_start_dt, simul_range_end_dt, data_type)

    def load_quote_in_range2(self, markets, simul_start_dt, simul_end_dt, data_type):
        if data_type == CandleType.DAYS:
            target_dfs = self._1d_dfs
        elif data_type == CandleType.HOUR4:  # for DataType.HOUR4
            target_dfs = self._4h_dfs
        elif data_type == CandleType.HOUR:  # for DataType.HOUR
            target_dfs = self._1h_dfs
        elif data_type == CandleType.MINUTES_1:
            target_dfs = self._1m_dfs
        elif data_type == CandleType.MINUTES_3:
            target_dfs = self._3m_dfs
        elif data_type == CandleType.MINUTES_5:
            target_dfs = self._5m_dfs
        elif data_type == CandleType.MINUTES_10:
            target_dfs = self._10m_dfs
        elif data_type == CandleType.MINUTES_15:
            target_dfs = self._15m_dfs
        elif data_type == CandleType.MINUTES_30:
            target_dfs = self._30m_dfs


        simul_start_str = dt.strftime(simul_start_dt, "%Y-%m-%dT%H:%M:%S")
        simul_end_str = dt.strftime(simul_end_dt, "%Y-%m-%dT%H:%M:%S")
        ranged_dfs = {}
        for market in markets:
            target_df = target_dfs[market]
            target_df.set_index(target_df.columns[2], inplace=True, drop=False)
            target_df.sort_index(inplace=True, ascending=True)
            ranged_df = target_df.loc[simul_start_str:simul_end_str]
            ranged_dfs[market] = ranged_df
        return ranged_dfs