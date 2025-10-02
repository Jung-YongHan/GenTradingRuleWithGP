import unittest

import json
import pandas as pd
from bt4.quote.ExchangeQuoteDispatcher import ExchangeQuoteDispatcher
from bt4.quote.QuoteConnector import UpbitQuoteConnector, UniversalQuoteConnector
from bt4.utils.market_utils import is_update_time
from bt4.utils.mylog import init_log
import bt4.utils.mylog as log_module
from bt4.Constants import QUOTE_MODE, CandleType, ExType, QItem
import time

from bt4.utils.pandas_utils import remove_last_row, append_new_row
from bt4.utils.python_utils import svr2local_dt, get_1min_before_dt, get_1min_after_dt, create_dt_at, \
    from_utc_int_timestamp
from bt3_config.quote_conf import QUOTE_PARAMS
from bt3_test._30_support_test._S22_LocalQuoteDispatcherTest import TestQuoteReceiver

pd.set_option('display.max_columns', None)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('max_colwidth', None)

from bt4.utils.python_utils import dt2str

log_module.log_mode = 'quote'
log = init_log()

## TODO: 지우고 Append할수 있도록 코드 변경
## 22.01.16(stkim) 이렇게 해야 df의 index까지 모두 새로운것으로 업데이트됨
def update_min_quote(dfs, _1m_quote_dfs):
    for market in dfs:
        remove_last_row(dfs[market])

        to_be_updated = _1m_quote_dfs[_1m_quote_dfs.market == market].iloc[-1]
        to_be_updated.name = to_be_updated.candle_date_time_kst
        # update_last_row(dfs[market], to_be_updated)
        dfs[market] = append_new_row(dfs[market], to_be_updated, True)


