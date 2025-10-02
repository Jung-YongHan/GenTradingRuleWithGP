
import asyncio
import datetime

import jwt
import websockets
import threading
import json
import time
import pytz
import pandas as pd

from bt4.Constants import ExType, CandleType
from bt4.quote.QuoteConnector import UniversalQuoteConnector

pd.set_option('display.max_columns', None)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('max_colwidth', None)

from bt4.utils.python_utils import now_dt, str2dt, dt2str, to_kst_time, get_1min_before_dt, start_timing, \
    end_n_elapsed_time


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


    def update(self, trade_json):
        market = trade_json["cd"]
        trading_date = trade_json["td"]
        trading_time = trade_json["ttm"]
        tt_dt = str2dt(f"{trading_date}T{trading_time}")
        trading_price = trade_json["tp"]
        trading_volume = trade_json["tv"]
        ask_bid = trade_json["ab"]
        # print(trade_json)
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
            print(f"[{dt2str(self._1m_last_min_dt)}]{market=},{self._1m_open=},{self._1m_high=},{self._1m_low=},{self._1m_close=},{self._1m_volume=},{self._1m_ask_vol=},{self._1m_bid_vol=}")
            candle_time_dt = self._1m_last_min_dt.replace(second = 0, microsecond = 0)
            if pd.Timestamp(dt2str(candle_time_dt)) in self._1m_df.index:
                self._1m_df = self._1m_df.drop(pd.Timestamp(dt2str(candle_time_dt)))
            # print(f"[1] Add New after getting Tick")
            # current_df = pd.DataFrame({"market":[market], "open": [self._1m_open], "high": [self._1m_high], "low":[self._1m_low], "close": [self._1m_close],
            #                                               "vol": [self._1m_volume], "ask_vol": [self._1m_ask_vol], "bid_vol": [self._1m_bid_vol]}, index = [dt2str(candle_time_dt)])
            current_df = pd.DataFrame({"market":[market], "open": [self._1m_open], "high": [self._1m_high], "low":[self._1m_low], "close": [self._1m_close],
                                                          "vol": [self._1m_volume]}, index = [dt2str(candle_time_dt)])
            current_df.index = pd.to_datetime(current_df.index)
            if len(self._1m_df) == 0:
                self._1m_df = current_df
            else:
                self._1m_df = pd.concat([self._1m_df, current_df])
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

    def get_1m_df(self, desired_kst_time_dt):
        print(f"get_1m_df-checking time:{desired_kst_time_dt}")
        desired_timestamp = pd.Timestamp(desired_kst_time_dt)
        if desired_timestamp not in self._1m_df.index:  ## tick업데이트보다 check하는 시점이 빠르면
            print(f"[2] Add New in checking time because the data have not been updated yet.")
            self._1m_df.loc[desired_timestamp] = {"market"     : self.coin,
                                                  "open"       : self._1m_close,
                                                  "high"       : self._1m_close,
                                                  "low"        : self._1m_close,
                                                  "close"      : self._1m_close,
                                                  "vol"     : 0  # , "ask_vol"    : 0, "bid_vol"    : 0
                                                  }

        self.__update_other_candles__(self._1m_df)
        return self._1m_df

    def __update_other_candles__(self, _1m_df):

        _3m_df = self.__resample_with_base__(_1m_df, "3T", "0T")
        self._3m_df = self.__join_df__(_3m_df, self._3m_df)
        _5m_df = self.__resample_with_base__(_1m_df, "5T", "0T")
        self._5m_df = self.__join_df__(_5m_df, self._5m_df)
        _15m_df = self.__resample_with_base__(_1m_df, "15T", "0T")
        self._15m_df = self.__join_df__(_15m_df, self._15m_df)
        _30m_df = self.__resample_with_base__(_1m_df, "30T", "0T")
        self._30m_df = self.__join_df__(_30m_df, self._30m_df)
        _1h_df = self.__resample_with_base__(_1m_df, "1H", "0T")
        self._1h_df = self.__join_df__(_1h_df, self._1h_df)
        _4h_df = self.__resample_with_base__(_1m_df, "4H", "1H")
        self._4h_df = self.__join_df__(_4h_df, self._4h_df)
        _1d_df = self.__resample_with_base__(_1m_df, "1D", "9H")
        self._1d_df = self.__join_df__(_1d_df, self._1d_df)

        for tf_idx in range(CandleType.DAYS_0.value, CandleType.DAYS_23.value + 1):
            hour_offset = tf_idx - CandleType.DAYS_0.value
            self._tf_dfs[CandleType(tf_idx)] = self.__resample_with_base__(self._1h_df, "24H", f"{hour_offset}H")

        print(f"1m({len(self._1m_df)}):\r\n{self._1m_df.tail(10)}")
        print(f"3m({len(self._3m_df)}):\r\n{self._3m_df.tail(10)}")
        print(f"5m({len(self._5m_df)}):\r\n{self._5m_df.tail(10)}")
        print(f"15m({len(self._15m_df)}):\r\n{self._15m_df.tail(10)}")
        print(f"30m({len(self._30m_df)}):\r\n{self._30m_df.tail(10)}")
        print(f"1h({len(self._1h_df)}):\r\n{self._1h_df.tail(10)}")
        print(f"4h({len(self._4h_df)}):\r\n{self._4h_df.tail(10)}")
        print(f"1d({len(self._1d_df)}):\r\n{self._1d_df.tail(10)}")

        for tf_idx in range(CandleType.DAYS_0.value, CandleType.DAYS_23.value + 1) :
            if tf_idx == 0 or tf_idx == 23:
                print(f"1d-tf {CandleType(tf_idx).name}({len(self._tf_dfs[CandleType(tf_idx)])}):{self._tf_dfs[CandleType(tf_idx)].tail(10)}")

    def __update_after_resampled__(self, tgt_df, _1m_df):
        recent_1m_df = _1m_df[tgt_df.tail(1).index[0].strftime('%Y-%m-%d %H:%M:%S'):]
        if len(recent_1m_df) > 0:
            tgt_df.loc[recent_1m_df.tail(1).index[0]] = \
                {"market" : self.coin, "open"   : recent_1m_df.head(1)["open"].item(),
                 "high"   : recent_1m_df["high"].max(), "low"    : recent_1m_df["low"].min(),
                 "close"  : recent_1m_df.tail(1)["close"].item(), "vol"    : recent_1m_df["vol"].sum()}

        return tgt_df

    def __resample_with_base__(self, df, rule, offset) :
        return df.resample(rule, offset = offset).agg({
            'market' : 'first',
            'open'   : 'first',
            'high'   : 'max',
            'low'    : 'min',
            'close'  : 'last',
            'vol' : 'sum'
        })

    def calibrate(self, frozen_df):
        print(f"frozen: {frozen_df.tail(5)}, len : {len(frozen_df)}")
        print(f"1m_df : {self._1m_df.tail(5)}, len : {len(self._1d_df)}")

        # self._1m_df = self._1m_df[~self._1m_df.index.isin(frozen_df.index)]
        # self._1m_df = pd.concat([frozen_df, self._1m_df])
        self._1m_df = self.__join_df__(self._1m_df, frozen_df)
        print(f"merge done!  : {self._1m_df.tail(20)}")

    def completes(self, market_frozen_cdl_dfs):
        for cdl in market_frozen_cdl_dfs:
            market_cdl_df = market_frozen_cdl_dfs[cdl]
            if cdl == CandleType.MINUTES_3:
                len_before = len(self._3m_df)
                self._3m_df = self.__join_df__(self._3m_df, market_cdl_df)
                len_after = len(self._3m_df)
                print(f"_3m_df len: {len_before} -> {len_after}")
            elif cdl == CandleType.MINUTES_5:
                len_before = len(self._5m_df)
                self._5m_df = self.__join_df__(self._5m_df, market_cdl_df)
                len_after = len(self._5m_df)
                print(f"_5m_df len: {len_before} -> {len_after}")
            elif cdl == CandleType.MINUTES_15:
                len_before = len(self._15m_df)
                self._15m_df = self.__join_df__(self._15m_df, market_cdl_df)
                len_after = len(self._15m_df)
                print(f"_15m_df len: {len_before} -> {len_after}")
            elif cdl == CandleType.MINUTES_30:
                len_before = len(self._30m_df)
                self._30m_df = self.__join_df__(self._30m_df, market_cdl_df)
                len_after = len(self._30m_df)
                print(f"_30m_df len: {len_before} -> {len_after}")
            elif cdl == CandleType.HOUR:
                len_before = len(self._1h_df)
                self._1h_df = self.__join_df__(self._1h_df, market_cdl_df)
                len_after = len(self._1h_df)
                print(f"_1h_df len: {len_before} -> {len_after}")
            elif cdl == CandleType.HOUR4:
                len_before = len(self._4h_df)
                self._4h_df = self.__join_df__(self._4h_df, market_cdl_df)
                len_after = len(self._4h_df)
                print(f"_4h_df len: {len_before} -> {len_after}")
            elif cdl == CandleType.DAYS:
                len_before = len(self._1d_df)
                self._1d_df = self.__join_df__(self._1d_df, market_cdl_df)
                len_after = len(self._1d_df)
                print(f"_1d_df len: {len_before} -> {len_after}")

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

        self.coins = ["KRW-BTC"]
        # self.coins = ["KRW-BTC", "KRW-ETH"]
        # self.coins = ["KRW-BTC","KRW-ETH","KRW-XRP","KRW-TRX","KRW-ETC","KRW-ADA", "KRW-DOGE","KRW-BTG","KRW-EOS","KRW-BCH","KRW-XLM"]
        # self.coins = ["KRW-CRO"]
        # self.coins = UniversalQuoteConnector.instance().get_available_markets(ExType.upbit)

    def generate_jwt_token(self) :
        payload = {
            'access_key' : self.access_key,
            'nonce'      : int(time.time() * 1000)
        }
        token = jwt.encode(payload, self.secret_key, algorithm = 'HS256')
        return token

    async def connect(self) :
        while self.running :
            try :
                token = self.generate_jwt_token()
                headers = {
                    'Authorization' : f'Bearer {token}'
                }
                async with websockets.connect(self.uri, extra_headers = headers) as websocket :
                    subscribe_msg = [
                        {"ticket" : "test"},
                        {"type" : "trade", "codes" : self.coins},
                        {"format" : "SIMPLE"}
                    ]

                    for code in self.coins :
                        self.coin_1m_cdl_mgrs[code] = Coin1M_OHLCV(code)

                    await websocket.send(json.dumps(subscribe_msg))
                    print("Connected to Upbit WebSocket.")

                    while self.running :
                        response = await websocket.recv()
                        trade_json = json.loads(response)
                        coin = trade_json["cd"]
                        # print(trade_json)
                        if coin not in self.coin_1m_cdl_mgrs :
                            self.coin_1m_cdl_mgrs[coin] = Coin1M_OHLCV(code)
                        self.coin_1m_cdl_mgrs[coin].update(trade_json)

            except (websockets.ConnectionClosed, websockets.InvalidURI, websockets.InvalidHandshake) as e :
                print(f"Connection error: {e}. Reconnecting in 5 seconds...")
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

    def completes(self, market_frozen_cdl_dfs):
        for coin in self.coin_1m_cdl_mgrs:
            self.coin_1m_cdl_mgrs[coin].calibrate_remaining_cdls(market_frozen_cdl_dfs[coin])


