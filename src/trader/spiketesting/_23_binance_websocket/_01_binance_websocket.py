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
    uri = 'wss://stream.binance.com:9443'
    markets = ['BTCUSDT', 'ETHUSDT']
    stream = 'kline_1m'

    params = '/'.join([f'{market.lower()}@{stream}' for market in markets])
    uri = uri + f'/stream?streams={params}'

    ssl_context = ssl.create_default_context()
    self_signed_cert = pathlib.Path(__file__).with_name("selfsigned.crt")
    ssl_context.load_verify_locations(self_signed_cert)

    async with websockets.connect(uri, ssl=ssl_context, ping_interval=60, ping_timeout=180) as websocket:
        var = asyncio.Event()

        def sigint_handler(var, signal, frame):
            print('< recv SIGINT')
            var.set()

        signal.signal(signal.SIGINT, partial(sigint_handler, var))

        while not var.is_set():
            recv_data = await websocket.recv()
            res = json.loads(recv_data)['data']
            print(f"> {res}")

asyncio.get_event_loop().run_until_complete(recv_ticker())


