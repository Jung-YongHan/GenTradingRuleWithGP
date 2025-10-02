import json
import unittest

import pandas
import pyupbit
from spiketesting.upbit.DataCollector import DataCollector
from bulltrader.Constants import DataType
import datetime as dt
import requests
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('max_colwidth', None)
from bulltrader.utils.python_utils import create_dt_at, to_utc_time, dt2str


class MyTestCase(unittest.TestCase):

    def test_fetchmarket_min15(self):
        data_type = DataType.MINUTES_15
        dc = DataCollector()
        simul_start = '2018-09-30T09:00:00'
        df = dc.fetchMarketBulk2('KRW-BTC', simul_start, data_type=data_type)
        df.sort_values(by='candle_date_time_kst', ascending=True, inplace=True)
        df.to_csv('KRW-BTC_'+data_type.name+'.csv')



    @unittest.skip("Tested")
    def test_execute_data_collector(self):
        dc = DataCollector()
        market = 'KRW-BTC'
        date_time_as_string = '2018-09-27T01:00:00'
        ma_period = 5
        print(f'date_time_as_string:{date_time_as_string}')
        opens, highs, lows, closes = dc.fetchMA(market, date_time_as_string, ma_period,
                                                                    data_type=DataType.HOUR4)
        for open, high, low, close in zip(reversed(opens), reversed(highs), reversed(lows), reversed(closes)):
            print(f'open:{open}, high:{high}, low:{low}, close:{close}')

        date_time_as_string = '2021-09-27T07:00:00' ## 현재시간을 넣어주면 4시간 전의 데이터를 가져옴.
        print(f'date_time_as_string:{date_time_as_string}')
        h4_o, h4_h, h4_l, h4_c = dc.fetchDayMarket(market, date_time_as_string,
                                                                    data_type=DataType.HOUR4)
        print(f'h4_o:{h4_o}, h4_h:{h4_h}, h4_l:{h4_l}, close:{h4_c}')
        date_time_as_string = '2021-09-27T07:00:00'
        # 52899000.0, 53559000.0, 52300000.0, 52798000.0    ## 이녀석은 KST시간으로 7시를 의미함.


    @unittest.skip("Tested")
    def test_execute_cascaded_quote_loading(self):
        dc = DataCollector()

        # markets = ('KRW-BTC', )
        markets = ('KRW-BTC', 'KRW-ETH', 'KRW-XRP')
        # markets = ('KRW-BTC', 'KRW-ETH', 'KRW-XRP', 'KRW-ADA')
        # markets = ('KRW-SAND', 'KRW-BCHA', 'KRW-DOT', 'KRW-ETC',
        #            'KRW-PLA', 'KRW-DOGE', 'KRW-AHT', 'KRW-KAVA', 'KRW-LSK',
        # markets = ('KRW-QTUM', 'KRW-BTG', 'KRW-EOS',
        #            'KRW-TRX', 'KRW-XTZ', 'KRW-BCH')
        # markets = ('KRW-TRX', 'KRW-XTZ', 'KRW-BCH')
        # markets = ('KRW-TRX', 'KRW-BCH')
        # markets = ('KRW-BTC', 'KRW-ETH', 'KRW-MTL', 'KRW-XRP', 'KRW-SRM', 'KRW-SAND', 'KRW-BCHA', 'KRW-DOT', 'KRW-ETC',
        # 'KRW-PLA', 'KRW-DOGE', 'KRW-ADA', 'KRW-AHT', 'KRW-KAVA', 'KRW-LSK', 'KRW-QTUM', 'KRW-BTG', 'KRW-EOS',
        # 'KRW-TRX', 'KRW-XTZ', 'KRW-BCH')
        # markets = ('KRW-CRO', 'KRW-AHT', 'KRW-MVL')

        start = '2020-01-01T00:00:00'
        end   =  dt.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        datatype = DataType.MINUTES_1

        market_dfs_as_list, market_dfs, df_all = dc.execute_cascaded_quote_loading(markets, start, datatype)

        time_ordered_market_dfs = []
        for i, market in enumerate(markets):
            column_start = i*11
            time_ordered_market_df = df_all.iloc[:, [(column_start + x) for x in range(0, 11)]]
            time_ordered_market_dfs.append(time_ordered_market_df)
            print(time_ordered_market_df)


        print('loaded markets:', market_dfs.keys())
        # df_all = None
        # for key in market_dfs.keys():
        #     market_df = market_dfs[key]
        #     market_df.fillna(0)
        #     market_df.set_index(market_df.columns[2], inplace=True, drop=False)
        #     if df_all is None:
        #         df_all = market_df
        #     else:
        #         df_all = df_all.join(market_df, how='outer', lsuffix='_left', rsuffix='_right')
        #
        #     print('loaded markets:', key)
        #     print('length of markets:', len(market_dfs[key]))

        # for market_dfs_item in market_dfs_as_list:
        #     print(market_dfs_item.head())
        #     print('---------------------------')


    @unittest.skip("Tested")
    def test_load_quote_from_exchange(self):
        dc = DataCollector()

        market_dfs = {}
        # markets = ('KRW-BTC', 'KRW-ETH', 'KRW-XRP', 'KRW-ADA')
        missing_markets_in_mongo = ('KRW-CRO','KRW-AHT', 'KRW-MVL')
        start = '2018-10-01T09:00:00'
        datatype = DataType.MINUTES_1

        missing_markets_in_files = dc._load_quote_from_exchange(market_dfs, missing_markets_in_mongo, start, datatype)
        print('loaded file:', market_dfs.keys())
        print('missing file:', len(missing_markets_in_files))
        print('missing file:', missing_markets_in_files)


    @unittest.skip("Tested")
    def test_load_quote_from_mongo(self):
        dc = DataCollector()

        market_dfs = {}
        # markets = ('KRW-BTC', 'KRW-ETH', 'KRW-XRP', 'KRW-ADA')
        markets = ('KRW-CRO',)
        start = '2018-10-01T09:00:00'
        datatype = DataType.MINUTES_1

        missing_markets_in_files = dc._load_quote_from_mongo(market_dfs, markets, start, datatype)
        print('loaded file:', market_dfs.keys())
        print('missing file:', len(missing_markets_in_files))
        print('missing file:', missing_markets_in_files)

    # @unittest.skip("Tested")
    def test_load_quote_from_file(self):
        dc = DataCollector()

        market_dfs = {}
        # markets = ('KRW-BTC', 'KRW-ETH', 'KRW-XRP', 'KRW-ADA')
        markets = ('KRW-CRO',)
        start = '2018-10-01T09:00:00'
        datatype = DataType.MINUTES_1

        missing_markets_in_files = dc._load_quote_from_file(market_dfs, markets, start, datatype)
        print('loaded file:', market_dfs.keys())
        print('missing file:', len(missing_markets_in_files))
        print('missing file:', missing_markets_in_files)


    '''
https://github.com/sharebook-kr/pyupbit

        df = get_ohlcv(ticker, interval="minute60")
        df = df.resample('24H', base=base).agg(
            {'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'})
        return df
    '''
    def test_fetch_market3(self):

        df = pyupbit.get_daily_ohlcv_from_base("KRW-BTC", base=9)
        print('=================================================================')
        print(len(df))
        print(df.columns)
        print(df.tail(5))

        df = pyupbit.get_daily_ohlcv_from_base("KRW-BTC", base=10)
        print('=================================================================')
        print(len(df))
        print(df.columns)
        print(df.tail(5))

        df = pyupbit.get_daily_ohlcv_from_base("KRW-BTC", base=13)
        print('=================================================================')
        print(len(df))
        print(df.columns)
        print(df.tail(5))

    # @unittest.skip("Tested")
    def test_fetch_market2(self):
        dc = DataCollector()

        data_type = DataType.DAYS
        counts = 2
        market = 'KRW-BTC'

        kst_time_dt = create_dt_at(2022,1,16,19,0,0)
        utc_time_dt = to_utc_time(kst_time_dt)

        if data_type == DataType.DAYS:
            url = "https://api.upbit.com/v1/candles/days"
        elif data_type == DataType.MINUTES_1:
            url = "https://api.upbit.com/v1/candles/minutes/1"
        elif data_type == DataType.HOUR:
            url = "https://api.upbit.com/v1/candles/minutes/60"

        querystring = {"count": counts, "market": market}

        if utc_time_dt != None:
            querystring["to"] = dt2str(utc_time_dt) + 'Z'

        headers = {"Accept": "application/json"}
        response = requests.request("GET", url, headers=headers, params=querystring)
        print(response.text)
        if response.text != None and len(response.text) != 0:
            if response.text != 'Too many API requests.':
                a_json = json.loads(response.text)
                dataframe = pd.DataFrame.from_records(a_json)
                return dataframe, response.text
        else:
            return None, None



    @unittest.skip("Tested")
    def test_fetch_market(self):
        dc = DataCollector()

        data_type_value = DataType.MINUTES_1
        counts = 200

        df_krw_btc = dc.fetchMarket("KRW-BTC", counts, data_type=data_type_value)
        df_krw_btc.to_csv('krw_btc_'+data_type_value.name+'.csv')

        df_krw_eth = dc.fetchMarket("KRW-ETH", counts, data_type=data_type_value)
        df_krw_eth.to_csv('krw_eth_'+data_type_value.name+'.csv')

    # @unittest.skip("Tested")
    def test_fetch_yesterday(self):
        datacollector = DataCollector()
        market = "KRW-BTC"
        day = '2018-09-28T13:00:00'
        # o, h, l, c = fetchYesterdayDayMarket(market, day)
        o, h, l, c = datacollector.fetchDayMarket(market, day, data_type = DataType.MINUTES_1)
        print(o, h, l, c)

    @unittest.skip("Tested")
    def test_fetch_ma(self):
        market = "KRW-BTC"
        day = '2021-08-04T09:49:00'
        datacollector = DataCollector()

        ma5 = datacollector.fetchMA(market, day, 5)
        print('ma5', ma5)

    @unittest.skip("Tested")
    def test_fetch_current_market_ticks(self):
        tickers = pyupbit.get_tickers(fiat="KRW")

        dc = DataCollector()
        print(tickers)
        df = dc.fetch_current_market_ticks(tickers)
        print(df.head())

        # 2018-08-04T00:00:00
        print(df['trade_date'].apply(lambda x: x[0:4] + "-" + x[4:6] + "-" +x[6:8]) + "T" + df['trade_time'].apply(lambda x: x[0:2] + ":" + x[2:4] + ":" +x[4:6]))
        utc_time_data = df['trade_date'].apply(lambda x: x[0:4] + "-" + x[4:6] + "-" +x[6:8]) + "T" + df['trade_time'].apply(lambda x: x[0:2] + ":" + x[2:4] + ":" +x[4:6])
        kst_time_data = df['trade_date_kst'].apply(lambda x: x[0:4] + "-" + x[4:6] + "-" +x[6:8]) + "T" + df['trade_time_kst'].apply(lambda x: x[0:2] + ":" + x[2:4] + ":" +x[4:6])

        new_df = pandas.DataFrame(data={'market:': df['market'], 'candle_date_time_utc':utc_time_data, 'candle_date_time_kst' :kst_time_data,
                                        'opening_price' : df['opening_price'], 'high_price':df['opening_price'],  'low_price':df['low_price'],
                                        'trade_price': df['trade_price'],'timestamp': df['trade_timestamp'], 'candle_acc_trade_price':df['acc_trade_price'],
                                        'candle_acc_trade_volume':df['acc_trade_volume'], 'prev_closing_price':df['prev_closing_price'],
                                        'change_price': df['signed_change_price'],
                                        'change_rate': df['signed_change_rate']})
        print(new_df)


## Test 2
# df_krw_btc = fetchMarket("KRW-BTC", fetchDays)
# print( df_krw_btc.value_counts())
# print( df_krw_btc.candle_date_time_utc.min())
#
# df_krw_btc = fetchMarket("KRW-BTC", fetchDays, str(df_krw_btc.candle_date_time_utc.min() + 'Z'))
# print( df_krw_btc.value_counts())
# print( df_krw_btc.candle_date_time_utc.min())

## Test 3
# df = fetchMarketBulk1D("KRW-BTC", 10)
# df.sort_values(by='candle_date_time_kst', ascending=True, inplace=True)
# df.to_csv('test.csv')

# simul_start = '2018-10-01T09:00:00Z'
# simul_start = '2018-10-01T09:00:00'
# df = fetchMarketBulk2("KRW-BTC", simul_start, data_type_value)
# df.sort_values(by='candle_date_time_kst', ascending=True, inplace=True)
# df.to_csv('KRW-BTC_'+data_type_value.name+'.csv')