class MyTestCase(unittest.TestCase):

    def test_execute_multiple_ex_quote_dispatcher(self):
        eqd = ExchangeQuoteDispatcher(QUOTE_MODE.SELF)
        exchanges = QUOTE_PARAMS['exchanges']
        for ex in exchanges:
            eqd.addQuoteListener(TestQuoteReceiver(ex))

        eqd.process_quote()

    def test_update_last_row(self):
        uqc = UniversalQuoteConnector.instance()
        exchange = ExType.upbit
        markets = ['KRW-BTC']
        last_svr_time_tp = uqc.fetch_time(exchange)
        if last_svr_time_tp is not None:
            svr_korea_dt = from_utc_int_timestamp(last_svr_time_tp, True)
        desired_dt = get_1min_before_dt(svr_korea_dt, True)
        _1m_quote_dfs = uqc.fetch_quote_at(exchange, markets, desired_dt)

        _day_runtime_dfs = uqc.fetch_quote_num_candles(exchange, markets, 100, cdl_type=CandleType.DAYS)

        market = 'KRW-BTC'
        btc_df = _day_runtime_dfs[market]
        print('before update ##############################')
        print(btc_df.tail(5))
        if _1m_quote_dfs[QItem.market.value].isin([market]).any():
            _1m_market_df = _1m_quote_dfs[_1m_quote_dfs.market == market]
            remove_last_row(_day_runtime_dfs[market])
            last_row_df = _1m_quote_dfs[_1m_market_df.index == _1m_market_df.index.max()]
            _day_runtime_dfs[market] = pd.concat([_day_runtime_dfs[market], last_row_df], axis=0)


        print('after update ##############################')
        btc_df = _day_runtime_dfs[market]
        print(btc_df.tail(5))

    @unittest.skip("Tested")
    def test_execute_exchange_quote_disptacher(self):
        eqd = ExchangeQuoteDispatcher(QUOTE_MODE.SELF)
        eqd.process_quote()

    @unittest.skip("Tested")
    def test_compute_prev_candle_time(self):
        eqd = ExchangeQuoteDispatcher(QUOTE_MODE.SELF)

        dt1 = create_dt_at(2022, 1, 13, 16, 59, 0)
        prev_candle_dt = eqd.compute_prev_candle_dt(dt1, CandleType.HOUR)
        print(f'{CandleType.HOUR.value}:{dt2str(dt1)} ==> {dt2str(prev_candle_dt)}')

        dt1 = create_dt_at(2022, 1, 13, 16, 58, 0)
        prev_candle_dt = eqd.compute_prev_candle_dt(dt1, CandleType.HOUR)
        print(f'{CandleType.HOUR.value}:{dt2str(dt1)} ==> {dt2str(prev_candle_dt)}')

        dt1 = create_dt_at(2022, 1, 13, 16, 58, 0)
        prev_candle_dt = eqd.compute_prev_candle_dt(dt1, CandleType.HOUR4)
        print(f'{CandleType.HOUR4.value}:{dt2str(dt1)} ==> {dt2str(prev_candle_dt)}')

        dt1 = create_dt_at(2022, 1, 13, 16, 59, 0)
        prev_candle_dt = eqd.compute_prev_candle_dt(dt1, CandleType.HOUR4)
        print(f'{CandleType.HOUR4.value}:{dt2str(dt1)} ==> {dt2str(prev_candle_dt)}')


        dt1 = create_dt_at(2022, 1, 12, 0, 58, 0)
        prev_candle_dt = eqd.compute_prev_candle_dt(dt1, CandleType.HOUR4)
        print(f'{CandleType.HOUR4.value}:{dt2str(dt1)} ==> {dt2str(prev_candle_dt)}')

        dt1 = create_dt_at(2022, 1, 12, 0, 59, 0)
        prev_candle_dt = eqd.compute_prev_candle_dt(dt1, CandleType.HOUR4)
        print(f'{CandleType.HOUR4.value}:{dt2str(dt1)} ==> {dt2str(prev_candle_dt)}')

        dt1 = create_dt_at(2022, 1, 13, 0, 59, 0)
        prev_candle_dt = eqd.compute_prev_candle_dt(dt1, CandleType.DAYS)
        print(f'{CandleType.DAYS.value}:{dt2str(dt1)} ==> {dt2str(prev_candle_dt)}')

        dt1 = create_dt_at(2022, 1, 13, 8, 58, 0)
        prev_candle_dt = eqd.compute_prev_candle_dt(dt1, CandleType.DAYS)
        print(f'{CandleType.DAYS.value}:{dt2str(dt1)} ==> {dt2str(prev_candle_dt)}')

        dt1 = create_dt_at(2022, 1, 13, 8, 59, 0)
        prev_candle_dt = eqd.compute_prev_candle_dt(dt1, CandleType.DAYS)
        print(f'{CandleType.DAYS.value}:{dt2str(dt1)} ==> {dt2str(prev_candle_dt)}')


    def test_attach_1m_into_1d(self):
        q_connector = UpbitQuoteConnector()
        markets = ['KRW-BTC', 'KRW-ETH', 'KRW-XRP']

        _1d_dfs = q_connector.fetch_quote_num_candles(markets, 60, data_type = CandleType.DAYS)
        for key in _1d_dfs:
            print(_1d_dfs[key].head(1).market)
            # print(_1d_dfs[key].head(5).candle_date_time_kst)
            print(_1d_dfs[key].tail(5).candle_date_time_kst)

        # svr_time_dt = create_dt_at(2022, 1, 24, 9, 2, 0)    # Server Fetching Time
        # desired_dt = create_dt_at(2022, 1, 24, 9, 1, 0)     # Quote that we want to get

        svr_time_dt = create_dt_at(2022, 1, 17, 4, 19, 0)    # Server Fetching Time
        desired_dt = create_dt_at(2022, 1, 17, 4, 12, 0)     # Quote that we want to get (XRP Data is missing)

        # svr_time_dt = create_dt_at(2022, 1, 17, 4, 18, 0)    # Server Fetching Time
        # desired_dt = create_dt_at(2022, 1, 17, 4, 17, 0)     # Quote that we want to get

        json_string, svr_time = q_connector.fetch_quote_at(markets, desired_dt, svr_time_dt)
        a_json = json.loads(json_string)
        _1m_quote_dfs = pd.DataFrame.from_records(a_json)
        is_day_update_time, is_4h_update_time, is_1h_update_time = is_update_time(desired_dt)

        update_min_quote(_1d_dfs, _1m_quote_dfs)

        for key in _1d_dfs:
            print(_1d_dfs[key].head(1).market)
            print(_1d_dfs[key].tail(5))


    @unittest.skip("Tested")
    def test_fetch_all_KRW_market_of_1minute(self):
        q_connector = UpbitQuoteConnector()
        markets = ['KRW-BTC', 'KRW-ETH', 'KRW-XRP']

        dfs = q_connector.fetch_quote_num_candles(markets, 60, data_type = CandleType.DAYS)
        for key in dfs:
            print(dfs[key].head(1).market)
            print(dfs[key].head(5).candle_date_time_kst)
            print(dfs[key].tail(5).candle_date_time_kst)

        _4h_dfs = q_connector.fetch_quote_num_candles(markets, 4 * 60, data_type=CandleType.HOUR4)
        for key in _4h_dfs:
            print(_4h_dfs[key].head(1).market)
            print(_4h_dfs[key].head(5).candle_date_time_kst)
            print(_4h_dfs[key].tail(5).candle_date_time_kst)

        _1h_dfs = q_connector.fetch_quote_num_candles(markets, 20 * 24, data_type=CandleType.HOUR)
        for key in _1h_dfs:
            print(_1h_dfs[key].head(1).market)
            print(_1h_dfs[key].head(5).candle_date_time_kst)
            print(_1h_dfs[key].tail(5).candle_date_time_kst)

    @unittest.skip("Tested")
    def test_fetch_current_market_ticks_for_each_1_minute(self):
        q_connector = UpbitQuoteConnector()
        markets = ['KRW-BTC', 'KRW-ETH', 'KRW-XRP']
        json_string, last_svr_time = q_connector.fetch_quote(markets)
        korea_dt = svr2local_dt(last_svr_time)

        while True:
            start = time.time()
            _1min_before_korea_dt = get_1min_before_dt(korea_dt, True)
            json_string, last_svr_time = q_connector.fetch_quote_at(markets, _1min_before_korea_dt)
            if last_svr_time is not None:
                korea_dt = svr2local_dt(last_svr_time)
                svr_sec = korea_dt.second

                #######################################################
                a_json = json.loads(json_string)
                all_quote_df = pd.DataFrame.from_records(a_json)
                print(all_quote_df.head(10))

                ########################################################
                sleep_time = 62.0 - svr_sec
                print(f'svr time:{last_svr_time}, svr_sec : {svr_sec} and korea time: {dt2str(korea_dt)}')
                print(f'sleep for {sleep_time} sec. to fetch quote and dispatch it to strategies...')
                if sleep_time < 0:
                    sleep_time = 1
                time.sleep(sleep_time)
                korea_dt = get_1min_after_dt(korea_dt)
            else:
                time.sleep(60)


    @unittest.skip("Tested")
    def test_fetch_current_market_ticks(self):
        q_connector = UpbitQuoteConnector()
        markets = ['KRW-BTC', 'KRW-ETH', 'KRW-XRP']
        json_string, last_svr_time = q_connector.fetch_quote(markets)
        print(last_svr_time)
        print(json_string)



        ## Ticker를 사용한 현재 시세 정보, 하나의 Request에 100개 정도의 시장 정보를 가져옴
        ## 문제: 1일봉을 기반으로 하고 있으며, OHL은 당일의 OHL을 의미하고, C는 Request당시의 당시의 현재 가격을 의미
        ## 장점: 현재 가격이 초단위로 정확함 한번에 100개의 Request를 대체가능함,
        ##  단점, OHL을 당일의 OHL이라 정확히는 분봉이 아님
        ## Volume은 하루종일의 Volume을 의미함.
        # [['KRW-BTC' '2021-09-01T07:43:45' '2021-09-01T16:43:45' 55228000.0
        #   55228000.0 54538000.0 55160000.0 1630482225000 186997392636.81082
        # 3397.30196975 55230000.0 -70000.0 -0.0012674271]]

        ## Pyupbit을 사용한 1분봉 정보 -> Simulation은 이데이터를 활용함, 하나의 Request당 하나의 시장 정보만 가져옴
        ## 100개의 데이터를 분석하기 위해서는 100번의 호출이 필요함.
        # [['KRW-BTC' '2021-09-01T07:43:00' '2021-09-01T16:43:00' 55191000.0
        #   55212000.0 55141000.0 55168000.0 1630482226481 518525771.98098
        #   9.39740165 1]]OK



if __name__ == '__main__':
    unittest.main()
    #
    # qd = QuoteDispatcher()
    # df = qd.process_quote()