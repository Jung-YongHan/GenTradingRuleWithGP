# import eventlet
import ccxt
import urllib3
from ccxt import upbit

from bt4.Constants import CandleType, ExType, QItem
from bt4.quote.quote_support import MarketID
from bt4.utils.exchange_filter import ExFilterFactory
from bt4.utils.exchange_utils import bithumb_2_uniformed_mkt_ids, uniformed_2_std_mkt_id, std_2_uniformed_mkt_ids
from bt4.utils.market_utils import find_minutes_before_candles, find_minutes_before_candles2
from bt4.utils.python_utils import get_1day_before_dt, SingletonInstance, to_utc_int_timestamp, TIME_FORMAT, svr2local_dt
from bt4.utils.mylog import init_log
from bt4.utils.pandas_utils import remove_last_row
from abc import *
import time
import requests
import pandas as pd
from datetime import timedelta
import datetime
import json

from bt4.utils.python_utils import dt2str, str2dt, to_utc_time, start_timing, end_n_elapsed_time

from os.path import dirname, join
import os
from dateutil.relativedelta import relativedelta

from bt4_cfg.quote_conf import QUOTE_PARAMS

log = init_log()

read_timeout_sec = 3


class UniversalQuoteConnector(SingletonInstance):

    def __init__(self):
        self.exchanges = QUOTE_PARAMS['exchanges']
        self.connectors = {}
        self.on_cache = False
        self._1h_timeframe_dfs = {}
        self.retry = 0

    def load_cache(self, ex_type, _1h_timeframe_dfs):
        self.on_cache = True
        self._1h_timeframe_dfs[ex_type.value] = _1h_timeframe_dfs

    def get_exchanges(self):
        return self.exchanges

    def get_markets(self, ex_type):
        return QUOTE_PARAMS[ex_type]['markets']

    def get_timeframe(self, ex_type):
        return QUOTE_PARAMS[ex_type]['timeframe']

    def __create_connector__(self, ex_type):
        exchange_class = getattr(ccxt, ex_type.value)
        exchange = exchange_class()
        if ex_type == ExType.upbit:
            exchange = upbit_ex(exchange)
        return exchange

    def __get_ex_connector__(self, ex_type):
        if ex_type not in self.connectors:
            conn = self.__create_connector__(ex_type)
            self.connectors[ex_type] = conn
        return self.connectors[ex_type]

    def fetch_time(self, ex_type):
        ex = self.__get_ex_connector__(ex_type)
        return ex.fetch_time()

    def fetch_quote_num_candles(self, ex_type, markets, num_candles, cdl_type=CandleType.DAYS):
        """
        upbit   KRW-BTC -> KRW-BTC
        bithumb KRW-BTC -> BTC/KRW

        :param ex_type:
        :param markets: KRW-BTC (standardized mkt id)
        :param num_candles:
        :param cdl_type:
        :return:
        """
        conn = self.__get_ex_connector__(ex_type)

        market_dfs = {}
        num_of_candle_for_dispatching = 180
        current_num_of_candles = 0
        for market in markets:
            df = None
            to_now_dt = datetime.datetime.now()
            # to_now_dt = str2dt('2023-01-01T21:15:00')

            i = 0
            while True:
                log.debug(f'### download quote #{i} ~ {ex_type.name}: {market} - {cdl_type.name} - {to_now_dt}')
                i = i + 1

                df2 = self.fetch_tick_quote(ex_type, market, num_of_candle_for_dispatching, to_now_dt, cdl_type)

                if df2 is not None and not df2.empty:
                    if len(df2) >= num_candles:
                        df = df2
                        log.debug(f'##########{len(df2)}/{num_candles}')
                        break
                    else:
                        if df is None:
                            df = df2
                        else:
                            df = pd.concat([df, df2], axis=0)
                            if len(df) > num_candles:
                                log.debug(f'##########{len(df)}/{num_candles}')
                                break
                    # to_now_dt = str2dt(df2.index.min())  # The Query Time is UTC Time, not KST Time
                    to_be_updated_to_now_dt = pd.to_datetime(df2.index.min()).to_pydatetime()
                    if to_be_updated_to_now_dt == to_now_dt:
                        break
                    else:
                        to_now_dt = to_be_updated_to_now_dt
                else:
                    break
                time.sleep(0.3)
            df.sort_index(inplace=True, ascending=True)
            remove_last_row(df)
            df = df.loc[~df.index.duplicated(keep='first')]
            market_dfs[market] = df

        return market_dfs


    def fetch_quote_at(self, ex_type, markets, desired_dt, to_dt = None):
        log.debug(f'UniversalQuoteConnector : desired_dt : {dt2str(desired_dt)}')

        last_fetch_server_time = None
        market_dfs = pd.DataFrame()
        for i, market in enumerate(markets):
            market_df = self.fetch_tick_quote(ex_type, market, 30, to_dt, cdl_type=CandleType.MINUTES_1)

            if market_df is not None:
                desired_df = market_df.loc[market_df.index == pd.to_datetime(desired_dt)]

                if len(desired_df) == 0:
                    desired_df = find_minutes_before_candles2(market, market_df, desired_dt)

                if desired_df is None:
                    log.warning(
                        f'ERROR: Desired Quote of {market} at {dt2str(desired_dt)} does not exist in {market_df.index}')
                    continue  ## Ignore the quote data at this time.
                else:
                    market_dfs = pd.concat([market_dfs, desired_df], axis=0)

                ## Due to the quation request API is limited in 10 times a sec.
                time.sleep(0.12)
                ## So the sleep time is little bit more than 0.1.
                ## check https://docs.upbit.com/docs/user-request-guide

        return market_dfs

    def fetch_quote(self, ex_type, markets):
        pass


    def fetch_tick_quote(self, ex_type, market, count, to_dt=None, cdl_type=CandleType.DAYS):
        """

            uqc = UniversalQuoteConnector.instance()
            ccxt_df = uqc.fetch_tick_quote(ExType.upbit, market, 180, to_now_dt, CandleType.DAYS)

            svr_time = uqc.fetch_time(ExType.upbit)
            kor_dt = from_utc_int_timestamp(svr_time, True)

        :param ex_type:
        :param market:
        :param count:
        :param to_dt:
        :param cdl_type:
        :return:
        """
        exchange = self.__get_ex_connector__(ex_type)

        since_dt = None
        if to_dt is not None :
            since_dt = (pd.to_datetime(to_dt) - pd.Timedelta(minutes = cdl_type.value * count)).to_pydatetime()

        utc_int_tp = None
        if cdl_type == CandleType.DAYS:
            MAX_RETRY = 1
        elif cdl_type == CandleType.HOUR4:
            MAX_RETRY = 2
        elif cdl_type == CandleType.HOUR:
            MAX_RETRY = 5
        elif cdl_type == CandleType.MINUTES_30:
            MAX_RETRY = 10
        elif cdl_type == CandleType.MINUTES_15:
            MAX_RETRY = 20
        elif cdl_type == CandleType.MINUTES_10:
            MAX_RETRY = 30
        elif cdl_type == CandleType.MINUTES_5:
            MAX_RETRY = 60
        elif cdl_type == CandleType.MINUTES_3:
            MAX_RETRY = 100
        elif cdl_type == CandleType.MINUTES_1:
            MAX_RETRY = 300

        COUNT_RETRY = 0

        ex_filter = ExFilterFactory.instance().get(ex_type)

        try :
            while(True):
                if since_dt is not None :
                    utc_int_tp = to_utc_int_timestamp(since_dt)

                market = ex_filter.filter_market_id_before(market)
                ohlcv_list = exchange.fetch_ohlcv(market, timeframe=cdl_type.to_ccxt(), since=utc_int_tp, limit=count)
                market = ex_filter.filter_market_id_after(market)
                if ohlcv_list is not None and len(ohlcv_list) != 0:
                    df = pd.DataFrame(ohlcv_list, columns=[QItem.time.value, QItem.open.value, QItem.high.value,
                                                           QItem.low.value, QItem.close.value, QItem.vol.value])
                    df[QItem.market.value] = market
                    df = df[[QItem.time.value, QItem.market.value, QItem.open.value, QItem.high.value,
                             QItem.low.value, QItem.close.value, QItem.vol.value]]
                    df = df.sort_index(ascending=False)
                    if cdl_type == CandleType.DAYS:
                        df[QItem.time.value] = pd.to_datetime(df[QItem.time.value], unit='ms')
                        df[QItem.time.value] = df[QItem.time.value].dt.strftime(TIME_FORMAT)
                        df[QItem.time.value] = pd.to_datetime(df[QItem.time.value]) + pd.Timedelta(hours=9) # To KOR TIME
                    else:
                        df[QItem.time.value] = pd.to_datetime(df[QItem.time.value], unit='ms') + pd.Timedelta(hours=9)

                    df.set_index(QItem.time.value, inplace=True)
                    df.index.name = QItem.time.value

                    self.retry = 0
                    return df
                elif len(ohlcv_list) == 0:
                    retry_since_dt = (pd.to_datetime(since_dt) - pd.Timedelta(minutes=cdl_type.value)).to_pydatetime()
                    log.debug(f"[{market}::{cdl_type.name}] ({COUNT_RETRY}/{MAX_RETRY})th Retry to fetch quote with {retry_since_dt} adjusted from {since_dt}...")
                    since_dt = retry_since_dt
                    if COUNT_RETRY > MAX_RETRY - 1:
                        return None

                    COUNT_RETRY += 1
                    time.sleep(0.2)
                    continue

        # except urllib3.exceptions.ReadTimeoutError as rte:
        #     log.error("ReadTimeoutError Error : ", rte)
        # except ccxt.base.errors.RequestTimeout as errr:
        #     log.error("RequestTimeout Error : ", errr)
        except requests.exceptions.ReadTimeout as ertt:
            log.error("ReadTimeout Error : ", ertt)
        except requests.exceptions.Timeout as errd:
            log.error("Timeout Error : ", errd)
        except requests.exceptions.ConnectionError as errc:
            log.error("Error Connecting : ", errc)
        except requests.exceptions.HTTPError as errb:
            log.error("Http Error : ", errb)
        except requests.exceptions.RequestException as erra:
            log.error("AnyException : ", erra)
        except Exception as exp:
            log.error("Exception : ", exp)

        return self.__retry_fetch_tick_quote(ex_type, market, count, to_dt, cdl_type)

    def __retry_fetch_tick_quote(self, ex_type, market, count, to_dt, cdl_type):
        # if response.text is None or len(response.text) == 0:
        if self.retry < 3:
            self.retry = self.retry + 1
            log.warning(f'Retry to fetch {market} quote...Now it\'s {self.retry} times after sleeping 1 second.')
            time.sleep(1)  # Retry
            return self.fetch_tick_quote(ex_type, market, count, to_dt, cdl_type)
        else:
            self.retry = 0
            return None

    def extract_timeframe_quotes(self, ex_type: ExType, _1h_dfs: dict, timeframe_hours: list) -> dict:

        _1d_quotes = {}
        for timeframe_hour in timeframe_hours:
            key = f'{CandleType.DAYS.name}_{timeframe_hour}'
            key_enum = CandleType[key]
            _1d_quotes_for_timeframe = {}

            for market in _1h_dfs:
                if self.on_cache:
                    _1d_quotes_for_timeframe[market] = self.__get_timeframe_from_cache(ex_type, _1h_dfs, market, key)
                else:
                    _1d_quotes_for_timeframe[market] = self.extract_1d_quote_for_timeframe(_1h_dfs[market], timeframe_hour)

            _1d_quotes[key_enum] = _1d_quotes_for_timeframe
        return _1d_quotes

    def extract_1d_quote_for_timeframe(self, _1h_df, base_hour):
        resampled_df = _1h_df.resample('24H', origin='epoch', offset=timedelta(hours=base_hour)). \
            agg({QItem.market.value: 'first', QItem.open.value: 'first',
                 QItem.high.value: 'max', QItem.low.value: 'min',
                 QItem.close.value: 'last', QItem.vol.value: 'sum'})
        resampled_df.index.name = QItem.time.value
        return resampled_df

    def __get_timeframe_from_cache(self, ex_type, _1h_dfs, market, key):
        simul_end = _1h_dfs[market].index.max()
        simul_start = _1h_dfs[market].index.min()
        resampled_df = self._1h_timeframe_dfs[ex_type][key][market]
        try:
            return resampled_df.loc[simul_start:simul_end]
        except:
            return pd.DataFrame(columns=resampled_df.columns)

    def get_available_markets(self, ex_type):
        exchange = self.__get_ex_connector__(ex_type)
        markets_details = exchange.fetch_markets()
        markets = []
        for mkt_detail in markets_details:
            if mkt_detail["active"] == True:
                mkt_id = None
                if ex_type == ExType.upbit or ex_type == ExType.bithumb:
                    if mkt_detail["quote"] == "KRW":
                        mkt_id = MarketID(ex_type, mkt_detail["id"])
                elif ex_type == ExType.binance:
                    if mkt_detail["quote"] == "USDT" :
                        mkt_id = MarketID(ex_type, mkt_detail["id"])
                if mkt_id is not None:
                    markets.append(mkt_id.get_universal_id())
        return markets



