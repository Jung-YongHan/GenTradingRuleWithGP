import asyncio
import ssl
import pathlib
import signal
from functools import partial
import websockets
import json

from datetime import datetime
import pytz

class Ticker:
    def __init__(self, code, timestamp, open, high, low, close, volume):
        self.code = code
        self.timestamp = timestamp
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume

    @staticmethod
    def from_json(json):
        return Ticker(
            code=json['s'],
            timestamp=datetime.fromtimestamp(json['k']['t'] / 1000, tz=pytz.timezone('Asia/Seoul')),
            open=json['k']['o'],
            high=json['k']['h'],
            low=json['k']['l'],
            close=json['k']['c'],
            volume=json['k']['v']
        )

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return (
            f'Ticker <code: {self.code}, timestamp: {self.timestamp.strftime("%Y-%m-%d %H:%M:%S")}, '
            f'open: {self.open}, high: {self.high}, low: {self.low}, close: {self.close}, volume: {self.volume}>'
        )


async def recv_ticker():
    # uri = 'wss://stream.binance.com:9443'
    # markets = ['BTCUSDT', 'ETHUSDT']
    # stream = 'kline_1m'
    #
    # params = '/'.join([f'{market.lower()}@{stream}' for market in markets])
    # uri = uri + f'/stream?streams={params}'

    uri = "wss://stream.binance.com:9443/ws"

    ssl_context = ssl.create_default_context()
    self_signed_cert = pathlib.Path(__file__).with_name("selfsigned.crt")
    ssl_context.load_verify_locations(self_signed_cert)

    # subscribe_msg = {"method": "SUBSCRIBE","params":["btcusdt@kline_1m", "ethusdt@kline_1m"],"id": 1}
    # subscribe_msg = {"method" : "SUBSCRIBE", "params" : ["btcusdt@kline_1m"], "id" : 1}
    subscribe_msg = {
        "method" : "SUBSCRIBE",
        "params" : [
            # "btcusdt@aggTrade",
            # "btcusdt@depth",
            # "btcusdt@depth5",
            # "btcusdt@depth10",
            # "btcusdt@depth20",
            # "btcusdt@miniTicker",
            # "btcusdt@ticker",
            # "btcusdt@bookTicker",
            "btcusdt@trade"
        ],
        "id"     : 1
    }

    async with websockets.connect(uri, ssl=ssl_context, ping_interval=60, ping_timeout=180) as websocket:

        await websocket.send(json.dumps( subscribe_msg))

        while True :
            response = await websocket.recv()
            trade_json = json.loads(response)
            print(trade_json)

asyncio.get_event_loop().run_until_complete(recv_ticker())


