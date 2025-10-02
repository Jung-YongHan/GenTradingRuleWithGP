import asyncio
import datetime
import sys

import jwt
import redis as redis
import websockets
import threading
import json
import time
import pytz
import pandas as pd
from kafka import KafkaProducer
from kafka.errors import KafkaTimeoutError

import bt4.GlobalProperties as global_prop
from bt4.Constants import ExType, CandleType
from bt4.quote.QuoteConnector import UniversalQuoteConnector
from bt4.quote.QuoteSupport import Quote, Tick
from bt4_cfg.upbit.upbit_websocket_quote_cfg import WEB_SOCKET_PARAMS

pd.set_option('display.max_columns', None)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('max_colwidth', None)

from bt4.utils.mylog import init_log
log = init_log()
from bt4.utils.python_utils import now_dt, str2dt, dt2str, to_kst_time, get_1min_before_dt, start_timing, \
    end_n_elapsed_time, dt2str2

def_num_cdles = 300
def_num_cdles_1h = 5000

flag_quote_dispatching = False

class Coin1M_OHLCV:
    def __init__(self, coin):
        self.coin = coin
        self._1m_open = 0
        self._1m_high = 0
        self._1m_low = 0
        self._1m_close = 0
        self._1m_volume = 0
        self._1m_ask_vol = 0
        self._1m_bid_vol = 0
        self._1m_last_min_dt = now_dt()

        self._1m_df = pd.DataFrame(columns = ["market", "open", "high", "low", "close", "vol"])
        self._3m_df = pd.DataFrame(columns = ["market", "open", "high", "low", "close", "vol"])
        self._5m_df = pd.DataFrame(columns = ["market", "open", "high", "low", "close", "vol"])
        self._15m_df = pd.DataFrame(columns = ["market", "open", "high", "low", "close", "vol"])
        self._30m_df = pd.DataFrame(columns = ["market", "open", "high", "low", "close", "vol"])
        self._1h_df = pd.DataFrame(columns = ["market", "open", "high", "low", "close", "vol"])
        self._4h_df = pd.DataFrame(columns = ["market", "open", "high", "low", "close", "vol"])
        self._1d_df = pd.DataFrame(columns = ["market", "open", "high", "low", "close", "vol"])
        self._tf_dfs = {}
        for tf_idx in range(CandleType.DAYS_0.value, CandleType.DAYS_23.value+1):
            self._tf_dfs[CandleType(tf_idx)] = pd.DataFrame(columns = ["market", "open", "high", "low", "close", "vol"])

        self.lock = threading.Lock()
        self.supported_candles = WEB_SOCKET_PARAMS["supported_candles"]

    def update(self, trade_json):
        market = trade_json["cd"]
        trading_date = trade_json["td"]
        trading_time = trade_json["ttm"]
        tt_dt = str2dt(f"{trading_date}T{trading_time}")
        trading_price = trade_json["tp"]
        trading_volume = trade_json["tv"]
        ask_bid = trade_json["ab"]
        if WEB_SOCKET_PARAMS["enable_log_tick"]:
            log.info(trade_json)
        tt_dt = pytz.utc.localize(tt_dt)
        kst_time_dt = to_kst_time(tt_dt)  # Convert UST -> KST

        if self._1m_last_min_dt.minute == kst_time_dt.minute :
            if trading_price > self._1m_high :
                self._1m_high = trading_price

            if trading_price < self._1m_low :
                self._1m_low = trading_price

            self._1m_close = trading_price
            self._1m_volume = self._1m_volume + trading_volume

            if ask_bid == "ASK" :
                self._1m_ask_vol = self._1m_ask_vol + trading_volume
            else :
                self._1m_bid_vol = self._1m_bid_vol + trading_volume
        else :
            # log.debug(f"[{dt2str(self._1m_last_min_dt)}]{market=},{self._1m_open=},{self._1m_high=},{self._1m_low=},{self._1m_close=},{self._1m_volume=},{self._1m_ask_vol=},{self._1m_bid_vol=}")
            candle_time_dt = self._1m_last_min_dt.replace(second = 0, microsecond = 0)
            #########----------------------------------------------------------------------------------
            with self.lock:
                if pd.Timestamp(dt2str(candle_time_dt)) in self._1m_df.index:
                    self._1m_df = self._1m_df.drop(pd.Timestamp(dt2str(candle_time_dt)))
                current_df = pd.DataFrame({"market":[market], "open": [self._1m_open], "high": [self._1m_high], "low":[self._1m_low], "close": [self._1m_close],
                                                              "vol": [round(self._1m_volume, 8)]}, index = [dt2str(candle_time_dt)])
                current_df.index = pd.to_datetime(current_df.index)
                if len(self._1m_df) == 0:
                    self._1m_df = current_df
                else:
                    self._1m_df = pd.concat([self._1m_df, current_df])
            #########----------------------------------------------------------------------------------
            # print(self._1m_df.tail(5))

            self._1m_last_min_dt = kst_time_dt
            self._1m_open = trading_price
            self._1m_high = trading_price
            self._1m_low = trading_price
            self._1m_close = trading_price
            self._1m_volume = trading_volume

            if ask_bid == "ASK" :
                self._1m_ask_vol = trading_volume
                self._1m_bid_vol = 0
            else :
                self._1m_bid_vol = trading_volume
                self._1m_ask_vol = 0

    def get_cld_dfs(self, desired_kst_time_dt):
        desired_timestamp = pd.Timestamp(desired_kst_time_dt)
        #########----------------------------------------------------------------------------------
        with self.lock :
            if desired_timestamp not in self._1m_df.index:  ## tick업데이트보다 check하는 시점이 빠르면
                # log.debug(f"[2] Add New {self.coin} in checking time because the data have not been updated yet.")
                self._1m_df.loc[desired_timestamp] = {"market"     : self.coin,
                                                      "open"       : self._1m_open,
                                                      "high"       : self._1m_high,
                                                      "low"        : self._1m_low,
                                                      "close"      : self._1m_close,
                                                      "vol"     : round(self._1m_volume, 8)  # , "ask_vol"    : 0, "bid_vol"    : 0
                                                      }
        #########----------------------------------------------------------------------------------
        cdl_dfs = {}
        cdl_dfs[CandleType.MINUTES_1] = self._1m_df
        self.__update_other_candles__(self._1m_df, cdl_dfs)
        self._1m_df = self._1m_df.tail(def_num_cdles)
        return cdl_dfs

    def __update_other_candles__(self, _1m_df, cdl_dfs):

        self._3m_df = self.__resample_and_update__(self._3m_df, _1m_df, cdl_dfs, "3T", "0T", CandleType.MINUTES_3, def_num_cdles)
        self._5m_df = self.__resample_and_update__(self._5m_df, _1m_df, cdl_dfs, "5T", "0T", CandleType.MINUTES_5, def_num_cdles)
        self._15m_df = self.__resample_and_update__(self._15m_df, _1m_df, cdl_dfs, "15T", "0T", CandleType.MINUTES_15, def_num_cdles)
        self._30m_df = self.__resample_and_update__(self._30m_df, _1m_df, cdl_dfs, "30T", "0T", CandleType.MINUTES_30, def_num_cdles)
        self._1h_df = self.__resample_and_update__(self._1h_df, _1m_df, cdl_dfs, "1H", "0T", CandleType.HOUR, def_num_cdles_1h)
        self._4h_df = self.__resample_and_update__(self._4h_df, _1m_df, cdl_dfs, "4H", "1H", CandleType.HOUR4, def_num_cdles)
        self._1d_df = self.__resample_and_update__(self._1d_df, _1m_df, cdl_dfs, "1D", "9H", CandleType.DAYS, def_num_cdles)

        for tf_idx in range(CandleType.DAYS_0.value, CandleType.DAYS_23.value + 1):
            hour_offset = tf_idx - CandleType.DAYS_0.value
            self._tf_dfs[CandleType(tf_idx)] = self.__resample_with_base__(self._1h_df, "24H", f"{hour_offset}H").tail(def_num_cdles)

        cdl_dfs.update(self._tf_dfs)
        self.print_logs()

    def print_logs(self, force_print=False):

        if WEB_SOCKET_PARAMS["enable_log_1m"] or force_print == True:
            log.debug(f"1m({len(self._1m_df)}):\r\n{self._1m_df.tail(10)}")

        if WEB_SOCKET_PARAMS["enable_log_remainders"] or force_print == True:
            log.debug(f"3m({len(self._3m_df)}):\r\n{self._3m_df.tail(10)}")
            log.debug(f"5m({len(self._5m_df)}):\r\n{self._5m_df.tail(10)}")
            log.debug(f"15m({len(self._15m_df)}):\r\n{self._15m_df.tail(10)}")
            log.debug(f"30m({len(self._30m_df)}):\r\n{self._30m_df.tail(10)}")
            log.debug(f"1h({len(self._1h_df)}):\r\n{self._1h_df.tail(10)}")
            log.debug(f"4h({len(self._4h_df)}):\r\n{self._4h_df.tail(10)}")
            log.debug(f"1d({len(self._1d_df)}):\r\n{self._1d_df.tail(10)}")

            for tf_idx in range(CandleType.DAYS_0.value, CandleType.DAYS_23.value + 1) :
                if tf_idx == CandleType.DAYS_0.value or tf_idx == CandleType.DAYS_23.value:
                    if CandleType(tf_idx) in self._tf_dfs:
                        log.debug(f"1d-tf {CandleType(tf_idx).name}({len(self._tf_dfs[CandleType(tf_idx)])}):{self._tf_dfs[CandleType(tf_idx)].tail(10)}")

    def __resample_and_update__(self, tgt_df, _1m_df, cdl_dfs, rule, offset, cdl_type, num_cdls) :
        temp_df = self.__resample_with_base__(_1m_df, rule, offset)
        tgt_df.loc[temp_df.tail(1).index[0]] = temp_df.iloc[-1].to_dict()
        cdl_dfs[cdl_type] = tgt_df.tail(num_cdls)
        return tgt_df

    def __update_after_resampled__(self, tgt_df, _1m_df):
        recent_1m_df = _1m_df[tgt_df.tail(1).index[0].strftime('%Y-%m-%d %H:%M:%S'):]
        if len(recent_1m_df) > 0:
            tgt_df.loc[recent_1m_df.tail(1).index[0]] = \
                {"market" : self.coin, "open"   : recent_1m_df.head(1)["open"].item(),
                 "high"   : recent_1m_df["high"].max(), "low"    : recent_1m_df["low"].min(),
                 "close"  : recent_1m_df.tail(1)["close"].item(), "vol"    : recent_1m_df["vol"].sum()}

        return tgt_df

    def recover_candles(self, recovered_cdl_dict):
        self._1m_df = recovered_cdl_dict[CandleType.MINUTES_1]
        self._3m_df = recovered_cdl_dict[CandleType.MINUTES_3]
        self._5m_df = recovered_cdl_dict[CandleType.MINUTES_5]
        self._15m_df = recovered_cdl_dict[CandleType.MINUTES_15]
        self._30m_df = recovered_cdl_dict[CandleType.MINUTES_30]
        self._1h_df = recovered_cdl_dict[CandleType.HOUR]
        self._4h_df = recovered_cdl_dict[CandleType.HOUR4]
        self._1d_df = recovered_cdl_dict[CandleType.DAYS]

        self._tf_dfs = {}
        for tf_idx in range(CandleType.DAYS_0.value, CandleType.DAYS_23.value + 1) :
            self._tf_dfs[CandleType(tf_idx)] = recovered_cdl_dict[CandleType(tf_idx)]

        # recent_row = self._1m_df.tail(1)
        # self._1m_open = recent_row["open"]
        # self._1m_high = recent_row["high"]
        # self._1m_low = recent_row["low"]
        # self._1m_close = recent_row["close"]
        # self._1m_volume = recent_row["vol"]
        # self._1m_ask_vol = 0
        # self._1m_bid_vol = 0
        # self._1m_last_min_dt = now_dt()



    def __resample_with_base__(self, df, rule, offset) :
        r_sampled_df = df.resample(rule, origin = "epoch", offset = offset).agg({
            'market' : 'first', 'open'   : 'first',
            'high'   : 'max', 'low'    : 'min',
            'close'  : 'last','vol' : 'sum'
        })
        r_sampled_df["vol"] = r_sampled_df["vol"].round(8)
        return r_sampled_df

    def calibrate_1m_cdl(self, frozen_df):
        log.debug(f"frozen: {frozen_df.tail(5)}, len : {len(frozen_df)}")
        log.debug(f"1m_df : {self._1m_df.tail(5)}, len : {len(self._1d_df)}")
        self._1m_df = self.__join_df__(self._1m_df, frozen_df)
        # log.debug(f"merge done!  : {self._1m_df.tail(20)}")

    def calibrate_remaining_cdls(self, market_frozen_cdl_dfs):
        for cdl in market_frozen_cdl_dfs:
            market_frozen_cdl_df = market_frozen_cdl_dfs[cdl]
            if cdl == CandleType.MINUTES_3:
                self._3m_df = self.__merge_cdl_df__(cdl, self._3m_df, market_frozen_cdl_df, def_num_cdles)
            elif cdl == CandleType.MINUTES_5:
                self._5m_df = self.__merge_cdl_df__(cdl, self._5m_df, market_frozen_cdl_df, def_num_cdles)
            elif cdl == CandleType.MINUTES_15:
                self._15m_df = self.__merge_cdl_df__(cdl, self._15m_df, market_frozen_cdl_df, def_num_cdles)
            elif cdl == CandleType.MINUTES_30:
                self._30m_df = self.__merge_cdl_df__(cdl, self._30m_df, market_frozen_cdl_df, def_num_cdles)
            elif cdl == CandleType.HOUR:
                self._1h_df = self.__merge_cdl_df__(cdl, self._1h_df, market_frozen_cdl_df, def_num_cdles_1h)
            elif cdl == CandleType.HOUR4:
                self._4h_df = self.__merge_cdl_df__(cdl, self._4h_df, market_frozen_cdl_df, def_num_cdles)
            elif cdl == CandleType.DAYS:
                self._1d_df = self.__merge_cdl_df__(cdl, self._1d_df, market_frozen_cdl_df, def_num_cdles)

    def __merge_cdl_df__(self, cdl, df, market_frozen_cdl_df, num_of_cdl):
        len_before = len(df)
        temp_df = self.__join_df__(df, market_frozen_cdl_df)
        temp_df = temp_df.tail(num_of_cdl)
        len_after = len(temp_df)
        log.debug(f"{cdl.name} len: {len_before} -> {len_after}")
        return temp_df
    def __join_df__(self, tgt_df, frozen_df):
        tgt_df = tgt_df[~tgt_df.index.isin(frozen_df.index)]
        return pd.concat([frozen_df, tgt_df])


