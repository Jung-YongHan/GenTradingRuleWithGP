import datetime
import threading
import time

from bt4.Constants import CandleType
from bt4.utils.mylog import init_log
from talib import abstract
from collections import OrderedDict
import bulltrader_conf.quote.quote_config as QC
from bt4.utils.python_utils import load_func_from_module, dt2str, str2dt
import numpy as np
from os.path import dirname, join, isfile
import pandas as pd
import os
import json
log = init_log()


class TAIndicatorMgr:
    '''
    Check the documentation for talib
    https://mrjbq7.github.io/ta-lib/doc_index.html
    '''

    def __init__(self, qd_params, on_cache=False):
        self.qd_params = qd_params
        self.ta_indicators_list = qd_params[QC.PARAM_TA_INDICATORS]
        ignore_data = ['connector', 'markets', 'timeframe_hours', 'ta_indicators']
        self.simul_tais = [ta for ta in qd_params.keys() if ta not in ignore_data]
        self._tais_min_dfs = {}
        self._tais_hour_dfs = {}
        self.on_cache = on_cache
        if self.on_cache:
            self.tais_cache_buffer = TAICacheBuffer()
            self.__ready_tais_cache()

    def compute_ta_indicators(self, inputs, simul_tais = None, time_dt = None):
        markets = inputs['markets']
        result_markets = OrderedDict()

        for market in markets:
            # result_list = []
            result_list = OrderedDict()
            # print(time_dt)
            if time_dt:
                current_tais_cache, target_date = self.__get_tais_cache(market, time_dt)
            # else:
            #     current_tais_cache, target_date =
            tai_list = None

            if simul_tais is not None:
                # tai_list = simul_tais[market]
                tai_list = simul_tais
            else:
                tai_list = self.ta_indicators_list

            for alias in tai_list:
                # 캐시 데이터 읽기
                # print(f'{market=}, {alias=}, {current_tais_cache=}')
                if self.on_cache and not current_tais_cache.empty and alias in current_tais_cache and not pd.isna(current_tais_cache[alias]):
                    result_list[alias] = json.loads(f'[{current_tais_cache[alias]}]')

                else: # 캐시가 없는 경우 계산
                    params = self.qd_params[alias]
                    if params is None:
                        log.error(f'ERROR: There is no configuation for {alias} in conf.quote.QuoteConfig.py.')
                        continue

                    result_target = self.call_function(market, inputs, alias, params)
                    # if isinstance(result_target[alias], int):
                    #     result_target[alias] = float(result_target[alias])
                    # log.info(f'{market} - {alias} ==> {result_target}')
                    result_list[alias] = result_target[alias]

                    if self.on_cache:
                        self.__cache_new_tai(result_target, alias, target_date, market) # 계산 후 저장
            result_markets[market] = result_list
        return result_markets

    def __get_tais_cache(self, market: str, time_dt: datetime.datetime) -> (str, pd.DataFrame):
        target_date = dt2str(time_dt)
        if self.on_cache and market in self._tais_min_dfs.keys() and target_date in self._tais_min_dfs[market].index:
            current_tais_cache = self._tais_min_dfs[market].loc[target_date]  # 새로운 기간 추가시 인덱스 없음
        else:
            current_tais_cache = pd.DataFrame()
        return current_tais_cache, target_date

    def __cache_new_tai(self, result_target: dict, alias: str, target_date: str, market: str) -> None:
        value = json.dumps(result_target[alias])[1:-1]
        target_date_dt = str2dt(target_date)

        if not market in self._tais_min_dfs.keys():
            self._tais_min_dfs[market] = pd.DataFrame() # 분봉 데이터 초기화

        if not market in self._tais_hour_dfs.keys():
            self._tais_hour_dfs[market] = pd.DataFrame() # 시간봉 데이터 초기화

        if target_date in self._tais_min_dfs[market].index: # 함께 생성하기 때문에 혼용 가능할 것이라 판단
            axis = 1
        else:
            axis = 0

        self.__concat_cache(alias, market, target_date, value, axis, self._tais_min_dfs)
        if target_date_dt.minute == 59:
            target_hour = target_date_dt - datetime.timedelta(minutes=59)
            self.__concat_cache(alias, market, dt2str(target_hour), value, axis, self._tais_hour_dfs)

        self.__write_cache_tais(market)

    def __concat_cache(self, alias: str, market: str, target_date: str, json_string: str, axis: int, dfs: dict) -> None:
        if alias in dfs[market].columns and target_date in dfs[market].index:
            dfs[market].loc[target_date, alias] = json_string
        else:
            temp_tai_dict = {alias: json_string}
            temp_min_df = pd.DataFrame(temp_tai_dict, index=[target_date])
            temp_min_df.index.name = 'candle_date_time_kst'
            dfs[market] = pd.concat([dfs[market], temp_min_df], axis=axis)
            dfs[market].index.name = 'candle_date_time_kst'

    def __write_cache_tais(self,  market: str) -> None:
        if self.tais_cache_buffer.is_store_time(market):
            root_dir = dirname(dirname(dirname(__file__)))
            cache_name = 'tais'

            min_file_name = f'daily_{cache_name}_min_cache_base_{market}.csv'
            min_file_path = join(root_dir, f'./data/cache/{cache_name}/{min_file_name}')

            hour_file_name = f'daily_{cache_name}_hour_cache_base_{market}.csv'
            hour_file_path = join(root_dir, f'./data/cache/{cache_name}/{hour_file_name}')

            self.tais_cache_buffer.store_csv(self._tais_min_dfs[market], self._tais_hour_dfs[market], min_file_path, hour_file_path, market)
            # self._tais_min_dfs[market].to_csv(file_path)
        else:
            self.tais_cache_buffer.stack_data(market)

    def __ready_tais_cache(self) -> None:
        ignore_data = ['connector', 'markets', 'timeframe_hours', 'ta_indicators']
        simul_tais = [ta for ta in self.qd_params.keys() if ta not in ignore_data]
        root_dir = dirname(dirname(dirname(__file__)))
        markets = self.qd_params['markets']

        def read_cache_tais(cache_name: str, datatype: str) -> dict:
            _all_tais = {}
            DATE_KEY = 'candle_date_time_kst'
            for market in markets:
                file_name = f'daily_{cache_name}_{datatype}_cache_base_{market}.csv'
                file_path = join(root_dir, 'data', 'cache', cache_name, file_name) # f'./data/cache/{cache_name}/{file_name}'
                if isfile(file_path):
                    tai_data = pd.read_csv(file_path, index_col=DATE_KEY)
                    _all_tais[market] = tai_data
                else:
                    # 필요시 예외 발생
                    log.warning(f'[{cache_name}] {file_name} 캐시 데이터가 없습니다.')
            return _all_tais

        cache_name_str = 'tais'
        cache_file_path = join(root_dir, f'./data/cache/{cache_name_str}')
        if not os.path.exists(cache_file_path):
            os.makedirs(cache_file_path)

        if len(os.listdir(cache_file_path)) == 0:
            for market in markets:
                self._tais_min_dfs[market] = pd.DataFrame(columns=simul_tais)
                self._tais_hour_dfs[market] = pd.DataFrame(columns=simul_tais)
        else:
            self._tais_min_dfs = read_cache_tais(cache_name_str, 'min')
            self._tais_hour_dfs = read_cache_tais(cache_name_str, 'hour')

        for market in markets:
            if market in self._tais_min_dfs.keys():
                self.__drop_dependent_tai(simul_tais, self._tais_min_dfs, market)

            if market in self._tais_hour_dfs.keys():
                self.__drop_dependent_tai(simul_tais, self._tais_hour_dfs, market)

        # self.tais_cache_buffer.init_stack_count(markets)
        # self.tais_cache_buffer.start()

    def __drop_dependent_tai(self, simul_tais: list, df: dict, market: str) -> None:
        uncached_tais_hour = list(set(simul_tais) - set(df[market].columns))
        dependent_tai_hour = set([])
        for tai in uncached_tais_hour:
            dependent_tai_hour.update(self.qd_params[tai]['input'])

        for tai in dependent_tai_hour:
            if tai in df[market].columns:
                df[market].drop(tai, axis=1, inplace=True)

    def call_function(self, market, inputs, alias, params):
        func_name = params['function']
        # log.debug(f'###############################################################')
        # log.debug(f'CALL: {alias} - function : {func_name}')
        # log.debug(f'inputs ==> {inputs}')
        result = self.call_ta_functions(market, inputs, alias, params)
        if result is not None:
            result_target = {}
            for result_elem_key in result:
                # log.debug(f'{result_elem_key} ==> {result[result_elem_key]}')
                if result_elem_key.endswith('_raw'):
                    origin_alias = result_elem_key.replace('_raw','')
                    inputs[origin_alias] = result[result_elem_key]
                else:
                    result_target[result_elem_key] = result[result_elem_key]
            return result_target
        else:
            log.error(f'ERROR: Computation of {alias} is None. Please check the parameters or temporal values for input {inputs.keys()}')

    def call_ta_functions(self, market, inputs, alias, params):
        func_name = params['function']
        df_param = params['dataframe']
        target_market_df = inputs[df_param][market]
        input_name_list = params['input']
        param_list = params['params']

        input_list = []
        for input_name in input_name_list:
            if input_name in target_market_df.columns:
                temp_float = target_market_df[input_name].astype(float)
                input_list.append(temp_float.to_numpy())
            else:
                input_list.append(inputs[input_name])

        result_set = {}
        try:
            func = abstract.Function(func_name)
            result = func(*input_list, *param_list)  ### TALib CALL Function
        except Exception:
            # print(f'The designated function ({func_name}) does not exist in talib. Call custom function.')
            func = load_func_from_module(__package__+'.CustomTAIndicators', func_name)
            result = func(*input_list, *param_list) ### Custom CALL Function

        recent_result_set = []
        if isinstance(result, list):
            for result_elem in result:
                result_elem = np.round(result_elem, decimals=4)  ## Result round up (e.g., 3.3333333333 --> 3.3333)
                if isinstance(result_elem, (list,np.ndarray)):
                    recent_result_set.append(float(result_elem[-1]))
                else:
                    recent_result_set.append(float(result_elem))
        else:
            result = np.round(result, decimals=4)  ## Result round up (e.g., 3.3333333333 --> 3.3333)
            recent_result_set.append(float(result[-1]))

        result_set[alias] = recent_result_set
        result_set[alias+'_raw'] = result
        return result_set


