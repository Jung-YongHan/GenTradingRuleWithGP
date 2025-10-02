from bt4.Constants import CandleType, ExType

QUOTE_PARAMS = {

    ## 'exchanges' lists all exchanges that the exchange quote dispatcher will fetch quotes and distributes them.
    # 'exchanges' : (ExType.upbit, ExType.binanceusdm, ExType.binance),
    'exchanges' : (ExType.upbit, ),

    ## 'markets' and 'candles' for upbits
    ## If it does not list markets, quotes of all markets that the upbit exchange support will be supported.
    ## if it does not list cdl_types_needed, all candles(MINUTES_1, MINUTES_3, MINUTES_5, MINUTES_15, CandleType.MINUTES_30,
    ##  HOUR, HOUR4, DAYS_TF,DAYS) will be supported.
    # ExType.upbit : {
    #     'markets' : [],             # for dispatching all markets
    #     'cdl_types_needed' : []     # for dispatching all candles of each markets
    # },

    ExType.upbit : {
        # 'markets' : ['KRW-BTC', 'KRW-ETH', 'KRW-XRP'],
        'markets' : ['KRW-BTC'],
        # 'markets':'KRW-BTC KRW-ETH KRW-XRP KRW-SOL KRW-DOGE KRW-ADA KRW-SHIB KRW-AVAX KRW-TRX KRW-DOT KRW-BCH KRW-LINK KRW-NEAR KRW-MATIC KRW-ETC KRW-HBAR KRW-APT KRW-ATOM KRW-MNT KRW-CRO'.split(), #정보를 읽어와 진행 필요
        'cdl_types_needed' : [  CandleType.MINUTES_1,
                                CandleType.MINUTES_3,
                                CandleType.MINUTES_5,
                                CandleType.MINUTES_15,
                                CandleType.MINUTES_30,
                                CandleType.HOUR,
                                CandleType.HOUR4,
                                CandleType.DAYS_TF,
                                CandleType.DAYS]
    },

    ExType.binance : {
        'markets' : ['BTC/USDT', 'ETH/USDT', 'XRP/USDT'],
        'cdl_types_needed' : [
                                # CandleType.MINUTES_1,
                                # CandleType.MINUTES_3,
                                # CandleType.MINUTES_5,
                                # CandleType.MINUTES_15,
                                # CandleType.MINUTES_30,
                                CandleType.HOUR,
                                CandleType.HOUR4,
                                CandleType.DAYS]
    },

    ExType.binanceusdm: {
        'markets': ['BTC/USDT', 'ETH/USDT', 'XRP/USDT'],
        'cdl_types_needed' : [
                                # CandleType.MINUTES_1,
                                # CandleType.MINUTES_3,
                                # CandleType.MINUTES_5,
                                # CandleType.MINUTES_15,
                                # CandleType.MINUTES_30,
                                CandleType.HOUR,
                                CandleType.HOUR4,
                                CandleType.DAYS]
    },

}
