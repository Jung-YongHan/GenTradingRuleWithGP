import datetime
import os
import unittest
from multiprocessing import cpu_count
from os.path import dirname, join

import pandas as pd

from bt4.utils.pandas_utils import rename_columns, sort_df
from bt4.utils.python_utils import dt2str

def divide_period(start_pdt, end_pdt, num_of_split):
    bt_period = pd.date_range(start=start_pdt, end=end_pdt, freq='M')
    bins = pd.date_range(start=start_pdt, end=end_pdt, periods=num_of_split+1)
    results = pd.cut(bt_period, bins=bins)
    return results.categories


class MyTestCase(unittest.TestCase):

    def test_datetime2(self):
        simul_start_dt = '2018-10-01T08:59:00'
        simul_end_dt = dt2str(datetime.datetime.now())

        start_pdt = pd.to_datetime(simul_start_dt)
        end_pdt = pd.to_datetime(simul_end_dt)

        cpus = 16
        categories = divide_period(start_pdt, end_pdt, cpus-2)

        df = self.load_quote()
        print(f'loading... done : {len(df)} rows')

        for idx, category in enumerate(categories):
            left = pd.to_datetime(category.left)
            right = pd.to_datetime(category.right)
            print(f'range {idx}: {left} ~ {right}')
            df2 = df[left:right]
            print(f'ranged df : {len(df2)}')

    def load_quote(self):
        root_dir = dirname(dirname(dirname(__file__)))  ## parent of parent of directory of simulator.py
        market = 'KRW-BTC'
        data_type_name = 'MINUTES_1'
        file_name = join(root_dir, f'data{os.sep}{market}_{data_type_name}.csv')
        df = pd.read_csv(file_name, header=None)
        c_name_dic = {}
        # column_names = self.q_connector.get_column_names() # Why does not this work?
        column_names = ['market', 'candle_date_time_utc', 'candle_date_time_kst', 'opening_price', 'high_price',
                        'low_price', 'trade_price', 'timestamp', 'candle_acc_trade_price',
                        'candle_acc_trade_volume', 'unit']
        for i, cname in enumerate(column_names):
            c_name_dic[f'{i}'] = cname
            c_name_dic[i] = cname
        rename_columns(df, c_name_dic)
        sort_df(df, 'candle_date_time_kst')
        df.index = pd.to_datetime(df.index)
        return df

    def test_datetime(self):
        simul_start_dt = '2018-10-01T08:59:00'
        simul_end_dt = dt2str(datetime.datetime.now())

        start_pdt = pd.to_datetime(simul_start_dt)
        end_pdt = pd.to_datetime(simul_end_dt)

        # cpus = cpu_count()
        cpus = 16
        bt_period = pd.date_range(start=start_pdt, end=end_pdt, freq='M')
        bins = pd.date_range(start=start_pdt, end=end_pdt, periods=cpus-1)
        print(f'{bins=}')
        results = pd.cut(bt_period, bins=bins)
        print(f'{results=}')

        for idx, category in enumerate(results.categories):
            left = pd.to_datetime(category.left)
            right = pd.to_datetime(category.right)
            print(f'range {idx}: {left} ~ {right}')




if __name__ == '__main__':
    unittest.main()
