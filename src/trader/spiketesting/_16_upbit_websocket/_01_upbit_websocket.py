import datetime
import json
import time

import jwt  # PyJWT
import uuid
import websocket  # websocket-client
import pandas as pd
import schedule
from bt4.utils.python_utils import str2dt, dt2str, now_dt
import multiprocessing as mp
import asyncio

class Coin1M_OHLCV:
    def __init__(self, coin):
        self.coin = coin
        self._1m_open = -1
        self._1m_high = -1
        self._1m_low = -1
        self._1m_close = -1
        self._1m_volume = -1
        self._1m_ask_vol = -1
        self._1m_bid_vol = -1
        self._1m_last_min_dt = now_dt()
        self._1m_df = pd.DataFrame()

    def update(self, trade_json):
        market = trade_json["cd"]
        timestamp = trade_json["tms"]
        trading_date = trade_json["td"]
        trading_time = trade_json["ttm"]
        tt_dt = str2dt(f"{trading_date}T{trading_time}")
        trading_price = trade_json["tp"]
        trading_volume = trade_json["tv"]
        ask_bid = trade_json["ab"]

        if self._1m_last_min_dt.minute == tt_dt.minute :
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
            print(f"[{dt2str(self._1m_last_min_dt)}]{market=},{timestamp=},{self._1m_open=},{self._1m_high=},{self._1m_low=},{self._1m_close=},{self._1m_volume=},{self._1m_ask_vol=},{self._1m_bid_vol=}")
            current_df = pd.DataFrame({"market":[market], "timestamp":[timestamp], "open": [self._1m_open], "high": [self._1m_high], "low":[self._1m_low], "close": [self._1m_close],
                                                                "volume": [self._1m_volume], "ask_vol": [self._1m_ask_vol], "bid_vol": [self._1m_bid_vol]}, index = [dt2str(self._1m_last_min_dt)])
            current_df.index = pd.to_datetime(current_df.index)
            self._1m_df = pd.concat([self._1m_df, current_df])

            self._1m_last_min_dt = tt_dt
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

    def get_1m_df(self):
        print(f"{self.coin} - collect coin info now")
        return self._1m_df


class UpbitWebsocketMgr:
    def __init__(self):
        pass

    def start_websocket(self):
        payload = {
            'access_key' : "kOzKkEnwOtxhVptCkxZE7UHlFvWzQWSBR8WpKENG",
            'nonce'      : str(uuid.uuid4()),
        }

        jwt_token = jwt.encode(payload, "cPZvKf82vX2P2l8boxTPK1oDyO9Da2k6rMhcZfz8");
        authorization_token = 'Bearer {}'.format(jwt_token)
        headers = {"Authorization" : authorization_token}

        ws_app = websocket.WebSocketApp("wss://api.upbit.com/websocket/v1",
                                        header = headers,
                                        on_message = self.on_message,
                                        on_open = self.on_connect,
                                        on_error = self.on_error,
                                        on_close = self.on_close)

        # self.collect_1m()
        schedule.every(5).seconds.do(self.collect_1m)

        ws_app.run_forever()

        # svr_korea_dt = datetime.datetime.now().astimezone()
        # svr_sec = svr_korea_dt.second
        # sleep_time = 62.0 - svr_sec
        # if sleep_time < 0 :
        #     sleep_time = 1
        # print(f"current - {svr_korea_dt}, sleep {sleep_time} seconds..")
        # time.sleep(sleep_time)




    def on_message(self, ws, message) :
        # do something
        data = message.decode('utf-8')
        trade_json = json.loads(data)
        print(trade_json)
        coin = trade_json["cd"]
        if coin not in self.coin_1m_cdls:
            self.coin_1m_cdls[coin] = Coin1M_OHLCV(code)
        self.coin_1m_cdls[coin].update(trade_json)


    def on_connect(self, ws) :
        print("connected!")
        # Request after connection
        # codes = ["KRW-BTC","KRW-ETH","KRW-XRP","KRW-TRX","KRW-ETC","KRW-ADA", "KRW-DOGE","KRW-BTG","KRW-EOS","KRW-BCH","KRW-LTC","KRW-XLM"],
        codes = ["KRW-BTC", "KRW-ETH"]
        subscribe_fmt = [
            {"ticket" : "bt4"},
            {
                "type"           : "trade",
                "codes"          : codes,
                "isOnlyRealtime" : True
            },
            {"format" : "SIMPLE"}
        ]
        subscribe_data = json.dumps(subscribe_fmt)

        self.coin_1m_cdls = {}
        for code in codes:
            self.coin_1m_cdls[code] = Coin1M_OHLCV(code)

        ws.send(subscribe_data)

    def on_error(self, ws, err) :
        print(err)

    def on_close(self, ws, status_code, msg) :
        print("closed!")

    def collect_1m(self,queue):
        print(f"collect_1m:{dt2str(now_dt())}")
        for coin in self.coin_1m_cdls:
            print(self.coin_1m_cdls[coin].get_1m_df().head(5))


if __name__ == '__main__':
    uwm = UpbitWebsocketMgr()
    uwm.start_websocket()
