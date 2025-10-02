import unittest
from datetime import timedelta
from os.path import dirname, join

import pandas as pd
import numpy as np

from bulltrader.utils.pandas_utils import rename_columns, sort_df

pd.set_option('display.max_columns', None)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('max_colwidth', None)

def extract_1d_quote_for_timeframe_in_upbit(_1h_df, base_hour):
    temp_df = _1h_df[['market', 'candle_date_time_utc', 'candle_date_time_kst', 'opening_price', 'high_price', 'low_price',
         'trade_price', 'timestamp', 'candle_acc_trade_price', 'candle_acc_trade_volume', 'unit']]
    temp_df.index = pd.to_datetime(_1h_df.index)

    resampled_df = temp_df.resample('24H', origin='epoch', offset=timedelta(hours=base_hour)). \
        agg(
        {'market': 'first', 'candle_date_time_utc': 'first', 'candle_date_time_kst': 'first', 'opening_price': 'first',
         'high_price': 'max', 'low_price': 'min', 'trade_price': 'last', 'timestamp': 'first',
         'candle_acc_trade_price': 'sum', 'candle_acc_trade_volume': 'sum', 'unit': 'first'})
    print(resampled_df.tail(20))

    return resampled_df




class MyTestCase(unittest.TestCase):

    def test_pandas_resample2(self):
        root_dir = dirname(dirname(dirname(__file__)))
        # btc_1h_csv = join(root_dir, './data/KRW-BTC_HOUR.csv')
        btc_1h_csv = '1h_df.csv'

        btc_1h_df = pd.read_csv(btc_1h_csv, header=None)

        columns = ['market', 'candle_date_time_utc', 'candle_date_time_kst', 'opening_price', 'high_price',
                   'low_price', 'trade_price', 'timestamp', 'candle_acc_trade_price', 'candle_acc_trade_volume', 'unit']

        old_new_col_name_dic = {}
        for i, column in enumerate(columns):
            old_new_col_name_dic[i] = column

        # btc_1h_df.loc[:, 1] = btc_1h_df.loc[:, 1].str.strip()
        # btc_1h_df.loc[:, 2] = btc_1h_df.loc[:, 2].str.strip()

        rename_columns(btc_1h_df, old_new_col_name_dic)
        btc_1h_df.set_index(['candle_date_time_kst'], inplace=True, drop=False)
        # btc_1h_df = btc_1h_df.reset_index()
        # btc_1h_df.set_index(['candle_date_time_kst'], inplace=True, drop=False)
        # btc_1h_df.index = pd.to_datetime(btc_1h_df.index)
        btc_1h_df.index = pd.to_datetime(btc_1h_df.index)

        print(f'index type:{type(btc_1h_df.index)}')
        print(f'columns:{btc_1h_df.columns}')
        print(f'index:{btc_1h_df.index}')
        print(btc_1h_df.tail(20))

        sort_df(btc_1h_df, 'candle_date_time_kst')
        my_base = 8

        resampled_df = extract_1d_quote_for_timeframe_in_upbit(btc_1h_df, my_base)

        # temp_df = btc_1h_df[
        #     ['market', 'candle_date_time_utc', 'candle_date_time_kst', 'opening_price', 'high_price', 'low_price', 'trade_price',
        #                           'timestamp', 'candle_acc_trade_price', 'candle_acc_trade_volume', 'unit']]
        # temp_df.index = pd.to_datetime(btc_1h_df.index)
        #
        # resampled_df = temp_df.resample('24H', origin='epoch', offset=timedelta(hours=my_base)).\
        #     agg({'market': 'first', 'candle_date_time_utc':'first', 'candle_date_time_kst': 'first', 'opening_price': 'first',
        #          'high_price': 'max', 'low_price': 'min', 'trade_price': 'last', 'timestamp': 'first',
        #          'candle_acc_trade_price': 'sum', 'candle_acc_trade_volume': 'sum', 'unit' : 'first'})
        print(resampled_df.tail(20))


        # temp_df = btc_1h_df[['market', 'candle_date_time_utc', 'opening_price', 'high_price', 'low_price', 'trade_price',
        #                      'timestamp', 'candle_acc_trade_price', 'candle_acc_trade_volume', 'unit']]
        # temp_df['candle_date_time_kst'] = btc_1h_df.index
        # # temp_df.reset_index()
        # temp_df.index = pd.to_datetime(temp_df.index)
        # print(f'index type:{type(temp_df.index)}')
        # print(f'columns:{temp_df.columns}')
        # print(f'index:{temp_df.index}')
        #
        # resampled_df = temp_df.resample('24H', origin='epoch', offset=timedelta(hours=my_base)). \
        #     agg({'market': 'first', 'candle_date_time_utc':'first', 'candle_date_time_kst': 'first', 'opening_price': 'first',
        #          'high_price': 'max', 'low_price': 'min', 'trade_price': 'last', 'timestamp': 'first',
        #          'candle_acc_trade_price': 'sum', 'candle_acc_trade_volume': 'sum', 'unit' : 'first'})
        # print(resampled_df.tail(20))



    def test_pandas_resample(self):
        range = pd.date_range('2020-12-20', '2020-12-25', freq='60min')
        my_size = 100
        df = pd.DataFrame(index=range)[:my_size]
        np.random.seed(seed=1004)  # for reproducibility
        df['price'] = np.random.randint(low=10, high=100, size=my_size)
        df['amount'] = np.random.randint(low=1, high=5, size=my_size)
        print('Shape of df DataFrame:', df.shape)

        print(df.tail(my_size))
        df.to_csv('price_amount.csv')
        df_summary = pd.DataFrame()
        # interval = '10T'
        interval = '24H'
        df_summary['price_24H_first'] = df.settled_price.resample(interval).first()
        df_summary['price_24H_last'] = df.settled_price.resample(interval).last()
        df_summary['amount_24H_first'] = df.amount.resample(interval).first()
        df_summary['amount_24H_last'] = df.amount.resample(interval).last()
        print('---------------------------------------')
        print(df_summary.tail(my_size))

        my_base = 10
        resampled_df = df.resample('24H', base=my_base).agg({'price': 'first', 'amount': 'sum'})
        print(resampled_df.tail(my_size))

        my_base = 10
        resampled_df = df.resample('24H', origin='start', offset=timedelta(hours=my_base)).agg({'price': 'first', 'amount': 'sum'})
        print(resampled_df.tail(my_size))

        my_base = 11
        resampled_df = df.resample('24H', base=my_base).agg({'price': 'first', 'amount': 'sum'})
        print(resampled_df.tail(my_size))

        # df = get_ohlcv(ticker, interval="minute60")
        # df = df.resample('24H', base=base).agg(
        #     {'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'})



if __name__ == '__main__':
    unittest.main()
