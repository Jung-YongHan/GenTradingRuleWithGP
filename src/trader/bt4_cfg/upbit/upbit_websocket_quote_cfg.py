from bt4.Constants import ExType, CandleType

'''
This parameter settins are only for upbit
'''
WEB_SOCKET_PARAMS = {
    "access_key" : "kOzKkEnwOtxhVptCkxZE7UHlFvWzQWSBR8WpKENG",
    "secrete_key" : "cPZvKf82vX2P2l8boxTPK1oDyO9Da2k6rMhcZfz8",
    # "markets" : [],             # "markets":[] ==> For all markets from upbit
    "markets" : ["KRW-BTC"],
    # "markets" : ["KRW-BTC", "KRW-ETH", "KRW-XRP"],  # "markets":[] ==> For all markets from upbit
    "supported_candles" : [CandleType.MINUTES_1, CandleType.MINUTES_3, CandleType.MINUTES_5,
                          CandleType.MINUTES_15, CandleType.MINUTES_30, CandleType.HOUR,
                          CandleType.HOUR4, CandleType.DAYS_TF, CandleType.DAYS],  # "cdl_types_needed":[] ==> fetch all candles of the desiginated markets

    "enable_log_1m" : True,
    "enable_log_remainders" : True,
    "enable_log_tick" : False
}