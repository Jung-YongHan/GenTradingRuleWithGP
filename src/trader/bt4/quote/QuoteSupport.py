import copy
import io
import json
import zlib
from io import StringIO

import pandas as pd
from collections import OrderedDict

import redis

from bt4.Constants import CandleType, ExType, QItem
from bt4.utils.market_utils import handle_dummy_ex
from bt4.utils.python_utils import dt2str, str2dt, dt2str_for_filename
import bt4.GlobalProperties as global_prop
from bt4.utils.stopwatch import StopWatch

pd.set_option('display.max_columns', None)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('max_colwidth', None)

class Tick:
    def __init__(self, datetime, market, open, high, low, close, volume):
        self.datetime = datetime
        self.market = market
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume

    @classmethod
    def from_dict(cls, source_dict):
        tick = Tick.__new__(Tick)
        tick.__dict__.update(source_dict)
        return tick

    @classmethod
    def from_list(self, data):
        datetime = data[0]
        market = data[1]
        open = data[2]
        high = data[3]
        low = data[4]
        close = data[5]
        volume = data[6]
        return Tick(datetime, market, open, high, low, close, volume)

    def __str__(self):
        return f'datetime: {self.datetime}, market:{self.market}, open:{self.open}, high:{self.high}, low:{self.low}, close:{self.close}, volume:{self.volume}'


candle_dic = {}