class UpbitWebSocketClient :
    def __init__(self, access_key, secret_key) :
        self.uri = "wss://api.upbit.com/websocket/v1"
        self.access_key = access_key
        self.secret_key = secret_key
        self.running = True
        self.coin_1m_cdl_mgrs = {}

        if len(WEB_SOCKET_PARAMS["markets"]) != 0:
            self.coins = WEB_SOCKET_PARAMS["markets"]
        else:  # fetch all coins
            self.coins = UniversalQuoteConnector.instance().get_available_markets(ExType.upbit)

        for code in self.coins :
            self.coin_1m_cdl_mgrs[code] = Coin1M_OHLCV(code)

    def generate_jwt_token(self) :
        payload = {
            'access_key' : self.access_key,
            'nonce'      : int(time.time() * 1000)
        }
        token = jwt.encode(payload, self.secret_key, algorithm = 'HS256')
        return token

    async def connect(self) :
        global flag_quote_fetching
        while self.running :
            try :
                token = self.generate_jwt_token()
                headers = {
                    'Authorization' : f'Bearer {token}'
                }
                async with websockets.connect(self.uri, extra_headers = headers, ping_interval = 60) as websocket :
                    subscribe_msg = [
                        {"ticket" : "test"},
                        {"type" : "trade", "codes" : self.coins},
                        {"format" : "SIMPLE"}
                    ]

                    await websocket.send(json.dumps(subscribe_msg))
                    log.debug("Connected to Upbit WebSocket.")

                    while self.running :
                        response = await websocket.recv()

                        trade_json = json.loads(response)
                        coin = trade_json["cd"]
                        # print(trade_json)
                        if coin not in self.coin_1m_cdl_mgrs :
                            self.coin_1m_cdl_mgrs[coin] = Coin1M_OHLCV(coin)
                        self.coin_1m_cdl_mgrs[coin].update(trade_json)
                        flag_quote_fetching = True

            except (websockets.ConnectionClosed, websockets.InvalidURI, websockets.InvalidHandshake) as e :
                flag_quote_fetching = False
                log.debug(f"{flag_quote_fetching} is set to be False, because websocket has been crashed!.")
                log.debug(f"Connection error: {e}. Reconnecting in 5 seconds...")
                # self.recover_runtime_cdl_from_redis()
                await asyncio.sleep(5)
            except Exception as e:
                flag_quote_fetching = False
                log.debug(f"{flag_quote_fetching} is set to be False, because websocket has been crashed!.")
                log.debug(f"Etc. Error: {e}. Reconnecting in 5 seconds ...")
                # self.recover_runtime_cdl_from_redis()
                await asyncio.sleep(5)


    def start(self) :
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.connect())

    def stop(self) :
        self.running = False

    def get_coin_1m_cdl_mgrs(self) :
        return self.coin_1m_cdl_mgrs

    def calibrates(self, frozen_dfs):
        for coin in self.coin_1m_cdl_mgrs:
            self.coin_1m_cdl_mgrs[coin].calibrate_1m_cdl(frozen_dfs[coin])

    def calibrate_remaining_cdls(self, market_frozen_cdl_dfs):
        for coin in self.coin_1m_cdl_mgrs:
            self.coin_1m_cdl_mgrs[coin].calibrate_remaining_cdls(market_frozen_cdl_dfs[coin])

    def recover_runtime_cdl_from_redis(self):
        log.info(f"Start to recover runtime candles from Redis!!")
        quote_redis_ip = global_prop.QUOTE_REDIS_IP_ADDR
        redis_storage = redis.StrictRedis(host = quote_redis_ip, port = global_prop.REDIS_PORT, db = 0)

        ex_type = ExType.upbit
        loaded_json = redis_storage.get(f"{ex_type.name}/quote")
        quote = Quote.unmarshal(loaded_json)

        cdl_market_dict = quote.ex_quote[ex_type]
        market_cdl_dict = {}
        for cdl in cdl_market_dict :
            for market in cdl_market_dict[cdl] :
                if market not in market_cdl_dict :
                    market_cdl_dict[market] = {}
                market_cdl_dict[market][cdl] = cdl_market_dict[cdl][market]

        ## Print
        for market in market_cdl_dict :
            self.coin_1m_cdl_mgrs[market].print_logs(True)

        if set(self.coins) == set(market_cdl_dict.keys()) :
            for market in market_cdl_dict :
                self.coin_1m_cdl_mgrs[market].recover_candles(market_cdl_dict[market])
        else :
            print("Error: Requested coins and Redis stored coins are different!")

        ## Print
        for market in market_cdl_dict :
            self.coin_1m_cdl_mgrs[market].print_logs(True)

        log.info(f"Recovering runtime candles done!!")


