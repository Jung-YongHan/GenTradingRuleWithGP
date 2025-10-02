import gc
import io
import os
import sys
import unittest
import redis
import pandas as pd
import time
import datetime
import pickle
import zlib

from bt4.Constants import QItem, ExType, CandleType
from bt4.utils.memory_profiler import MemoryProfiler
from bt4.utils.python_utils import now_dt, dt2str, dt2str_for_filename


class CustomTestCase(unittest.TestCase):

    def setUp(self):
        """테스트 시작되기 전 파일 작성"""
        self.rds = redis.StrictRedis(host='localhost', port=6379, db=0)

    def tearDown(self):
        """테스트 종료 후 파일 삭제 """
        self.rds.close()

    @unittest.skip('Tested')
    def test_redis_connection(self):
        self.rds.set("a", "aaaaaa")  # 레디스에 키-값 저장
        print(self.rds.get("a"))  # 레디스에서 키를 사용해서 값 가져오기

    @unittest.skip('Tested')
    def test_store_string_to_redis(self):
        start = time.time()
        self.df = pd.read_csv('/data/upbit/KRW-BTC_MINUTES_1.csv')
        end = time.time()
        sec = (end - start)
        result = datetime.timedelta(seconds=sec)
        print('read csv file time:', result)

        zip_df = zlib.compress(pickle.dumps(self.df))
        zip_df_size = sys.getsizeof(zip_df)
        print('check file size:', zip_df_size)

        # Set
        EXPIRATION_SECONDS = 600
        self.rds.setex("key", EXPIRATION_SECONDS, zlib.compress(pickle.dumps(self.df)))  # 데이터의 시간 부여 - 세션으로 활용 가능

        start_redis = time.time()
        self.rds.set("df:string", zlib.compress(pickle.dumps(self.df)))  # 시간 부여 없이 지속되는 데이터
        end_redis = time.time()

        sec_redis = (end_redis - start_redis)
        result_redis = datetime.timedelta(seconds=sec_redis)
        print('redis df:string store time:', result_redis)

        start_redis = time.time()
        self.rds.hset("df:hash", '1', zlib.compress(pickle.dumps(self.df)))  # 시간 부여 없이 지속되는 데이터
        end_redis = time.time()
        sec_redis = (end_redis - start_redis)
        result_redis = datetime.timedelta(seconds=sec_redis)
        print('redis df:hash store time:', result_redis)

        start_redis = time.time()
        # Get
        redis_df = pickle.loads(zlib.decompress(self.rds.get("df:string")))
        # redis_df = pd.read_msgpack(redis_conn.get("btc_day_df"))
        end_redis = time.time()

        # print(redis_df)

        sec_redis = (end_redis - start_redis)
        result_redis = datetime.timedelta(seconds=sec_redis)
        print('redis df:string read time:', result_redis)

        start_redis = time.time()
        # Get
        redis_df = pickle.loads(zlib.decompress(self.rds.hget("df:hash", '1')))
        # redis_df = pd.read_msgpack(redis_conn.get("btc_day_df"))
        end_redis = time.time()

        # print(redis_df)

        sec_redis = (end_redis - start_redis)
        result_redis = datetime.timedelta(seconds=sec_redis)
        print('redis df:hash read time:',result_redis)

        # result_list = str(datetime.timedelta(seconds=sec)).split(".")
        # print(result_list[0])

    @unittest.skip('Tested')
    def test_direct_redis_lib(self):  # 성능이 좋지 않아 사용하지 않음
        from direct_redis import DirectRedis
        r = DirectRedis(host='localhost', port=6379)

        start = time.time()
        df = pd.read_csv('/data/upbit/KRW-BTC_MINUTES_1.csv')
        end = time.time()
        print(df)

        r.set('df', df)

        start_redis = time.time()
        # Get
        tmp = r.get('df')
        # redis_df = pd.read_msgpack(redis_conn.get("btc_day_df"))
        end_redis = time.time()

        print(tmp)
        sec = (end - start)
        result = datetime.timedelta(seconds=sec)
        print(result)

        sec_redis = (end_redis - start_redis)
        result_redis = datetime.timedelta(seconds=sec_redis)
        print(result_redis)

    def test_delete_all(self):
        self.rds.flushdb()

    @unittest.skip('Tested')
    def test_redis_key_check(self):
        print(self.rds.exists("df:string"))
        print(self.rds.exists("df:hash"))
        if self.rds.exists("df:hash"):  # 숫자로 0 또는 1을 반환하기 때문에
            print("df:hash 없음")

    @unittest.skip('Tested')
    def test_redis_write_perf_by_zip(self):
        start = time.time()
        self.df = pd.read_csv('/data/upbit/KRW-BTC_MINUTES_1.csv')
        end = time.time()

        sec = (end - start)
        result = datetime.timedelta(seconds=sec)
        print('read csv file time:', result)

        start_redis = time.time()
        zip_df = zlib.compress(pickle.dumps(self.df))
        zip_df_size = sys.getsizeof(zip_df)
        print('check file size:', zip_df_size)

        self.rds.set("df:zip_df", zlib.compress(pickle.dumps(self.df)))  # 시간 부여 없이 지속되는 데이터
        end_redis = time.time()

        sec_redis = (end_redis - start_redis)
        result_redis = datetime.timedelta(seconds=sec_redis)
        print('redis df:zip_df store time:', result_redis)

        #####################################################################

        start_redis = time.time()
        df = pickle.dumps(self.df)
        df_size = sys.getsizeof(df)
        print('check file size:', df_size)

        self.rds.set("df:original", zlib.compress(pickle.dumps(self.df)))  # 시간 부여 없이 지속되는 데이터
        end_redis = time.time()

        sec_redis = (end_redis - start_redis)
        result_redis = datetime.timedelta(seconds=sec_redis)
        print('redis df:original store time:', result_redis)

        ####################################################################



        start_redis = time.time()
        df = pickle.dumps(self.df)
        df_size = sys.getsizeof(df)
        print('check file size:', df_size)

        self.rds.hset("df:hash_original", '1', pickle.dumps(self.df))  # 시간 부여 없이 지속되는 데이터
        end_redis = time.time()

        sec_redis = (end_redis - start_redis)
        result_redis = datetime.timedelta(seconds=sec_redis)
        print('redis df:hash_original store time:', result_redis)

        ####################################################################

        start_redis = time.time()
        df = pickle.dumps(self.df)
        df_size = sys.getsizeof(df)
        print('check file size:', df_size)

        self.rds.hset("df:hash_zip", '1', zlib.compress(pickle.dumps(self.df)))  # 시간 부여 없이 지속되는 데이터
        end_redis = time.time()

        sec_redis = (end_redis - start_redis)
        result_redis = datetime.timedelta(seconds=sec_redis)
        print('redis df:hash_zip store time:', result_redis)

    @unittest.skip('Tested')
    def test_redis_read_perf_by_zip(self):
        start_redis = time.time()
        redis_df = pickle.loads(zlib.decompress(self.rds.get("df:zip_df"))) # 시간 부여 없이 지속되는 데이터
        print('check file size:', redis_df)
        end_redis = time.time()

        sec_redis = (end_redis - start_redis)
        result_redis = datetime.timedelta(seconds=sec_redis)
        print('redis df:zip_df read time:', result_redis)

        #####################################################################

        start_redis = time.time()
        # print(self.rds.exists("df:original"))
        # print(self.rds.get("df:original"))
        redis_df = pickle.loads(zlib.decompress(self.rds.get("df:original")))
        print('check file size:', redis_df)
        end_redis = time.time()

        sec_redis = (end_redis - start_redis)
        result_redis = datetime.timedelta(seconds=sec_redis)
        print('redis df:original store time:', result_redis)

        #####################################################################

        start_redis = time.time()
        # print(self.rds.exists("df:original"))
        # print(self.rds.get("df:original"))
        redis_df = pickle.loads(self.rds.hget("df:hash_original", '1'))
        print('check file size:', redis_df)
        end_redis = time.time()

        sec_redis = (end_redis - start_redis)
        result_redis = datetime.timedelta(seconds=sec_redis)
        print('redis df:hash_original store time:', result_redis)

        #####################################################################

        start_redis = time.time()
        # print(self.rds.exists("df:original"))
        # print(self.rds.get("df:original"))
        redis_df = pickle.loads(zlib.decompress(self.rds.hget("df:hash_zip", '1')))
        print('check file size:', redis_df)
        end_redis = time.time()

        sec_redis = (end_redis - start_redis)
        result_redis = datetime.timedelta(seconds=sec_redis)
        print('redis df:hash_zip store time:', result_redis)

    def test_redis_delete(self):

        candles = {CandleType.DAYS, CandleType.HOUR4, CandleType.HOUR}
        markets = [f"{x}_mkt" for x in range(0, 120)]
        df = pd.read_csv("KRW-BTC_MINUTES_1.csv", index_col = 0)
        df = df.iloc[:300]

        for col in df.columns:
            print(f"{col} : {df[col].dtype} =>", end="")
            if col == "market":
                df[col] = df[col].astype("category")
            else:
                df[col] = df[col].astype("float64")
            print(df[col].dtype)

        self.mem_profiler = MemoryProfiler()
        self.mem_profiler.take_1st_snapshot()

        count = 0
        while True:
            now_time = dt2str_for_filename(now_dt())

            print(f"{count} : {now_time}")
            for key in self.rds.scan_iter("quote:candle:*"):
                self.rds.delete(key)

            for cdl in candles:
                for mkt in markets:
                    buffer = io.BytesIO()
                    df.to_pickle(buffer)
                    df_binary = buffer.getvalue()
                    self.rds.set(f"quote:candle:{now_time}:{cdl.name}:{mkt}", df_binary)
                    buffer.close()

            for cdl in candles:
                for mkt in markets :
                    df_bin = self.rds.get(f"quote:candle:{now_time}:{cdl.name}:{mkt}")
                    buffer = io.BytesIO(df_bin)
                    df = pd.read_pickle(buffer)
                    buffer.close()

            self.mem_profiler.take_2nd_snapshot_and_show_topN(40)
            self.mem_profiler.print_mem_usage()
            gc.collect()

            if count > 100:
                break
            else:
                count += 1

            time.sleep(1)



    @unittest.skip('Tested')
    def test_enum(self):
        for ex_type in ExType:
            print(ex_type.name)
            print(ex_type.value)


if __name__ == '__main__':
    unittest.main()