def dispatch_task(upbit_websocket_obj) :
    while True :
        now = now_dt()
        next_run = now.replace(second = 2, microsecond = 0)

        # If the current time is past the next run time in this minute, schedule for the next minute
        if now >= next_run :
            next_run += datetime.timedelta(minutes = 1)

        sleep_duration = (next_run - now).total_seconds()
        time.sleep(sleep_duration)

        now = now_dt()
        desired_time = get_1min_before_dt(now, True)
        coin_1m_cdl_mgrs = upbit_websocket_obj.get_coin_1m_cdl_mgrs()
        print(f"==" * 100)
        for coin in coin_1m_cdl_mgrs:
            coin_1m_cdl = coin_1m_cdl_mgrs[coin]
            coin_1m_cdl.get_cld_dfs(desired_time)

def calibrate_1m_cdl_task(upbit_websocket_obj):
    markets = upbit_websocket_obj.coins

    __time_all_process = start_timing()
    market_dfs = UniversalQuoteConnector.instance().fetch_quote_num_candles(ExType.upbit, markets, 300,
                                                                            CandleType.MINUTES_1)
    upbit_websocket_obj.calibrates(market_dfs)
    print(f"all markets: {market_dfs.keys()}")
    print(end_n_elapsed_time(__time_all_process, 'calibrating 1m cdl task'))