def dispatch_task(upbit_websocket_obj) :
    global flag_quote_dispatching
    global flag_quote_fetching
    ## Initialize Kafka
    bootstrap_svr = global_prop.kafka_bootstrap_svr
    producer = KafkaProducer(bootstrap_servers = bootstrap_svr)
    if producer.bootstrap_connected() :
        print(f"Kafka Bootstrap has been connected to {bootstrap_svr}")

    ## Initialize Redis
    quote_redis_ip = global_prop.QUOTE_REDIS_IP_ADDR
    redis_storage = redis.StrictRedis(host = quote_redis_ip, port = global_prop.REDIS_PORT, db = 0)

    while True :

        ## waiting for 2 seconds of each minute
        now = now_dt()
        next_run = now.replace(second = 2, microsecond = 0)

        # If the current time is past the next run time in this minute, schedule for the next minute
        if now >= next_run :
            next_run += datetime.timedelta(minutes = 1)

        sleep_duration = (next_run - now).total_seconds()
        time.sleep(sleep_duration)
        ##
        if not flag_quote_fetching:
            log.info(f"[{dt2str(now)}] Waiting for fetching quote from websocket. It will start at the 2nd seconds of the next minute.")
            continue
        ##
        now = now_dt()
        desired_time_dt = get_1min_before_dt(now, True)

        log.debug(f"==" * 100)
        log.debug(f"Processing quote for {desired_time_dt}")
        #############################################################################
        ## 1. Build Quotes
        quote = Quote(desired_time_dt)

        coin_1m_cdl_mgrs = upbit_websocket_obj.get_coin_1m_cdl_mgrs()
        runtime_cdl_dfs = {}
        market_ticks = {}
        for coin in coin_1m_cdl_mgrs:
            coin_1m_cdl = coin_1m_cdl_mgrs[coin]
            market_cdl_dfs = coin_1m_cdl.get_cld_dfs(desired_time_dt)

            for market_cdl in market_cdl_dfs:
                if market_cdl == CandleType.MINUTES_1:
                    recent_tick_list = market_cdl_dfs[market_cdl].iloc[-1].tolist()
                    recent_tick_list = list([float(x) if type(x) != str else x for x in recent_tick_list])
                    recent_tick_list[-1] = round(recent_tick_list[-1], 8)
                    recent_tick_list.insert(0, dt2str2(desired_time_dt))
                    market_ticks[coin] = Tick.from_list(recent_tick_list)

                if market_cdl not in runtime_cdl_dfs:
                    runtime_cdl_dfs[market_cdl] = {}
                runtime_cdl_dfs[market_cdl][coin] = market_cdl_dfs[market_cdl]

        quote.add_quote(ExType.upbit, runtime_cdl_dfs, market_ticks)

        #############################################################################
        ## 2. store quote and send request pull through kafka
        # encoded_json = quote.marshal()
        quote_pull_req_channel = global_prop.kafka_channel_quote_pull_request
        log.info(f"STORE QUOTE in Redis at {desired_time_dt}")
        try :
            # 1. update redis for the current quote
            # redis_storage.set(f"{ExType.upbit.name}/quote", encoded_json)
            quote.to_redis()
            # 2. send quote pull request - receive using QuotePullRequestReceiver
            exchange = ExType.upbit.name
            time_str = dt2str2(quote.time_dt)
            message = f"{exchange}/{time_str}"
            if flag_quote_dispatching :
                log.info(f"SEND \"{message}\" message through the KAFKA ({quote_pull_req_channel}) channel.")
                producer.send(quote_pull_req_channel, message.encode("utf-8"))
        except KafkaTimeoutError as err :
            log.error(f'KafkaTimeoutError : {err=}')



