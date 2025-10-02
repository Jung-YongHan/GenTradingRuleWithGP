import redis
import pandas as pd
import time
import datetime
import os
from os.path import dirname, join
import pickle
import zlib
from enum import IntEnum
import numpy as np

from bt4 import GlobalProperties

redisConn = redis.StrictRedis(host=GlobalProperties.REDIS_HOST, port=GlobalProperties.REDIS_PORT, db=0)


class DataType(IntEnum):
    DAYS = 1440
    MINUTES_1 = 1
    MINUTES_3 = 3
    MINUTES_5 = 5
    MINUTES_10 = 10
    MINUTES_15 = 15
    MINUTES_30 = 30
    HOUR = 60
    HOUR4 = 240


def merge_df(_1m_simul_dfs):
    df_all = None
    for i, market in enumerate(_1m_simul_dfs):
        market_df = _1m_simul_dfs[market]

        market_df.set_index(market_df.columns[2], inplace=True, drop=False)
        market_df = market_df.fillna(0)
        if df_all is None:
            df_all = market_df
        else:
            # handling the missing candles with inner join
            # df_all = df_all.join(market_df, how='inner', lsuffix='_left', rsuffix='_right')     ## Inner Product to remove the missing minute data in all markets

            # handling the missing candles with outer join
            df_all = df_all.join(market_df, how='outer', lsuffix='_left',
                                 rsuffix='_right')  ## Inner Product to remove the missing minute data in all markets
            # log.info(
            #     f'The loaded data has {df_all.isna().any(axis=1).sum()} Nan Rows! It is replaced by the upper row values.')
            df_all.fillna(method='ffill', inplace=True)  ## Fill Nan with Upper Rows

            for j in range(0, i + 1, 1):
                df_all.iloc[:,
                2 + (j * 11)] = df_all.index  ## Replace the KST time from the upper rows to the index kst time

    merged_dfs = []
    for i, market in enumerate(_1m_simul_dfs):
        column_start = i * 11
        time_ordered_market_df = df_all.iloc[:, [(column_start + x) for x in range(0, 11)]]
        merged_dfs.append(time_ordered_market_df.fillna(0))
        # log.debug(f'########## Loading {market} data : {len(time_ordered_market_df)} items.. Done!')

    return df_all.index.to_numpy(), merged_dfs


def sort_df(df, index_col, ascending=True):
    df.reset_index(drop=True)
    df.set_index([index_col], drop=False, inplace=True)
    df.sort_index(inplace=True, ascending=ascending)


def load_past_quote(data_type, markets):
    root_dir = dirname(dirname(dirname(__file__)))  ## parent of parent of directory of simulator.py
    print(root_dir)
    missing_market_in_files = []
    dfs = {}

    for market in markets:  # 1.
        # C:\Users\jg_hong\PycharmProjects\bt4\data\upbit\spot
        file_name = join(root_dir, f'data{os.sep}upbit{os.sep}spot{os.sep}{market}_{data_type.name}.csv')
        if os.path.isfile(file_name):  # 1.1
            df = pd.read_csv(file_name, header=None)
            print('fetching markets from ' + file_name)
            dfs[market] = df
        else:
            missing_market_in_files.append(market)

    for market in markets:
        c_name_dic = {}
        # column_names = self.q_connector.get_column_names() # Why does not this work?
        column_names = ['market', 'candle_date_time_utc', 'candle_date_time_kst', 'opening_price', 'high_price',
                        'low_price', 'trade_price', 'timestamp', 'candle_acc_trade_price',
                        'candle_acc_trade_volume', 'unit']
        for i, cname in enumerate(column_names):
            c_name_dic[f'{i}'] = cname
            c_name_dic[i] = cname
        dfs[market].rename(columns=c_name_dic, inplace=True)
        sort_df(dfs[market], 'candle_date_time_kst')
        # shift_rows_of_columns(dfs[market], ['opening_price', 'high_price',
        #    'low_price', 'trade_price', 'timestamp', 'candle_acc_trade_price', 'candle_acc_trade_volume'], 1)

    return dfs


time_list = []
markets = 'KRW-BTC KRW-ETH KRW-XRP'.split()
start = time.time()
for data_type in DataType:
    print(data_type.name)
    tmp_df = load_past_quote(data_type, markets)
    print(tmp_df)
    if data_type == DataType.MINUTES_1:
        list_of_time, _1m_time_based_merged_dfs = merge_df(tmp_df)

        listOfMarkets = [np.nan_to_num(x.to_numpy()) for x in _1m_time_based_merged_dfs]
        listOfMarkets.insert(0, list_of_time)
        print(listOfMarkets)

end = time.time()

sec = (end - start)
result = datetime.timedelta(seconds=sec)
print(result)
time_list.append(sec)
# start2 = time.time()
# for data_type in DataType:
#     print(data_type.name)
#     tmp_df = load_past_quote(data_type, markets)
#     redisConn.set(f'{data_type.name}', zlib.compress(pickle.dumps(tmp_df)))  # 시간 부여 없이 지속되는 데이터
#     print(tmp_df)
#     if data_type == DataType.MINUTES_1:
#         list_of_time, _1m_time_based_merged_dfs = merge_df(tmp_df)
#
#         listOfMarkets = [np.nan_to_num(x.to_numpy()) for x in _1m_time_based_merged_dfs]
#         listOfMarkets.insert(0, list_of_time)
#         print(listOfMarkets)
#         redisConn.set(f'listOfMarkets', zlib.compress(pickle.dumps(tmp_df)))  # 시간 부여 없이 지속되는 데이터
#
# end2 = time.time()
#
# sec2 = (end2 - start2)
# result2 = datetime.timedelta(seconds=sec2)
# print(result2)


start2 = time.time()
for data_type in DataType:
    print(data_type.name)
    tmp_df = pickle.loads(zlib.decompress(redisConn.get(f'{data_type.name}')))
    print(tmp_df)
    if data_type == DataType.MINUTES_1:
        redis_df = pickle.loads(zlib.decompress(redisConn.get(f'listOfMarkets')))
        print(redis_df)
end2 = time.time()

sec2 = (end2 - start2)
result2 = datetime.timedelta(seconds=sec2)
print(result2)
time_list.append(sec2)

for time_item in time_list:
    print(time_item)

# for

# start = time.time()
# df = pd.read_csv('C:/Users/jg_hong/PycharmProjects/bt4/data/upbit/spot/KRW-BTC_MINUTES_1.csv')
# end = time.time()
# print(df)