class upbit_ex(upbit):

    def __init__(self, upbit):
        self.upbit = upbit
        super(upbit_ex, self).__init__()

    def fetch_time(self):
        try:
            url = 'https://api.upbit.com/v1/candles/minutes/1'
            querystring = {'count': 1, 'market': 'KRW-BTC'}
            headers = {'Accept': 'application/json'}
            response = requests.request("GET", url, headers=headers, params=querystring, timeout=read_timeout_sec)
            svr_time_str = response.headers['Date']
            local_svr_time_dt = svr2local_dt(svr_time_str)
            svr_time_tp = to_utc_int_timestamp(local_svr_time_dt)
            return svr_time_tp
        except requests.exceptions.Timeout as errd:
            log.error("Timeout Error : ", errd)
        except requests.exceptions.ConnectionError as errc:
            log.error("Error Connecting : ", errc)
        except requests.exceptions.HTTPError as errb:
            log.error("Http Error : ", errb)
        except requests.exceptions.RequestException as erra:
            log.error("AnyException : ", erra)
        except Exception as exp:
            log.error("Exception : ", exp)
        return -1




class QuoteConnector(metaclass=ABCMeta):

    @abstractmethod
    def get_column_names(self):
        pass

    @abstractmethod
    def fetch_quote_num_candles(self, markets, num_candles, data_type = CandleType.DAYS):
        pass

    @abstractmethod
    def fetch_quote_at(self, markets, desired_dt):
        pass

    @abstractmethod
    def fetch_quote(self, markets):
        pass

    @abstractmethod
    def fetch_tick_quote(self, market, count, start=None, data_type=CandleType.DAYS):
        pass

    @abstractmethod
    def extract_timeframe_quotes(self, _1h_dfs, timeframe_hours):
        pass