def calibrate_remaining_cdls_task(upbit_websocket_obj):
    print(f"#### start complete_remainders")
    __time_all_process = start_timing()
    markets = upbit_websocket_obj.coins
    # candle_types = [CandleType.MINUTES_3, ]

    candle_types = [CandleType.MINUTES_3, CandleType.MINUTES_5,
                    CandleType.MINUTES_15, CandleType.MINUTES_30,
                    CandleType.HOUR, CandleType.HOUR4, CandleType.DAYS]
    def_num_cdles = 300
    market_candles = {}
    for cdl_type in candle_types:
        fetched_dfs = UniversalQuoteConnector.instance().fetch_quote_num_candles(ExType.upbit, markets, def_num_cdles,
                                                                                 cdl_type = cdl_type)
        for market in markets:
            if market not in market_candles:
                market_candles[market] = {}
            market_candles[market][cdl_type] = fetched_dfs[market]
    upbit_websocket_obj.calibrate_remaining_cdls(market_candles)
    print(end_n_elapsed_time(__time_all_process, 'calibrating all remaining cdl task'))


if __name__ == '__main__' :
    ACCESS_KEY = 'kOzKkEnwOtxhVptCkxZE7UHlFvWzQWSBR8WpKENG'
    SECRET_KEY = 'cPZvKf82vX2P2l8boxTPK1oDyO9Da2k6rMhcZfz8'

    upbit_websocket_obj = UpbitWebSocketClient(ACCESS_KEY, SECRET_KEY)

    # # 웹소켓 클라이언트를 위한 스레드 생성
    websocket_thread = threading.Thread(target = upbit_websocket_obj.start)
    websocket_thread.start()

    # 주기적 작업을 위한 스레드 생성
    periodic_dispatch_thread = threading.Thread(target = dispatch_task, args = (upbit_websocket_obj,))
    periodic_dispatch_thread.start()

    time.sleep(120) # After two minutes, it starts calibrating quotes.

    calibrate_thread = threading.Thread(target = calibrate_1m_cdl_task, args = (upbit_websocket_obj,))
    calibrate_thread.start()

    time.sleep(120)  # After two minutes, it starts calibrating remaining candles.

    complete_remainders_thread = threading.Thread(target = calibrate_remaining_cdls_task, args = (upbit_websocket_obj,))
    complete_remainders_thread.start()

    try :
        while True :
            time.sleep(1)
    except KeyboardInterrupt:
        upbit_websocket_obj.stop()
        websocket_thread.join()
        periodic_dispatch_thread.join()
        calibrate_thread.join()
        complete_remainders_thread.join()
        print("Stopped.")