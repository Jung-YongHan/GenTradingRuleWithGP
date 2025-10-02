import asyncio
import datetime
import sys
import threading
import json
import time
import pytz
import pandas as pd
from kafka import KafkaProducer
from kafka.errors import KafkaTimeoutError
import jwt
import redis as redis
import websockets

from bt4.GlobalProperties import QUOTE_REDIS_IP_ADDR, REDIS_PORT, kafka_bootstrap_svr, kafka_channel_quote_pull_request
from bt4.Constants import ExType, CandleType
from bt4.utils.mylog import init_log
from bt4.utils.python_utils import now_dt, str2dt, dt2str, to_kst_time, get_1min_before_dt, start_timing, end_n_elapsed_time, dt2str2

log = init_log()

def_num_cdles = 300
def_num_cdles_1h = 5000

WEB_SOCKET_PARAMS = {
    ExType.upbit: {
        "uri": "wss://api.upbit.com/websocket/v1",
        "auth_required": True,
        "access_key": "kOzKkEnwOtxhVptCkxZE7UHlFvWzQWSBR8WpKENG",
        "secret_key": "cPZvKf82vX2P2l8boxTPK1oDyO9Da2k6rMhcZfz8",
    },
    ExType.bithumb: {
        "uri": "wss://pubwss.bithumb.com/pub/ws",
        "auth_required": False,
    },
    "common": {
        "markets": [],
        "supported_candles": [
            CandleType.MINUTES_1, CandleType.MINUTES_3, CandleType.MINUTES_5,
            CandleType.MINUTES_15, CandleType.MINUTES_30, CandleType.HOUR,
            CandleType.HOUR4, CandleType.DAYS_TF, CandleType.DAYS
        ],
        "enable_log_1m": False,
        "enable_log_remainders": False,
        "enable_log_tick": False
    }
}

class Coin1M_OHLCV:
    def __init__(self, coin):
        self.coin = coin
        self._1m_open = 0
        self._1m_high = 0
        self._1m_low = 0
        self._1m_close = 0
        self._1m_volume = 0
        self._1m_last_min_dt = now_dt()
        self._1m_df = pd.DataFrame(columns=["market", "open", "high", "low", "close", "vol"])
        self.lock = threading.Lock()

    def update(self, trade_json):
        if not all(k in trade_json for k in ["cd", "tp", "tv", "ttm"]):
            log.error("Missing keys in trade JSON")
            return
        coin = trade_json["cd"]
        price = trade_json["tp"]
        volume = trade_json["tv"]
        timestamp = trade_json["ttm"]
        pass

    def get_cld_dfs(self, desired_kst_time_dt):
        return self._1m_df

class WebSocketClientFactory:
    @staticmethod
    def create_client(ex_type):
        params = WEB_SOCKET_PARAMS[ex_type]
        return WebSocketClient(
            uri=params["uri"],
            auth_required=params.get("auth_required", False),
            access_key=params.get("access_key"),
            secret_key=params.get("secret_key"),
            markets=WEB_SOCKET_PARAMS["common"]["markets"]
        )

class WebSocketClient:
    def __init__(self, uri, auth_required, access_key=None, secret_key=None, markets=None):
        self.uri = uri
        self.auth_required = auth_required
        self.access_key = access_key
        self.secret_key = secret_key
        self.running = True
        self.markets = markets or []
        self.coin_1m_cdl_mgrs = {coin: Coin1M_OHLCV(coin) for coin in self.markets}

    def generate_jwt_token(self):
        if not self.auth_required:
            return None
        payload = {
            "access_key": self.access_key,
            "nonce": int(time.time() * 1000)
        }
        token = jwt.encode(payload, self.secret_key, algorithm="HS256")
        return token

    async def connect(self):
        while self.running:
            try:
                headers = {}
                if self.auth_required:
                    token = self.generate_jwt_token()
                    headers = {"Authorization": f"Bearer {token}"}

                async with websockets.connect(self.uri, extra_headers=headers, ping_interval=60) as websocket:
                    subscribe_msg = self._get_subscription_message()
                    await websocket.send(json.dumps(subscribe_msg))
                    log.debug(f"Connected to WebSocket at {self.uri}.")

                    while self.running:
                        response = await websocket.recv()
                        trade_json = json.loads(response)
                        coin = trade_json.get("cd")
                        if not coin:
                            log.warning("No coin identifier in message")
                            continue
                        if coin not in self.coin_1m_cdl_mgrs:
                            self.coin_1m_cdl_mgrs[coin] = Coin1M_OHLCV(coin)
                        self.coin_1m_cdl_mgrs[coin].update(trade_json)

            except (websockets.ConnectionClosed, websockets.InvalidURI, websockets.InvalidHandshake) as e:
                log.error(f"Connection error: {e}. Reconnecting in 5 seconds...")
                await asyncio.sleep(5)

    def _get_subscription_message(self):
        if "upbit" in self.uri:
            return [
                {"ticket": "test"},
                {"type": "trade", "codes": self.markets},
                {"format": "SIMPLE"}
            ]
        elif "bithumb" in self.uri:
            return [{"type": "transaction", "symbols": self.markets}]

    def start(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.connect())

    def stop(self):
        self.running = False

def start_websocket(ex_type):
    websocket_client = WebSocketClientFactory.create_client(ex_type)
    websocket_thread = threading.Thread(target=websocket_client.start)
    websocket_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        websocket_client.stop()
        websocket_thread.join()
        log.info("Stopped.")

if __name__ == '__main__':
    # if len(sys.argv) != 2:
    #     print("Usage: python script.py -extype [upbit|bithumb]")
    #     sys.exit(1)
    # extype_arg = sys.argv[1]

    # if extype_arg == "-extype upbit":
    start_websocket(ExType.upbit)

    # elif extype_arg == "-extype bithumb":

    start_websocket(ExType.bithumb)

    # else:
    #     print("Invalid exchange type. Use 'upbit' or 'bithumb'.")
    #     sys.exit(1)
