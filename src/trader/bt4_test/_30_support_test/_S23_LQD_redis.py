import os
import sys
import unittest
import redis
import pandas as pd
import time
import datetime
import pickle
import zlib

from bt4.Constants import CandleType, QItem
from bt4.quote.QuoteMgr import QuoteStorageMgr


class CustomTestCase(unittest.TestCase):

    def setUp(self):
        """테스트 시작되기 전 파일 작성"""
        self.rds = redis.StrictRedis(host='localhost', port=6379, db=0)

    def tearDown(self):
        """테스트 종료 후 파일 삭제 """
        self.rds.close()

    def test_candle(self):
        for candle in CandleType:
            print(candle)

    def test_store_candle(self):
        # 테이터 읽어오기
        markets: list = 'KRW-BTC KRW-ETH KRW-XRP'.split()
        start: datetime.datetime
        end: datetime.datetime
        cdl_types_needed: list = [CandleType.DAYS, CandleType.HOUR]
        exchange: str = 'upbit_spot'

        REDIS_EXIST: int = 1
        REDIS_NONE: int = 0

        # redis에서 key를 통해 데이터 확인 후 없을 경우 데이터 저장 과정 진행
        for market in markets:
            for cdl_type in cdl_types_needed:
                # key = f'{exchange}:{cdl_type.name}:{market}'
                key = f'{exchange}:{cdl_type.name}'
                if self.rds.hexists(key, market) == REDIS_NONE:
                    # todo timeframe의 경우 존재하지 않을 때 전체 기간의 해당 타임프레임 데이터를 생성하고 저장하도록 구현
                    print(f'key: {key} 은/는 캐시 DB에 없습니다. 초기 데이터를 저장합니다.')

                    path_parts = exchange.split('_')
                    candle_path = f"../data/{path_parts[0]}/{path_parts[1]}/{market}_{cdl_type.name}.csv"
                    print(f'경로: {candle_path}로 데이터를 읽습니다.')

                    col_list = 'market,candle_date_time_utc,candle_date_time_kst,opening_price,high_price,low_price,trade_price,timestamp,candle_acc_trade_price,candle_acc_trade_volume,unit'.split(',')
                    df = pd.read_csv(candle_path)
                    df.columns = col_list
                    # print(df)

                    zip_df = zlib.compress(pickle.dumps(df))
                    self.rds.hset(key, '201810', zip_df)  # todo 추후 월별로 변경되도록 구성
                    # self.rds.set(key, zip_df)

                else:
                    print(f'key: {key} 이/가 존재합니다. 데이터를 캐시 DB에서 읽어옵니다.')
                    df = pickle.loads(zlib.decompress(self.rds.hget(key, '20181001')))
                    print(df)
        # 마켓별 캔들 데이터 읽어오기

    def test_init_QS(self):
        # markets: list = ['KRW-BTC', 'KRW-ETH', 'KRW-XRP']
        markets: list = ['KRW-BTC', 'KRW-ETH']
        markets: list = ['KRW-BTC']
        cdl_types_needed: list = [CandleType.DAYS, CandleType.HOUR]
        QuoteStorageMgr(markets, cdl_types_needed)

        markets: list = ['KRW-ETH']
        QuoteStorageMgr(markets, cdl_types_needed)

        markets: list = ['KRW-XRP']
        QuoteStorageMgr(markets, cdl_types_needed)

    def test_load_quote_in_range(self):
        markets: list = ['KRW-BTC', 'KRW-ETH', 'KRW-XRP']
        cdl_types_needed: list = [CandleType.DAYS, CandleType.HOUR]

        simul_start_dt = datetime.datetime(2023, 1, 1, 8, 59, 0)
        cdl_type = CandleType.MINUTES_1

        self.simul_storage = QuoteStorageMgr(markets, cdl_types_needed)

        num_back_candles = 200
        self.simul_storage.load_quote_in_range(markets, simul_start_dt, num_back_candles, cdl_type)

        simul_range_end_dt = datetime.datetime(2023, 1, 30, 8, 59, 0)
        self.simul_storage.load_quote_in_range2(markets, simul_start_dt, simul_range_end_dt, cdl_type)


if __name__ == '__main__':
    unittest.main()