def calibrate_1m_cdl_task(upbit_websocket_obj):
    markets = upbit_websocket_obj.coins

    __time_all_process = start_timing()
    market_dfs = UniversalQuoteConnector.instance().fetch_quote_num_candles(ExType.upbit, markets, def_num_cdles,
                                                                            CandleType.MINUTES_1)
    upbit_websocket_obj.calibrates(market_dfs)
    log.debug(f"all markets: {market_dfs.keys()}")
    print(end_n_elapsed_time(__time_all_process, 'calibrating 1m cdl task'))

def calibrate_remaining_cdls_task(upbit_websocket_obj):
    global flag_quote_dispatching
    log.debug(f"#### start complete_remainders")
    __time_all_process = start_timing()
    markets = upbit_websocket_obj.coins
    # candle_types = [CandleType.MINUTES_3, ]

    candle_types = list(set(WEB_SOCKET_PARAMS["supported_candles"]) - set([CandleType.MINUTES_1]))

    market_candles = {}
    for cdl_type in candle_types:
        num_cdles = def_num_cdles if cdl_type != CandleType.HOUR else def_num_cdles_1h
        if cdl_type != CandleType.DAYS_TF:
            fetched_dfs = UniversalQuoteConnector.instance().fetch_quote_num_candles(ExType.upbit, markets, num_cdles,
                                                                                     cdl_type = cdl_type)
        for market in markets:
            if market not in market_candles:
                market_candles[market] = {}
            market_candles[market][cdl_type] = fetched_dfs[market]
    upbit_websocket_obj.calibrate_remaining_cdls(market_candles)
    log.debug(end_n_elapsed_time(__time_all_process, 'calibrating all remaining cdl task!'))

    log.info("Now Service Ready! Sending Candle Pull Request will start!")
    flag_quote_dispatching = True