@DeprecationWarning
class UpbitQuoteConnector(QuoteConnector):
    def __init__(self):
        self.columns = ['market', 'candle_date_time_utc', 'candle_date_time_kst', 'opening_price', 'high_price',
               'low_price', 'trade_price', 'timestamp', 'candle_acc_trade_price', 'candle_acc_trade_volume', 'unit']
        self.dfs = {}
        self.retry = 0
        self._1h_timeframe_dfs = {}
        self.on_cache = False

    def get_column_names(self):
        return self.columns

    def fetch_quote_num_candles(self, markets, num_candles, data_type = CandleType.DAYS):
        market_dfs = {}
        for market in markets:
            df = None
            to_now_dt = datetime.datetime.now()

            i = 0
            while True:
                log.debug(f'### i:{i}')
                i = i + 1

                _, _, df2 = self.fetch_tick_quote(market, num_candles, to_now_dt, data_type)

                if df2 is not None and not df2.empty:
                    if len(df2) >= num_candles:
                        df = df2
                        log.debug(f'##########{len(df2)}/{num_candles}')
                        break
                    else:
                        if df is None:
                            df = df2
                        else:
                            df = pd.concat([df, df2], axis=0)
                            if len(df) > num_candles:
                                log.debug(f'##########{len(df)}/{num_candles}')
                                break
                    to_now_dt = str2dt(df2['candle_date_time_kst'].min()) #The Query Time is UTC Time, not KST Time
                else:
                    break
                time.sleep(0.3)
            df = self.__filter_out_1d_specific_columns(df, data_type)
            df.set_index(keys=['candle_date_time_kst'], drop=False, inplace=True)
            df.sort_index(inplace=True, ascending=True)
            self.__filter_out_last_candle__(df, data_type)
            # shift_rows_of_columns(df, ['opening_price', 'high_price',
            #                             'low_price', 'trade_price', 'timestamp', 'candle_acc_trade_price',
            #                             'candle_acc_trade_volume'], 1)
            market_dfs[market] = df
        return market_dfs

    def __filter_out_1d_specific_columns(self, df, data_type):
        if 'prev_closing_price' in df.columns:  # the columns only exists in Day
            df = df.drop(['prev_closing_price', 'change_price', 'change_rate'], axis=1)  # remove columns to match unit1
            df['unit'] = data_type.value
        return df

    def __filter_out_last_candle__(self, df, data_type):
        last_time_str = df.iloc[-1]['candle_date_time_kst']
        range_start = str2dt(last_time_str)
        # if data_type == DataType.DAYS:
        peroid = timedelta(days=1)
        if data_type == CandleType.HOUR4:
            peroid = timedelta(hours=4)
        elif data_type == CandleType.HOUR:
            peroid = timedelta(hours=1)

        range_end_dt = range_start - timedelta(minutes=1) + peroid
        now = datetime.datetime.now()

        if  range_start < now and now <= range_end_dt:
            remove_last_row(df)

    def fetch_quote_at0(self, market, desired_dt, to_dt=None):
        kst_time = dt2str(datetime.datetime.now())

        all_market_json_string = '''[{"market": "KRW-BTC", "candle_date_time_utc": "2022-02-03T05:25:00",
          "candle_date_time_kst": "'''+kst_time + '''", "opening_price": 45659000.00000000,
          "high_price": 45659000.00000000, "low_price": 45659000.00000000, "trade_price": 45659000.00000000,
          "timestamp": 1643865902843, "candle_acc_trade_price": 1191390.33198000, "candle_acc_trade_volume": 0.02609322,
          "unit": 1},
          {"market": "KRW-ETH", "candle_date_time_utc": "2022-02-03T05:25:00",
          "candle_date_time_kst": "'''+kst_time + '''", "opening_price": 3280000.00000000,
          "high_price": 3280000.00000000, "low_price": 3280000.00000000, "trade_price": 3280000.00000000,
          "timestamp": 1643865902901, "candle_acc_trade_price": 107999.96960000, "candle_acc_trade_volume": 0.03292682,
          "unit": 1},
        {"market": "KRW-XRP", "candle_date_time_utc": "2022-02-03T05:25:00",
          "candle_date_time_kst": "'''+kst_time + '''", "opening_price": 745.00000000, "high_price": 745.00000000,
          "low_price": 744.00000000, "trade_price": 745.00000000, "timestamp": 1643865903356,
          "candle_acc_trade_price": 1033052.19889640, "candle_acc_trade_volume": 1387.98952872, "unit": 1}]'''

        # all_market_json_string = '''[
        # {"market": "KRW-XRP", "candle_date_time_utc": "2022-02-03T05:25:00",
        #   "candle_date_time_kst": "'''+kst_time + '''", "opening_price": 745.00000000, "high_price": 745.00000000,
        #   "low_price": 744.00000000, "trade_price": 745.00000000, "timestamp": 1643865903356,
        #   "candle_acc_trade_price": 1033052.19889640, "candle_acc_trade_volume": 1387.98952872, "unit": 1}]'''

        # return all_market_json_string, kst_time
        # return None, kst_time
        return None, None

    def fetch_quote_at(self, markets, desired_dt, to_dt=None):
        log.debug(f'UpbitQuoteConnector: desired_dt : {dt2str(desired_dt)}')

        all_market_json_string = '['
        last_fetch_server_time = None
        for i, market in enumerate(markets):
            json_data, svr_time, dataframe = self.fetch_tick_quote(market, 5, to_dt, data_type=CandleType.MINUTES_1)
            pd.DataFrame()
            if i == len(markets) - 1:
                last_fetch_server_time = svr_time
            if json_data is not None:
                desired_df = dataframe[dataframe['candle_date_time_kst'] == dt2str(desired_dt)]

                if len(desired_df) == 0:
                    desired_df = find_minutes_before_candles(dataframe, desired_dt)

                if desired_df is None:
                    log.warning(f'ERROR: Desired Quote of {market} at {dt2str(desired_dt)} does not exist in {dataframe.candle_date_time_kst}')
                    continue   ## Ignore the quote data at this time.
                else:
                    json_data = desired_df.iloc[0].to_json()
                    all_market_json_string = all_market_json_string + json_data + ','

                ## Due to the quation request API is limited in 10 times a sec.
                time.sleep(0.12)
                ## So the sleep time is little bit more than 0.1.
                ## check https://docs.upbit.com/docs/user-request-guide

        all_market_json_string = all_market_json_string[0:-1] + ']'
        return all_market_json_string, last_fetch_server_time

    def fetch_quote(self, markets):
        all_market_json_string = '['
        last_fetch_server_time = None
        for i, market in enumerate(markets):
            json_data, svr_time, dataframe = self.fetch_tick_quote(market, count=5, data_type=CandleType.MINUTES_1)
            pd.DataFrame()
            if i == len(markets) - 1:
                last_fetch_server_time = svr_time

            if json_data is not None:
                # json_data = pd.DataFrame(dataframe.iloc[-1]).to_json()   # For fetching the recent(not most recent) quote data.  if cur time 15:18:00, get 15:17 for getting the recent close.
                json_data = dataframe.iloc[-1].to_json()
                all_market_json_string = all_market_json_string + json_data + ','

                ## Due to the quation request API is limited in 10 times a sec.
                time.sleep(0.12)
                ## So the sleep time is little bit more than 0.1.
                ## check https://docs.upbit.com/docs/user-request-guide

        all_market_json_string = all_market_json_string[0:-1] + ']'
        return all_market_json_string, last_fetch_server_time

    def __retry_fetch_tick_quote(self, market, count, to_dt, data_type):
        # if response.text is None or len(response.text) == 0:
        if self.retry < 10:
            self.retry = self.retry + 1
            log.warning(f'Retry to fetch {market} quote...Now it\'s {self.retry} times after sleeping 1 second.')
            time.sleep(1)  # Retry
            return self.fetch_tick_quote(market, count, to_dt, data_type)
        else:
            self.retry = 0
            return None, None, None

    def fetch_tick_quote(self, market, count, to_dt = None, data_type = CandleType.DAYS):
        url = self.__get_url_for__(data_type)

        querystring = {"count": count, "market": market}

        if to_dt != None:
            utc_dt = to_utc_time(to_dt)
            querystring["to"] = dt2str(utc_dt) + 'Z'

        try:
            headers = {"Accept": "application/json"}
            response = requests.request("GET", url, headers=headers, params=querystring, timeout=read_timeout_sec)
            # response = request2("GET", url, strict_timeout = read_timeout_sec, headers=headers, params=querystring)

            # if data_type == DataType.MINUTES_1:       # For Debugging
            #     raise eventlet.Timeout('Eventlet TIMEOUT!! On PURPOSE!!')
            log.debug(response.text)
            if response.text != None and len(response.text) != 0:
                if response.text != 'Too many API requests.' and response.text != '502 Bad Gateway':
                    a_json = json.loads(response.text)
                    dataframe = pd.DataFrame.from_records(a_json)

                    dataframe = self.__filter_out_1d_specific_columns(dataframe, data_type)
                    self.retry = 0
                    return response.text, response.headers['Date'], dataframe
        # except eventlet.Timeout as te:
        #     print(f'Eventlet.Timeout Exception: the request does not executed within {str(te)} sec.')
        except requests.exceptions.Timeout as errd:
            log.error("Timeout Error : ", errd)
        except requests.exceptions.ConnectionError as errc:
            log.error("Error Connecting : ", errc)
        except requests.exceptions.HTTPError as errb:
            log.error("Http Error : ", errb)
        except requests.exceptions.RequestException as erra:
            log.error("AnyException : ", erra)
        except Exception as exp:
            log.error("Exception : ", exp)

        return self.__retry_fetch_tick_quote(market, count, to_dt, data_type)

    '''
    _1d_quotes = 
        {
            'DAY_7': {KRW-BTC, KRW-ETH, KRW-XRP}
            'DAY_8': {KRW-BTC, KRW-ETH, KRW-XRP}
            ...
        }
    '''
    def extract_timeframe_quotes(self, _1h_dfs: dict, timeframe_hours: list) -> dict:

        if self.on_cache and not self._1h_timeframe_dfs:
            self.__ready_cache(list(_1h_dfs.keys()), timeframe_hours)

        _1d_quotes = {}
        for timeframe_hour in timeframe_hours:
            key = f'{CandleType.DAYS.name}_{timeframe_hour}'
            key_enum = CandleType[key]
            _1d_quotes_for_timeframe = {}

            for market in _1h_dfs:
                if self.on_cache:
                    _1d_quotes_for_timeframe[market] = self.__get_timeframe_from_cache(_1h_dfs, market, key)
                else:
                    _1d_quotes_for_timeframe[market] = []

                if len(_1d_quotes_for_timeframe[market]) < 20:
                    resampled_df = self._extract_1d_quote_for_timeframe_in_upbit(_1h_dfs[market], timeframe_hour)
                    _1d_quotes_for_timeframe[market] = resampled_df

                    if self.on_cache:
                        self.__write_cache_timeframe(resampled_df, market, timeframe_hour)

            _1d_quotes[key_enum] = _1d_quotes_for_timeframe
        return _1d_quotes

    def _extract_1d_quote_for_timeframe_in_upbit(self, _1h_df, base_hour):
        _1h_df.set_index(['candle_date_time_kst'], inplace=True, drop=False)
        temp_df = _1h_df[self.columns]
        temp_df.index = pd.to_datetime(_1h_df.index)
        resampled_df = temp_df.resample('24H', origin='epoch', offset=timedelta(hours=base_hour)). \
            agg(
            {'market': 'first', 'candle_date_time_utc': 'first', 'candle_date_time_kst': 'first',
             'opening_price': 'first',
             'high_price': 'max', 'low_price': 'min', 'trade_price': 'last', 'timestamp': 'first',
             'candle_acc_trade_price': 'sum', 'candle_acc_trade_volume': 'sum', 'unit': 'first'})
        return resampled_df

    def __get_url_for__(self, data_type):
        if data_type == CandleType.DAYS:
            url = "https://api.upbit.com/v1/candles/days"
        else:
            url = "https://api.upbit.com/v1/candles/minutes/" + str(data_type.value)

        return url

    def __ready_cache(self, markets: list, timeframe_hours: list) -> None:
        root_dir = dirname(dirname(dirname(__file__)))
        DATE_KEY = 'candle_date_time_kst'

        def read_cache_timeframe(cache_name: str, markets: list) -> dict:
            _1d_quotes = {}
            for timeframe_hour in timeframe_hours:
                key = f'{CandleType.DAYS.name}_{timeframe_hour}'
                _1d_quotes_for_timeframe = {}
                for market in markets:
                    cache_key = f'{market}_{key}'
                    file_name = f'daily_{cache_name}_cache_base_{cache_key}.csv'
                    file_path = join(root_dir, f'./data/cache/{cache_name}/{file_name}')
                    if os.path.isfile(file_path):
                        resampled_df = pd.read_csv(file_path)
                        resampled_df.index = resampled_df[DATE_KEY]
                        _1d_quotes_for_timeframe[market] = resampled_df
                    else:
                        log.warning(f'[{cache_name}] {file_name} 캐시 데이터가 없습니다.')
                        _1d_quotes_for_timeframe[market] = pd.DataFrame()
                _1d_quotes[key] = _1d_quotes_for_timeframe
            return _1d_quotes

        cache_name_str = 'timeframe'
        cache_file_path = join(root_dir, f'./data/cache/{cache_name_str}')
        if not os.path.exists(cache_file_path):
            os.makedirs(cache_file_path)

        self._1h_timeframe_dfs = read_cache_timeframe(cache_name_str, markets)
        # self.buffer = CacheBuffer(markets, timeframe_hours)
        # self.buffer.start()


    def __get_timeframe_from_cache(self, _1h_dfs: dict, market: list, key: str) -> pd.DataFrame:
        simul_end_str = _1h_dfs[market].iloc[-1]['candle_date_time_kst']
        simul_end_dt = get_1day_before_dt(str2dt(simul_end_str))
        simul_start_dt = simul_end_dt - relativedelta(days=20)
        simul_start_str = dt2str(simul_start_dt)
        simul_end_str = dt2str(simul_end_dt)
        resampled_df = self._1h_timeframe_dfs[key][market]
        try:
            return resampled_df.loc[simul_start_str:simul_end_str]
        except:
            return pd.DataFrame(columns=self.columns)

    def __write_cache_timeframe(self, resampled_df: pd.DataFrame, market: str, timeframe_hour: str) -> None:
        DATE_KEY = 'candle_date_time_kst'
        root_dir = dirname(dirname(dirname(__file__)))
        cache_name = 'timeframe'
        # todo 저장할 때만 사용할 수 있도록 변경
        key = f'{CandleType.DAYS.name}_{timeframe_hour}'
        cache_key = f'{market}_{key}'
        file_name = f'daily_{cache_name}_cache_base_{cache_key}.csv'
        file_path = join(root_dir, f'./data/cache/{cache_name}/{file_name}')

        temp_1h_timeframe = self._1h_timeframe_dfs[key][market]
        if not temp_1h_timeframe.empty:
            if timeframe_hour != str2dt(temp_1h_timeframe.iloc[0][DATE_KEY]).hour \
                    or timeframe_hour != str2dt(resampled_df.iloc[-1][DATE_KEY]).hour:
                return

        # start = start_timing()
        self._1h_timeframe_dfs[key][market] = pd.concat([temp_1h_timeframe, resampled_df.iloc[1:]])
        # print(end_n_elapsed_time(start, 'pd.concat'))

        # start = start_timing()
        self._1h_timeframe_dfs[key][market].drop_duplicates([DATE_KEY], keep='first', inplace=True)
        # print(end_n_elapsed_time(start, 'pd.drop_duplicates'))
        # todo 저장 버퍼 - 따로 스레드를 빼서 진행되도록 한다.
        #  또한 에러가 없도록 한다.
        # if len(self._1h_timeframe_dfs[key][market]) % 200 == 0:
        self._1h_timeframe_dfs[key][market].to_csv(file_path, index=False)
        # self.buffer.stack_data(self._1h_timeframe_dfs)