class TimeframeCacheBuffer(threading.Thread):
    def __init__(self,  markets, timeframe_hours):
        super().__init__()
        self.markets = markets
        self.timeframe_hours = timeframe_hours
        self.stack_count = 0
        self._1h_timeframe_dfs = None

    def stack_data(self):
        # self._1h_timeframe_dfs = _1h_timeframe_dfs
        self.stack_count += 1
        # print(f'{self.stack_count}')

    def check_stack_count(self) -> bool:
        # self._1h_timeframe_dfs = _1h_timeframe_dfs
        return self.stack_count > 1000
        # print(f'{self.stack_count}')

    def store_csv(self, _1h_timeframe_dfs):
        # self._1h_timeframe_dfs = _1h_timeframe_dfs
        self._1h_timeframe_dfs = _1h_timeframe_dfs
        # print(f'{self.stack_count}')

    def run(self):
        DATE_KEY = 'candle_date_time_kst'
        root_dir = dirname(dirname(dirname(__file__)))
        cache_name = 'timeframe'

        while True:
            if self.stack_count > 1000:
                for timeframe_hour in self.timeframe_hours:
                    key = f'{CandleType.DAYS.name}_{timeframe_hour}'
                    print(f'{key=}')
                    for market in self.markets:
                        cache_key = f'{market}_{key}'
                        file_name = f'daily_{cache_name}_cache_base_{cache_key}.csv'
                        file_path = join(root_dir, f'./data/cache/{cache_name}/{file_name}')
                        self._1h_timeframe_dfs[key][market].drop_duplicates([DATE_KEY], keep='first', inplace=True)
                        self._1h_timeframe_dfs[key][market].to_csv(file_path, index=False)
                self.stack_count = 0
            time.sleep(10)

    def store_cache(self):
        DATE_KEY = 'candle_date_time_kst'
        root_dir = dirname(dirname(dirname(__file__)))
        cache_name = 'timeframe'
        print('시작')
        while True:
            if self.stack_count > 3:
                for timeframe_hour in self.timeframe_hours:
                    key = f'{CandleType.DAYS.name}_{timeframe_hour}'
                    for market in self.markets:
                        cache_key = f'{market}_{key}'
                        file_name = f'daily_{cache_name}_cache_base_{cache_key}.csv'
                        file_path = join(root_dir, f'./data/cache/{cache_name}/{file_name}')
                        self._1h_timeframe_dfs.drop_duplicates([DATE_KEY], keep='first', inplace=True)
                        self._1h_timeframe_dfs.to_csv(file_path, index=False)

            time.sleep(10)

    def ready_cache(self):
        pass


class TAICacheBuffer(threading.Thread):
    def __init__(self):
        super().__init__()
        self.df_min = None
        self.df_hour = None
        self.stack_count = {}
        self.min_file_path = ''
        self.hour_file_path = ''
        self.market = ''

    def init_stack_count(self, markets):
        for market in markets:
            self.stack_count[market] = 0

    def stack_data(self, market) -> None:
        # print(f'{market not in self.stack_count.keys()=}, {market=}')
        if market in self.stack_count.keys() and market != '':
            self.stack_count[market] += 1

    def is_store_time(self, market) -> bool:
        # print(f'{self.stack_count=}, {market=}')
        if self.stack_count and market != '':
            return self.stack_count[market] > 5000

    def store_csv(self, df_min: pd.DataFrame, df_hour: pd.DataFrame, min_file_path: str, hour_file_path: str, market: str) -> None:
        if self.is_store_time(market) and df_min is not None and df_hour is not None:
            df_min.fillna(0)
            df_min.sort_index(inplace=True)
            df_min.to_csv(min_file_path)

            df_hour.fillna(0)
            df_hour.sort_index(inplace=True)
            df_hour.to_csv(hour_file_path)

            self.stack_count[market] = 0

    def run(self):
        while True:
            time.sleep(10)