def start_upbit_quote_service():
    ACCESS_KEY = WEB_SOCKET_PARAMS["access_key"]
    SECRET_KEY = WEB_SOCKET_PARAMS["secrete_key"]

    upbit_websocket_obj = UpbitWebSocketClient(ACCESS_KEY, SECRET_KEY)

    # # 웹소켓 클라이언트를 위한 스레드 생성
    websocket_thread = threading.Thread(target = upbit_websocket_obj.start)
    websocket_thread.start()

    # 주기적 작업을 위한 스레드 생성
    periodic_dispatch_thread = threading.Thread(target = dispatch_task, args = (upbit_websocket_obj,))
    periodic_dispatch_thread.start()
    log.info("Calibrating 1m candles will start after 120 sec.")
    time.sleep(120)  # After two minutes, it starts calibrating quotes.

    log.info("Calibrating 1m candles start now!")
    calibrate_thread = threading.Thread(target = calibrate_1m_cdl_task, args = (upbit_websocket_obj,))
    calibrate_thread.start()

    log.info("Calibrating remaining candles candles will start after 120 sec.")
    time.sleep(120)  # After two minutes, it starts calibrating remaining candles.

    log.info("Calibrating remaining candles start now!")
    complete_remainders_thread = threading.Thread(target = calibrate_remaining_cdls_task, args = (upbit_websocket_obj,))
    complete_remainders_thread.start()

    try :
        while True :
            time.sleep(1)
    except KeyboardInterrupt :
        upbit_websocket_obj.stop()
        websocket_thread.join()
        periodic_dispatch_thread.join()
        calibrate_thread.join()
        complete_remainders_thread.join()
        log.debug("Stopped.")

if __name__ == '__main__' :
    start_upbit_quote_service()