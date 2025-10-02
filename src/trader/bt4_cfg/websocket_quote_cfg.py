from bt4.Constants import ExType, CandleType
from bt4.model.storage_mgr import StrategyStorage

'''
This parameter settings for web socket
'''



WS_PARAMS = {
    ExType.upbit: {
        "uri": "wss://api.upbit.com/websocket/v1",
        "auth_type" : "jwt_token", ## "jwt_token" -> upbit, None -> bithumb, "ssl" -> binance
        "auth_extra" : {
            "usr_id" : "7abb8d90-fdfe-4ebb-a8dd-36fb6e9fd68c"
        },
        # "markets" : [],             # "markets":[] ==> For all markets from upbit
        "markets"  : ["KRW-BTC"],
        # "markets" : ["KRW-BTC", "KRW-ETH", "KRW-XRP"],  # "markets":[] ==> For all markets from upbit
        "supported_candles" : [CandleType.MINUTES_1, CandleType.MINUTES_3, CandleType.MINUTES_5,
                               CandleType.MINUTES_15, CandleType.MINUTES_30, CandleType.HOUR,
                               CandleType.HOUR4, CandleType.DAYS_TF, CandleType.DAYS],
    },
    ExType.bithumb: {
        "uri": "wss://pubwss.bithumb.com/pub/ws",
        "auth_type": None,
        # "markets" : [],             # "markets":[] ==> For all markets from upbit
        # "markets"  : ["KRW-BTC"],
        "markets" : ["KRW-BTC", "KRW-ETH", "KRW-XRP"],  # "markets":[] ==> For all markets from upbit
        "supported_candles" : [CandleType.MINUTES_1, CandleType.MINUTES_3, CandleType.MINUTES_5,
                               CandleType.MINUTES_15, CandleType.MINUTES_30, CandleType.HOUR,
                               CandleType.HOUR4, CandleType.DAYS_TF, CandleType.DAYS],
    },
    ExType.binance : {
        "uri"               : "wss://stream.binance.com:9443/ws",
        "auth_type"     : "ssl",
        "auth_extra"        : {
            "ssl_path" : "selfsigned.crt"
            },
        # "markets" : [],             # "markets":[] ==> For all markets from upbit
        "markets"           : ["USDT-BTC", "USDT-ETH", "USDT-XRP"],
        "supported_candles" : [CandleType.MINUTES_1, CandleType.MINUTES_3, CandleType.MINUTES_5,
                               CandleType.MINUTES_15, CandleType.MINUTES_30, CandleType.HOUR,
                               CandleType.HOUR4, CandleType.DAYS_TF, CandleType.DAYS],
    },
    "common": {
        "enable_log_1m": True,
        "enable_log_remainders": False,
        "enable_log_tick": False
    }
}