import gc
import unittest
from os.path import dirname, join

import pandas as pd
import numpy as np

from bt4.Constants import QItem
from bt4.utils.memory_profiler import MemoryProfiler
from bt4.utils.stopwatch import StopWatch


class MyTestCase(unittest.TestCase) :
    def test_csv(self) :
        root_dir = dirname(dirname(dirname(__file__)))
        file_name = join(root_dir, f'data/upbit/KRW-BTC_MINUTES_3.csv')

        ############################################################
        ## pd.read_csv()
        print("pd.__version__: ", pd.__version__)

        mp = MemoryProfiler()
        sw = StopWatch()

        _1st_mem_usage = mp.keep_1st_mem_usage()
        sw.start()
        ## Read
        df = pd.read_csv(file_name, index_col = [QItem.time.value], parse_dates = True)
        print(f"read-elapsed time (sec): {sw.stop()}")

        _cur_mem_usage = mp.get_mem_usage()
        print(f"memory_usage(MB) : {_cur_mem_usage - _1st_mem_usage}")
        ## Write
        sw.start()
        df.to_csv("aa.csv")
        print(f"write-elapsed time:(sec) {sw.stop()}")

        ## Memory Release
        del df
        gc.collect()
        mp.keep_2nd_mem_usage_calc_gap()

    def test_pickle(self) :

        root_dir = dirname(dirname(dirname(__file__)))
        file_name = join(root_dir, f'data/upbit/KRW-BTC_MINUTES_3.csv')

        ############################################################
        ## pd.read_csv()
        print("pd.__version__: ", pd.__version__)
        csv_df = pd.read_csv(file_name, index_col = [QItem.time.value], parse_dates = True)
        pd.to_pickle(csv_df, "pickle.pkl")

        mp = MemoryProfiler()
        sw = StopWatch()

        _1st_mem_usage = mp.keep_1st_mem_usage()
        sw.start()
        ## Read
        pkl_df = pd.read_pickle("pickle.pkl")
        print(f"read-elapsed time (sec): {sw.stop()}")

        _cur_mem_usage = mp.get_mem_usage()
        print(f"memory_usage(MB) : {_cur_mem_usage - _1st_mem_usage}")
        ## Write
        sw.start()
        pd.to_pickle(pkl_df, "pickle1.pkl")
        print(f"write-elapsed time:(sec) {sw.stop()}")

        ## Memory Release
        del pkl_df
        gc.collect()
        mp.keep_2nd_mem_usage_calc_gap()

    def test_parquet(self) :

        root_dir = dirname(dirname(dirname(__file__)))
        file_name = join(root_dir, f'data/upbit/KRW-BTC_MINUTES_3.csv')

        ############################################################
        ## pd.read_csv()
        print("pd.__version__: ", pd.__version__)
        csv_df = pd.read_csv(file_name, index_col = [QItem.time.value], parse_dates = True)
        csv_df.to_parquet('data.parquet', engine = 'pyarrow', index = False)

        mp = MemoryProfiler()
        sw = StopWatch()

        _1st_mem_usage = mp.keep_1st_mem_usage()
        sw.start()
        ## Read
        parquet_df = pd.read_parquet('data.parquet', engine = 'pyarrow')
        print(f"read-elapsed time (sec): {sw.stop()}")

        _cur_mem_usage = mp.get_mem_usage()
        print(f"memory_usage(MB) : {_cur_mem_usage - _1st_mem_usage}")
        ## Write
        sw.start()
        parquet_df.to_parquet('data1.parquet', engine = 'pyarrow', index = False)
        print(f"write-elapsed time:(sec) {sw.stop()}")

        ## Memory Release
        del parquet_df
        gc.collect()
        mp.keep_2nd_mem_usage_calc_gap()

    def test_feather(self) :
        root_dir = dirname(dirname(dirname(__file__)))
        file_name = join(root_dir, f'data/upbit/KRW-BTC_MINUTES_3.csv')

        ############################################################
        ## pd.read_csv()
        print("pd.__version__: ", pd.__version__)
        csv_df = pd.read_csv(file_name, index_col = [QItem.time.value], parse_dates = True)
        csv_df.to_feather('data.feather')

        mp = MemoryProfiler()
        sw = StopWatch()

        _1st_mem_usage = mp.keep_1st_mem_usage()
        sw.start()
        ## Read
        feather_df = pd.read_feather('data.feather', columns=None, use_threads=True)
        print(f"read-elapsed time (sec): {sw.stop()}")

        _cur_mem_usage = mp.get_mem_usage()
        print(f"memory_usage(MB) : {_cur_mem_usage - _1st_mem_usage}")
        ## Write
        sw.start()
        feather_df.to_feather('data1.feather')
        print(f"write-elapsed time:(sec) {sw.stop()}")

        ## Memory Release
        del feather_df
        gc.collect()
        mp.keep_2nd_mem_usage_calc_gap()

    def test_csv2(self) :
        root_dir = dirname(dirname(dirname(__file__)))
        file_name = join(root_dir, f'data/upbit/KRW-BTC_MINUTES_3.csv')

        ############################################################
        ## pd.read_csv()
        print("pd.__version__: ", pd.__version__)

        mp = MemoryProfiler()
        sw = StopWatch()

        _1st_mem_usage = mp.keep_1st_mem_usage()
        sw.start()
        ## Read
        df = pd.read_csv(file_name, index_col = [QItem.time.value], parse_dates = True)
        df = self.__convert_dtype__(df)
        print(f"read-elapsed time (sec): {sw.stop()}")

        _cur_mem_usage = mp.get_mem_usage()
        print(f"memory_usage(MB) : {_cur_mem_usage - _1st_mem_usage}")
        ## Write
        sw.start()
        df.to_csv("aa2.csv")
        print(f"write-elapsed time:(sec) {sw.stop()}")

        ## Memory Release
        del df
        gc.collect()
        mp.keep_2nd_mem_usage_calc_gap()

    def test_pickle2(self) :
        root_dir = dirname(dirname(dirname(__file__)))
        file_name = join(root_dir, f'data/upbit/KRW-BTC_MINUTES_3.csv')

        ############################################################
        ## pd.read_csv()
        print("pd.__version__: ", pd.__version__)

        csv_df = pd.read_csv(file_name, index_col = [QItem.time.value], parse_dates = True)
        ## convert datatype
        csv_df = self.__convert_dtype__(csv_df)
        pd.to_pickle(csv_df, "pickle.pkl")

        mp = MemoryProfiler()
        sw = StopWatch()

        _1st_mem_usage = mp.keep_1st_mem_usage()
        sw.start()
        ## Read
        pkl_df = pd.read_pickle("pickle.pkl")
        print(f"read-elapsed time (sec): {sw.stop()}")

        _cur_mem_usage = mp.get_mem_usage()
        print(f"memory_usage(MB) : {_cur_mem_usage - _1st_mem_usage}")
        print(pkl_df.dtypes)

        ## Write
        sw.start()
        pd.to_pickle(pkl_df, "pickle2.pkl")
        print(f"write-elapsed time:(sec) {sw.stop()}")

        ## Memory Release
        del pkl_df
        gc.collect()
        mp.keep_2nd_mem_usage_calc_gap()

    def test_parquet2(self) :

        root_dir = dirname(dirname(dirname(__file__)))
        file_name = join(root_dir, f'data/upbit/KRW-BTC_MINUTES_3.csv')

        ############################################################
        ## pd.read_csv()
        print("pd.__version__: ", pd.__version__)
        csv_df = pd.read_csv(file_name, index_col = [QItem.time.value], parse_dates = True)
        csv_df = self.__convert_dtype__(csv_df)
        csv_df.to_parquet('data.parquet', engine = 'pyarrow', index = False)

        mp = MemoryProfiler()
        sw = StopWatch()

        _1st_mem_usage = mp.keep_1st_mem_usage()
        sw.start()
        ## Read
        parquet_df = pd.read_parquet('data.parquet', engine = 'pyarrow')
        print(f"read-elapsed time (sec): {sw.stop()}")

        _cur_mem_usage = mp.get_mem_usage()
        print(f"memory_usage(MB) : {_cur_mem_usage - _1st_mem_usage}")
        ## Write
        sw.start()
        parquet_df.to_parquet('data2.parquet', engine = 'pyarrow', index = False)
        print(f"write-elapsed time:(sec) {sw.stop()}")

        ## Memory Release
        del parquet_df
        gc.collect()
        mp.keep_2nd_mem_usage_calc_gap()

    def test_feather2(self) :
        root_dir = dirname(dirname(dirname(__file__)))
        file_name = join(root_dir, f'data/upbit/KRW-BTC_MINUTES_3.csv')

        ############################################################
        ## pd.read_csv()
        print("pd.__version__: ", pd.__version__)
        csv_df = pd.read_csv(file_name, index_col = [QItem.time.value], parse_dates = True)
        csv_df = self.__convert_dtype__(csv_df)
        csv_df.to_feather('data.feather')

        mp = MemoryProfiler()
        sw = StopWatch()

        _1st_mem_usage = mp.keep_1st_mem_usage()
        sw.start()
        ## Read
        feather_df = pd.read_feather('data.feather', columns=None, use_threads=True)
        print(f"read-elapsed time (sec): {sw.stop()}")

        _cur_mem_usage = mp.get_mem_usage()
        print(f"memory_usage(MB) : {_cur_mem_usage - _1st_mem_usage}")
        ## Write
        sw.start()
        feather_df.to_feather('data2.feather')
        print(f"write-elapsed time:(sec) {sw.stop()}")

        ## Memory Release
        del feather_df
        gc.collect()
        mp.keep_2nd_mem_usage_calc_gap()

    def __convert_dtype__(self, df):
        dtypes = {"market" : "category",
                 "open"   : "float32",
                 "high"   : "float32",
                 "low"    : "float32",
                 "close"  : "float32",
                 "vol"    : "float32"}

        for key, dtype in dtypes.items():
            df[key] = df[key].astype(dtype)
        return df

if __name__ == '__main__' :
    unittest.main()
