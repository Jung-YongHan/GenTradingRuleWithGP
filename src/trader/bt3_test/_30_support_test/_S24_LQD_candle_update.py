import unittest
import redis
import pandas as pd
import time
import datetime
import pickle
import zlib

from bt4.Constants import CandleType, ExType
from bt4.quote.QuoteMgr import QuoteStorageMgr
from bt4.quote.QuoteConnector import UniversalQuoteConnector

from multiprocessing import cpu_count
from multiprocessing.pool import ThreadPool
import math

class CustomTestCase(unittest.TestCase):

    def setUp(self):
        """테스트 시작되기 전 파일 작성"""
        self.rds = redis.StrictRedis(host='localhost', port=6379, db=0)
        self.uq_connector = UniversalQuoteConnector.instance()

    def tearDown(self):
        """테스트 종료 후 파일 삭제 """
        self.rds.close()

    def fetch_candle(self, args):
        ex_type = args[0]
        market = args[1]
        num_of_candle = args[2]
        now_dt = args[3]
        candle_type = args[4]
        end_dt = args[5]

        delta = now_dt - end_dt  # 두 datetime 객체 간의 차이
        minute_diff = math.ceil(delta.total_seconds() / candle_type.value / 60) # 차이를 분 단위로 변환
        iter_num = math.ceil(minute_diff / num_of_candle)

        total_df = None
        for i in range(iter_num):
            print(f'{market}의 {candle_type.name} - {i+1}번째 수집({200*(i+1)}/{minute_diff})')
            df = self.uq_connector.fetch_tick_quote(ex_type, market, num_of_candle, now_dt,candle_type)
            if total_df is not None:
                total_df = pd.concat([total_df, df])
            else:
                total_df = df
            now_dt = now_dt - datetime.timedelta(minutes = num_of_candle * candle_type.value)
        return (total_df, market, candle_type)

    def download_parallel(self, args) -> dict:
        cpus = cpu_count()
        cpus = 10
        pool = ThreadPool(cpus - 1)
        results = pool.imap_unordered(self.fetch_candle, args)
        pool.close()
        pool.join()

        dfs = {}
        for result in results:
            print('df:', result[0], 'market:', result[1], 'candle_type:', result[2])
            result[0].to_csv(f"../data/upbit/{result[1]}_{result[2].name}.csv")
        return dfs

    # @unittest.skip('Tested')
    def test_multi_fetch(self):
        # markets = 'KRW-BTC KRW-ETH KRW-XRP KRW-KAVA KRW-SOL KRW-WAVES'.split()
        needed_cdl_type = [CandleType.DAYS, CandleType.HOUR, CandleType.HOUR4, CandleType.MINUTES_1, CandleType.MINUTES_3]
        markets = ['KRW-BTC', 'KRW-ETH', 'KRW-NEO', 'KRW-MTL', 'KRW-XRP', 'KRW-ETC', 'KRW-SNT', 'KRW-WAVES', 'KRW-XEM', 'KRW-QTUM', 'KRW-LSK', 'KRW-STEEM', 'KRW-XLM', 'KRW-ARDR', 'KRW-ARK', 'KRW-STORJ', 'KRW-GRS', 'KRW-ADA', 'KRW-SBD', 'KRW-POWR', 'KRW-BTG', 'KRW-ICX', 'KRW-EOS', 'KRW-TRX', 'KRW-SC', 'KRW-ONT', 'KRW-ZIL', 'KRW-POLYX', 'KRW-ZRX', 'KRW-LOOM', 'KRW-BCH', 'KRW-BAT', 'KRW-IOST', 'KRW-RFR', 'KRW-CVC', 'KRW-IQ', 'KRW-IOTA', 'KRW-HIFI', 'KRW-ONG', 'KRW-GAS', 'KRW-UPP', 'KRW-ELF', 'KRW-KNC', 'KRW-BSV', 'KRW-THETA', 'KRW-QKC', 'KRW-BTT', 'KRW-MOC', 'KRW-ENJ', 'KRW-TFUEL', 'KRW-MANA', 'KRW-ANKR', 'KRW-AERGO', 'KRW-ATOM', 'KRW-TT', 'KRW-CRE', 'KRW-MBL', 'KRW-WAXP', 'KRW-HBAR', 'KRW-MED', 'KRW-MLK', 'KRW-STPT', 'KRW-ORBS', 'KRW-VET', 'KRW-CHZ', 'KRW-STMX', 'KRW-DKA', 'KRW-HIVE', 'KRW-KAVA', 'KRW-AHT', 'KRW-LINK', 'KRW-XTZ', 'KRW-BORA', 'KRW-JST', 'KRW-CRO', 'KRW-TON', 'KRW-SXP', 'KRW-HUNT', 'KRW-PLA', 'KRW-DOT', 'KRW-MVL', 'KRW-STRAX', 'KRW-AQT', 'KRW-GLM', 'KRW-SSX', 'KRW-META', 'KRW-FCT2', 'KRW-CBK', 'KRW-SAND', 'KRW-HPO', 'KRW-DOGE', 'KRW-STRK', 'KRW-PUNDIX', 'KRW-FLOW', 'KRW-DAWN', 'KRW-AXS', 'KRW-STX', 'KRW-XEC', 'KRW-SOL', 'KRW-MATIC', 'KRW-AAVE', 'KRW-1INCH', 'KRW-ALGO', 'KRW-NEAR', 'KRW-AVAX', 'KRW-T', 'KRW-CELO', 'KRW-GMT', 'KRW-APT', 'KRW-SHIB', 'KRW-MASK', 'KRW-ARB', 'KRW-EGLD', 'KRW-SUI', 'KRW-GRT', 'KRW-BLUR', 'KRW-IMX', 'KRW-SEI']
        # markets = ['KRW-SEI']
        # needed_cdl_type = [CandleType.MINUTES_1]

        ex_type = ExType.upbit
        num_of_candle_for_dispatching = 200
        end_dt = datetime.datetime(2023, 11, 5, 9, 0, 0)
        # end_dt = datetime.datetime(2023, 8, 17, 9, 0, 0)

        task = []
        to_now_dt = datetime.datetime.now()
        for market in markets:
            for candle_type in needed_cdl_type:
                task.append((ex_type, market, num_of_candle_for_dispatching, to_now_dt, candle_type, end_dt))
        self.download_parallel(task)

    @unittest.skip('Tested')
    def test_store_candle(self):
        # 테이터 읽어오기
        markets: list = 'KRW-BTC KRW-ETH KRW-XRP'.split()
        start: datetime.datetime
        end: datetime.datetime
        cdl_types_needed: list = [CandleType.DAYS, CandleType.HOUR]
        exchange: str = 'upbit'

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

    @unittest.skip('Tested')
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

    def test_load_stored_quote(self):
        markets = 'KRW-BTC KRW-ETH KRW-XRP'.split()

        ex_type = ExType.upbit
        needed_cdl_type = [CandleType.DAYS,
                           CandleType.HOUR,
                           CandleType.HOUR4,
                           CandleType.MINUTES_1,
                           CandleType.MINUTES_3,
                           CandleType.MINUTES_5,
                           CandleType.MINUTES_15,
                           CandleType.MINUTES_30,
                           ]

        total_dfs = QuoteStorageMgr(markets, needed_cdl_type).load_stored_quote(ex_type)

        print(total_dfs)


if __name__ == '__main__':
    unittest.main()