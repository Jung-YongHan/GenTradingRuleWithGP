import datetime
import json
import os.path
import time
from datetime import datetime as dt
from datetime import timedelta
from os.path import dirname, join

import pandas as pd
import requests

import bulltrader.GlobalProperties as global_prop
from bulltrader.Constants import DataType
from bulltrader.utils.mongodb import MongoDBHandler

import bt4.common.ReportSupport



class DataCollector:

    def __init__(self):
        self.columns = ['date', 'market', 'open', 'high', 'low', 'close']
        self.cache_df_for_minutes = None
        self.cache_df_for_days = None
        self.cache_df_for_hour4 = None
        self.cache_df_for_hour  = None
        self.cache_df = None

        self.last_fetch_time = -1
        self.duration = 300

        # self.mongo = MongoDBHandler.instance()

    def fetch_daily_candles(self, market, base_time, ma_period, data_type = DataType.DAYS):
        initial_time = dt.strptime(base_time, '%Y-%m-%dT%H:%M:%S')
        if data_type == DataType.DAYS:
            time = datetime.time(9, 0, 0)
            if initial_time.hour >= 9:
                date = datetime.date(initial_time.year, initial_time.month, initial_time.day)
                range_end = dt.combine(date, time)
            else:
                range_end = initial_time - timedelta(days=1)
                date = datetime.date(range_end.year, range_end.month, range_end.day)
                range_end = dt.combine(date, time)
            range_end_time = dt.strftime(range_end, "%Y-%m-%dT%H:%M:%S")
        elif data_type == DataType.HOUR4: # for DataType.HOUR4
            if initial_time.hour != 0: # hour is greater than 0
                date = datetime.date(initial_time.year, initial_time.month, initial_time.day)
                range_end_hour = 4 * (initial_time.hour // 4) + 1
                time = datetime.time(range_end_hour, 0, 0)
                range_end = dt.combine(date, time)
            else:                       # hour is zero, the fetch time should be previous day's 21h.
                range_end = initial_time - timedelta(days=1)
                date = datetime.date(range_end.year, range_end.month, range_end.day)
                time = datetime.time(21, 0, 0)
                range_end = dt.combine(date, time)

        elif data_type == DataType.HOUR:  # for DataType.HOUR
            date = datetime.date(initial_time.year, initial_time.month, initial_time.day)
            time = datetime.time(initial_time.hour, 0, 0)
            range_end = dt.combine(date, time)

        range_end_time = dt.strftime(range_end, "%Y-%m-%dT%H:%M:%S")

        opens, highs, lows, closes = self.fetchMA(market, range_end_time, ma_period, data_type)
        return opens, highs, lows, closes

    def fetchMA(self, market, day, count, data_type = DataType.DAYS):
        file_name = f'daily_market_cache_{data_type.name}.csv'
        dataframe = None
        if data_type == DataType.DAYS:
            self.cache_df = self.cache_df_for_days
            url = "https://api.upbit.com/v1/candles/days"
        elif data_type == DataType.HOUR4:
            self.cache_df = self.cache_df_for_hour4
            url = "https://api.upbit.com/v1/candles/minutes/240"
        elif data_type == DataType.HOUR:
            url = "https://api.upbit.com/v1/candles/minutes/60"
        elif data_type == DataType.MINUTES_15:
            url = "https://api.upbit.com/v1/candles/minutes/15"

        querystring = {"count": count, "market": market}

        if os.path.isfile(file_name):
            if self.cache_df is None:
                self.cache_df = pd.read_csv(file_name, index_col='date')
        else:
            self.cache_df = pd.DataFrame(columns=self.columns)
            self.cache_df.set_index(keys=['date'], drop=True, inplace=True)

        need_to_fetch = False

        if day is not None:
            tm_kst = dt.strptime(day, '%Y-%m-%dT%H:%M:%S')
            # dt_tm_utc = tm_kst - timedelta(hours=9) + timedelta(minutes=1)
            dt_tm_utc = tm_kst - timedelta(hours=9)
            dt_tm_utc_string = dt.strftime(dt_tm_utc, "%Y-%m-%dT%H:%M:%S")
            querystring["to"] = dt_tm_utc_string + 'Z' # for upbit query, the time zone should be utc (kst-9h)
            if data_type == DataType.DAYS:
                tm_kst_start = tm_kst - timedelta(days=count)
            elif data_type == DataType.HOUR4:
                tm_kst_start = tm_kst - timedelta(hours=count*4)
            elif data_type == DataType.HOUR:
                tm_kst_start = tm_kst - timedelta(hours=count)
            tm_kst_start_string = dt.strftime(tm_kst_start, "%Y-%m-%dT%H:%M:%S")
            tm_kst_end_string = dt.strftime(tm_kst, "%Y-%m-%dT%H:%M:%S")
        try:
            self.cache_df.sort_index(inplace=True, ascending=True)
            row = self.cache_df.loc[(self.cache_df.market == market)]
            ranged_row = row.loc[tm_kst_start_string:tm_kst_end_string]
            # print(f'row type:{type(ranged_row)}, {len(ranged_row)}, {ranged_row.shape[0]}')
            if len(ranged_row) > 0:
                dataframe = ranged_row
            else:
                need_to_fetch = True
        except KeyError:
            need_to_fetch = True

        ## To Store All Data (Comment out for enabling Cache)
        # need_to_fetch = True
        if need_to_fetch:
            headers = {"Accept": "application/json"}
            response = requests.request("GET", url, headers=headers, params=querystring)
            print(f'fetch MA from svr: {response.text}')
            if response.text is not None and len(response.text) != 0:
                if response.text != 'Too many API requests.':
                    a_json = json.loads(response.text)
                    from_svr = pd.DataFrame.from_records(a_json)

                    dataframe = pd.DataFrame(columns=self.columns)
                    dataframe['date'] = from_svr['candle_date_time_kst']
                    dataframe['market'] = from_svr['market']
                    dataframe['open'] = from_svr['opening_price']
                    dataframe['high'] = from_svr['high_price']
                    dataframe['low'] = from_svr['low_price']
                    dataframe['close'] = from_svr['trade_price']
                    dataframe = dataframe.set_index(['date'])
                    dataframe.sort_index(inplace=True, ascending=True)
                    self.cache_df = pd.concat([self.cache_df, dataframe])
                    self.cache_df.to_csv(file_name, index_label = 'date')

                    if data_type == DataType.DAYS:
                        self.cache_df_for_days = self.cache_df
                    elif data_type == DataType.HOUR4:
                        self.cache_df_for_hour4 = self.cache_df
                    elif data_type == DataType.HOUR:
                        self.cache_df_for_hour = self.cache_df

            else:
                return [],[],[],[]

        if (dataframe is not None) and (len(dataframe) > 0):
            open_prices = dataframe['open']
            high_prices = dataframe['high']
            low_prices = dataframe['low']
            close_prices = dataframe["close"]
            return open_prices, high_prices, low_prices, close_prices
        else:
            return [],[],[],[]

    def fetchDayMarket(self, market, day, data_type = DataType.DAYS):
        file_name = f'daily_market_cache_{data_type.name}.csv'

        if data_type == DataType.DAYS:
            self.cache_df = self.cache_df_for_days
        elif data_type == DataType.MINUTES_1:
            self.cache_df = self.cache_df_for_minutes
        elif data_type == DataType.HOUR4:
            self.cache_df = self.cache_df_for_hour4
        elif data_type == DataType.HOUR:
            self.cache_df = self.cache_df_for_hour

        if os.path.isfile(file_name) :
            if self.cache_df is None:
                self.cache_df = pd.read_csv(file_name, index_col = 'date')
        else:
            self.cache_df = pd.DataFrame(columns=self.columns)

        row = self.cache_df.loc[(self.cache_df.market == market) & (self.cache_df.index == day)]
        # print(f'fetchDayMarket - {data_type} - cache: len - {len(row)} , {market}, {day}')
        if len(row) > 0 :
            open = row['open'].values[0]
            high = row['high'].values[0]
            low = row['low'].values[0]
            close = row['close'].values[0]
            if data_type == DataType.DAYS:
                self.cache_df_for_days = self.cache_df
            elif data_type == DataType.MINUTES_1:
                self.cache_df_for_minutes = self.cache_df
            elif data_type == DataType.HOUR4:
                self.cache_df_for_hour4 = self.cache_df
            elif data_type == DataType.HOUR:
                self.cache_df_for_hour = self.cache_df
            return open, high, low, close
        else:
            if time.time() - self.last_fetch_time > self.duration:
                print('sleep for 0.1 sec.')
                time.sleep(0.1)

            if data_type == DataType.DAYS:
                url = "https://api.upbit.com/v1/candles/days"
            elif data_type == DataType.MINUTES_1:
                url = "https://api.upbit.com/v1/candles/minutes/1"
            elif data_type == DataType.HOUR4:
                url = "https://api.upbit.com/v1/candles/minutes/240"
            elif data_type == DataType.HOUR:
                url = "https://api.upbit.com/v1/candles/minutes/60"

            querystring = {"count": 1, "market": market}
            dt_tm_utc = dt.strptime(day, '%Y-%m-%dT%H:%M:%S')
            tm_kst = dt_tm_utc - timedelta(hours=9)
            tm_kst_string = dt.strftime(tm_kst, "%Y-%m-%dT%H:%M:%S")

            querystring["to"] = tm_kst_string + 'Z'
            headers = {"Accept": "application/json"}

            response = requests.request("GET", url, headers=headers, params=querystring)
            print(response.text)
            if response.text != None and len(response.text) != 0:
                if response.text != 'Too many API requests.':
                    a_json = json.loads(response.text)
                    json_obj = a_json[0]
                    kst = json_obj['candle_date_time_kst']
                    open = json_obj["opening_price"]
                    high = json_obj["high_price"]
                    low = json_obj["low_price"]
                    close = json_obj["trade_price"]

                    new_df = pd.DataFrame({'market': market,
                                           'open': open,
                                           'high': high,
                                           'low': low,
                                           'close': close}, index=[day])

                    self.cache_df = pd.concat([self.cache_df, new_df])
                    self.cache_df.sort_index(inplace=True, ascending=True)
                    self.cache_df.to_csv(file_name, index_label='date')
                    last_fetch_time = time.time()

                    if data_type == DataType.DAYS:
                        self.cache_df_for_days = self.cache_df
                    elif data_type == DataType.MINUTES_1:
                        self.cache_df_for_minutes = self.cache_df
                    elif data_type == DataType.HOUR4:
                        self.cache_df_for_hour4 = self.cache_df
                    elif data_type == DataType.HOUR:
                        self.cache_df_for_hour = self.cache_df
                    self.cache_df = None
                    return open, high, low, close
                else:
                    if data_type == DataType.DAYS:
                        self.cache_df_for_days = self.cache_df
                    elif data_type == DataType.MINUTES_1:
                        self.cache_df_for_minutes = self.cache_df
                    elif data_type == DataType.HOUR4:
                        self.cache_df_for_hour4 = self.cache_df

                    self.cache_df = None
                    return None, None, None, None

    # def fetchYesterdayDayMarket(self, market, day):
    #     curr_day = dt.strptime(day, "%Y-%m-%dT%H:%M:%S")
    #     yesterday_dt = curr_day - timedelta(1)
    #     yesterday_string = dt.strftime(yesterday_dt, "%Y-%m-%dT%H:%M:%S")
    #     return self.fetchDayMarket(market, yesterday_string)

    ## 분단위 데이터를 수신하는 용도.
    ## 동일한 코드를 QuoteDispatcher에도 복사해서 넣어놓음.
    ## 향후에 이 코드는 DataCollector에서는 삭제해야함.
    def fetchMarket(self, market, count, to = None, data_type = DataType.DAYS):
        if data_type == DataType.DAYS:
            url = "https://api.upbit.com/v1/candles/days"
        elif data_type == DataType.MINUTES_1:
            url = "https://api.upbit.com/v1/candles/minutes/1"
        elif data_type == DataType.MINUTES_15:
            url = "https://api.upbit.com/v1/candles/minutes/15"
        elif data_type == DataType.MINUTES_30:
            url = "https://api.upbit.com/v1/candles/minutes/30"
        elif data_type == DataType.HOUR:
            url = "https://api.upbit.com/v1/candles/minutes/60"

        querystring = {"count": count, "market": market}

        if to != None:
            querystring["to"] = to + 'Z'

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

    def fetchMarketBulk(self, market, iteration=10, start = None, data_type = DataType.DAYS):
        df, _ = self.fetchMarket(market, 180, start,data_type)

        for i in range(iteration):
            nextTime = df.candle_date_time_utc.min()
            df2, _ = self.fetchMarket(market, 180, nextTime, data_type)
            if df2.empty == False:
                df = pd.concat([df, df2], axis=0)
            else:
                break
        return df

    #2018-10-01T09:00:00Z
    def fetchMarketBulk2(self, market, start, data_type = DataType.DAYS):
        start_date = dt.strptime(start, "%Y-%m-%dT%H:%M:%S")
        df, _ = self.fetchMarket(market, 180, None, data_type)
        while True:
            nextTime = df.candle_date_time_utc.min()
            next_date = dt.strptime(nextTime, "%Y-%m-%dT%H:%M:%S")
            if  next_date > start_date:
                time.sleep(0.3)
                df2, _ = self.fetchMarket(market, 180, nextTime, data_type)
                if not df2.empty :
                    df = pd.concat([df, df2], axis=0)
                else:
                    break
            else:
                break
        return df

    def execute_cascaded_quote_loading(self, markets, start, end, data_type):
        # 0. define market_dfs = []
        market_dfs = {}

        # 0. missing_mongo_markets = []
        missing_market_mongos = []

        # 1. load quote data from files
        missing_markets_in_files = self._load_quote_from_file(market_dfs, markets, data_type)
        if len(missing_markets_in_files) == 0:
            df_all = self._post_processing(market_dfs, start, end)
            return df_all

        # 3. load quote data from exchange
        self._load_quote_from_exchange(market_dfs, missing_markets_in_files, start, data_type)
        df_all = self._post_processing(market_dfs, start)
        return df_all

        # # 2. load quote data from mongo db
        # missing_markets_in_mongo = self._load_quote_from_mongo(market_dfs, missing_markets_in_files, start, data_type)
        # if len(missing_markets_in_mongo) == 0:
        #     df_all = self._post_processing(market_dfs, start)
        #     return self._market_dfs_to_list(markets,market_dfs), market_dfs, df_all

    def _post_processing(self, market_dfs, start, end):
        df_all = None
        for key in market_dfs.keys():
            market_df = market_dfs[key]
            # print(market_df.head())
            market_df.loc[:,1] = market_df.loc[:,1].str.strip()
            market_df.loc[:,2] = market_df.loc[:,2].str.strip()

            ## Merge All
            market_df.set_index(market_df.columns[2], inplace=True, drop=False)
            market_df = market_df.fillna(0)
            if df_all is None:
                df_all = market_df
            else:
                df_all = df_all.join(market_df, how='inner', lsuffix='_left', rsuffix='_right')

        df_all = df_all.sort_index(ascending=False)
        if end is None:
            now = dt.now().strftime("%Y-%m-%dT%H:%M:%S")
            df_all = df_all.loc[now: start] ## Filtering Time
        else:
            df_all = df_all.loc[end: start]  ## Filtering Time

        df_all = df_all.sort_index(ascending=True)
        return df_all

    def _market_dfs_to_list(self, markets, market_dfs):
        market_dfs_as_list = []
        for market in markets:
            market_dfs_as_list.append(market_dfs[market])
        return market_dfs_as_list

    def _load_quote_from_exchange(self, market_dfs, missing_markets_in_mongo, start, data_type):
        '''
        # 6. if the missing_mongo_markets is not empty
        # 7. fetch market data back until the date is matched with the start date
        #   7.1 store them into the mongodb
        #   7.2 write them into the missing_file_markets
        # 8. close all fetched marekt_file
        # 9. load the market_file into the dataframe and append them into market_dfs
        # 10. filter out the date

        :param market_dfs:
        :param markets:
        :param start:
        :param data_type:
        :return:
        '''

        ## Fetch All Data as possible
        for market in missing_markets_in_mongo:
            df = None
            start_date = dt.now().strftime("%Y-%m-%dT%H:%M:%S")

            i = 0
            while True:
                print('### i:', i)
                i = i + 1
                # if i > 15:
                #     break

                df2, json_string = self.fetchMarket(market, 180, start_date, data_type)
                if df is None:
                    df = df2
                else:
                    if not df2.empty:
                        df = pd.concat([df, df2], axis=0)
                        # self._store_quote_in_mongo(df2, market, json_string)
                        self._store_quote_in_file(df2, market, data_type)
                        start_date = df2['candle_date_time_utc'].min() #The Query Time is UTC Time, not KST Time
                    else:
                        break
                time.sleep(0.3)

            # print(f'### download all minute data for {market} and start to storing time to db..')
            #################
            # root_dir = dirname(dirname(dirname(__file__)))
            # file_name = join(root_dir, f'data\\{market}_{data_type.name}.csv')
            # t1 = threading.Thread(target=store_quote_to_mongo_from_file, args=(file_name))
            # t1.start()
            # threads.append(t1)
            market_dfs[market] = df


    def _store_quote_in_mongo(self, df2, market, json_string):
        json_obj = json.loads(json_string)
        if len(df2) != len(json_obj):
            print(f'two size is different df({len(df2)}), jsonobj({len(json_obj)}) !!!')
            return

        for idx, row in df2.iterrows():
            filter = {'time': dt.strptime(row['candle_date_time_kst'], "%Y-%m-%dT%H:%M:%S")}
            count_docs = self.mongo.count_documents('quote', filter)
            if count_docs <= 0:
                data = {}
                data['time'] = filter['time']
                data[row['market']] = json_obj[idx]
                self.mongo.replace_item_one('quote', filter, data)
            else:
                cursor = self.mongo.find_item('quote', filter)
                for data in cursor:
                    data[row['market']] = json_obj[idx]
                    self.mongo.replace_item_one('quote', filter, data)
                cursor.close()

    def _store_quote_in_file(self, df2, market, data_type):
        root_dir = dirname(dirname(dirname(__file__)))
        file_name = join(root_dir, f'data\\{market}_{data_type.name}.csv')
        market_files = open(file_name, mode = "a")
        market_files.write(df2.to_csv(header=None, index=False))  ## SKIP the 'CRLF'
        market_files.close()

    def _load_quote_from_file(self, market_dfs, markets, data_type):
        '''
            # 1. for all markets
            #  1.1 if the market file exists
            #    1.1.1 load each market from each file
            #    1.1.2 if the market info is successfully loaded, then append it into market_dfs
            #  1.2 else the market file does not exist
            #    1.2.1 append the market into the missing_file_markets
        :param markets:
        :param start:
        :param data_type:
        :return:
        '''
        root_dir = dirname(dirname(dirname(__file__)))  ## parent of parent of directory of simulator.py
        missing_market_in_files = []

        for market in markets:      # 1.
            file_name = join(root_dir, f'data\\{market}_{data_type.name}.csv')
            if os.path.isfile(file_name):   # 1.1
                df = pd.read_csv(file_name, header=None)
                print('fetching markets from ' + file_name)
                # market_dfs[market] = df
                market_dfs[market] = df
            else:
                missing_market_in_files.append(market)

        return missing_market_in_files

    def _load_quote_from_mongo(self, market_dfs, markets, start, data_type):
        '''
            # 2. open market_file for each missing_file_markets
            # 3. for all missing_file_markets
            #  3.1 for all minutes data in the mongo db collection (quote)
            #   3.1.1 if the market data exists in the collection
            #     3.1.1.1 write the data into missing file
            #   3.1.2 if the market data does not exist
            #     3.1.2.1 append the market in toe missing_mongo_markets
            # 4. close all market_file for the loaded market in the mongo db
            # 5. load the market_file into the dataframe and append them into market_dfs
        :param market_dfs:
        :param markets:
        :param start:
        :param data_type:
        :return:
        '''

        ## Find: from the start time to the recent.
        cursor = self.mongo.find_item("quote",
            {'time': {'$gte': dt.strptime(start, "%Y-%m-%dT%H:%M:%S")}})

        market_files = {}
        market_file_names = []
        root_dir = dirname(dirname(dirname(__file__)))
        for data in cursor:
            for key in data:  # key - 'time', 'KRW-BTC', 'KRW-ETH',...
                if key != 'time':
                    if key in markets:
                        if key not in market_files.keys():
                            file_name = join(root_dir, f'data\\{key}_{data_type.name}.csv')
                            market_files[key] = open(file_name, "w")
                            market_file_names.append(file_name)
                        market_string = data[key].values().__str__()[13:-2].replace('\'', '') + '\r'
                        market_files[key].write(market_string)
        cursor.close()

        # close files
        for key in market_files:
            market_files[key].close()

        for market in market_files.keys():
            file_name = join(root_dir, f'data\\{market}_{data_type.name}.csv')
            df = pd.read_csv(file_name, header=None)
            market_dfs[market] = df

        return markets - market_files.keys()


def store_quote_to_mongo_from_file(file_name):
    print('start \'store quote_to_mongo_from_file\' started!!!')
    df = pd.read_csv(file_name)
    print(df.head())

    ### TODO
    #
    # df2, market, json_string):
    # json_obj = json.loads(json_string)
    # if len(df2) != len(json_obj):
    #     print(f'two size is different df({len(df2)}), jsonobj({len(json_obj)}) !!!')
    #     return
    #
    # for idx, row in df2.iterrows():
    #     filter = {'time': dt.strptime(row['candle_date_time_kst'], "%Y-%m-%dT%H:%M:%S")}
    #     count_docs = self.mongo.count_documents('quote', filter)
    #     if count_docs <= 0:
    #         data = {}
    #         data['time'] = filter['time']
    #         data[row['market']] = json_obj[idx]
    #         self.mongo.replace_item_one('quote', filter, data)
    #     else:
    #         cursor = self.mongo.find_item('quote', filter)
    #         for data in cursor:
    #             data[row['market']] = json_obj[idx]
    #             self.mongo.replace_item_one('quote', filter, data)
    #         cursor.close()