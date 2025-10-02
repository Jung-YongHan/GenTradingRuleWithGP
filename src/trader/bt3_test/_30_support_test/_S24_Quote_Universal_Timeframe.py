import os
import sys
import unittest
import redis
import pandas as pd
import time
import datetime
import pickle
import zlib

from bt4.Constants import CandleType, QItem, ExType
from bt4.quote.QuoteConnector import UniversalQuoteConnector
from bt4.quote.QuoteMgr import QuoteStorageMgr
from bt3_config.quote_conf import QUOTE_PARAMS


class CustomTestCase(unittest.TestCase):

    def setUp(self):
        """테스트 시작되기 전 파일 작성"""
        self.rds = redis.StrictRedis(host='localhost', port=6379, db=0)

    def tearDown(self):
        """테스트 종료 후 파일 삭제 """
        self.rds.close()

    def test_timeframe_creation(self):
        self.markets = ['KRW-BTC']
        self.start_pdt = datetime.datetime(2022, 1, 1, 8, 59, 0)
        self.end_pdt = datetime.datetime(2023, 1, 1, 8, 59, 0)

        self.ex_type = QUOTE_PARAMS['exchange']
        self.markets = QUOTE_PARAMS[self.ex_type]['markets']
        self.cdl_types_needed = QUOTE_PARAMS[self.ex_type]['cdl_types_needed']
        self.uq_connector = UniversalQuoteConnector.instance()
        self.timeframe_hours = [x for x in range(0, 24)]

        tmp_dict = {}
        key = f'{ExType.upbit.value}:{CandleType.HOUR.name}:KRW-BTC'
        print(key)
        df_1h = pickle.loads(zlib.decompress(self.rds.hget(key, '201810')))
        # df_1h = pd.read_csv('C:/Users/jg_hong/PycharmProjects/bulltrader3/data/upbit/KRW-BTC_MINUTES_1.csv')
        tmp_dict['KRW-BTC'] = df_1h
        # todo 전체 기간의 타임프레임을 생성하고 저장하도록
        result = self.uq_connector.extract_timeframe_quotes(self.ex_type, tmp_dict, self.timeframe_hours)
        print(result)
