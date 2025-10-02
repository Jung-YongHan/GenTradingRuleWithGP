import time
import unittest
from os.path import dirname, join

import objgraph

from bt4.Constants import QItem
from bt4.utils.memory_profiler import MemoryProfiler
import sys

import gc
import os.path

import psutil
import sys

import pandas as pd

from memory_profiler import profile

class MyTestCase(unittest.TestCase) :
    def test_sws_day_hdg_asym_vol_memory_profiling(self) :
        mp = MemoryProfiler()
        mp.take_1st_snapshot()
        sys.argv = ['BullTraderMain', 'backtestor', '-conf', 'bt3_config.upbit.sws_day_hdg_asym_vol']
        import bt4.exec.BullTraderMain as bm
        ctx, result_file = bm.main(sys.argv)
        mp.take_2nd_snapshot_and_show_topN()

    def test_sws_day_hdg_asym_vol_memory_usage(self) :
        mp = MemoryProfiler()
        sys.argv = ['BullTraderMain', 'backtestor', '-conf', 'bt3_config.upbit.sws_day_hdg_asym_vol']
        import bt4.exec.BullTraderMain as bm
        ctx, result_file = bm.main(sys.argv)
        mp.show_top5_current_memory_usage()

    def test_sws_day_hdg_asym_vol_memory_usage(self) :
        mp = MemoryProfiler()
        sys.argv = ['BullTraderMain', 'backtestor', '-conf', 'bt3_config.upbit.sws_day_hdg_asym_vol']
        import bt4.exec.BullTraderMain as bm
        ctx, result_file = bm.main(sys.argv)
        mp.print_mem_usage()

    def test_pandas_read_csv_memory_leak(self):

        root_dir = dirname(dirname(dirname(__file__)))
        file_name = join(root_dir, f'data/upbit/KRW-BTC_MINUTES_15.csv')


        print("pd.__version__: ", pd.__version__)


        memory_before_read = psutil.Process().memory_info().rss / 1024 ** 2
        print("memory_before_read: ", memory_before_read)

        df = pd.read_csv(file_name, index_col = [QItem.time.value], parse_dates = True)

        print("df.shape: ", df.shape)
        df.info()
        memory_after_read = psutil.Process().memory_info().rss / 1024 ** 2
        print("memory_after_read: ", memory_after_read)

        objgraph.show_refs([df], filename = 'df-graph.png')
        del df

        gc.collect()

        # objgraph.show_refs([df], filename = 'df-graph2.png')

        df = pd.DataFrame()


        memory_after_gc = psutil.Process().memory_info().rss / 1024 ** 2
        print("memory_after_gc: ", memory_after_gc)
        print("memory leak: ", memory_after_gc - memory_before_read)

        if len(gc.garbage) > 0 :
            # Inspect the output of the garbage collector
            print("-" * 120)
            print("ERROR: gc.garbage:")
            print("-" * 120)
            print(gc.garbage)
            print()

    def test_modin_read_csv_memory_leak(self):
        import modin.pandas as mpd

        root_dir = dirname(dirname(dirname(__file__)))
        file_name = join(root_dir, f'data/upbit/KRW-BTC_MINUTES_15.csv')

        print("pd.__version__: ", mpd.__version__)


        memory_before_read = psutil.Process().memory_info().rss / 1024 ** 2
        print("memory_before_read: ", memory_before_read)

        df = mpd.read_csv(file_name, index_col = [QItem.time.value], parse_dates = True)

        print("df.shape: ", df.shape)
        df.info()
        memory_after_read = psutil.Process().memory_info().rss / 1024 ** 2
        print("memory_after_read: ", memory_after_read)

        objgraph.show_refs([df], filename = 'df-graph.png')
        del df

        gc.collect()

        # objgraph.show_refs([df], filename = 'df-graph2.png')

        df = pd.DataFrame()


        memory_after_gc = psutil.Process().memory_info().rss / 1024 ** 2
        print("memory_after_gc: ", memory_after_gc)
        print("memory leak: ", memory_after_gc - memory_before_read)

        if len(gc.garbage) > 0 :
            # Inspect the output of the garbage collector
            print("-" * 120)
            print("ERROR: gc.garbage:")
            print("-" * 120)
            print(gc.garbage)
            print()

    def test_pandas_read_pickle_memory_leak(self):


        root_dir = dirname(dirname(dirname(__file__)))
        file_name = join(root_dir, f'data/upbit/KRW-BTC_MINUTES_15.csv')
        csv_df = pd.read_csv(file_name, index_col = [QItem.time.value], parse_dates = True)

        pickle_file_name = "BTC_MINUTES_15.pickle"
        csv_df.to_pickle(pickle_file_name)

        print("pd.__version__: ", pd.__version__)

        memory_before_read = psutil.Process().memory_info().rss / 1024 ** 2
        print("memory_before_read: ", memory_before_read)

        # df = pd.read_csv(file_name, index_col = [QItem.time.value], parse_dates = True)
        df = pd.read_pickle(pickle_file_name)

        print("df.shape: ", df.shape)
        df.info()
        memory_after_read = psutil.Process().memory_info().rss / 1024 ** 2
        print("memory_after_read: ", memory_after_read)

        objgraph.show_refs([df], filename = 'df-graph.png')
        del df

        gc.collect()

        # objgraph.show_refs([df], filename = 'df-graph2.png')

        df = pd.DataFrame()


        memory_after_gc = psutil.Process().memory_info().rss / 1024 ** 2
        print("memory_after_gc: ", memory_after_gc)
        print("memory leak: ", memory_after_gc - memory_before_read)

        if len(gc.garbage) > 0 :
            # Inspect the output of the garbage collector
            print("-" * 120)
            print("ERROR: gc.garbage:")
            print("-" * 120)
            print(gc.garbage)
            print()

    def test_pandas_read_feather_memory_leak(self):

        root_dir = dirname(dirname(dirname(__file__)))
        file_name = join(root_dir, f'data/upbit/KRW-BTC_MINUTES_15.csv')
        csv_df = pd.read_csv(file_name, index_col = [QItem.time.value], parse_dates = True)

        feather_file_name = "BTC_MINUTES_15.feather"
        csv_df.to_feather(feather_file_name)

        print("pd.__version__: ", pd.__version__)

        memory_before_read = psutil.Process().memory_info().rss / 1024 ** 2
        print("memory_before_read: ", memory_before_read)

        # df = pd.read_csv(file_name, index_col = [QItem.time.value], parse_dates = True)
        df = pd.read_feather(feather_file_name)

        print("df.shape: ", df.shape)
        df.info()
        memory_after_read = psutil.Process().memory_info().rss / 1024 ** 2
        print("memory_after_read: ", memory_after_read)

        objgraph.show_refs([df], filename = 'df-graph.png')
        del df

        time.sleep(5)
        gc.collect()

        # objgraph.show_refs([df], filename = 'df-graph2.png')

        df = pd.DataFrame()


        memory_after_gc = psutil.Process().memory_info().rss / 1024 ** 2
        print("memory_after_gc: ", memory_after_gc)
        print("memory leak: ", memory_after_gc - memory_before_read)

        if len(gc.garbage) > 0 :
            # Inspect the output of the garbage collector
            print("-" * 120)
            print("ERROR: gc.garbage:")
            print("-" * 120)
            print(gc.garbage)
            print()








if __name__ == '__main__' :
    unittest.main()