class Quote:


    def __init__(self, time_dt):
        self.time_dt = time_dt
        self.ex_quote = {}
        self.ex_market_ticks = {}
        self.redis = redis.StrictRedis(host = global_prop.QUOTE_REDIS_IP_ADDR, port = global_prop.REDIS_PORT, db = 0)

    def clean_memory(self):
        for ex_type in self.ex_quote:
            candle_data = self.ex_quote[ex_type]
            for cdl_type in candle_data :
                cdl_market_dfs = candle_data[cdl_type]
                keys = list(cdl_market_dfs.keys())
                for market in keys:
                    del cdl_market_dfs[market]

            market_ticks = self.ex_market_ticks[ex_type]
            keys = list(market_ticks.keys())
            for market in keys :
                del market_ticks[market]

    def remove_markets(self, ex_type, markets):
        candle_data = self.ex_quote[ex_type]
        for cdl_type in candle_data :
            cdl_market_dfs = candle_data[cdl_type]
            keys = list(cdl_market_dfs.keys())
            for market in keys:
                if market in markets:
                    del cdl_market_dfs[market]

        market_ticks = self.ex_market_ticks[ex_type]
        keys = list(market_ticks.keys())
        for market in keys :
            if market in markets :
                del market_ticks[market]


    def get_time(self):
        return self.time_dt

    def get_exchanges(self):
        return self.ex_quote.keys()

    def get_candle_types(self, ex_type):
        return self.ex_quote[handle_dummy_ex(ex_type)]

    def get_market_ticks(self, ex_type):
        return self.ex_market_ticks[handle_dummy_ex(ex_type)]

    def get_markets(self, ex_type):
        markets = []
        cdls = self.get_candle_types(handle_dummy_ex(ex_type))
        for cdl_type in cdls:
            for market in cdls[cdl_type]:
                markets.append(market)
            break
        return markets

    def add_quote(self, ex_type, cdl_types_n_market_dict, market_ticks):
        _ex_type = handle_dummy_ex(ex_type)
        self.ex_quote[_ex_type] = cdl_types_n_market_dict
        self.ex_market_ticks[_ex_type] = market_ticks

    def print(self):
        exchanges = self.get_exchanges()
        print(f'===' * 30)
        for ex_type in exchanges:
            cdls = self.get_candle_types(ex_type)
            for cdl_type in cdls:
                for market in cdls[cdl_type]:
                    print(f'#### {ex_type.name} {cdl_type.name}-{market}')
                    print(cdls[cdl_type][market].tail(6))
            market_ticks = self.get_market_ticks(ex_type)
            for market in market_ticks:
                print(market_ticks[market])

    def pick_market(self, ex_type, market):
        _ex_type = handle_dummy_ex(ex_type)
        new_quote = Quote(self.time_dt)
        mkt_ticks = self.get_market_ticks(_ex_type)
        pick_mkt_ticks = {}
        pick_mkt_ticks[market] = mkt_ticks[market]
        cdl_types = self.get_candle_types(_ex_type)
        new_quote.add_quote(ex_type, cdl_types, pick_mkt_ticks)
        return new_quote



    def marshal(self) -> str:
        json_data = OrderedDict()
        json_data['_time'] = dt2str(self.time_dt)
        for idx, ex_type in enumerate(self.ex_quote):
            json_data[f'{idx}._name'] = ex_type.name
            candle_data = self.ex_quote[ex_type]
            for cdl_type in candle_data:
                cdl_market_dfs = candle_data[cdl_type]
                for market in cdl_market_dfs:
                    json_data[f'{idx}.{cdl_type.name}.{market}'] = cdl_market_dfs[market].to_csv(index_label=QItem.time.value)
                    # json_data[f'{idx}.{cdl_type.name}.{market}'] = cdl_market_dfs[market].to_pickle(index_label=QItem.time.value)
            market_ticks = self.ex_market_ticks[ex_type]
            for market in market_ticks:
                market_tick = market_ticks[market]
                json_data[f'{idx}.tick.{market}'] = json.dumps(market_tick.__dict__)

        json_network_data = json.dumps(json_data)
        encoded_json = json_network_data.encode()
        compressed_data = zlib.compress(encoded_json, zlib.Z_BEST_COMPRESSION)

        return compressed_data

    @classmethod
    def unmarshal(self, compressed_json):
        encoded_json = zlib.decompress(compressed_json)
        json_message = encoded_json.decode()

        if json_message is not None:
            a_json = json.loads(json_message)
            time = str2dt(a_json['_time'])
            quote = Quote(time)

            cur_idx = -1
            cur_ex = None
            cur_market = ''
            cur_cdl_type = ''
            cdl_types_n_market_dict = {}
            market_ticks = {}
            for key in list(a_json.keys()):
                key_splitted = key.split('.')
                if len(key_splitted) == 2:  # 0._name
                    idx = int(key_splitted[0])
                    if idx != cur_idx:
                        if len(cdl_types_n_market_dict) != 0 and len(market_ticks) != 0:
                            quote.add_quote(cur_ex, cdl_types_n_market_dict, market_ticks)
                            cdl_types_n_market_dict = {}
                            market_ticks = {}
                        else:
                            cur_ex = None
                            cur_market = ''
                            cur_cdl_type = ''
                            cdl_types_n_market_dict = {}
                            market_ticks = {}
                    if key_splitted[1] == '_name':
                        cur_ex = ExType[a_json[key]]
                elif len(key_splitted) == 3: # 0.KRW-BTC.DAYS, 0.KRW-ETH.DAYS
                    cur_idx = int(key_splitted[0])
                    cur_cdl_type = key_splitted[1]
                    cur_market = key_splitted[2]
                    if cur_cdl_type == 'tick':
                        market_ticks[cur_market] = Tick.from_dict(json.loads(a_json[key]))
                    else:
                        csv_data = StringIO(a_json[key])
                        cdl_df = pd.read_csv(csv_data, index_col = [QItem.time.value], parse_dates = True)
                        candle_dic[cur_market] = cdl_df

                        cdl_df.index.name = QItem.time.value
                        cur_cdl_type = CandleType[cur_cdl_type]
                        if cur_cdl_type not in cdl_types_n_market_dict :
                            cdl_types_n_market_dict[cur_cdl_type] = {}
                        cdl_types_n_market_dict[cur_cdl_type][cur_market] = cdl_df

                        # csv_data = StringIO(a_json[key])
                        # cdl_df = pd.read_csv(csv_data, index_col=[QItem.time.value], parse_dates=True)
                        # cdl_df.index.name = QItem.time.value
                        # cur_cdl_type = CandleType[cur_cdl_type]
                        # if cur_cdl_type not in cdl_types_n_market_dict:
                        #     cdl_types_n_market_dict[cur_cdl_type] = {}
                        # cdl_types_n_market_dict[cur_cdl_type][cur_market] = cdl_df

            if len(cdl_types_n_market_dict) != 0:
                quote.add_quote(cur_ex, cdl_types_n_market_dict, market_ticks)

            return quote
        else:
            return None

    def to_redis(self) :
        redis_quote_key = "quote:candle"
        redis_ticks_key = "quote:ticks"
        sw = StopWatch()
        sw.start()

        for ex_type in self.ex_quote :
            for key in self.redis.scan_iter(f"{redis_quote_key}:{ex_type.name}:*"):
                self.redis.delete(key)

            for key in self.redis.scan_iter(f"{redis_ticks_key}:{ex_type.name}:*"):
                self.redis.delete(key)

        time_key = dt2str_for_filename(self.time_dt)

        total_size_of_candle = 0
        num_of_candle_key = 0
        size_of_candle_df = {}

        # all_ex_df_list = []
        for ex_type in self.ex_quote:
            candle_data = self.ex_quote[ex_type]
            ex_df_list_for_merge = []
            for cdl_type in candle_data:
                cdl_market_dfs = candle_data[cdl_type]
                if cdl_type not in size_of_candle_df:
                    size_of_candle_df[cdl_type] = 0
                mkt_cdl_df_list_for_merge = []
                for market in cdl_market_dfs:
                    cdl_market_dfs[market] = cdl_market_dfs[market].reset_index()
                    mkt_cdl_df_list_for_merge.append(cdl_market_dfs[market])
                cdl_merge_df = pd.concat(mkt_cdl_df_list_for_merge, ignore_index=True)
                cdl_merge_df["candle"] = cdl_type.value
                ex_df_list_for_merge.append(cdl_merge_df)
            ex_df = pd.concat(ex_df_list_for_merge, ignore_index=True)

            buffer = io.BytesIO()
            ex_df.to_pickle(buffer)
            df_binary = buffer.getvalue()
            total_size_of_candle += len(df_binary)
            num_of_candle_key += 1
            size_of_candle_df[cdl_type] += 1
            self.redis.set(f"{redis_quote_key}:{ex_type.value}:{time_key}", df_binary)
            buffer.close()

            # ex_df["ex_type"] = ex_type.value
        #     all_ex_df_list.append(ex_df)
        # all_df = pd.concat(all_ex_df_list, ignore_index=True)

        total_size_of_tick = 0
        for ex_type in self.ex_market_ticks:
            market_ticks = self.ex_market_ticks[ex_type]
            for market in market_ticks:
                market_tick = market_ticks[market]
                mkt_json_dump = json.dumps(market_tick.__dict__)
                total_size_of_tick += len(mkt_json_dump)
                self.redis.set(f"{redis_ticks_key}:{ex_type.name}:{time_key}:{market}", mkt_json_dump.encode())
                del mkt_json_dump

        elapsed_time = sw.stop()
        print(f"#### Storing REDIS {time_key} - elapsed time: {elapsed_time}, {num_of_candle_key=}, {total_size_of_candle=} bytes, {size_of_candle_df=}, {total_size_of_tick=} bytes...")
        return True

    @classmethod
    def from_redis(cls, time_dt, _redis, includes = None) :
        '''
        includes[ex_type] = [market list that must include]
        if includes is None, all quotes will be fetched.

        :param time_dt:
        :param includes:
        :return:
        '''
        redis_quote_key = "quote:candle"
        redis_ticks_key = "quote:ticks"

        quote = Quote(time_dt)
        time_key = dt2str_for_filename(time_dt)

        if includes == None:
            ex_types_from_redis = []
            for key in _redis.scan_iter(f"{redis_quote_key}:*"):
                key_tokens = key.decode().split(":")
                if len(key_tokens) == 4:  # quote:candle:upbit:2025-01-01T19_52
                    print(f"{key=}")
                    ex_types_from_redis.append(ExType(key_tokens[3]))
        else:
            ex_types_from_redis = list(includes.keys())

        for ex_type in ex_types_from_redis:

            if (ex_type not in quote.ex_quote) and \
                    ((includes is None) or ((includes is not None) and (ex_type in includes))):
                quote.ex_quote[ex_type] = {}

            key = f"{redis_quote_key}:{ex_type.value}:{time_key}"
            df_bin = _redis.get(key)
            buffer = io.BytesIO(df_bin)
            ex_df = pd.read_pickle(buffer)
            buffer.close()

            for cdl in ex_df["candle"].unique():
                cdl_type = CandleType(cdl)
                if cdl_type not in quote.ex_quote[ex_type] :
                    quote.ex_quote[ex_type][cdl_type] = {}

                cdl_merge_df = ex_df.loc[ex_df["candle"] == cdl]

                for mkt in cdl_merge_df["market"].unique():
                    if (mkt not in quote.ex_quote[ex_type][cdl_type]) and \
                            ((includes is None) or ((includes is not None) and \
                                                    ((ex_type in includes) and (mkt in includes[ex_type])))) :
                        cdl_market_df = cdl_merge_df.loc[cdl_merge_df["market"] == mkt][["index", "market", "open", "high", "low", "close", "vol"]]
                        cdl_market_df["index"] = pd.to_datetime(cdl_market_df["index"])
                        cdl_market_df = cdl_market_df.set_index(keys="index")
                        quote.ex_quote[ex_type][cdl_type][mkt] = cdl_market_df
            del ex_df

        # key: quote:ticks:{ex_type.name}:{time_key}:{market}
        for ex_type in ex_types_from_redis:
            for key in _redis.scan_iter(f"{redis_ticks_key}:{ex_type.value}:{time_key}:*"):
                if (ex_type not in quote.ex_market_ticks) and \
                        ((includes is None) or ((includes is not None) and (ex_type in includes))):
                    quote.ex_market_ticks[ex_type] = {}

                parts = key.decode().split(":")
                mkt = parts[-1]
                if (mkt not in quote.ex_market_ticks[ex_type]) and \
                        ((includes is None) or ((includes is not None) and \
                                                (ex_type in includes) and (mkt in includes[ex_type]))) :
                    json_bin = _redis.get(key)
                    quote.ex_market_ticks[ex_type][mkt] = Tick.from_dict(json.loads(json_bin.decode()))
                    del json_bin
        return quote

    # def to_redis(self) :
    #     redis_quote_key = "quote:candle"
    #     redis_ticks_key = "quote:ticks"
    #     sw = StopWatch()
    #     sw.start()
    #
    #     for key in self.redis.scan_iter(f"{redis_quote_key}:*"):
    #         self.redis.delete(key)
    #
    #     for key in self.redis.scan_iter(f"{redis_ticks_key}:*"):
    #         self.redis.delete(key)
    #
    #     time_key = dt2str_for_filename(self.time_dt)
    #
    #     total_size_of_candle = 0
    #     num_of_candle_key = 0
    #     size_of_candle_df = {}
    #     for ex_type in self.ex_quote:
    #         candle_data = self.ex_quote[ex_type]
    #         for cdl_type in candle_data:
    #             cdl_market_dfs = candle_data[cdl_type]
    #             if cdl_type not in size_of_candle_df:
    #                 size_of_candle_df[cdl_type] = 0
    #             for market in cdl_market_dfs:
    #                 buffer = io.BytesIO()
    #                 df = cdl_market_dfs[market]
    #                 df.to_pickle(buffer)
    #                 df_binary = buffer.getvalue()
    #                 total_size_of_candle += len(df_binary)
    #                 num_of_candle_key += 1
    #                 size_of_candle_df[cdl_type] += 1
    #                 self.redis.set(f"{redis_quote_key}:{time_key}:{ex_type.name}:{cdl_type.value}:{market}", df_binary)
    #                 buffer.close()
    #
    #     total_size_of_tick = 0
    #     for ex_type in self.ex_market_ticks:
    #         market_ticks = self.ex_market_ticks[ex_type]
    #         for market in market_ticks:
    #             market_tick = market_ticks[market]
    #             mkt_json_dump = json.dumps(market_tick.__dict__)
    #             total_size_of_tick += len(mkt_json_dump)
    #             self.redis.set(f"{redis_ticks_key}:{time_key}:{ex_type.name}:{market}", mkt_json_dump.encode())
    #             del mkt_json_dump
    #
    #     elapsed_time = sw.stop()
    #     print(f"#### Storing REDIS {time_key} - elapsed time: {elapsed_time}, {num_of_candle_key=}, {total_size_of_candle=} bytes, {size_of_candle_df=}, {total_size_of_tick=} bytes...")
    #     return True

    # @classmethod
    # def from_redis(cls, time_dt, _redis, includes = None) :
    #     '''
    #     includes[ex_type] = [market list that must include]
    #     if includes is None, all quotes will be fetched.
    #
    #     :param time_dt:
    #     :param includes:
    #     :return:
    #     '''
    #     redis_quote_key = "quote:candle"
    #     redis_ticks_key = "quote:ticks"
    #
    #     quote = Quote(time_dt)
    #     time_key = dt2str_for_filename(time_dt)
    #
    #     # key : quote:candle:2024-10-31T16_23:upbit:DAYS:KRW-BTC
    #     for key in _redis.scan_iter(f"{redis_quote_key}:{time_key}:*"):
    #         parts = key.decode().split(":")
    #         ex_type = ExType(parts[3])
    #         if (ex_type not in quote.ex_quote) and \
    #                 ((includes is None) or ((includes is not None) and (ex_type in includes))):
    #             quote.ex_quote[ex_type] = {}
    #
    #         cdl_type = CandleType(int(parts[4]))
    #         if cdl_type not in quote.ex_quote[ex_type]:
    #             quote.ex_quote[ex_type][cdl_type] = {}
    #
    #         mkt = parts[5]
    #         if (mkt not in quote.ex_quote[ex_type][cdl_type]) and \
    #                 ((includes is None) or ((includes is not None) and \
    #                                         ((ex_type in includes) and (mkt in includes[ex_type])))):
    #             df_bin = _redis.get(key)
    #             buffer = io.BytesIO(df_bin)
    #             quote.ex_quote[ex_type][cdl_type][mkt] = pd.read_pickle(buffer)
    #             buffer.close()
    #
    #     # key : quote:ticks:2024-10-31T16_23:upbit:KRW-BTC
    #     for key in _redis.scan_iter(f"{redis_ticks_key}:{time_key}:*"):
    #         parts = key.decode().split(":")
    #         ex_type = ExType(parts[3])
    #         if (ex_type not in quote.ex_market_ticks) and \
    #                 ((includes is None) or ((includes is not None) and (ex_type in includes))):
    #             quote.ex_market_ticks[ex_type] = {}
    #
    #         mkt = parts[4]
    #         if (mkt not in quote.ex_market_ticks[ex_type]) and \
    #                 ((includes is None) or ((includes is not None) and \
    #                                         (ex_type in includes) and (mkt in includes[ex_type]))) :
    #             json_bin = _redis.get(key)
    #             quote.ex_market_ticks[ex_type][mkt] = Tick.from_dict(json.loads(json_bin.decode()))
    #             del json_bin
    #     return quote
