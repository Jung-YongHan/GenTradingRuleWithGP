
PARAM_QUOTE_CONNECTOR = 'connector'
PARAM_MARKET = 'markets'
PARAM_TA_INDICATORS = 'ta_indicators'
PARAM_TAI_MA = 'ma'
PARAM_TAI_RSI = 'rsi'
PARAM_TAI_BB_PRICE = 'bb_price'
PARAM_TIMEFRAME_HOURS = 'timeframe_hours'

QUOTE_DISPATCHER_PARAMS = {
    #################################################################################################
    ## Target Quote Connector
    'connector' : 'Upbit',

    #################################################################################################
    ## Target Markets
    'markets': ['KRW-BTC', 'KRW-ETH', 'KRW-XRP'],
    # 'markets': ['KRW-BTC', 'KRW-ETH', 'KRW-XRP', 'KRW-SAND', 'KRW-ETC', 'KRW-WAVES'],

    # 'markets' : ['KRW-BTC','KRW-ETH' ,'KRW-MTL','KRW-XRP','KRW-SRM' ,'KRW-SAND' ,'KRW-DOT' ,'KRW-ETC' ,
    #                     'KRW-PLA','KRW-DOGE','KRW-ADA' ,'KRW-AHT' ,'KRW-KAVA' ,'KRW-LSK' ,'KRW-QTUM' ,'KRW-BTG' ,'KRW-EOS',
    #                     'KRW-TRX','KRW-XTZ','KRW-BCH'],

    #################################################################################################
    ## Timeframe support
    'timeframe_hours' : [0 ,1 ,2 ,3 ,4 ,5 ,6 ,7 ,8 ,9 ,10 ,11 ,12 ,13 ,14 ,15 ,16 ,17 ,18 ,19 ,20 ,21 ,22 ,23], # It can be accessed by 'DAY_7', 'DAY_8', 'DAY_...'
    # 'timeframe_hours' : [], # It can be accessed by 'DAY_7', 'DAY_8', 'DAY_...'

    #################################################################################################
    ##### Indicator List for Target Markets
    'ta_indicators' : ['vol', 'vol5', 'range', 'vol_4h', 'vol5_4h',
                       'ma3', 'ma5', 'ma5_1h', 'ma10', 'ma20', 'ma60',
                       # 'plus_di', 'minus_di', 'plus_di_4h', 'minus_di_4h'     ## for SWKIM1 Strategy
                       # 'ma5_1h', 'ma48_1h', 'ma72_1h', 'ma120_1h',

                       ## for Timeframes for ws_hdg, sws_hdg
                       'ma5_0', 'ma5_1', 'ma5_2', 'ma5_3', 'ma5_4', 'ma5_5', 'ma5_6', 'ma5_7', 'ma5_8' ,'ma5_9',
                       'ma5_10' ,'ma5_11' ,'ma5_12' ,'ma5_13' ,'ma5_14' ,'ma5_15' ,'ma5_16' ,'ma5_17' ,'ma5_18'
                      ,'ma5_19',
                       'ma5_20' ,'ma5_21' ,'ma5_22' ,'ma5_23',

                       ## for Timeframes for sws_hdg
                       'ma3_0', 'ma3_1', 'ma3_2', 'ma3_3', 'ma3_4', 'ma3_5', 'ma3_6', 'ma3_7', 'ma3_8', 'ma3_9',
                       'ma3_10', 'ma3_11', 'ma3_12', 'ma3_13', 'ma3_14', 'ma3_15', 'ma3_16', 'ma3_17', 'ma3_18',
                       'ma3_19' ,'ma3_20', 'ma3_21', 'ma3_22', 'ma3_23',
                       'ma10_0', 'ma10_1', 'ma10_2', 'ma10_3', 'ma10_4', 'ma10_5', 'ma10_6', 'ma10_7', 'ma10_8', 'ma10_9',
                       'ma10_10', 'ma10_11', 'ma10_12', 'ma10_13', 'ma10_14', 'ma10_15', 'ma10_16', 'ma10_17', 'ma10_18',
                       'ma10_19' ,'ma10_20', 'ma10_21', 'ma10_22', 'ma10_23',
                       'ma20_0', 'ma20_1', 'ma20_2', 'ma20_3', 'ma20_4', 'ma20_5', 'ma20_6', 'ma20_7', 'ma20_8', 'ma20_9',
                       'ma20_10', 'ma20_11', 'ma20_12', 'ma20_13', 'ma20_14', 'ma20_15', 'ma20_16', 'ma20_17', 'ma20_18',
                       'ma20_19' ,'ma20_20', 'ma20_21', 'ma20_22', 'ma20_23',

                       ## Ranges for volatility breakout - hedge
                       'range_0', 'range_1', 'range_2', 'range_3', 'range_4', 'range_5',
                       'range_6', 'range_7', 'range_8', 'range_9', 'range_10',
                       'range_11', 'range_12', 'range_13', 'range_14', 'range_15',
                       'range_16', 'range_17', 'range_18', 'range_19', 'range_20',
                       'range_21', 'range_22', 'range_23',

                       # 'ma5_1h', 'ma20_1h', 'ma5_4h', 'ma20_4h',
                       # 'rsi14', 'macd', 'bb_close', 'bb_rsi14',
                       # 'atr', 'natr', 'trange'
                       'trb10' ,'trb20' ,'trb55' ,'trb4h_24' ,'ema4h_30' ,'ema4h_60' ,'ema4h_100',
                       'atr',
                       ## for Timeframes for ws_hdg, sws_hdg
                       'ema5_0', 'ema5_1', 'ema5_2', 'ema5_3', 'ema5_4', 'ema5_5', 'ema5_6', 'ema5_7', 'ema5_8', 'ema5_9',
                       'ema5_10', 'ema5_11', 'ema5_12', 'ema5_13', 'ema5_14', 'ema5_15', 'ema5_16', 'ema5_17', 'ema5_18',
                       'ema5_19',
                       'ema5_20', 'ema5_21', 'ema5_22', 'ema5_23',

                       ## for Timeframes for sws_hdg
                       'ema3_0', 'ema3_1', 'ema3_2', 'ema3_3', 'ema3_4', 'ema3_5', 'ema3_6', 'ema3_7', 'ema3_8', 'ema3_9',
                       'ema3_10', 'ema3_11', 'ema3_12', 'ema3_13', 'ema3_14', 'ema3_15', 'ema3_16', 'ema3_17', 'ema3_18',
                       'ema3_19', 'ema3_20', 'ema3_21', 'ema3_22', 'ema3_23',
                       'ema10_0', 'ema10_1', 'ema10_2', 'ema10_3', 'ema10_4', 'ema10_5', 'ema10_6', 'ema10_7', 'ema10_8',
                       'ema10_9',
                       'ema10_10', 'ema10_11', 'ema10_12', 'ema10_13', 'ema10_14', 'ema10_15', 'ema10_16', 'ema10_17',
                       'ema10_18',
                       'ema10_19', 'ema10_20', 'ema10_21', 'ema10_22', 'ema10_23',
                       'ema20_0', 'ema20_1', 'ema20_2', 'ema20_3', 'ema20_4', 'ema20_5', 'ema20_6', 'ema20_7', 'ema20_8',
                       'ema20_9',
                       'ema20_10', 'ema20_11', 'ema20_12', 'ema20_13', 'ema20_14', 'ema20_15', 'ema20_16', 'ema20_17',
                       'ema20_18',
                       'ema20_19', 'ema20_20', 'ema20_21', 'ema20_22', 'ema20_23',
                       ],

    ##### Indicator Parameters
    ## dataframe : 'DAYS'='DAYS_9', 'HOUR4', 'HOUR', 'DAYS_0',..'DAYS_23'
    'anr30' : {'function': 'anr', 'dataframe': 'DAYS', 'input': ['opening_price', 'high_price', 'low_price', 'trade_price'], 'params': [30]},  # p[0]: timeperiod
    'trb10': {'function': 'trb', 'dataframe': 'DAYS', 'input': ['high_price', 'low_price'], 'params': [10]}
    ,# p[0]: timeperiod
    'trb20': {'function': 'trb', 'dataframe': 'DAYS', 'input': ['high_price', 'low_price'], 'params': [20]}
    ,# p[0]: timeperiod
    'trb55': {'function': 'trb', 'dataframe': 'DAYS', 'input': ['high_price', 'low_price'], 'params': [55]}
    ,# p[0]: timeperiod
    'trb4h_24': {'function': 'trb', 'dataframe': 'HOUR4', 'input': ['high_price', 'low_price'], 'params': [24]}
    ,# p[0]: timeperiod
    'trb4h_48': {'function': 'trb', 'dataframe': 'HOUR4', 'input': ['high_price', 'low_price'], 'params': [48]}
    ,# p[0]: timeperiod
    'ema4h_30': {'function': 'ema', 'dataframe': 'HOUR4', 'input': ['trade_price'], 'params': [30]},  # p[0]: timeperiod
    'ema4h_60': {'function': 'ema', 'dataframe': 'HOUR4', 'input': ['trade_price'], 'params': [60]},  # p[0]: timeperiod
    'ema4h_100': {'function': 'ema', 'dataframe': 'HOUR4', 'input': ['trade_price'], 'params': [100]}
    ,# p[0]: timeperiod

    'trb4h_24':  {'function': 'trb', 'dataframe': 'HOUR4', 'input': ['high_price', 'low_price'], 'params': [24]},  # p[0]: timeperiod
    'trb4h_48':  {'function': 'trb', 'dataframe': 'HOUR4', 'input': ['high_price', 'low_price'], 'params': [48]},  # p[0]: timeperiod
    'ema4h_30':  {'function': 'ema', 'dataframe': 'HOUR4', 'input': ['trade_price'], 'params': [30]},  # p[0]: timeperiod
    'ema4h_60':  {'function': 'ema', 'dataframe': 'HOUR4', 'input': ['trade_price'], 'params': [60]},  # p[0]: timeperiod
    'ema4h_100':  {'function': 'ema', 'dataframe': 'HOUR4', 'input': ['trade_price'], 'params': [100]},  # p[0]: timeperiod

    'ma5_0':  {'function': 'sma', 'dataframe': 'DAYS_0', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    'ma5_1':  {'function': 'sma', 'dataframe': 'DAYS_1', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    'ma5_2':  {'function': 'sma', 'dataframe': 'DAYS_2', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    'ma5_3':  {'function': 'sma', 'dataframe': 'DAYS_3', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    'ma5_4':  {'function': 'sma', 'dataframe': 'DAYS_4', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    'ma5_5':  {'function': 'sma', 'dataframe': 'DAYS_5', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    'ma5_6':  {'function': 'sma', 'dataframe': 'DAYS_6', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    'ma5_7':  {'function': 'sma', 'dataframe': 'DAYS_7', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    'ma5_8':  {'function': 'sma', 'dataframe': 'DAYS_8', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    'ma5_9':  {'function': 'sma', 'dataframe': 'DAYS_9', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    'ma5_10': {'function': 'sma', 'dataframe': 'DAYS_10', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    'ma5_11': {'function': 'sma', 'dataframe': 'DAYS_11', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    'ma5_12': {'function': 'sma', 'dataframe': 'DAYS_12', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    'ma5_13': {'function': 'sma', 'dataframe': 'DAYS_13', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    'ma5_14': {'function': 'sma', 'dataframe': 'DAYS_14', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    'ma5_15': {'function': 'sma', 'dataframe': 'DAYS_15', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    'ma5_16': {'function': 'sma', 'dataframe': 'DAYS_16', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    'ma5_17': {'function': 'sma', 'dataframe': 'DAYS_17', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    'ma5_18': {'function': 'sma', 'dataframe': 'DAYS_18', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    'ma5_19': {'function': 'sma', 'dataframe': 'DAYS_19', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    'ma5_20': {'function': 'sma', 'dataframe': 'DAYS_20', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    'ma5_21': {'function': 'sma', 'dataframe': 'DAYS_21', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    'ma5_22': {'function': 'sma', 'dataframe': 'DAYS_22', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    'ma5_23': {'function': 'sma', 'dataframe': 'DAYS_23', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod

    'ma3_0': {'function': 'sma', 'dataframe': 'DAYS_0', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    'ma3_1': {'function': 'sma', 'dataframe': 'DAYS_1', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    'ma3_2': {'function': 'sma', 'dataframe': 'DAYS_2', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    'ma3_3': {'function': 'sma', 'dataframe': 'DAYS_3', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    'ma3_4': {'function': 'sma', 'dataframe': 'DAYS_4', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    'ma3_5': {'function': 'sma', 'dataframe': 'DAYS_5', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    'ma3_6': {'function': 'sma', 'dataframe': 'DAYS_6', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    'ma3_7': {'function': 'sma', 'dataframe': 'DAYS_7', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    'ma3_8': {'function': 'sma', 'dataframe': 'DAYS_8', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    'ma3_9': {'function': 'sma', 'dataframe': 'DAYS_9', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    'ma3_10': {'function': 'sma', 'dataframe': 'DAYS_10', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    'ma3_11': {'function': 'sma', 'dataframe': 'DAYS_11', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    'ma3_12': {'function': 'sma', 'dataframe': 'DAYS_12', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    'ma3_13': {'function': 'sma', 'dataframe': 'DAYS_13', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    'ma3_14': {'function': 'sma', 'dataframe': 'DAYS_14', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    'ma3_15': {'function': 'sma', 'dataframe': 'DAYS_15', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    'ma3_16': {'function': 'sma', 'dataframe': 'DAYS_16', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    'ma3_17': {'function': 'sma', 'dataframe': 'DAYS_17', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    'ma3_18': {'function': 'sma', 'dataframe': 'DAYS_18', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    'ma3_19': {'function': 'sma', 'dataframe': 'DAYS_19', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    'ma3_20': {'function': 'sma', 'dataframe': 'DAYS_20', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    'ma3_21': {'function': 'sma', 'dataframe': 'DAYS_21', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    'ma3_22': {'function': 'sma', 'dataframe': 'DAYS_22', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    'ma3_23': {'function': 'sma', 'dataframe': 'DAYS_23', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod

    'ma10_0': {'function': 'sma', 'dataframe': 'DAYS_0', 'input': ['trade_price'], 'params': [10]},  # p[0]: timeperiod
    'ma10_1': {'function': 'sma', 'dataframe': 'DAYS_1', 'input': ['trade_price'], 'params': [10]},  # p[0]: timeperiod
    'ma10_2': {'function': 'sma', 'dataframe': 'DAYS_2', 'input': ['trade_price'], 'params': [10]},  # p[0]: timeperiod
    'ma10_3': {'function': 'sma', 'dataframe': 'DAYS_3', 'input': ['trade_price'], 'params': [10]},  # p[0]: timeperiod
    'ma10_4': {'function': 'sma', 'dataframe': 'DAYS_4', 'input': ['trade_price'], 'params': [10]},  # p[0]: timeperiod
    'ma10_5': {'function': 'sma', 'dataframe': 'DAYS_5', 'input': ['trade_price'], 'params': [10]},  # p[0]: timeperiod
    'ma10_6': {'function': 'sma', 'dataframe': 'DAYS_6', 'input': ['trade_price'], 'params': [10]},  # p[0]: timeperiod
    'ma10_7': {'function': 'sma', 'dataframe': 'DAYS_7', 'input': ['trade_price'], 'params': [10]},  # p[0]: timeperiod
    'ma10_8': {'function': 'sma', 'dataframe': 'DAYS_8', 'input': ['trade_price'], 'params': [10]},  # p[0]: timeperiod
    'ma10_9': {'function': 'sma', 'dataframe': 'DAYS_9', 'input': ['trade_price'], 'params': [10]},  # p[0]: timeperiod
    'ma10_10': {'function': 'sma', 'dataframe': 'DAYS_10', 'input': ['trade_price'], 'params': [10]},  # p[0]: timeperiod
    'ma10_11': {'function': 'sma', 'dataframe': 'DAYS_11', 'input': ['trade_price'], 'params': [10]},  # p[0]: timeperiod
    'ma10_12': {'function': 'sma', 'dataframe': 'DAYS_12', 'input': ['trade_price'], 'params': [10]},  # p[0]: timeperiod
    'ma10_13': {'function': 'sma', 'dataframe': 'DAYS_13', 'input': ['trade_price'], 'params': [10]},  # p[0]: timeperiod
    'ma10_14': {'function': 'sma', 'dataframe': 'DAYS_14', 'input': ['trade_price'], 'params': [10]},  # p[0]: timeperiod
    'ma10_15': {'function': 'sma', 'dataframe': 'DAYS_15', 'input': ['trade_price'], 'params': [10]},  # p[0]: timeperiod
    'ma10_16': {'function': 'sma', 'dataframe': 'DAYS_16', 'input': ['trade_price'], 'params': [10]},  # p[0]: timeperiod
    'ma10_17': {'function': 'sma', 'dataframe': 'DAYS_17', 'input': ['trade_price'], 'params': [10]},  # p[0]: timeperiod
    'ma10_18': {'function': 'sma', 'dataframe': 'DAYS_18', 'input': ['trade_price'], 'params': [10]},  # p[0]: timeperiod
    'ma10_19': {'function': 'sma', 'dataframe': 'DAYS_19', 'input': ['trade_price'], 'params': [10]},  # p[0]: timeperiod
    'ma10_20': {'function': 'sma', 'dataframe': 'DAYS_20', 'input': ['trade_price'], 'params': [10]},  # p[0]: timeperiod
    'ma10_21': {'function': 'sma', 'dataframe': 'DAYS_21', 'input': ['trade_price'], 'params': [10]},  # p[0]: timeperiod
    'ma10_22': {'function': 'sma', 'dataframe': 'DAYS_22', 'input': ['trade_price'], 'params': [10]},  # p[0]: timeperiod
    'ma10_23': {'function': 'sma', 'dataframe': 'DAYS_23', 'input': ['trade_price'], 'params': [10]},  # p[0]: timeperiod

    'ma20_0': {'function': 'sma', 'dataframe': 'DAYS_0', 'input': ['trade_price'], 'params': [20]},  # p[0]: timeperiod
    'ma20_1': {'function': 'sma', 'dataframe': 'DAYS_1', 'input': ['trade_price'], 'params': [20]},  # p[0]: timeperiod
    'ma20_2': {'function': 'sma', 'dataframe': 'DAYS_2', 'input': ['trade_price'], 'params': [20]},  # p[0]: timeperiod
    'ma20_3': {'function': 'sma', 'dataframe': 'DAYS_3', 'input': ['trade_price'], 'params': [20]},  # p[0]: timeperiod
    'ma20_4': {'function': 'sma', 'dataframe': 'DAYS_4', 'input': ['trade_price'], 'params': [20]},  # p[0]: timeperiod
    'ma20_5': {'function': 'sma', 'dataframe': 'DAYS_5', 'input': ['trade_price'], 'params': [20]},  # p[0]: timeperiod
    'ma20_6': {'function': 'sma', 'dataframe': 'DAYS_6', 'input': ['trade_price'], 'params': [20]},  # p[0]: timeperiod
    'ma20_7': {'function': 'sma', 'dataframe': 'DAYS_7', 'input': ['trade_price'], 'params': [20]},  # p[0]: timeperiod
    'ma20_8': {'function': 'sma', 'dataframe': 'DAYS_8', 'input': ['trade_price'], 'params': [20]},  # p[0]: timeperiod
    'ma20_9': {'function': 'sma', 'dataframe': 'DAYS_9', 'input': ['trade_price'], 'params': [20]},  # p[0]: timeperiod
    'ma20_10': {'function': 'sma', 'dataframe': 'DAYS_10', 'input': ['trade_price'], 'params': [20]},    # p[0]: timeperiod
    'ma20_11': {'function': 'sma', 'dataframe': 'DAYS_11', 'input': ['trade_price'], 'params': [20]},    # p[0]: timeperiod
    'ma20_12': {'function': 'sma', 'dataframe': 'DAYS_12', 'input': ['trade_price'], 'params': [20]},    # p[0]: timeperiod
    'ma20_13': {'function': 'sma', 'dataframe': 'DAYS_13', 'input': ['trade_price'], 'params': [20]},    # p[0]: timeperiod
    'ma20_14': {'function': 'sma', 'dataframe': 'DAYS_14', 'input': ['trade_price'], 'params': [20]},    # p[0]: timeperiod
    'ma20_15': {'function': 'sma', 'dataframe': 'DAYS_15', 'input': ['trade_price'], 'params': [20]},    # p[0]: timeperiod
    'ma20_16': {'function': 'sma', 'dataframe': 'DAYS_16', 'input': ['trade_price'], 'params': [20]},    # p[0]: timeperiod
    'ma20_17': {'function': 'sma', 'dataframe': 'DAYS_17', 'input': ['trade_price'], 'params': [20]},    # p[0]: timeperiod
    'ma20_18': {'function': 'sma', 'dataframe': 'DAYS_18', 'input': ['trade_price'], 'params': [20]},    # p[0]: timeperiod
    'ma20_19': {'function': 'sma', 'dataframe': 'DAYS_19', 'input': ['trade_price'], 'params': [20]},    # p[0]: timeperiod
    'ma20_20': {'function': 'sma', 'dataframe': 'DAYS_20', 'input': ['trade_price'], 'params': [20]},    # p[0]: timeperiod
    'ma20_21': {'function': 'sma', 'dataframe': 'DAYS_21', 'input': ['trade_price'], 'params': [20]},    # p[0]: timeperiod
    'ma20_22': {'function': 'sma', 'dataframe': 'DAYS_22', 'input': ['trade_price'], 'params': [20]},    # p[0]: timeperiod
    'ma20_23': {'function': 'sma', 'dataframe': 'DAYS_23', 'input': ['trade_price'], 'params': [20]},    # p[0]: timeperiod

    'vol' :    {'function': 'vol', 'dataframe': 'DAYS', 'input': ['opening_price', 'high_price', 'low_price'], 'params': []}, # p[0]: timeperiod
    'vol5' :   {'function': 'sma', 'dataframe' :'DAYS', 'input': ['vol'], 'params': [5]}, # p[0]: timeperiod

    'range':   {'function': 'range', 'dataframe': 'DAYS', 'input': ['high_price', 'low_price'] ,'params': []},  # p[0]: timeperiod
    'range_0': {'function': 'range_c', 'dataframe': 'DAYS_0',   'input': ['high_price', 'low_price', 'trade_price']
                ,'params': []},  # p[0]: timeperiod
    'range_1': {'function': 'range_c', 'dataframe': 'DAYS_1',   'input': ['high_price', 'low_price', 'trade_price']
                ,'params': []},  # p[0]: timeperiod
    'range_2': {'function': 'range_c', 'dataframe': 'DAYS_2',   'input': ['high_price', 'low_price', 'trade_price']
                ,'params': []},  # p[0]: timeperiod
    'range_3': {'function': 'range_c', 'dataframe': 'DAYS_3',   'input': ['high_price', 'low_price', 'trade_price']
                ,'params': []},  # p[0]: timeperiod
    'range_4': {'function': 'range_c', 'dataframe': 'DAYS_4',   'input': ['high_price', 'low_price', 'trade_price']
                ,'params': []},  # p[0]: timeperiod
    'range_5': {'function': 'range_c', 'dataframe': 'DAYS_5',   'input': ['high_price', 'low_price', 'trade_price']
                ,'params': []},  # p[0]: timeperiod
    'range_6': {'function': 'range_c', 'dataframe': 'DAYS_6',   'input': ['high_price', 'low_price', 'trade_price']
                ,'params': []},  # p[0]: timeperiod
    'range_7': {'function': 'range_c', 'dataframe': 'DAYS_7',   'input': ['high_price', 'low_price', 'trade_price']
                ,'params': []},  # p[0]: timeperiod
    'range_8': {'function': 'range_c', 'dataframe': 'DAYS_8',   'input': ['high_price', 'low_price', 'trade_price']
                ,'params': []},  # p[0]: timeperiod
    'range_9': {'function': 'range_c', 'dataframe': 'DAYS_9',   'input': ['high_price', 'low_price', 'trade_price']
                ,'params': []},  # p[0]: timeperiod
    'range_10': {'function': 'range_c', 'dataframe': 'DAYS_10', 'input': ['high_price', 'low_price', 'trade_price']
                 ,'params': []},  # p[0]: timeperiod
    'range_11': {'function': 'range_c', 'dataframe': 'DAYS_11', 'input': ['high_price', 'low_price', 'trade_price']
                 ,'params': []},  # p[0]: timeperiod
    'range_12': {'function': 'range_c', 'dataframe': 'DAYS_12', 'input': ['high_price', 'low_price', 'trade_price']
                 ,'params': []},  # p[0]: timeperiod
    'range_13': {'function': 'range_c', 'dataframe': 'DAYS_13', 'input': ['high_price', 'low_price', 'trade_price']
                 ,'params': []},  # p[0]: timeperiod
    'range_14': {'function': 'range_c', 'dataframe': 'DAYS_14', 'input': ['high_price', 'low_price', 'trade_price']
                 ,'params': []},  # p[0]: timeperiod
    'range_15': {'function': 'range_c', 'dataframe': 'DAYS_15', 'input': ['high_price', 'low_price', 'trade_price']
                 ,'params': []},  # p[0]: timeperiod
    'range_16': {'function': 'range_c', 'dataframe': 'DAYS_16', 'input': ['high_price', 'low_price', 'trade_price']
                 ,'params': []},  # p[0]: timeperiod
    'range_17': {'function': 'range_c', 'dataframe': 'DAYS_17', 'input': ['high_price', 'low_price', 'trade_price']
                 ,'params': []},  # p[0]: timeperiod
    'range_18': {'function': 'range_c', 'dataframe': 'DAYS_18', 'input': ['high_price', 'low_price', 'trade_price']
                 ,'params': []},  # p[0]: timeperiod
    'range_19': {'function': 'range_c', 'dataframe': 'DAYS_19', 'input': ['high_price', 'low_price', 'trade_price']
                 ,'params': []},  # p[0]: timeperiod
    'range_20': {'function': 'range_c', 'dataframe': 'DAYS_20', 'input': ['high_price', 'low_price', 'trade_price']
                 ,'params': []},  # p[0]: timeperiod
    'range_21': {'function': 'range_c', 'dataframe': 'DAYS_21', 'input': ['high_price', 'low_price', 'trade_price']
                 ,'params': []},  # p[0]: timeperiod
    'range_22': {'function': 'range_c', 'dataframe': 'DAYS_22', 'input': ['high_price', 'low_price', 'trade_price']
                 ,'params': []},  # p[0]: timeperiod
    'range_23': {'function': 'range_c', 'dataframe': 'DAYS_23', 'input': ['high_price', 'low_price', 'trade_price']
                 ,'params': []},  # p[0]: timeperiod

    'vol_1h': {'function': 'vol', 'dataframe': 'HOUR', 'input': ['opening_price', 'high_price', 'low_price']
               ,'params': []},  # p[0]: timeperiod
    'vol5_1h': {'function': 'sma', 'dataframe': 'DAYS', 'input': ['vol_1h'], 'params': [5]},  # p[0]: timeperiod
    'vol_4h':  {'function': 'vol', 'dataframe': 'HOUR4', 'input': ['opening_price', 'high_price', 'low_price']
               ,'params': []},  # p[0]: timeperiod
    'vol5_4h': {'function': 'sma', 'dataframe': 'DAYS', 'input': ['vol_4h'], 'params': [5]},  # p[0]: timeperiod
    'ma3':     {'function': 'sma', 'dataframe': 'DAYS', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    'ma5':     {'function': 'sma', 'dataframe': 'DAYS', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    'ma10':    {'function': 'sma', 'dataframe': 'DAYS', 'input': ['trade_price'], 'params': [10]},  # p[0]: timeperiod
    'ma20':    {'function': 'sma', 'dataframe': 'DAYS', 'input': ['trade_price'], 'params': [20]},  # p[0]: timeperiod
    'ma60':    {'function': 'sma', 'dataframe': 'DAYS', 'input': ['trade_price'], 'params': [60]},  # p[0]: timeperiod
    'ma3_4h':  {'function': 'sma', 'dataframe': 'HOUR4', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    'ma5_4h':  {'function': 'sma', 'dataframe': 'HOUR4', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    'ma10_4h': {'function': 'sma', 'dataframe': 'HOUR4', 'input': ['trade_price'], 'params': [10]},  # p[0]: timeperiod
    'ma20_4h': {'function': 'sma', 'dataframe': 'HOUR4', 'input': ['trade_price'], 'params': [20]},  # p[0]: timeperiod
    'ma60_4h': {'function': 'sma', 'dataframe': 'HOUR4', 'input': ['trade_price'], 'params': [60]},  # p[0]: timeperiod
    'ma3_1h':  {'function': 'sma', 'dataframe': 'HOUR', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    'ma5_1h':  {'function': 'sma', 'dataframe': 'HOUR', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    'ma10_1h': {'function': 'sma', 'dataframe': 'HOUR', 'input': ['trade_price'], 'params': [10]},  # p[0]: timeperiod
    'ma20_1h': {'function': 'sma', 'dataframe': 'HOUR', 'input': ['trade_price'], 'params': [20]},  # p[0]: timeperiod
    'ma48_1h': {'function': 'sma', 'dataframe': 'HOUR', 'input': ['trade_price'], 'params': [48]},  # p[0]: timeperiod
    'ma50_1h': {'function': 'sma', 'dataframe': 'HOUR', 'input': ['trade_price'], 'params': [50]},  # p[0]: timeperiod
    'ma60_1h': {'function': 'sma', 'dataframe': 'HOUR', 'input': ['trade_price'], 'params': [60]},  # p[0]: timeperiod
    'ma72_1h': {'function': 'sma', 'dataframe': 'HOUR', 'input': ['trade_price'], 'params': [72]},  # p[0]: timeperiod
    'ma100_1h': {'function': 'sma', 'dataframe': 'HOUR', 'input': ['trade_price'], 'params': [100]},  # p[0]: timeperiod
    'ma200_1h': {'function': 'sma', 'dataframe': 'HOUR', 'input': ['trade_price'], 'params': [200]},  # p[0]: timeperiod
    'ma120_1h' :{'function': 'sma', 'dataframe': 'HOUR', 'input': ['trade_price'], 'params': [120]},  # p[0]: timeperiod
    'rsi14':   {'function': 'rsi', 'dataframe': 'DAYS', 'input': ['trade_price'], 'params': [14]}, # p[0]: timeperiod(def=14)
    'macd':    {'function': 'macd', 'dataframe': 'DAYS', 'input': ['trade_price'], 'params': [12, 26, 9]}, # p[0] : fastperiod(def=12), p[1] : slowperiod(def=26), p[2]: signalperiod (def=9)
    'bb_close' :{'function': 'bbands', 'dataframe': 'DAYS', 'input': ['trade_price'], 'params': [5, 2.0, 2.0, 0]}, # p[0] : timeperiod(def=5), p[1] : nbdevup(def=2), p[2]: nbdevdn(def=2), p[3]: matype(def=0)
    'bb_rsi14' :{'function': 'bbands', 'dataframe': 'DAYS', 'input': ['rsi14'], 'params': [5, 2.0, 2.0, 0]}
    ,# p[0] : timeperiod(def=5), p[1] : nbdevup(def=2), p[2]: nbdevdn(def=2), p[3]: matype(def=0)
    'atr':     {'function': 'atr', 'dataframe': 'DAYS', 'input': ['high_price', 'low_price', 'trade_price'], 'params': [14]},  # p[0]: timeperiod(def=14)
    'natr' :   {'function': 'atr', 'dataframe': 'DAYS', 'input': ['high_price', 'low_price', 'trade_price'], 'params': [14]}, # p[0]: timeperiod (def=14)
    'trange' : {'function': 'atr', 'dataframe': 'DAYS', 'input': ['high_price', 'low_price', 'trade_price'], 'params': []}, # p[0]: timeperiod
    'plus_di' : {'function': 'PLUS_DI', 'dataframe': 'DAYS', 'input': ['high_price', 'low_price', 'trade_price'], 'params': [14]}, # p[0]: timeperiod
    'minus_di' : {'function': 'MINUS_DI', 'dataframe': 'DAYS', 'input': ['high_price', 'low_price', 'trade_price'], 'params': [14]}, # p[0]: timeperiod
    'plus_di_4h': {'function': 'PLUS_DI', 'dataframe': 'HOUR4', 'input': ['high_price', 'low_price', 'trade_price'],
                   'params': [14]},  # p[0]: timeperiod
    'minus_di_4h': {'function': 'MINUS_DI', 'dataframe': 'HOUR4', 'input': ['high_price', 'low_price', 'trade_price'],
                    'params': [14]},  # p[0]: timeperiod
    'plus_di_0'  : {'function': 'PLUS_DI', 'dataframe': 'DAYS_0', 'input': ['high_price', 'low_price', 'trade_price'], 'params': [14]},
    'plus_di_1'  : {'function': 'PLUS_DI', 'dataframe': 'DAYS_1', 'input': ['high_price', 'low_price', 'trade_price'], 'params': [14]},
    'plus_di_2'  : {'function': 'PLUS_DI', 'dataframe': 'DAYS_2', 'input': ['high_price', 'low_price', 'trade_price'], 'params': [14]},
    'plus_di_3'  : {'function': 'PLUS_DI', 'dataframe': 'DAYS_3', 'input': ['high_price', 'low_price', 'trade_price'], 'params': [14]},
    'plus_di_4'  : {'function': 'PLUS_DI', 'dataframe': 'DAYS_4', 'input': ['high_price', 'low_price', 'trade_price'], 'params': [14]},
    'plus_di_5'  : {'function': 'PLUS_DI', 'dataframe': 'DAYS_5', 'input': ['high_price', 'low_price', 'trade_price'], 'params': [14]},
    'plus_di_6'  : {'function': 'PLUS_DI', 'dataframe': 'DAYS_6', 'input': ['high_price', 'low_price', 'trade_price'], 'params': [14]},
    'plus_di_7'  : {'function': 'PLUS_DI', 'dataframe': 'DAYS_7', 'input': ['high_price', 'low_price', 'trade_price'], 'params': [14]},
    'plus_di_8'  : {'function': 'PLUS_DI', 'dataframe': 'DAYS_8', 'input': ['high_price', 'low_price', 'trade_price'], 'params': [14]},
    'plus_di_9'  : {'function': 'PLUS_DI', 'dataframe': 'DAYS_9', 'input': ['high_price', 'low_price', 'trade_price'], 'params': [14]},
    'plus_di_10' : {'function': 'PLUS_DI', 'dataframe': 'DAYS_10', 'input': ['high_price', 'low_price', 'trade_price'], 'params': [14]},
    'plus_di_11' : {'function': 'PLUS_DI', 'dataframe': 'DAYS_11', 'input': ['high_price', 'low_price', 'trade_price'], 'params': [14]},
    'plus_di_12' : {'function': 'PLUS_DI', 'dataframe': 'DAYS_12', 'input': ['high_price', 'low_price', 'trade_price'], 'params': [14]},
    'plus_di_13' : {'function': 'PLUS_DI', 'dataframe': 'DAYS_13', 'input': ['high_price', 'low_price', 'trade_price'], 'params': [14]},
    'plus_di_14' : {'function': 'PLUS_DI', 'dataframe': 'DAYS_14', 'input': ['high_price', 'low_price', 'trade_price'], 'params': [14]},
    'plus_di_15' : {'function': 'PLUS_DI', 'dataframe': 'DAYS_15', 'input': ['high_price', 'low_price', 'trade_price'], 'params': [14]},
    'plus_di_16' : {'function': 'PLUS_DI', 'dataframe': 'DAYS_16', 'input': ['high_price', 'low_price', 'trade_price'], 'params': [14]},
    'plus_di_17' : {'function': 'PLUS_DI', 'dataframe': 'DAYS_17', 'input': ['high_price', 'low_price', 'trade_price'], 'params': [14]},
    'plus_di_18' : {'function': 'PLUS_DI', 'dataframe': 'DAYS_18', 'input': ['high_price', 'low_price', 'trade_price'], 'params': [14]},
    'plus_di_19' : {'function': 'PLUS_DI', 'dataframe': 'DAYS_19', 'input': ['high_price', 'low_price', 'trade_price'], 'params': [14]},
    'plus_di_20' : {'function': 'PLUS_DI', 'dataframe': 'DAYS_20', 'input': ['high_price', 'low_price', 'trade_price'], 'params': [14]},
    'plus_di_21' : {'function': 'PLUS_DI', 'dataframe': 'DAYS_21', 'input': ['high_price', 'low_price', 'trade_price'], 'params': [14]},
    'plus_di_22' : {'function': 'PLUS_DI', 'dataframe': 'DAYS_22', 'input': ['high_price', 'low_price', 'trade_price'], 'params': [14]},
    'plus_di_23' : {'function': 'PLUS_DI', 'dataframe': 'DAYS_23', 'input': ['high_price', 'low_price', 'trade_price'], 'params': [14]},
    'minus_di_0' : {'function': 'MINUS_DI', 'dataframe': 'DAYS_0', 'input': ['high_price', 'low_price', 'trade_price'], 'params': [14]},
    'minus_di_1' : {'function': 'MINUS_DI', 'dataframe': 'DAYS_1', 'input': ['high_price', 'low_price', 'trade_price'], 'params': [14]},
    'minus_di_2' : {'function': 'MINUS_DI', 'dataframe': 'DAYS_2', 'input': ['high_price', 'low_price', 'trade_price'], 'params': [14]},
    'minus_di_3' : {'function': 'MINUS_DI', 'dataframe': 'DAYS_3', 'input': ['high_price', 'low_price', 'trade_price'], 'params': [14]},
    'minus_di_4' : {'function': 'MINUS_DI', 'dataframe': 'DAYS_4', 'input': ['high_price', 'low_price', 'trade_price'], 'params': [14]},
    'minus_di_5' : {'function': 'MINUS_DI', 'dataframe': 'DAYS_5', 'input': ['high_price', 'low_price', 'trade_price'], 'params': [14]},
    'minus_di_6' : {'function': 'MINUS_DI', 'dataframe': 'DAYS_6', 'input': ['high_price', 'low_price', 'trade_price'], 'params': [14]},
    'minus_di_7' : {'function': 'MINUS_DI', 'dataframe': 'DAYS_7', 'input': ['high_price', 'low_price', 'trade_price'], 'params': [14]},
    'minus_di_8' : {'function': 'MINUS_DI', 'dataframe': 'DAYS_8', 'input': ['high_price', 'low_price', 'trade_price'], 'params': [14]},
    'minus_di_9' : {'function': 'MINUS_DI', 'dataframe': 'DAYS_9', 'input': ['high_price', 'low_price', 'trade_price'], 'params': [14]},
    'minus_di_10': {'function': 'MINUS_DI', 'dataframe': 'DAYS_10', 'input': ['high_price', 'low_price', 'trade_price'], 'params': [14]},
    'minus_di_11': {'function': 'MINUS_DI', 'dataframe': 'DAYS_11', 'input': ['high_price', 'low_price', 'trade_price'], 'params': [14]},
    'minus_di_12': {'function': 'MINUS_DI', 'dataframe': 'DAYS_12', 'input': ['high_price', 'low_price', 'trade_price'], 'params': [14]},
    'minus_di_13': {'function': 'MINUS_DI', 'dataframe': 'DAYS_13', 'input': ['high_price', 'low_price', 'trade_price'], 'params': [14]},
    'minus_di_14': {'function': 'MINUS_DI', 'dataframe': 'DAYS_14', 'input': ['high_price', 'low_price', 'trade_price'], 'params': [14]},
    'minus_di_15': {'function': 'MINUS_DI', 'dataframe': 'DAYS_15', 'input': ['high_price', 'low_price', 'trade_price'], 'params': [14]},
    'minus_di_16': {'function': 'MINUS_DI', 'dataframe': 'DAYS_16', 'input': ['high_price', 'low_price', 'trade_price'], 'params': [14]},
    'minus_di_17': {'function': 'MINUS_DI', 'dataframe': 'DAYS_17', 'input': ['high_price', 'low_price', 'trade_price'], 'params': [14]},
    'minus_di_18': {'function': 'MINUS_DI', 'dataframe': 'DAYS_18', 'input': ['high_price', 'low_price', 'trade_price'], 'params': [14]},
    'minus_di_19': {'function': 'MINUS_DI', 'dataframe': 'DAYS_19', 'input': ['high_price', 'low_price', 'trade_price'], 'params': [14]},
    'minus_di_20': {'function': 'MINUS_DI', 'dataframe': 'DAYS_20', 'input': ['high_price', 'low_price', 'trade_price'], 'params': [14]},
    'minus_di_21': {'function': 'MINUS_DI', 'dataframe': 'DAYS_21', 'input': ['high_price', 'low_price', 'trade_price'], 'params': [14]},
    'minus_di_22': {'function': 'MINUS_DI', 'dataframe': 'DAYS_22', 'input': ['high_price', 'low_price', 'trade_price'], 'params': [14]},
    'minus_di_23': {'function': 'MINUS_DI', 'dataframe': 'DAYS_23', 'input': ['high_price', 'low_price', 'trade_price'], 'params': [14]},

    'dema3': {'function': 'DEMA', 'dataframe': 'DAYS', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    'dema5': {'function': 'DEMA', 'dataframe': 'DAYS', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    'dema10': {'function': 'DEMA', 'dataframe': 'DAYS', 'input': ['trade_price'], 'params': [10]},  # p[0]: timeperiod
    'dema20': {'function': 'DEMA', 'dataframe': 'DAYS', 'input': ['trade_price'], 'params': [20]},  # p[0]: timeperiod

    'ema3': {'function': 'EMA', 'dataframe': 'DAYS', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    'ema5': {'function': 'EMA', 'dataframe': 'DAYS', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    'ema10': {'function': 'EMA', 'dataframe': 'DAYS', 'input': ['trade_price'], 'params': [10]},  # p[0]: timeperiod
    'ema20': {'function': 'EMA', 'dataframe': 'DAYS', 'input': ['trade_price'], 'params': [20]},  # p[0]: timeperiod

    'kama3': {'function': 'KAMA', 'dataframe': 'DAYS', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    'kama5': {'function': 'KAMA', 'dataframe': 'DAYS', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    'kama10': {'function': 'KAMA', 'dataframe': 'DAYS', 'input': ['trade_price'], 'params': [10]},  # p[0]: timeperiod
    'kama20': {'function': 'KAMA', 'dataframe': 'DAYS', 'input': ['trade_price'], 'params': [20]},  # p[0]: timeperiod

    'tema3': {'function': 'TEMA', 'dataframe': 'DAYS', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    'tema5': {'function': 'TEMA', 'dataframe': 'DAYS', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    'tema10': {'function': 'TEMA', 'dataframe': 'DAYS', 'input': ['trade_price'], 'params': [10]},  # p[0]: timeperiod
    'tema20': {'function': 'TEMA', 'dataframe': 'DAYS', 'input': ['trade_price'], 'params': [20]},  # p[0]: timeperiod

    'trima3': {'function': 'TRIMA', 'dataframe': 'DAYS', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    'trima5': {'function': 'TRIMA', 'dataframe': 'DAYS', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    'trima10': {'function': 'TRIMA', 'dataframe': 'DAYS', 'input': ['trade_price'], 'params': [10]},  # p[0]: timeperiod
    'trima20': {'function': 'TRIMA', 'dataframe': 'DAYS', 'input': ['trade_price'], 'params': [20]},  # p[0]: timeperiod

    'wma3': {'function': 'WMA', 'dataframe': 'DAYS', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    'wma5': {'function': 'WMA', 'dataframe': 'DAYS', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    'wma10': {'function': 'WMA', 'dataframe': 'DAYS', 'input': ['trade_price'], 'params': [10]},  # p[0]: timeperiod
    'wma20': {'function': 'WMA', 'dataframe': 'DAYS', 'input': ['trade_price'], 'params': [20]},  # p[0]: timeperiod

    'mama': {'function': 'MAMA', 'dataframe': 'DAYS', 'input': ['trade_price'], 'params': []},  # fastlimit=0, slowlimit=0
    'midpoint': {'function': 'MIDPOINT', 'dataframe': 'DAYS', 'input': ['trade_price'], 'params': []},  # timeperiod=14

    # 'midprice': {'function': 'MIDPRICE', 'dataframe': 'DAYS', 'input': ['trade_price'], 'params': []},  # timeperiod=14
    'sar': {'function': 'SAR', 'dataframe': 'DAYS', 'input': ['high_price', 'low_price'], 'params': []},  # acceleration=0, maximum=0
    'sar_1h': {'function': 'SAR', 'dataframe': 'HOUR', 'input': ['high_price', 'low_price'], 'params': []},  # acceleration=0, maximum=0
    'sarext': {'function': 'SAREXT', 'dataframe': 'DAYS', 'input': ['high_price', 'low_price'], 'params': []},  # startvalue=0, offsetonreverse=0, accelerationinitlong=0, accelerationlong=0, accelerationmaxlong=0, accelerationinitshort=0, accelerationshort=0, accelerationmaxshort=0
    't3': {'function': 'T3', 'dataframe': 'DAYS', 'input': ['trade_price'], 'params': []},  # timeperiod=5, vfactor=0

    'ht_trendline': {'function': 'HT_TRENDLINE', 'dataframe': 'DAYS', 'input': ['trade_price'], 'params': []},  # p[0]: timeperiod
    'adx': {'function': 'ADX', 'dataframe': 'DAYS', 'input': ['high_price', 'low_price', 'trade_price'], 'params': []},  # timeperiod=14
    'adxr': {'function': 'ADXR', 'dataframe': 'DAYS', 'input': ['high_price', 'low_price', 'trade_price'], 'params': []},  # timeperiod=14
    'apo': {'function': 'APO', 'dataframe': 'DAYS', 'input': ['trade_price'], 'params': []},  # fastperiod=12, slowperiod=26, matype=0
    'aroon': {'function': 'AROON', 'dataframe': 'DAYS', 'input': ['high_price', 'low_price'], 'params': []},  # timeperiod=14
    # 'aroonosc': {'function': 'AROONOSC', 'dataframe': 'DAYS', 'input': ['trade_price'], 'params': []},  # timeperiod=14
    'bop': {'function': 'BOP', 'dataframe': 'DAYS', 'input': ['opening_price', 'high_price', 'low_price', 'trade_price'], 'params': []},
    'ccl': {'function': 'CCI', 'dataframe': 'DAYS', 'input': ['high_price', 'low_price', 'trade_price'], 'params': []},  # timeperiod=14
    'dx': {'function': 'DX', 'dataframe': 'DAYS', 'input': ['high_price', 'low_price', 'trade_price'], 'params': []},  # timeperiod=14
    'cmo': {'function': 'CMO', 'dataframe': 'DAYS', 'input': ['trade_price'], 'params': []}  ,# timeperiod=14
    'macdext': {'function': 'MACDEXT', 'dataframe': 'DAYS', 'input': ['trade_price'], 'params': []}
    ,# fastperiod=12, fastmatype=0, slowperiod=26, slowmatype=0, signalperiod=9, signalmatype=0
    'macdfix': {'function': 'MACDFIX', 'dataframe': 'DAYS', 'input': ['trade_price'], 'params': []}  ,# signalperiod=9
    'mfi': {'function': 'MFI', 'dataframe': 'DAYS', 'input': ['high_price', 'low_price', 'trade_price', 'candle_acc_trade_volume'], 'params': []}, # timeperiod=14
    'minus_dm': {'function': 'MINUS_DM', 'dataframe': 'DAYS', 'input': ['high_price', 'low_price'], 'params': []}, # timeperiod=14
    'plus_dm': {'function': 'PLUS_DM', 'dataframe': 'DAYS', 'input': ['high_price', 'low_price'], 'params': []}, # timeperiod=14
    'mom': {'function': 'MOM', 'dataframe': 'DAYS', 'input': ['trade_price'], 'params': []}  ,# timeperiod=10
    'ppo': {'function': 'PPO', 'dataframe': 'DAYS', 'input': ['trade_price'], 'params': []}
    ,# fastperiod=12, slowperiod=26, matype=0
    'roc': {'function': 'ROC', 'dataframe': 'DAYS', 'input': ['trade_price'], 'params': []}  ,# timeperiod=10
    'rocp': {'function': 'ROCP', 'dataframe': 'DAYS', 'input': ['trade_price'], 'params': []}  ,# timeperiod=10
    'rocr': {'function': 'ROCR', 'dataframe': 'DAYS', 'input': ['trade_price'], 'params': []}  ,# timeperiod=10
    'rocr100': {'function': 'ROCR100', 'dataframe': 'DAYS', 'input': ['trade_price'], 'params': []}  ,# timeperiod=10
    'stoch': {'function': 'STOCH', 'dataframe': 'DAYS', 'input': ['high_price', 'low_price', 'trade_price'], 'params': []}  ,# fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0
    'stochf': {'function': 'STOCHF', 'dataframe': 'DAYS', 'input': ['high_price', 'low_price', 'trade_price'], 'params': []}  ,# fastk_period=5, fastd_period=3, fastd_matype=0
    'ultosc': {'function': 'ULTOSC', 'dataframe': 'DAYS', 'input': ['high_price', 'low_price', 'trade_price'], 'params': []}  ,# timeperiod1=7, timeperiod2=14, timeperiod3=28
    'willr': {'function': 'WILLR', 'dataframe': 'DAYS', 'input': ['high_price', 'low_price', 'trade_price'], 'params': []}  ,# timeperiod=14
    'stochrsi': {'function': 'STOCHRSI', 'dataframe': 'DAYS', 'input': ['trade_price'], 'params': []}
    ,# timeperiod=14, fastk_period=5, fastd_period=3, fastd_matype=0
    'trix': {'function': 'TRIX', 'dataframe': 'DAYS', 'input': ['trade_price'], 'params': []}  ,# timeperiod=30

    'ad': {'function': 'AD', 'dataframe': 'DAYS', 'input': ['high_price', 'low_price', 'trade_price', 'candle_acc_trade_volume'], 'params': []}, # timeperiod=14
    'adosc': {'function': 'ADOSC', 'dataframe': 'DAYS', 'input': ['high_price', 'low_price', 'trade_price', 'candle_acc_trade_volume'], 'params': []}, # timeperiod=14
    # 'obv': {'function': 'OBV', 'dataframe': 'DAYS', 'input': ['high_price', 'low_price', 'trade_price', 'candle_acc_trade_volume'], 'params': []}, # timeperiod=14

    'ht_dcperiod': {'function': 'HT_DCPERIOD', 'dataframe': 'DAYS', 'input': ['trade_price'], 'params': []},
    'ht_dcphase': {'function': 'HT_DCPHASE', 'dataframe': 'DAYS', 'input': ['trade_price'], 'params': []},
    'ht_phasor': {'function': 'HT_PHASOR', 'dataframe': 'DAYS', 'input': ['trade_price'], 'params': []},
    'ht_sine': {'function': 'HT_SINE', 'dataframe': 'DAYS', 'input': ['trade_price'], 'params': []},
    # 'ht_trendmode': {'function': 'HT_TRENDMODE', 'dataframe': 'DAYS', 'input': ['trade_price'], 'params': []},
    'ema100_0':  {'function': 'EMA', 'dataframe': 'HOUR', 'input': ['trade_price'], 'params': [100]},  # p[0]: timeperiod
    'ema200_0':  {'function': 'EMA', 'dataframe': 'HOUR', 'input': ['trade_price'], 'params': [200]},  # p[0]: timeperiod
    # p[0] : fastperiod(def=12), p[1] : slowperiod(def=26), p[2]: signalperiod (def=9)

    # 'dema5_0':  {'function': 'DEMA', 'dataframe': 'DAYS_0', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    # 'dema5_1':  {'function': 'DEMA', 'dataframe': 'DAYS_1', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    # 'dema5_2':  {'function': 'DEMA', 'dataframe': 'DAYS_2', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    # 'dema5_3':  {'function': 'DEMA', 'dataframe': 'DAYS_3', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    # 'dema5_4':  {'function': 'DEMA', 'dataframe': 'DAYS_4', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    # 'dema5_5':  {'function': 'DEMA', 'dataframe': 'DAYS_5', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    # 'dema5_6':  {'function': 'DEMA', 'dataframe': 'DAYS_6', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    # 'dema5_7':  {'function': 'DEMA', 'dataframe': 'DAYS_7', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    # 'dema5_8':  {'function': 'DEMA', 'dataframe': 'DAYS_8', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    # 'dema5_9':  {'function': 'DEMA', 'dataframe': 'DAYS_9', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    # 'dema5_10':  {'function': 'DEMA', 'dataframe': 'DAYS_10', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    # 'dema5_11':  {'function': 'DEMA', 'dataframe': 'DAYS_11', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    # 'dema5_12':  {'function': 'DEMA', 'dataframe': 'DAYS_12', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    # 'dema5_13':  {'function': 'DEMA', 'dataframe': 'DAYS_13', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    # 'dema5_14':  {'function': 'DEMA', 'dataframe': 'DAYS_14', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    # 'dema5_15':  {'function': 'DEMA', 'dataframe': 'DAYS_15', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    # 'dema5_16':  {'function': 'DEMA', 'dataframe': 'DAYS_16', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    # 'dema5_17':  {'function': 'DEMA', 'dataframe': 'DAYS_17', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    # 'dema5_18':  {'function': 'DEMA', 'dataframe': 'DAYS_18', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    # 'dema5_19':  {'function': 'DEMA', 'dataframe': 'DAYS_19', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    # 'dema5_20':  {'function': 'DEMA', 'dataframe': 'DAYS_20', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    # 'dema5_21':  {'function': 'DEMA', 'dataframe': 'DAYS_21', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    # 'dema5_22':  {'function': 'DEMA', 'dataframe': 'DAYS_22', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    # 'dema5_23':  {'function': 'DEMA', 'dataframe': 'DAYS_23', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    #
    # 'dema3_0': {'function': 'DEMA', 'dataframe': 'DAYS_0', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    # 'dema3_1': {'function': 'DEMA', 'dataframe': 'DAYS_1', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    # 'dema3_2': {'function': 'DEMA', 'dataframe': 'DAYS_2', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    # 'dema3_3': {'function': 'DEMA', 'dataframe': 'DAYS_3', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    # 'dema3_4': {'function': 'DEMA', 'dataframe': 'DAYS_4', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    # 'dema3_5': {'function': 'DEMA', 'dataframe': 'DAYS_5', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    # 'dema3_6': {'function': 'DEMA', 'dataframe': 'DAYS_6', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    # 'dema3_7': {'function': 'DEMA', 'dataframe': 'DAYS_7', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    # 'dema3_8': {'function': 'DEMA', 'dataframe': 'DAYS_8', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    # 'dema3_9': {'function': 'DEMA', 'dataframe': 'DAYS_9', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    # 'dema3_10': {'function': 'DEMA', 'dataframe': 'DAYS_10', 'input': ['trade_price'], 'params': [3]},
    # 'dema3_11': {'function': 'DEMA', 'dataframe': 'DAYS_11', 'input': ['trade_price'], 'params': [3]},
    # 'dema3_12': {'function': 'DEMA', 'dataframe': 'DAYS_12', 'input': ['trade_price'], 'params': [3]},
    # 'dema3_13': {'function': 'DEMA', 'dataframe': 'DAYS_13', 'input': ['trade_price'], 'params': [3]},
    # 'dema3_14': {'function': 'DEMA', 'dataframe': 'DAYS_14', 'input': ['trade_price'], 'params': [3]},
    # 'dema3_15': {'function': 'DEMA', 'dataframe': 'DAYS_15', 'input': ['trade_price'], 'params': [3]},
    # 'dema3_16': {'function': 'DEMA', 'dataframe': 'DAYS_16', 'input': ['trade_price'], 'params': [3]},
    # 'dema3_17': {'function': 'DEMA', 'dataframe': 'DAYS_17', 'input': ['trade_price'], 'params': [3]},
    # 'dema3_18': {'function': 'DEMA', 'dataframe': 'DAYS_18', 'input': ['trade_price'], 'params': [3]},
    # 'dema3_19': {'function': 'DEMA', 'dataframe': 'DAYS_19', 'input': ['trade_price'], 'params': [3]},
    # 'dema3_20': {'function': 'DEMA', 'dataframe': 'DAYS_20', 'input': ['trade_price'], 'params': [3]},
    # 'dema3_21': {'function': 'DEMA', 'dataframe': 'DAYS_21', 'input': ['trade_price'], 'params': [3]},
    # 'dema3_22': {'function': 'DEMA', 'dataframe': 'DAYS_22', 'input': ['trade_price'], 'params': [3]},
    # 'dema3_23': {'function': 'DEMA', 'dataframe': 'DAYS_23', 'input': ['trade_price'], 'params': [3]},
    #
    # 'dema10_0': {'function': 'DEMA', 'dataframe': 'DAYS_0', 'input': ['trade_price'], 'params': [10]},
    # 'dema10_1': {'function': 'DEMA', 'dataframe': 'DAYS_1', 'input': ['trade_price'], 'params': [10]},
    # 'dema10_2': {'function': 'DEMA', 'dataframe': 'DAYS_2', 'input': ['trade_price'], 'params': [10]},
    # 'dema10_3': {'function': 'DEMA', 'dataframe': 'DAYS_3', 'input': ['trade_price'], 'params': [10]},
    # 'dema10_4': {'function': 'DEMA', 'dataframe': 'DAYS_4', 'input': ['trade_price'], 'params': [10]},
    # 'dema10_5': {'function': 'DEMA', 'dataframe': 'DAYS_5', 'input': ['trade_price'], 'params': [10]},
    # 'dema10_6': {'function': 'DEMA', 'dataframe': 'DAYS_6', 'input': ['trade_price'], 'params': [10]},
    # 'dema10_7': {'function': 'DEMA', 'dataframe': 'DAYS_7', 'input': ['trade_price'], 'params': [10]},
    # 'dema10_8': {'function': 'DEMA', 'dataframe': 'DAYS_8', 'input': ['trade_price'], 'params': [10]},
    # 'dema10_9': {'function': 'DEMA', 'dataframe': 'DAYS_9', 'input': ['trade_price'], 'params': [10]},
    # 'dema10_10': {'function': 'DEMA', 'dataframe': 'DAYS_10', 'input': ['trade_price'], 'params': [10]},
    # 'dema10_11': {'function': 'DEMA', 'dataframe': 'DAYS_11', 'input': ['trade_price'], 'params': [10]},
    # 'dema10_12': {'function': 'DEMA', 'dataframe': 'DAYS_12', 'input': ['trade_price'], 'params': [10]},
    # 'dema10_13': {'function': 'DEMA', 'dataframe': 'DAYS_13', 'input': ['trade_price'], 'params': [10]},
    # 'dema10_14': {'function': 'DEMA', 'dataframe': 'DAYS_14', 'input': ['trade_price'], 'params': [10]},
    # 'dema10_15': {'function': 'DEMA', 'dataframe': 'DAYS_15', 'input': ['trade_price'], 'params': [10]},
    # 'dema10_16': {'function': 'DEMA', 'dataframe': 'DAYS_16', 'input': ['trade_price'], 'params': [10]},
    # 'dema10_17': {'function': 'DEMA', 'dataframe': 'DAYS_17', 'input': ['trade_price'], 'params': [10]},
    # 'dema10_18': {'function': 'DEMA', 'dataframe': 'DAYS_18', 'input': ['trade_price'], 'params': [10]},
    # 'dema10_19': {'function': 'DEMA', 'dataframe': 'DAYS_19', 'input': ['trade_price'], 'params': [10]},
    # 'dema10_20': {'function': 'DEMA', 'dataframe': 'DAYS_20', 'input': ['trade_price'], 'params': [10]},
    # 'dema10_21': {'function': 'DEMA', 'dataframe': 'DAYS_21', 'input': ['trade_price'], 'params': [10]},
    # 'dema10_22': {'function': 'DEMA', 'dataframe': 'DAYS_22', 'input': ['trade_price'], 'params': [10]},
    # 'dema10_23': {'function': 'DEMA', 'dataframe': 'DAYS_23', 'input': ['trade_price'], 'params': [10]},
    #
    # 'dema20_0': {'function': 'DEMA', 'dataframe': 'DAYS_0', 'input': ['trade_price'], 'params': [20]},
    # 'dema20_1': {'function': 'DEMA', 'dataframe': 'DAYS_1', 'input': ['trade_price'], 'params': [20]},
    # 'dema20_2': {'function': 'DEMA', 'dataframe': 'DAYS_2', 'input': ['trade_price'], 'params': [20]},
    # 'dema20_3': {'function': 'DEMA', 'dataframe': 'DAYS_3', 'input': ['trade_price'], 'params': [20]},
    # 'dema20_4': {'function': 'DEMA', 'dataframe': 'DAYS_4', 'input': ['trade_price'], 'params': [20]},
    # 'dema20_5': {'function': 'DEMA', 'dataframe': 'DAYS_5', 'input': ['trade_price'], 'params': [20]},
    # 'dema20_6': {'function': 'DEMA', 'dataframe': 'DAYS_6', 'input': ['trade_price'], 'params': [20]},
    # 'dema20_7': {'function': 'DEMA', 'dataframe': 'DAYS_7', 'input': ['trade_price'], 'params': [20]},
    # 'dema20_8': {'function': 'DEMA', 'dataframe': 'DAYS_8', 'input': ['trade_price'], 'params': [20]},
    # 'dema20_9': {'function': 'DEMA', 'dataframe': 'DAYS_9', 'input': ['trade_price'], 'params': [20]},
    # 'dema20_10': {'function': 'DEMA', 'dataframe': 'DAYS_10', 'input': ['trade_price'], 'params': [20]},
    # 'dema20_11': {'function': 'DEMA', 'dataframe': 'DAYS_11', 'input': ['trade_price'], 'params': [20]},
    # 'dema20_12': {'function': 'DEMA', 'dataframe': 'DAYS_12', 'input': ['trade_price'], 'params': [20]},
    # 'dema20_13': {'function': 'DEMA', 'dataframe': 'DAYS_13', 'input': ['trade_price'], 'params': [20]},
    # 'dema20_14': {'function': 'DEMA', 'dataframe': 'DAYS_14', 'input': ['trade_price'], 'params': [20]},
    # 'dema20_15': {'function': 'DEMA', 'dataframe': 'DAYS_15', 'input': ['trade_price'], 'params': [20]},
    # 'dema20_16': {'function': 'DEMA', 'dataframe': 'DAYS_16', 'input': ['trade_price'], 'params': [20]},
    # 'dema20_17': {'function': 'DEMA', 'dataframe': 'DAYS_17', 'input': ['trade_price'], 'params': [20]},
    # 'dema20_18': {'function': 'DEMA', 'dataframe': 'DAYS_18', 'input': ['trade_price'], 'params': [20]},
    # 'dema20_19': {'function': 'DEMA', 'dataframe': 'DAYS_19', 'input': ['trade_price'], 'params': [20]},
    # 'dema20_20': {'function': 'DEMA', 'dataframe': 'DAYS_20', 'input': ['trade_price'], 'params': [20]},
    # 'dema20_21': {'function': 'DEMA', 'dataframe': 'DAYS_21', 'input': ['trade_price'], 'params': [20]},
    # 'dema20_22': {'function': 'DEMA', 'dataframe': 'DAYS_22', 'input': ['trade_price'], 'params': [20]},
    # 'dema20_23': {'function': 'DEMA', 'dataframe': 'DAYS_23', 'input': ['trade_price'], 'params': [20]},
    #
    'ema5_0':  {'function': 'EMA', 'dataframe': 'DAYS_0', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    'ema5_1':  {'function': 'EMA', 'dataframe': 'DAYS_1', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    'ema5_2':  {'function': 'EMA', 'dataframe': 'DAYS_2', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    'ema5_3':  {'function': 'EMA', 'dataframe': 'DAYS_3', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    'ema5_4':  {'function': 'EMA', 'dataframe': 'DAYS_4', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    'ema5_5':  {'function': 'EMA', 'dataframe': 'DAYS_5', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    'ema5_6':  {'function': 'EMA', 'dataframe': 'DAYS_6', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    'ema5_7':  {'function': 'EMA', 'dataframe': 'DAYS_7', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    'ema5_8':  {'function': 'EMA', 'dataframe': 'DAYS_8', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    'ema5_9':  {'function': 'EMA', 'dataframe': 'DAYS_9', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    'ema5_10':  {'function': 'EMA', 'dataframe': 'DAYS_10', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    'ema5_11':  {'function': 'EMA', 'dataframe': 'DAYS_11', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    'ema5_12':  {'function': 'EMA', 'dataframe': 'DAYS_12', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    'ema5_13':  {'function': 'EMA', 'dataframe': 'DAYS_13', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    'ema5_14':  {'function': 'EMA', 'dataframe': 'DAYS_14', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    'ema5_15':  {'function': 'EMA', 'dataframe': 'DAYS_15', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    'ema5_16':  {'function': 'EMA', 'dataframe': 'DAYS_16', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    'ema5_17':  {'function': 'EMA', 'dataframe': 'DAYS_17', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    'ema5_18':  {'function': 'EMA', 'dataframe': 'DAYS_18', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    'ema5_19':  {'function': 'EMA', 'dataframe': 'DAYS_19', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    'ema5_20':  {'function': 'EMA', 'dataframe': 'DAYS_20', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    'ema5_21':  {'function': 'EMA', 'dataframe': 'DAYS_21', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    'ema5_22':  {'function': 'EMA', 'dataframe': 'DAYS_22', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    'ema5_23':  {'function': 'EMA', 'dataframe': 'DAYS_23', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod

    'ema3_0': {'function': 'EMA', 'dataframe': 'DAYS_0', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    'ema3_1': {'function': 'EMA', 'dataframe': 'DAYS_1', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    'ema3_2': {'function': 'EMA', 'dataframe': 'DAYS_2', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    'ema3_3': {'function': 'EMA', 'dataframe': 'DAYS_3', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    'ema3_4': {'function': 'EMA', 'dataframe': 'DAYS_4', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    'ema3_5': {'function': 'EMA', 'dataframe': 'DAYS_5', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    'ema3_6': {'function': 'EMA', 'dataframe': 'DAYS_6', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    'ema3_7': {'function': 'EMA', 'dataframe': 'DAYS_7', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    'ema3_8': {'function': 'EMA', 'dataframe': 'DAYS_8', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    'ema3_9': {'function': 'EMA', 'dataframe': 'DAYS_9', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    'ema3_10': {'function': 'EMA', 'dataframe': 'DAYS_10', 'input': ['trade_price'], 'params': [3]},
    'ema3_11': {'function': 'EMA', 'dataframe': 'DAYS_11', 'input': ['trade_price'], 'params': [3]},
    'ema3_12': {'function': 'EMA', 'dataframe': 'DAYS_12', 'input': ['trade_price'], 'params': [3]},
    'ema3_13': {'function': 'EMA', 'dataframe': 'DAYS_13', 'input': ['trade_price'], 'params': [3]},
    'ema3_14': {'function': 'EMA', 'dataframe': 'DAYS_14', 'input': ['trade_price'], 'params': [3]},
    'ema3_15': {'function': 'EMA', 'dataframe': 'DAYS_15', 'input': ['trade_price'], 'params': [3]},
    'ema3_16': {'function': 'EMA', 'dataframe': 'DAYS_16', 'input': ['trade_price'], 'params': [3]},
    'ema3_17': {'function': 'EMA', 'dataframe': 'DAYS_17', 'input': ['trade_price'], 'params': [3]},
    'ema3_18': {'function': 'EMA', 'dataframe': 'DAYS_18', 'input': ['trade_price'], 'params': [3]},
    'ema3_19': {'function': 'EMA', 'dataframe': 'DAYS_19', 'input': ['trade_price'], 'params': [3]},
    'ema3_20': {'function': 'EMA', 'dataframe': 'DAYS_20', 'input': ['trade_price'], 'params': [3]},
    'ema3_21': {'function': 'EMA', 'dataframe': 'DAYS_21', 'input': ['trade_price'], 'params': [3]},
    'ema3_22': {'function': 'EMA', 'dataframe': 'DAYS_22', 'input': ['trade_price'], 'params': [3]},
    'ema3_23': {'function': 'EMA', 'dataframe': 'DAYS_23', 'input': ['trade_price'], 'params': [3]},

    'ema10_0': {'function': 'EMA', 'dataframe': 'DAYS_0', 'input': ['trade_price'], 'params': [10]},
    'ema10_1': {'function': 'EMA', 'dataframe': 'DAYS_1', 'input': ['trade_price'], 'params': [10]},
    'ema10_2': {'function': 'EMA', 'dataframe': 'DAYS_2', 'input': ['trade_price'], 'params': [10]},
    'ema10_3': {'function': 'EMA', 'dataframe': 'DAYS_3', 'input': ['trade_price'], 'params': [10]},
    'ema10_4': {'function': 'EMA', 'dataframe': 'DAYS_4', 'input': ['trade_price'], 'params': [10]},
    'ema10_5': {'function': 'EMA', 'dataframe': 'DAYS_5', 'input': ['trade_price'], 'params': [10]},
    'ema10_6': {'function': 'EMA', 'dataframe': 'DAYS_6', 'input': ['trade_price'], 'params': [10]},
    'ema10_7': {'function': 'EMA', 'dataframe': 'DAYS_7', 'input': ['trade_price'], 'params': [10]},
    'ema10_8': {'function': 'EMA', 'dataframe': 'DAYS_8', 'input': ['trade_price'], 'params': [10]},
    'ema10_9': {'function': 'EMA', 'dataframe': 'DAYS_9', 'input': ['trade_price'], 'params': [10]},
    'ema10_10': {'function': 'EMA', 'dataframe': 'DAYS_10', 'input': ['trade_price'], 'params': [10]},
    'ema10_11': {'function': 'EMA', 'dataframe': 'DAYS_11', 'input': ['trade_price'], 'params': [10]},
    'ema10_12': {'function': 'EMA', 'dataframe': 'DAYS_12', 'input': ['trade_price'], 'params': [10]},
    'ema10_13': {'function': 'EMA', 'dataframe': 'DAYS_13', 'input': ['trade_price'], 'params': [10]},
    'ema10_14': {'function': 'EMA', 'dataframe': 'DAYS_14', 'input': ['trade_price'], 'params': [10]},
    'ema10_15': {'function': 'EMA', 'dataframe': 'DAYS_15', 'input': ['trade_price'], 'params': [10]},
    'ema10_16': {'function': 'EMA', 'dataframe': 'DAYS_16', 'input': ['trade_price'], 'params': [10]},
    'ema10_17': {'function': 'EMA', 'dataframe': 'DAYS_17', 'input': ['trade_price'], 'params': [10]},
    'ema10_18': {'function': 'EMA', 'dataframe': 'DAYS_18', 'input': ['trade_price'], 'params': [10]},
    'ema10_19': {'function': 'EMA', 'dataframe': 'DAYS_19', 'input': ['trade_price'], 'params': [10]},
    'ema10_20': {'function': 'EMA', 'dataframe': 'DAYS_20', 'input': ['trade_price'], 'params': [10]},
    'ema10_21': {'function': 'EMA', 'dataframe': 'DAYS_21', 'input': ['trade_price'], 'params': [10]},
    'ema10_22': {'function': 'EMA', 'dataframe': 'DAYS_22', 'input': ['trade_price'], 'params': [10]},
    'ema10_23': {'function': 'EMA', 'dataframe': 'DAYS_23', 'input': ['trade_price'], 'params': [10]},

    'ema20_0': {'function': 'EMA', 'dataframe': 'DAYS_0', 'input': ['trade_price'], 'params': [20]},
    'ema20_1': {'function': 'EMA', 'dataframe': 'DAYS_1', 'input': ['trade_price'], 'params': [20]},
    'ema20_2': {'function': 'EMA', 'dataframe': 'DAYS_2', 'input': ['trade_price'], 'params': [20]},
    'ema20_3': {'function': 'EMA', 'dataframe': 'DAYS_3', 'input': ['trade_price'], 'params': [20]},
    'ema20_4': {'function': 'EMA', 'dataframe': 'DAYS_4', 'input': ['trade_price'], 'params': [20]},
    'ema20_5': {'function': 'EMA', 'dataframe': 'DAYS_5', 'input': ['trade_price'], 'params': [20]},
    'ema20_6': {'function': 'EMA', 'dataframe': 'DAYS_6', 'input': ['trade_price'], 'params': [20]},
    'ema20_7': {'function': 'EMA', 'dataframe': 'DAYS_7', 'input': ['trade_price'], 'params': [20]},
    'ema20_8': {'function': 'EMA', 'dataframe': 'DAYS_8', 'input': ['trade_price'], 'params': [20]},
    'ema20_9': {'function': 'EMA', 'dataframe': 'DAYS_9', 'input': ['trade_price'], 'params': [20]},
    'ema20_10': {'function': 'EMA', 'dataframe': 'DAYS_10', 'input': ['trade_price'], 'params': [20]},
    'ema20_11': {'function': 'EMA', 'dataframe': 'DAYS_11', 'input': ['trade_price'], 'params': [20]},
    'ema20_12': {'function': 'EMA', 'dataframe': 'DAYS_12', 'input': ['trade_price'], 'params': [20]},
    'ema20_13': {'function': 'EMA', 'dataframe': 'DAYS_13', 'input': ['trade_price'], 'params': [20]},
    'ema20_14': {'function': 'EMA', 'dataframe': 'DAYS_14', 'input': ['trade_price'], 'params': [20]},
    'ema20_15': {'function': 'EMA', 'dataframe': 'DAYS_15', 'input': ['trade_price'], 'params': [20]},
    'ema20_16': {'function': 'EMA', 'dataframe': 'DAYS_16', 'input': ['trade_price'], 'params': [20]},
    'ema20_17': {'function': 'EMA', 'dataframe': 'DAYS_17', 'input': ['trade_price'], 'params': [20]},
    'ema20_18': {'function': 'EMA', 'dataframe': 'DAYS_18', 'input': ['trade_price'], 'params': [20]},
    'ema20_19': {'function': 'EMA', 'dataframe': 'DAYS_19', 'input': ['trade_price'], 'params': [20]},
    'ema20_20': {'function': 'EMA', 'dataframe': 'DAYS_20', 'input': ['trade_price'], 'params': [20]},
    'ema20_21': {'function': 'EMA', 'dataframe': 'DAYS_21', 'input': ['trade_price'], 'params': [20]},
    'ema20_22': {'function': 'EMA', 'dataframe': 'DAYS_22', 'input': ['trade_price'], 'params': [20]},
    'ema20_23': {'function': 'EMA', 'dataframe': 'DAYS_23', 'input': ['trade_price'], 'params': [20]},
    #
    # 'ht_tredline_0': {'function': 'HT_TRENDLINE', 'dataframe': 'DAYS_0', 'input': ['trade_price'], 'params': []},
    # 'ht_tredline_1': {'function': 'HT_TRENDLINE', 'dataframe': 'DAYS_1', 'input': ['trade_price'], 'params': []},
    # 'ht_tredline_2': {'function': 'HT_TRENDLINE', 'dataframe': 'DAYS_2', 'input': ['trade_price'], 'params': []},
    # 'ht_tredline_3': {'function': 'HT_TRENDLINE', 'dataframe': 'DAYS_3', 'input': ['trade_price'], 'params': []},
    # 'ht_tredline_4': {'function': 'HT_TRENDLINE', 'dataframe': 'DAYS_4', 'input': ['trade_price'], 'params': []},
    # 'ht_tredline_5': {'function': 'HT_TRENDLINE', 'dataframe': 'DAYS_5', 'input': ['trade_price'], 'params': []},
    # 'ht_tredline_6': {'function': 'HT_TRENDLINE', 'dataframe': 'DAYS_6', 'input': ['trade_price'], 'params': []},
    # 'ht_tredline_7': {'function': 'HT_TRENDLINE', 'dataframe': 'DAYS_7', 'input': ['trade_price'], 'params': []},
    # 'ht_tredline_8': {'function': 'HT_TRENDLINE', 'dataframe': 'DAYS_8', 'input': ['trade_price'], 'params': []},
    # 'ht_tredline_9': {'function': 'HT_TRENDLINE', 'dataframe': 'DAYS_9', 'input': ['trade_price'], 'params': []},
    # 'ht_tredline_10': {'function': 'HT_TRENDLINE', 'dataframe': 'DAYS_10', 'input': ['trade_price'], 'params': []},
    # 'ht_tredline_11': {'function': 'HT_TRENDLINE', 'dataframe': 'DAYS_11', 'input': ['trade_price'], 'params': []},
    # 'ht_tredline_12': {'function': 'HT_TRENDLINE', 'dataframe': 'DAYS_12', 'input': ['trade_price'], 'params': []},
    # 'ht_tredline_13': {'function': 'HT_TRENDLINE', 'dataframe': 'DAYS_13', 'input': ['trade_price'], 'params': []},
    # 'ht_tredline_14': {'function': 'HT_TRENDLINE', 'dataframe': 'DAYS_14', 'input': ['trade_price'], 'params': []},
    # 'ht_tredline_15': {'function': 'HT_TRENDLINE', 'dataframe': 'DAYS_15', 'input': ['trade_price'], 'params': []},
    # 'ht_tredline_16': {'function': 'HT_TRENDLINE', 'dataframe': 'DAYS_16', 'input': ['trade_price'], 'params': []},
    # 'ht_tredline_17': {'function': 'HT_TRENDLINE', 'dataframe': 'DAYS_17', 'input': ['trade_price'], 'params': []},
    # 'ht_tredline_18': {'function': 'HT_TRENDLINE', 'dataframe': 'DAYS_18', 'input': ['trade_price'], 'params': []},
    # 'ht_tredline_19': {'function': 'HT_TRENDLINE', 'dataframe': 'DAYS_19', 'input': ['trade_price'], 'params': []},
    # 'ht_tredline_20': {'function': 'HT_TRENDLINE', 'dataframe': 'DAYS_20', 'input': ['trade_price'], 'params': []},
    # 'ht_tredline_21': {'function': 'HT_TRENDLINE', 'dataframe': 'DAYS_21', 'input': ['trade_price'], 'params': []},
    # 'ht_tredline_22': {'function': 'HT_TRENDLINE', 'dataframe': 'DAYS_22', 'input': ['trade_price'], 'params': []},
    # 'ht_tredline_23': {'function': 'HT_TRENDLINE', 'dataframe': 'DAYS_23', 'input': ['trade_price'], 'params': []},
    #
    # 'kama5_0': {'function': 'KAMA', 'dataframe': 'DAYS_0', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    # 'kama5_1': {'function': 'KAMA', 'dataframe': 'DAYS_1', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    # 'kama5_2': {'function': 'KAMA', 'dataframe': 'DAYS_2', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    # 'kama5_3': {'function': 'KAMA', 'dataframe': 'DAYS_3', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    # 'kama5_4': {'function': 'KAMA', 'dataframe': 'DAYS_4', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    # 'kama5_5': {'function': 'KAMA', 'dataframe': 'DAYS_5', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    # 'kama5_6': {'function': 'KAMA', 'dataframe': 'DAYS_6', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    # 'kama5_7': {'function': 'KAMA', 'dataframe': 'DAYS_7', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    # 'kama5_8': {'function': 'KAMA', 'dataframe': 'DAYS_8', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    # 'kama5_9': {'function': 'KAMA', 'dataframe': 'DAYS_9', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    # 'kama5_10': {'function': 'KAMA', 'dataframe': 'DAYS_10', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    # 'kama5_11': {'function': 'KAMA', 'dataframe': 'DAYS_11', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    # 'kama5_12': {'function': 'KAMA', 'dataframe': 'DAYS_12', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    # 'kama5_13': {'function': 'KAMA', 'dataframe': 'DAYS_13', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    # 'kama5_14': {'function': 'KAMA', 'dataframe': 'DAYS_14', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    # 'kama5_15': {'function': 'KAMA', 'dataframe': 'DAYS_15', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    # 'kama5_16': {'function': 'KAMA', 'dataframe': 'DAYS_16', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    # 'kama5_17': {'function': 'KAMA', 'dataframe': 'DAYS_17', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    # 'kama5_18': {'function': 'KAMA', 'dataframe': 'DAYS_18', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    # 'kama5_19': {'function': 'KAMA', 'dataframe': 'DAYS_19', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    # 'kama5_20': {'function': 'KAMA', 'dataframe': 'DAYS_20', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    # 'kama5_21': {'function': 'KAMA', 'dataframe': 'DAYS_21', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    # 'kama5_22': {'function': 'KAMA', 'dataframe': 'DAYS_22', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    # 'kama5_23': {'function': 'KAMA', 'dataframe': 'DAYS_23', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    #
    # 'kama3_0': {'function': 'KAMA', 'dataframe': 'DAYS_0', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    # 'kama3_1': {'function': 'KAMA', 'dataframe': 'DAYS_1', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    # 'kama3_2': {'function': 'KAMA', 'dataframe': 'DAYS_2', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    # 'kama3_3': {'function': 'KAMA', 'dataframe': 'DAYS_3', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    # 'kama3_4': {'function': 'KAMA', 'dataframe': 'DAYS_4', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    # 'kama3_5': {'function': 'KAMA', 'dataframe': 'DAYS_5', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    # 'kama3_6': {'function': 'KAMA', 'dataframe': 'DAYS_6', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    # 'kama3_7': {'function': 'KAMA', 'dataframe': 'DAYS_7', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    # 'kama3_8': {'function': 'KAMA', 'dataframe': 'DAYS_8', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    # 'kama3_9': {'function': 'KAMA', 'dataframe': 'DAYS_9', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    # 'kama3_10': {'function': 'KAMA', 'dataframe': 'DAYS_10', 'input': ['trade_price'], 'params': [3]},
    # 'kama3_11': {'function': 'KAMA', 'dataframe': 'DAYS_11', 'input': ['trade_price'], 'params': [3]},
    # 'kama3_12': {'function': 'KAMA', 'dataframe': 'DAYS_12', 'input': ['trade_price'], 'params': [3]},
    # 'kama3_13': {'function': 'KAMA', 'dataframe': 'DAYS_13', 'input': ['trade_price'], 'params': [3]},
    # 'kama3_14': {'function': 'KAMA', 'dataframe': 'DAYS_14', 'input': ['trade_price'], 'params': [3]},
    # 'kama3_15': {'function': 'KAMA', 'dataframe': 'DAYS_15', 'input': ['trade_price'], 'params': [3]},
    # 'kama3_16': {'function': 'KAMA', 'dataframe': 'DAYS_16', 'input': ['trade_price'], 'params': [3]},
    # 'kama3_17': {'function': 'KAMA', 'dataframe': 'DAYS_17', 'input': ['trade_price'], 'params': [3]},
    # 'kama3_18': {'function': 'KAMA', 'dataframe': 'DAYS_18', 'input': ['trade_price'], 'params': [3]},
    # 'kama3_19': {'function': 'KAMA', 'dataframe': 'DAYS_19', 'input': ['trade_price'], 'params': [3]},
    # 'kama3_20': {'function': 'KAMA', 'dataframe': 'DAYS_20', 'input': ['trade_price'], 'params': [3]},
    # 'kama3_21': {'function': 'KAMA', 'dataframe': 'DAYS_21', 'input': ['trade_price'], 'params': [3]},
    # 'kama3_22': {'function': 'KAMA', 'dataframe': 'DAYS_22', 'input': ['trade_price'], 'params': [3]},
    # 'kama3_23': {'function': 'KAMA', 'dataframe': 'DAYS_23', 'input': ['trade_price'], 'params': [3]},
    #
    # 'kama10_0': {'function': 'KAMA', 'dataframe': 'DAYS_0', 'input': ['trade_price'], 'params': [10]},
    # 'kama10_1': {'function': 'KAMA', 'dataframe': 'DAYS_1', 'input': ['trade_price'], 'params': [10]},
    # 'kama10_2': {'function': 'KAMA', 'dataframe': 'DAYS_2', 'input': ['trade_price'], 'params': [10]},
    # 'kama10_3': {'function': 'KAMA', 'dataframe': 'DAYS_3', 'input': ['trade_price'], 'params': [10]},
    # 'kama10_4': {'function': 'KAMA', 'dataframe': 'DAYS_4', 'input': ['trade_price'], 'params': [10]},
    # 'kama10_5': {'function': 'KAMA', 'dataframe': 'DAYS_5', 'input': ['trade_price'], 'params': [10]},
    # 'kama10_6': {'function': 'KAMA', 'dataframe': 'DAYS_6', 'input': ['trade_price'], 'params': [10]},
    # 'kama10_7': {'function': 'KAMA', 'dataframe': 'DAYS_7', 'input': ['trade_price'], 'params': [10]},
    # 'kama10_8': {'function': 'KAMA', 'dataframe': 'DAYS_8', 'input': ['trade_price'], 'params': [10]},
    # 'kama10_9': {'function': 'KAMA', 'dataframe': 'DAYS_9', 'input': ['trade_price'], 'params': [10]},
    # 'kama10_10': {'function': 'KAMA', 'dataframe': 'DAYS_10', 'input': ['trade_price'], 'params': [10]},
    # 'kama10_11': {'function': 'KAMA', 'dataframe': 'DAYS_11', 'input': ['trade_price'], 'params': [10]},
    # 'kama10_12': {'function': 'KAMA', 'dataframe': 'DAYS_12', 'input': ['trade_price'], 'params': [10]},
    # 'kama10_13': {'function': 'KAMA', 'dataframe': 'DAYS_13', 'input': ['trade_price'], 'params': [10]},
    # 'kama10_14': {'function': 'KAMA', 'dataframe': 'DAYS_14', 'input': ['trade_price'], 'params': [10]},
    # 'kama10_15': {'function': 'KAMA', 'dataframe': 'DAYS_15', 'input': ['trade_price'], 'params': [10]},
    # 'kama10_16': {'function': 'KAMA', 'dataframe': 'DAYS_16', 'input': ['trade_price'], 'params': [10]},
    # 'kama10_17': {'function': 'KAMA', 'dataframe': 'DAYS_17', 'input': ['trade_price'], 'params': [10]},
    # 'kama10_18': {'function': 'KAMA', 'dataframe': 'DAYS_18', 'input': ['trade_price'], 'params': [10]},
    # 'kama10_19': {'function': 'KAMA', 'dataframe': 'DAYS_19', 'input': ['trade_price'], 'params': [10]},
    # 'kama10_20': {'function': 'KAMA', 'dataframe': 'DAYS_20', 'input': ['trade_price'], 'params': [10]},
    # 'kama10_21': {'function': 'KAMA', 'dataframe': 'DAYS_21', 'input': ['trade_price'], 'params': [10]},
    # 'kama10_22': {'function': 'KAMA', 'dataframe': 'DAYS_22', 'input': ['trade_price'], 'params': [10]},
    # 'kama10_23': {'function': 'KAMA', 'dataframe': 'DAYS_23', 'input': ['trade_price'], 'params': [10]},
    #
    # 'kama20_0': {'function': 'KAMA', 'dataframe': 'DAYS_0', 'input': ['trade_price'], 'params': [20]},
    # 'kama20_1': {'function': 'KAMA', 'dataframe': 'DAYS_1', 'input': ['trade_price'], 'params': [20]},
    # 'kama20_2': {'function': 'KAMA', 'dataframe': 'DAYS_2', 'input': ['trade_price'], 'params': [20]},
    # 'kama20_3': {'function': 'KAMA', 'dataframe': 'DAYS_3', 'input': ['trade_price'], 'params': [20]},
    # 'kama20_4': {'function': 'KAMA', 'dataframe': 'DAYS_4', 'input': ['trade_price'], 'params': [20]},
    # 'kama20_5': {'function': 'KAMA', 'dataframe': 'DAYS_5', 'input': ['trade_price'], 'params': [20]},
    # 'kama20_6': {'function': 'KAMA', 'dataframe': 'DAYS_6', 'input': ['trade_price'], 'params': [20]},
    # 'kama20_7': {'function': 'KAMA', 'dataframe': 'DAYS_7', 'input': ['trade_price'], 'params': [20]},
    # 'kama20_8': {'function': 'KAMA', 'dataframe': 'DAYS_8', 'input': ['trade_price'], 'params': [20]},
    # 'kama20_9': {'function': 'KAMA', 'dataframe': 'DAYS_9', 'input': ['trade_price'], 'params': [20]},
    # 'kama20_10': {'function': 'KAMA', 'dataframe': 'DAYS_10', 'input': ['trade_price'], 'params': [20]},
    # 'kama20_11': {'function': 'KAMA', 'dataframe': 'DAYS_11', 'input': ['trade_price'], 'params': [20]},
    # 'kama20_12': {'function': 'KAMA', 'dataframe': 'DAYS_12', 'input': ['trade_price'], 'params': [20]},
    # 'kama20_13': {'function': 'KAMA', 'dataframe': 'DAYS_13', 'input': ['trade_price'], 'params': [20]},
    # 'kama20_14': {'function': 'KAMA', 'dataframe': 'DAYS_14', 'input': ['trade_price'], 'params': [20]},
    # 'kama20_15': {'function': 'KAMA', 'dataframe': 'DAYS_15', 'input': ['trade_price'], 'params': [20]},
    # 'kama20_16': {'function': 'KAMA', 'dataframe': 'DAYS_16', 'input': ['trade_price'], 'params': [20]},
    # 'kama20_17': {'function': 'KAMA', 'dataframe': 'DAYS_17', 'input': ['trade_price'], 'params': [20]},
    # 'kama20_18': {'function': 'KAMA', 'dataframe': 'DAYS_18', 'input': ['trade_price'], 'params': [20]},
    # 'kama20_19': {'function': 'KAMA', 'dataframe': 'DAYS_19', 'input': ['trade_price'], 'params': [20]},
    # 'kama20_20': {'function': 'KAMA', 'dataframe': 'DAYS_20', 'input': ['trade_price'], 'params': [20]},
    # 'kama20_21': {'function': 'KAMA', 'dataframe': 'DAYS_21', 'input': ['trade_price'], 'params': [20]},
    # 'kama20_22': {'function': 'KAMA', 'dataframe': 'DAYS_22', 'input': ['trade_price'], 'params': [20]},
    # 'kama20_23': {'function': 'KAMA', 'dataframe': 'DAYS_23', 'input': ['trade_price'], 'params': [20]},
    #
    #
    # 'mama5_0': {'function': 'MAMA', 'dataframe': 'DAYS_0', 'input': ['trade_price'], 'params': []},  # p[0]: timeperiod
    # 'mama5_1': {'function': 'MAMA', 'dataframe': 'DAYS_1', 'input': ['trade_price'], 'params': []},  # p[0]: timeperiod
    # 'mama5_2': {'function': 'MAMA', 'dataframe': 'DAYS_2', 'input': ['trade_price'], 'params': []},  # p[0]: timeperiod
    # 'mama5_3': {'function': 'MAMA', 'dataframe': 'DAYS_3', 'input': ['trade_price'], 'params': []},  # p[0]: timeperiod
    # 'mama5_4': {'function': 'MAMA', 'dataframe': 'DAYS_4', 'input': ['trade_price'], 'params': []},  # p[0]: timeperiod
    # 'mama5_5': {'function': 'MAMA', 'dataframe': 'DAYS_5', 'input': ['trade_price'], 'params': []},  # p[0]: timeperiod
    # 'mama5_6': {'function': 'MAMA', 'dataframe': 'DAYS_6', 'input': ['trade_price'], 'params': []},  # p[0]: timeperiod
    # 'mama5_7': {'function': 'MAMA', 'dataframe': 'DAYS_7', 'input': ['trade_price'], 'params': []},  # p[0]: timeperiod
    # 'mama5_8': {'function': 'MAMA', 'dataframe': 'DAYS_8', 'input': ['trade_price'], 'params': []},  # p[0]: timeperiod
    # 'mama5_9': {'function': 'MAMA', 'dataframe': 'DAYS_9', 'input': ['trade_price'], 'params': []},  # p[0]: timeperiod
    # 'mama5_10': {'function': 'MAMA', 'dataframe': 'DAYS_10', 'input': ['trade_price'], 'params': []},
    # 'mama5_11': {'function': 'MAMA', 'dataframe': 'DAYS_11', 'input': ['trade_price'], 'params': []},
    # 'mama5_12': {'function': 'MAMA', 'dataframe': 'DAYS_12', 'input': ['trade_price'], 'params': []},
    # 'mama5_13': {'function': 'MAMA', 'dataframe': 'DAYS_13', 'input': ['trade_price'], 'params': []},
    # 'mama5_14': {'function': 'MAMA', 'dataframe': 'DAYS_14', 'input': ['trade_price'], 'params': []},
    # 'mama5_15': {'function': 'MAMA', 'dataframe': 'DAYS_15', 'input': ['trade_price'], 'params': []},
    # 'mama5_16': {'function': 'MAMA', 'dataframe': 'DAYS_16', 'input': ['trade_price'], 'params': []},
    # 'mama5_17': {'function': 'MAMA', 'dataframe': 'DAYS_17', 'input': ['trade_price'], 'params': []},
    # 'mama5_18': {'function': 'MAMA', 'dataframe': 'DAYS_18', 'input': ['trade_price'], 'params': []},
    # 'mama5_19': {'function': 'MAMA', 'dataframe': 'DAYS_19', 'input': ['trade_price'], 'params': []},
    # 'mama5_20': {'function': 'MAMA', 'dataframe': 'DAYS_20', 'input': ['trade_price'], 'params': []},
    # 'mama5_21': {'function': 'MAMA', 'dataframe': 'DAYS_21', 'input': ['trade_price'], 'params': []},
    # 'mama5_22': {'function': 'MAMA', 'dataframe': 'DAYS_22', 'input': ['trade_price'], 'params': []},
    # 'mama5_23': {'function': 'MAMA', 'dataframe': 'DAYS_23', 'input': ['trade_price'], 'params': []},
    #
    # 'mama3_0': {'function': 'MAMA', 'dataframe': 'DAYS_0', 'input': ['trade_price'], 'params': []},  # p[0]: timeperiod
    # 'mama3_1': {'function': 'MAMA', 'dataframe': 'DAYS_1', 'input': ['trade_price'], 'params': []},  # p[0]: timeperiod
    # 'mama3_2': {'function': 'MAMA', 'dataframe': 'DAYS_2', 'input': ['trade_price'], 'params': []},  # p[0]: timeperiod
    # 'mama3_3': {'function': 'MAMA', 'dataframe': 'DAYS_3', 'input': ['trade_price'], 'params': []},  # p[0]: timeperiod
    # 'mama3_4': {'function': 'MAMA', 'dataframe': 'DAYS_4', 'input': ['trade_price'], 'params': []},  # p[0]: timeperiod
    # 'mama3_5': {'function': 'MAMA', 'dataframe': 'DAYS_5', 'input': ['trade_price'], 'params': []},  # p[0]: timeperiod
    # 'mama3_6': {'function': 'MAMA', 'dataframe': 'DAYS_6', 'input': ['trade_price'], 'params': []},  # p[0]: timeperiod
    # 'mama3_7': {'function': 'MAMA', 'dataframe': 'DAYS_7', 'input': ['trade_price'], 'params': []},  # p[0]: timeperiod
    # 'mama3_8': {'function': 'MAMA', 'dataframe': 'DAYS_8', 'input': ['trade_price'], 'params': []},  # p[0]: timeperiod
    # 'mama3_9': {'function': 'MAMA', 'dataframe': 'DAYS_9', 'input': ['trade_price'], 'params': []},  # p[0]: timeperiod
    # 'mama3_10': {'function': 'MAMA', 'dataframe': 'DAYS_10', 'input': ['trade_price'], 'params': []},
    # 'mama3_11': {'function': 'MAMA', 'dataframe': 'DAYS_11', 'input': ['trade_price'], 'params': []},
    # 'mama3_12': {'function': 'MAMA', 'dataframe': 'DAYS_12', 'input': ['trade_price'], 'params': []},
    # 'mama3_13': {'function': 'MAMA', 'dataframe': 'DAYS_13', 'input': ['trade_price'], 'params': []},
    # 'mama3_14': {'function': 'MAMA', 'dataframe': 'DAYS_14', 'input': ['trade_price'], 'params': []},
    # 'mama3_15': {'function': 'MAMA', 'dataframe': 'DAYS_15', 'input': ['trade_price'], 'params': []},
    # 'mama3_16': {'function': 'MAMA', 'dataframe': 'DAYS_16', 'input': ['trade_price'], 'params': []},
    # 'mama3_17': {'function': 'MAMA', 'dataframe': 'DAYS_17', 'input': ['trade_price'], 'params': []},
    # 'mama3_18': {'function': 'MAMA', 'dataframe': 'DAYS_18', 'input': ['trade_price'], 'params': []},
    # 'mama3_19': {'function': 'MAMA', 'dataframe': 'DAYS_19', 'input': ['trade_price'], 'params': []},
    # 'mama3_20': {'function': 'MAMA', 'dataframe': 'DAYS_20', 'input': ['trade_price'], 'params': []},
    # 'mama3_21': {'function': 'MAMA', 'dataframe': 'DAYS_21', 'input': ['trade_price'], 'params': []},
    # 'mama3_22': {'function': 'MAMA', 'dataframe': 'DAYS_22', 'input': ['trade_price'], 'params': []},
    # 'mama3_23': {'function': 'MAMA', 'dataframe': 'DAYS_23', 'input': ['trade_price'], 'params': []},
    #
    # 'mama10_0': {'function': 'MAMA', 'dataframe': 'DAYS_0', 'input': ['trade_price'], 'params': []},
    # 'mama10_1': {'function': 'MAMA', 'dataframe': 'DAYS_1', 'input': ['trade_price'], 'params': []},
    # 'mama10_2': {'function': 'MAMA', 'dataframe': 'DAYS_2', 'input': ['trade_price'], 'params': []},
    # 'mama10_3': {'function': 'MAMA', 'dataframe': 'DAYS_3', 'input': ['trade_price'], 'params': []},
    # 'mama10_4': {'function': 'MAMA', 'dataframe': 'DAYS_4', 'input': ['trade_price'], 'params': []},
    # 'mama10_5': {'function': 'MAMA', 'dataframe': 'DAYS_5', 'input': ['trade_price'], 'params': []},
    # 'mama10_6': {'function': 'MAMA', 'dataframe': 'DAYS_6', 'input': ['trade_price'], 'params': []},
    # 'mama10_7': {'function': 'MAMA', 'dataframe': 'DAYS_7', 'input': ['trade_price'], 'params': []},
    # 'mama10_8': {'function': 'MAMA', 'dataframe': 'DAYS_8', 'input': ['trade_price'], 'params': []},
    # 'mama10_9': {'function': 'MAMA', 'dataframe': 'DAYS_9', 'input': ['trade_price'], 'params': []},
    # 'mama10_10': {'function': 'MAMA', 'dataframe': 'DAYS_10', 'input': ['trade_price'], 'params': []},
    # 'mama10_11': {'function': 'MAMA', 'dataframe': 'DAYS_11', 'input': ['trade_price'], 'params': []},
    # 'mama10_12': {'function': 'MAMA', 'dataframe': 'DAYS_12', 'input': ['trade_price'], 'params': []},
    # 'mama10_13': {'function': 'MAMA', 'dataframe': 'DAYS_13', 'input': ['trade_price'], 'params': []},
    # 'mama10_14': {'function': 'MAMA', 'dataframe': 'DAYS_14', 'input': ['trade_price'], 'params': []},
    # 'mama10_15': {'function': 'MAMA', 'dataframe': 'DAYS_15', 'input': ['trade_price'], 'params': []},
    # 'mama10_16': {'function': 'MAMA', 'dataframe': 'DAYS_16', 'input': ['trade_price'], 'params': []},
    # 'mama10_17': {'function': 'MAMA', 'dataframe': 'DAYS_17', 'input': ['trade_price'], 'params': []},
    # 'mama10_18': {'function': 'MAMA', 'dataframe': 'DAYS_18', 'input': ['trade_price'], 'params': []},
    # 'mama10_19': {'function': 'MAMA', 'dataframe': 'DAYS_19', 'input': ['trade_price'], 'params': []},
    # 'mama10_20': {'function': 'MAMA', 'dataframe': 'DAYS_20', 'input': ['trade_price'], 'params': []},
    # 'mama10_21': {'function': 'MAMA', 'dataframe': 'DAYS_21', 'input': ['trade_price'], 'params': []},
    # 'mama10_22': {'function': 'MAMA', 'dataframe': 'DAYS_22', 'input': ['trade_price'], 'params': []},
    # 'mama10_23': {'function': 'MAMA', 'dataframe': 'DAYS_23', 'input': ['trade_price'], 'params': []},
    #
    # 'mama20_0': {'function': 'MAMA', 'dataframe': 'DAYS_0', 'input': ['trade_price'], 'params': []},
    # 'mama20_1': {'function': 'MAMA', 'dataframe': 'DAYS_1', 'input': ['trade_price'], 'params': []},
    # 'mama20_2': {'function': 'MAMA', 'dataframe': 'DAYS_2', 'input': ['trade_price'], 'params': []},
    # 'mama20_3': {'function': 'MAMA', 'dataframe': 'DAYS_3', 'input': ['trade_price'], 'params': []},
    # 'mama20_4': {'function': 'MAMA', 'dataframe': 'DAYS_4', 'input': ['trade_price'], 'params': []},
    # 'mama20_5': {'function': 'MAMA', 'dataframe': 'DAYS_5', 'input': ['trade_price'], 'params': []},
    # 'mama20_6': {'function': 'MAMA', 'dataframe': 'DAYS_6', 'input': ['trade_price'], 'params': []},
    # 'mama20_7': {'function': 'MAMA', 'dataframe': 'DAYS_7', 'input': ['trade_price'], 'params': []},
    # 'mama20_8': {'function': 'MAMA', 'dataframe': 'DAYS_8', 'input': ['trade_price'], 'params': []},
    # 'mama20_9': {'function': 'MAMA', 'dataframe': 'DAYS_9', 'input': ['trade_price'], 'params': []},
    # 'mama20_10': {'function': 'MAMA', 'dataframe': 'DAYS_10', 'input': ['trade_price'], 'params': []},
    # 'mama20_11': {'function': 'MAMA', 'dataframe': 'DAYS_11', 'input': ['trade_price'], 'params': []},
    # 'mama20_12': {'function': 'MAMA', 'dataframe': 'DAYS_12', 'input': ['trade_price'], 'params': []},
    # 'mama20_13': {'function': 'MAMA', 'dataframe': 'DAYS_13', 'input': ['trade_price'], 'params': []},
    # 'mama20_14': {'function': 'MAMA', 'dataframe': 'DAYS_14', 'input': ['trade_price'], 'params': []},
    # 'mama20_15': {'function': 'MAMA', 'dataframe': 'DAYS_15', 'input': ['trade_price'], 'params': []},
    # 'mama20_16': {'function': 'MAMA', 'dataframe': 'DAYS_16', 'input': ['trade_price'], 'params': []},
    # 'mama20_17': {'function': 'MAMA', 'dataframe': 'DAYS_17', 'input': ['trade_price'], 'params': []},
    # 'mama20_18': {'function': 'MAMA', 'dataframe': 'DAYS_18', 'input': ['trade_price'], 'params': []},
    # 'mama20_19': {'function': 'MAMA', 'dataframe': 'DAYS_19', 'input': ['trade_price'], 'params': []},
    # 'mama20_20': {'function': 'MAMA', 'dataframe': 'DAYS_20', 'input': ['trade_price'], 'params': []},
    # 'mama20_21': {'function': 'MAMA', 'dataframe': 'DAYS_21', 'input': ['trade_price'], 'params': []},
    # 'mama20_22': {'function': 'MAMA', 'dataframe': 'DAYS_22', 'input': ['trade_price'], 'params': []},
    # 'mama20_23': {'function': 'MAMA', 'dataframe': 'DAYS_23', 'input': ['trade_price'], 'params': []},
    #
    # 'midpoint_0': {'function': 'MIDPOINT', 'dataframe': 'DAYS_0', 'input': ['trade_price'], 'params': [14]},
    # 'midpoint_1': {'function': 'MIDPOINT', 'dataframe': 'DAYS_1', 'input': ['trade_price'], 'params': [14]},
    # 'midpoint_2': {'function': 'MIDPOINT', 'dataframe': 'DAYS_2', 'input': ['trade_price'], 'params': [14]},
    # 'midpoint_3': {'function': 'MIDPOINT', 'dataframe': 'DAYS_3', 'input': ['trade_price'], 'params': [14]},
    # 'midpoint_4': {'function': 'MIDPOINT', 'dataframe': 'DAYS_4', 'input': ['trade_price'], 'params': [14]},
    # 'midpoint_5': {'function': 'MIDPOINT', 'dataframe': 'DAYS_5', 'input': ['trade_price'], 'params': [14]},
    # 'midpoint_6': {'function': 'MIDPOINT', 'dataframe': 'DAYS_6', 'input': ['trade_price'], 'params': [14]},
    # 'midpoint_7': {'function': 'MIDPOINT', 'dataframe': 'DAYS_7', 'input': ['trade_price'], 'params': [14]},
    # 'midpoint_8': {'function': 'MIDPOINT', 'dataframe': 'DAYS_8', 'input': ['trade_price'], 'params': [14]},
    # 'midpoint_9': {'function': 'MIDPOINT', 'dataframe': 'DAYS_9', 'input': ['trade_price'], 'params': [14]},
    # 'midpoint_10': {'function': 'MIDPOINT', 'dataframe': 'DAYS_10', 'input': ['trade_price'], 'params': [14]},
    # 'midpoint_11': {'function': 'MIDPOINT', 'dataframe': 'DAYS_11', 'input': ['trade_price'], 'params': [14]},
    # 'midpoint_12': {'function': 'MIDPOINT', 'dataframe': 'DAYS_12', 'input': ['trade_price'], 'params': [14]},
    # 'midpoint_13': {'function': 'MIDPOINT', 'dataframe': 'DAYS_13', 'input': ['trade_price'], 'params': [14]},
    # 'midpoint_14': {'function': 'MIDPOINT', 'dataframe': 'DAYS_14', 'input': ['trade_price'], 'params': [14]},
    # 'midpoint_15': {'function': 'MIDPOINT', 'dataframe': 'DAYS_15', 'input': ['trade_price'], 'params': [14]},
    # 'midpoint_16': {'function': 'MIDPOINT', 'dataframe': 'DAYS_16', 'input': ['trade_price'], 'params': [14]},
    # 'midpoint_17': {'function': 'MIDPOINT', 'dataframe': 'DAYS_17', 'input': ['trade_price'], 'params': [14]},
    # 'midpoint_18': {'function': 'MIDPOINT', 'dataframe': 'DAYS_18', 'input': ['trade_price'], 'params': [14]},
    # 'midpoint_19': {'function': 'MIDPOINT', 'dataframe': 'DAYS_19', 'input': ['trade_price'], 'params': [14]},
    # 'midpoint_20': {'function': 'MIDPOINT', 'dataframe': 'DAYS_20', 'input': ['trade_price'], 'params': [14]},
    # 'midpoint_21': {'function': 'MIDPOINT', 'dataframe': 'DAYS_21', 'input': ['trade_price'], 'params': [14]},
    # 'midpoint_22': {'function': 'MIDPOINT', 'dataframe': 'DAYS_22', 'input': ['trade_price'], 'params': [14]},
    # 'midpoint_23': {'function': 'MIDPOINT', 'dataframe': 'DAYS_23', 'input': ['trade_price'], 'params': [14]},
    #
    # 'midprice_0': {'function': 'MIDPRICE', 'dataframe': 'DAYS_0', 'input': ['high_price', 'low_price'], 'params': [14]},
    # 'midprice_1': {'function': 'MIDPRICE', 'dataframe': 'DAYS_1', 'input': ['high_price', 'low_price'], 'params': [14]},
    # 'midprice_2': {'function': 'MIDPRICE', 'dataframe': 'DAYS_2', 'input': ['high_price', 'low_price'], 'params': [14]},
    # 'midprice_3': {'function': 'MIDPRICE', 'dataframe': 'DAYS_3', 'input': ['high_price', 'low_price'], 'params': [14]},
    # 'midprice_4': {'function': 'MIDPRICE', 'dataframe': 'DAYS_4', 'input': ['high_price', 'low_price'], 'params': [14]},
    # 'midprice_5': {'function': 'MIDPRICE', 'dataframe': 'DAYS_5', 'input': ['high_price', 'low_price'], 'params': [14]},
    # 'midprice_6': {'function': 'MIDPRICE', 'dataframe': 'DAYS_6', 'input': ['high_price', 'low_price'], 'params': [14]},
    # 'midprice_7': {'function': 'MIDPRICE', 'dataframe': 'DAYS_7', 'input': ['high_price', 'low_price'], 'params': [14]},
    # 'midprice_8': {'function': 'MIDPRICE', 'dataframe': 'DAYS_8', 'input': ['high_price', 'low_price'], 'params': [14]},
    # 'midprice_9': {'function': 'MIDPRICE', 'dataframe': 'DAYS_9', 'input': ['high_price', 'low_price'], 'params': [14]},
    # 'midprice_10': {'function': 'MIDPRICE', 'dataframe': 'DAYS_10', 'input': ['high_price', 'low_price'], 'params': [14]},
    # 'midprice_11': {'function': 'MIDPRICE', 'dataframe': 'DAYS_11', 'input': ['high_price', 'low_price'], 'params': [14]},
    # 'midprice_12': {'function': 'MIDPRICE', 'dataframe': 'DAYS_12', 'input': ['high_price', 'low_price'], 'params': [14]},
    # 'midprice_13': {'function': 'MIDPRICE', 'dataframe': 'DAYS_13', 'input': ['high_price', 'low_price'], 'params': [14]},
    # 'midprice_14': {'function': 'MIDPRICE', 'dataframe': 'DAYS_14', 'input': ['high_price', 'low_price'], 'params': [14]},
    # 'midprice_15': {'function': 'MIDPRICE', 'dataframe': 'DAYS_15', 'input': ['high_price', 'low_price'], 'params': [14]},
    # 'midprice_16': {'function': 'MIDPRICE', 'dataframe': 'DAYS_16', 'input': ['high_price', 'low_price'], 'params': [14]},
    # 'midprice_17': {'function': 'MIDPRICE', 'dataframe': 'DAYS_17', 'input': ['high_price', 'low_price'], 'params': [14]},
    # 'midprice_18': {'function': 'MIDPRICE', 'dataframe': 'DAYS_18', 'input': ['high_price', 'low_price'], 'params': [14]},
    # 'midprice_19': {'function': 'MIDPRICE', 'dataframe': 'DAYS_19', 'input': ['high_price', 'low_price'], 'params': [14]},
    # 'midprice_20': {'function': 'MIDPRICE', 'dataframe': 'DAYS_20', 'input': ['high_price', 'low_price'], 'params': [14]},
    # 'midprice_21': {'function': 'MIDPRICE', 'dataframe': 'DAYS_21', 'input': ['high_price', 'low_price'], 'params': [14]},
    # 'midprice_22': {'function': 'MIDPRICE', 'dataframe': 'DAYS_22', 'input': ['high_price', 'low_price'], 'params': [14]},
    # 'midprice_23': {'function': 'MIDPRICE', 'dataframe': 'DAYS_23', 'input': ['high_price', 'low_price'], 'params': [14]},
    #
    # 'sar_0': {'function': 'SAR', 'dataframe': 'DAYS_0', 'input': ['high_price', 'low_price'], 'params': []},
    # 'sar_1': {'function': 'SAR', 'dataframe': 'DAYS_1', 'input': ['high_price', 'low_price'], 'params': []},
    # 'sar_2': {'function': 'SAR', 'dataframe': 'DAYS_2', 'input': ['high_price', 'low_price'], 'params': []},
    # 'sar_3': {'function': 'SAR', 'dataframe': 'DAYS_3', 'input': ['high_price', 'low_price'], 'params': []},
    # 'sar_4': {'function': 'SAR', 'dataframe': 'DAYS_4', 'input': ['high_price', 'low_price'], 'params': []},
    # 'sar_5': {'function': 'SAR', 'dataframe': 'DAYS_5', 'input': ['high_price', 'low_price'], 'params': []},
    # 'sar_6': {'function': 'SAR', 'dataframe': 'DAYS_6', 'input': ['high_price', 'low_price'], 'params': []},
    # 'sar_7': {'function': 'SAR', 'dataframe': 'DAYS_7', 'input': ['high_price', 'low_price'], 'params': []},
    # 'sar_8': {'function': 'SAR', 'dataframe': 'DAYS_8', 'input': ['high_price', 'low_price'], 'params': []},
    # 'sar_9': {'function': 'SAR', 'dataframe': 'DAYS_9', 'input': ['high_price', 'low_price'], 'params': []},
    # 'sar_10': {'function': 'SAR', 'dataframe': 'DAYS_10', 'input': ['high_price', 'low_price'], 'params': []},
    # 'sar_11': {'function': 'SAR', 'dataframe': 'DAYS_11', 'input': ['high_price', 'low_price'], 'params': []},
    # 'sar_12': {'function': 'SAR', 'dataframe': 'DAYS_12', 'input': ['high_price', 'low_price'], 'params': []},
    # 'sar_13': {'function': 'SAR', 'dataframe': 'DAYS_13', 'input': ['high_price', 'low_price'], 'params': []},
    # 'sar_14': {'function': 'SAR', 'dataframe': 'DAYS_14', 'input': ['high_price', 'low_price'], 'params': []},
    # 'sar_15': {'function': 'SAR', 'dataframe': 'DAYS_15', 'input': ['high_price', 'low_price'], 'params': []},
    # 'sar_16': {'function': 'SAR', 'dataframe': 'DAYS_16', 'input': ['high_price', 'low_price'], 'params': []},
    # 'sar_17': {'function': 'SAR', 'dataframe': 'DAYS_17', 'input': ['high_price', 'low_price'], 'params': []},
    # 'sar_18': {'function': 'SAR', 'dataframe': 'DAYS_18', 'input': ['high_price', 'low_price'], 'params': []},
    # 'sar_19': {'function': 'SAR', 'dataframe': 'DAYS_19', 'input': ['high_price', 'low_price'], 'params': []},
    # 'sar_20': {'function': 'SAR', 'dataframe': 'DAYS_20', 'input': ['high_price', 'low_price'], 'params': []},
    # 'sar_21': {'function': 'SAR', 'dataframe': 'DAYS_21', 'input': ['high_price', 'low_price'], 'params': []},
    # 'sar_22': {'function': 'SAR', 'dataframe': 'DAYS_22', 'input': ['high_price', 'low_price'], 'params': []},
    # 'sar_23': {'function': 'SAR', 'dataframe': 'DAYS_23', 'input': ['high_price', 'low_price'], 'params': []},
    #
    # 'sarext_0': {'function': 'SAREXT', 'dataframe': 'DAYS_0', 'input': ['high_price', 'low_price'], 'params': []},
    # 'sarext_1': {'function': 'SAREXT', 'dataframe': 'DAYS_1', 'input': ['high_price', 'low_price'], 'params': []},
    # 'sarext_2': {'function': 'SAREXT', 'dataframe': 'DAYS_2', 'input': ['high_price', 'low_price'], 'params': []},
    # 'sarext_3': {'function': 'SAREXT', 'dataframe': 'DAYS_3', 'input': ['high_price', 'low_price'], 'params': []},
    # 'sarext_4': {'function': 'SAREXT', 'dataframe': 'DAYS_4', 'input': ['high_price', 'low_price'], 'params': []},
    # 'sarext_5': {'function': 'SAREXT', 'dataframe': 'DAYS_5', 'input': ['high_price', 'low_price'], 'params': []},
    # 'sarext_6': {'function': 'SAREXT', 'dataframe': 'DAYS_6', 'input': ['high_price', 'low_price'], 'params': []},
    # 'sarext_7': {'function': 'SAREXT', 'dataframe': 'DAYS_7', 'input': ['high_price', 'low_price'], 'params': []},
    # 'sarext_8': {'function': 'SAREXT', 'dataframe': 'DAYS_8', 'input': ['high_price', 'low_price'], 'params': []},
    # 'sarext_9': {'function': 'SAREXT', 'dataframe': 'DAYS_9', 'input': ['high_price', 'low_price'], 'params': []},
    # 'sarext_10': {'function': 'SAREXT', 'dataframe': 'DAYS_10', 'input': ['high_price', 'low_price'], 'params': []},
    # 'sarext_11': {'function': 'SAREXT', 'dataframe': 'DAYS_11', 'input': ['high_price', 'low_price'], 'params': []},
    # 'sarext_12': {'function': 'SAREXT', 'dataframe': 'DAYS_12', 'input': ['high_price', 'low_price'], 'params': []},
    # 'sarext_13': {'function': 'SAREXT', 'dataframe': 'DAYS_13', 'input': ['high_price', 'low_price'], 'params': []},
    # 'sarext_14': {'function': 'SAREXT', 'dataframe': 'DAYS_14', 'input': ['high_price', 'low_price'], 'params': []},
    # 'sarext_15': {'function': 'SAREXT', 'dataframe': 'DAYS_15', 'input': ['high_price', 'low_price'], 'params': []},
    # 'sarext_16': {'function': 'SAREXT', 'dataframe': 'DAYS_16', 'input': ['high_price', 'low_price'], 'params': []},
    # 'sarext_17': {'function': 'SAREXT', 'dataframe': 'DAYS_17', 'input': ['high_price', 'low_price'], 'params': []},
    # 'sarext_18': {'function': 'SAREXT', 'dataframe': 'DAYS_18', 'input': ['high_price', 'low_price'], 'params': []},
    # 'sarext_19': {'function': 'SAREXT', 'dataframe': 'DAYS_19', 'input': ['high_price', 'low_price'], 'params': []},
    # 'sarext_20': {'function': 'SAREXT', 'dataframe': 'DAYS_20', 'input': ['high_price', 'low_price'], 'params': []},
    # 'sarext_21': {'function': 'SAREXT', 'dataframe': 'DAYS_21', 'input': ['high_price', 'low_price'], 'params': []},
    # 'sarext_22': {'function': 'SAREXT', 'dataframe': 'DAYS_22', 'input': ['high_price', 'low_price'], 'params': []},
    # 'sarext_23': {'function': 'SAREXT', 'dataframe': 'DAYS_23', 'input': ['high_price', 'low_price'], 'params': []},
    #
    # 't3_0': {'function': 'T3', 'dataframe': 'DAYS_0', 'input': ['trade_price'], 'params': []},  # p[0]: timeperiod
    # 't3_1': {'function': 'T3', 'dataframe': 'DAYS_1', 'input': ['trade_price'], 'params': []},  # p[0]: timeperiod
    # 't3_2': {'function': 'T3', 'dataframe': 'DAYS_2', 'input': ['trade_price'], 'params': []},  # p[0]: timeperiod
    # 't3_3': {'function': 'T3', 'dataframe': 'DAYS_3', 'input': ['trade_price'], 'params': []},  # p[0]: timeperiod
    # 't3_4': {'function': 'T3', 'dataframe': 'DAYS_4', 'input': ['trade_price'], 'params': []},  # p[0]: timeperiod
    # 't3_5': {'function': 'T3', 'dataframe': 'DAYS_5', 'input': ['trade_price'], 'params': []},  # p[0]: timeperiod
    # 't3_6': {'function': 'T3', 'dataframe': 'DAYS_6', 'input': ['trade_price'], 'params': []},  # p[0]: timeperiod
    # 't3_7': {'function': 'T3', 'dataframe': 'DAYS_7', 'input': ['trade_price'], 'params': []},  # p[0]: timeperiod
    # 't3_8': {'function': 'T3', 'dataframe': 'DAYS_8', 'input': ['trade_price'], 'params': []},  # p[0]: timeperiod
    # 't3_9': {'function': 'T3', 'dataframe': 'DAYS_9', 'input': ['trade_price'], 'params': []},  # p[0]: timeperiod
    # 't3_10': {'function': 'T3', 'dataframe': 'DAYS_10', 'input': ['trade_price'], 'params': []},  # p[0]: timeperiod
    # 't3_11': {'function': 'T3', 'dataframe': 'DAYS_11', 'input': ['trade_price'], 'params': []},  # p[0]: timeperiod
    # 't3_12': {'function': 'T3', 'dataframe': 'DAYS_12', 'input': ['trade_price'], 'params': []},  # p[0]: timeperiod
    # 't3_13': {'function': 'T3', 'dataframe': 'DAYS_13', 'input': ['trade_price'], 'params': []},  # p[0]: timeperiod
    # 't3_14': {'function': 'T3', 'dataframe': 'DAYS_14', 'input': ['trade_price'], 'params': []},  # p[0]: timeperiod
    # 't3_15': {'function': 'T3', 'dataframe': 'DAYS_15', 'input': ['trade_price'], 'params': []},  # p[0]: timeperiod
    # 't3_16': {'function': 'T3', 'dataframe': 'DAYS_16', 'input': ['trade_price'], 'params': []},  # p[0]: timeperiod
    # 't3_17': {'function': 'T3', 'dataframe': 'DAYS_17', 'input': ['trade_price'], 'params': []},  # p[0]: timeperiod
    # 't3_18': {'function': 'T3', 'dataframe': 'DAYS_18', 'input': ['trade_price'], 'params': []},  # p[0]: timeperiod
    # 't3_19': {'function': 'T3', 'dataframe': 'DAYS_19', 'input': ['trade_price'], 'params': []},  # p[0]: timeperiod
    # 't3_20': {'function': 'T3', 'dataframe': 'DAYS_20', 'input': ['trade_price'], 'params': []},  # p[0]: timeperiod
    # 't3_21': {'function': 'T3', 'dataframe': 'DAYS_21', 'input': ['trade_price'], 'params': []},  # p[0]: timeperiod
    # 't3_22': {'function': 'T3', 'dataframe': 'DAYS_22', 'input': ['trade_price'], 'params': []},  # p[0]: timeperiod
    # 't3_23': {'function': 'T3', 'dataframe': 'DAYS_23', 'input': ['trade_price'], 'params': []},  # p[0]: timeperiod
    #
    #
    # 'tema5_0': {'function': 'TEMA', 'dataframe': 'DAYS_0', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    # 'tema5_1': {'function': 'TEMA', 'dataframe': 'DAYS_1', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    # 'tema5_2': {'function': 'TEMA', 'dataframe': 'DAYS_2', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    # 'tema5_3': {'function': 'TEMA', 'dataframe': 'DAYS_3', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    # 'tema5_4': {'function': 'TEMA', 'dataframe': 'DAYS_4', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    # 'tema5_5': {'function': 'TEMA', 'dataframe': 'DAYS_5', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    # 'tema5_6': {'function': 'TEMA', 'dataframe': 'DAYS_6', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    # 'tema5_7': {'function': 'TEMA', 'dataframe': 'DAYS_7', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    # 'tema5_8': {'function': 'TEMA', 'dataframe': 'DAYS_8', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    # 'tema5_9': {'function': 'TEMA', 'dataframe': 'DAYS_9', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    # 'tema5_10': {'function': 'TEMA', 'dataframe': 'DAYS_10', 'input': ['trade_price'], 'params': [5]},
    # 'tema5_11': {'function': 'TEMA', 'dataframe': 'DAYS_11', 'input': ['trade_price'], 'params': [5]},
    # 'tema5_12': {'function': 'TEMA', 'dataframe': 'DAYS_12', 'input': ['trade_price'], 'params': [5]},
    # 'tema5_13': {'function': 'TEMA', 'dataframe': 'DAYS_13', 'input': ['trade_price'], 'params': [5]},
    # 'tema5_14': {'function': 'TEMA', 'dataframe': 'DAYS_14', 'input': ['trade_price'], 'params': [5]},
    # 'tema5_15': {'function': 'TEMA', 'dataframe': 'DAYS_15', 'input': ['trade_price'], 'params': [5]},
    # 'tema5_16': {'function': 'TEMA', 'dataframe': 'DAYS_16', 'input': ['trade_price'], 'params': [5]},
    # 'tema5_17': {'function': 'TEMA', 'dataframe': 'DAYS_17', 'input': ['trade_price'], 'params': [5]},
    # 'tema5_18': {'function': 'TEMA', 'dataframe': 'DAYS_18', 'input': ['trade_price'], 'params': [5]},
    # 'tema5_19': {'function': 'TEMA', 'dataframe': 'DAYS_19', 'input': ['trade_price'], 'params': [5]},
    # 'tema5_20': {'function': 'TEMA', 'dataframe': 'DAYS_20', 'input': ['trade_price'], 'params': [5]},
    # 'tema5_21': {'function': 'TEMA', 'dataframe': 'DAYS_21', 'input': ['trade_price'], 'params': [5]},
    # 'tema5_22': {'function': 'TEMA', 'dataframe': 'DAYS_22', 'input': ['trade_price'], 'params': [5]},
    # 'tema5_23': {'function': 'TEMA', 'dataframe': 'DAYS_23', 'input': ['trade_price'], 'params': [5]},
    #
    # 'tema3_0': {'function': 'TEMA', 'dataframe': 'DAYS_0', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    # 'tema3_1': {'function': 'TEMA', 'dataframe': 'DAYS_1', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    # 'tema3_2': {'function': 'TEMA', 'dataframe': 'DAYS_2', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    # 'tema3_3': {'function': 'TEMA', 'dataframe': 'DAYS_3', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    # 'tema3_4': {'function': 'TEMA', 'dataframe': 'DAYS_4', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    # 'tema3_5': {'function': 'TEMA', 'dataframe': 'DAYS_5', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    # 'tema3_6': {'function': 'TEMA', 'dataframe': 'DAYS_6', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    # 'tema3_7': {'function': 'TEMA', 'dataframe': 'DAYS_7', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    # 'tema3_8': {'function': 'TEMA', 'dataframe': 'DAYS_8', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    # 'tema3_9': {'function': 'TEMA', 'dataframe': 'DAYS_9', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    # 'tema3_10': {'function': 'TEMA', 'dataframe': 'DAYS_10', 'input': ['trade_price'], 'params': [3]},
    # 'tema3_11': {'function': 'TEMA', 'dataframe': 'DAYS_11', 'input': ['trade_price'], 'params': [3]},
    # 'tema3_12': {'function': 'TEMA', 'dataframe': 'DAYS_12', 'input': ['trade_price'], 'params': [3]},
    # 'tema3_13': {'function': 'TEMA', 'dataframe': 'DAYS_13', 'input': ['trade_price'], 'params': [3]},
    # 'tema3_14': {'function': 'TEMA', 'dataframe': 'DAYS_14', 'input': ['trade_price'], 'params': [3]},
    # 'tema3_15': {'function': 'TEMA', 'dataframe': 'DAYS_15', 'input': ['trade_price'], 'params': [3]},
    # 'tema3_16': {'function': 'TEMA', 'dataframe': 'DAYS_16', 'input': ['trade_price'], 'params': [3]},
    # 'tema3_17': {'function': 'TEMA', 'dataframe': 'DAYS_17', 'input': ['trade_price'], 'params': [3]},
    # 'tema3_18': {'function': 'TEMA', 'dataframe': 'DAYS_18', 'input': ['trade_price'], 'params': [3]},
    # 'tema3_19': {'function': 'TEMA', 'dataframe': 'DAYS_19', 'input': ['trade_price'], 'params': [3]},
    # 'tema3_20': {'function': 'TEMA', 'dataframe': 'DAYS_20', 'input': ['trade_price'], 'params': [3]},
    # 'tema3_21': {'function': 'TEMA', 'dataframe': 'DAYS_21', 'input': ['trade_price'], 'params': [3]},
    # 'tema3_22': {'function': 'TEMA', 'dataframe': 'DAYS_22', 'input': ['trade_price'], 'params': [3]},
    # 'tema3_23': {'function': 'TEMA', 'dataframe': 'DAYS_23', 'input': ['trade_price'], 'params': [3]},
    #
    # 'tema10_0': {'function': 'TEMA', 'dataframe': 'DAYS_0', 'input': ['trade_price'], 'params': [10]},
    # 'tema10_1': {'function': 'TEMA', 'dataframe': 'DAYS_1', 'input': ['trade_price'], 'params': [10]},
    # 'tema10_2': {'function': 'TEMA', 'dataframe': 'DAYS_2', 'input': ['trade_price'], 'params': [10]},
    # 'tema10_3': {'function': 'TEMA', 'dataframe': 'DAYS_3', 'input': ['trade_price'], 'params': [10]},
    # 'tema10_4': {'function': 'TEMA', 'dataframe': 'DAYS_4', 'input': ['trade_price'], 'params': [10]},
    # 'tema10_5': {'function': 'TEMA', 'dataframe': 'DAYS_5', 'input': ['trade_price'], 'params': [10]},
    # 'tema10_6': {'function': 'TEMA', 'dataframe': 'DAYS_6', 'input': ['trade_price'], 'params': [10]},
    # 'tema10_7': {'function': 'TEMA', 'dataframe': 'DAYS_7', 'input': ['trade_price'], 'params': [10]},
    # 'tema10_8': {'function': 'TEMA', 'dataframe': 'DAYS_8', 'input': ['trade_price'], 'params': [10]},
    # 'tema10_9': {'function': 'TEMA', 'dataframe': 'DAYS_9', 'input': ['trade_price'], 'params': [10]},
    # 'tema10_10': {'function': 'TEMA', 'dataframe': 'DAYS_10', 'input': ['trade_price'], 'params': [10]},
    # 'tema10_11': {'function': 'TEMA', 'dataframe': 'DAYS_11', 'input': ['trade_price'], 'params': [10]},
    # 'tema10_12': {'function': 'TEMA', 'dataframe': 'DAYS_12', 'input': ['trade_price'], 'params': [10]},
    # 'tema10_13': {'function': 'TEMA', 'dataframe': 'DAYS_13', 'input': ['trade_price'], 'params': [10]},
    # 'tema10_14': {'function': 'TEMA', 'dataframe': 'DAYS_14', 'input': ['trade_price'], 'params': [10]},
    # 'tema10_15': {'function': 'TEMA', 'dataframe': 'DAYS_15', 'input': ['trade_price'], 'params': [10]},
    # 'tema10_16': {'function': 'TEMA', 'dataframe': 'DAYS_16', 'input': ['trade_price'], 'params': [10]},
    # 'tema10_17': {'function': 'TEMA', 'dataframe': 'DAYS_17', 'input': ['trade_price'], 'params': [10]},
    # 'tema10_18': {'function': 'TEMA', 'dataframe': 'DAYS_18', 'input': ['trade_price'], 'params': [10]},
    # 'tema10_19': {'function': 'TEMA', 'dataframe': 'DAYS_19', 'input': ['trade_price'], 'params': [10]},
    # 'tema10_20': {'function': 'TEMA', 'dataframe': 'DAYS_20', 'input': ['trade_price'], 'params': [10]},
    # 'tema10_21': {'function': 'TEMA', 'dataframe': 'DAYS_21', 'input': ['trade_price'], 'params': [10]},
    # 'tema10_22': {'function': 'TEMA', 'dataframe': 'DAYS_22', 'input': ['trade_price'], 'params': [10]},
    # 'tema10_23': {'function': 'TEMA', 'dataframe': 'DAYS_23', 'input': ['trade_price'], 'params': [10]},
    #
    # 'tema20_0': {'function': 'TEMA', 'dataframe': 'DAYS_0', 'input': ['trade_price'], 'params': [20]},
    # 'tema20_1': {'function': 'TEMA', 'dataframe': 'DAYS_1', 'input': ['trade_price'], 'params': [20]},
    # 'tema20_2': {'function': 'TEMA', 'dataframe': 'DAYS_2', 'input': ['trade_price'], 'params': [20]},
    # 'tema20_3': {'function': 'TEMA', 'dataframe': 'DAYS_3', 'input': ['trade_price'], 'params': [20]},
    # 'tema20_4': {'function': 'TEMA', 'dataframe': 'DAYS_4', 'input': ['trade_price'], 'params': [20]},
    # 'tema20_5': {'function': 'TEMA', 'dataframe': 'DAYS_5', 'input': ['trade_price'], 'params': [20]},
    # 'tema20_6': {'function': 'TEMA', 'dataframe': 'DAYS_6', 'input': ['trade_price'], 'params': [20]},
    # 'tema20_7': {'function': 'TEMA', 'dataframe': 'DAYS_7', 'input': ['trade_price'], 'params': [20]},
    # 'tema20_8': {'function': 'TEMA', 'dataframe': 'DAYS_8', 'input': ['trade_price'], 'params': [20]},
    # 'tema20_9': {'function': 'TEMA', 'dataframe': 'DAYS_9', 'input': ['trade_price'], 'params': [20]},
    # 'tema20_10': {'function': 'TEMA', 'dataframe': 'DAYS_10', 'input': ['trade_price'], 'params': [20]},
    # 'tema20_11': {'function': 'TEMA', 'dataframe': 'DAYS_11', 'input': ['trade_price'], 'params': [20]},
    # 'tema20_12': {'function': 'TEMA', 'dataframe': 'DAYS_12', 'input': ['trade_price'], 'params': [20]},
    # 'tema20_13': {'function': 'TEMA', 'dataframe': 'DAYS_13', 'input': ['trade_price'], 'params': [20]},
    # 'tema20_14': {'function': 'TEMA', 'dataframe': 'DAYS_14', 'input': ['trade_price'], 'params': [20]},
    # 'tema20_15': {'function': 'TEMA', 'dataframe': 'DAYS_15', 'input': ['trade_price'], 'params': [20]},
    # 'tema20_16': {'function': 'TEMA', 'dataframe': 'DAYS_16', 'input': ['trade_price'], 'params': [20]},
    # 'tema20_17': {'function': 'TEMA', 'dataframe': 'DAYS_17', 'input': ['trade_price'], 'params': [20]},
    # 'tema20_18': {'function': 'TEMA', 'dataframe': 'DAYS_18', 'input': ['trade_price'], 'params': [20]},
    # 'tema20_19': {'function': 'TEMA', 'dataframe': 'DAYS_19', 'input': ['trade_price'], 'params': [20]},
    # 'tema20_20': {'function': 'TEMA', 'dataframe': 'DAYS_20', 'input': ['trade_price'], 'params': [20]},
    # 'tema20_21': {'function': 'TEMA', 'dataframe': 'DAYS_21', 'input': ['trade_price'], 'params': [20]},
    # 'tema20_22': {'function': 'TEMA', 'dataframe': 'DAYS_22', 'input': ['trade_price'], 'params': [20]},
    # 'tema20_23': {'function': 'TEMA', 'dataframe': 'DAYS_23', 'input': ['trade_price'], 'params': [20]},
    #
    # 'trima5_0': {'function': 'TRIMA', 'dataframe': 'DAYS_0', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    # 'trima5_1': {'function': 'TRIMA', 'dataframe': 'DAYS_1', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    # 'trima5_2': {'function': 'TRIMA', 'dataframe': 'DAYS_2', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    # 'trima5_3': {'function': 'TRIMA', 'dataframe': 'DAYS_3', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    # 'trima5_4': {'function': 'TRIMA', 'dataframe': 'DAYS_4', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    # 'trima5_5': {'function': 'TRIMA', 'dataframe': 'DAYS_5', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    # 'trima5_6': {'function': 'TRIMA', 'dataframe': 'DAYS_6', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    # 'trima5_7': {'function': 'TRIMA', 'dataframe': 'DAYS_7', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    # 'trima5_8': {'function': 'TRIMA', 'dataframe': 'DAYS_8', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    # 'trima5_9': {'function': 'TRIMA', 'dataframe': 'DAYS_9', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    # 'trima5_10': {'function': 'TRIMA', 'dataframe': 'DAYS_10', 'input': ['trade_price'], 'params': [5]},
    # 'trima5_11': {'function': 'TRIMA', 'dataframe': 'DAYS_11', 'input': ['trade_price'], 'params': [5]},
    # 'trima5_12': {'function': 'TRIMA', 'dataframe': 'DAYS_12', 'input': ['trade_price'], 'params': [5]},
    # 'trima5_13': {'function': 'TRIMA', 'dataframe': 'DAYS_13', 'input': ['trade_price'], 'params': [5]},
    # 'trima5_14': {'function': 'TRIMA', 'dataframe': 'DAYS_14', 'input': ['trade_price'], 'params': [5]},
    # 'trima5_15': {'function': 'TRIMA', 'dataframe': 'DAYS_15', 'input': ['trade_price'], 'params': [5]},
    # 'trima5_16': {'function': 'TRIMA', 'dataframe': 'DAYS_16', 'input': ['trade_price'], 'params': [5]},
    # 'trima5_17': {'function': 'TRIMA', 'dataframe': 'DAYS_17', 'input': ['trade_price'], 'params': [5]},
    # 'trima5_18': {'function': 'TRIMA', 'dataframe': 'DAYS_18', 'input': ['trade_price'], 'params': [5]},
    # 'trima5_19': {'function': 'TRIMA', 'dataframe': 'DAYS_19', 'input': ['trade_price'], 'params': [5]},
    # 'trima5_20': {'function': 'TRIMA', 'dataframe': 'DAYS_20', 'input': ['trade_price'], 'params': [5]},
    # 'trima5_21': {'function': 'TRIMA', 'dataframe': 'DAYS_21', 'input': ['trade_price'], 'params': [5]},
    # 'trima5_22': {'function': 'TRIMA', 'dataframe': 'DAYS_22', 'input': ['trade_price'], 'params': [5]},
    # 'trima5_23': {'function': 'TRIMA', 'dataframe': 'DAYS_23', 'input': ['trade_price'], 'params': [5]},
    #
    # 'trima3_0': {'function': 'TRIMA', 'dataframe': 'DAYS_0', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    # 'trima3_1': {'function': 'TRIMA', 'dataframe': 'DAYS_1', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    # 'trima3_2': {'function': 'TRIMA', 'dataframe': 'DAYS_2', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    # 'trima3_3': {'function': 'TRIMA', 'dataframe': 'DAYS_3', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    # 'trima3_4': {'function': 'TRIMA', 'dataframe': 'DAYS_4', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    # 'trima3_5': {'function': 'TRIMA', 'dataframe': 'DAYS_5', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    # 'trima3_6': {'function': 'TRIMA', 'dataframe': 'DAYS_6', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    # 'trima3_7': {'function': 'TRIMA', 'dataframe': 'DAYS_7', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    # 'trima3_8': {'function': 'TRIMA', 'dataframe': 'DAYS_8', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    # 'trima3_9': {'function': 'TRIMA', 'dataframe': 'DAYS_9', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    # 'trima3_10': {'function': 'TRIMA', 'dataframe': 'DAYS_10', 'input': ['trade_price'], 'params': [3]},
    # 'trima3_11': {'function': 'TRIMA', 'dataframe': 'DAYS_11', 'input': ['trade_price'], 'params': [3]},
    # 'trima3_12': {'function': 'TRIMA', 'dataframe': 'DAYS_12', 'input': ['trade_price'], 'params': [3]},
    # 'trima3_13': {'function': 'TRIMA', 'dataframe': 'DAYS_13', 'input': ['trade_price'], 'params': [3]},
    # 'trima3_14': {'function': 'TRIMA', 'dataframe': 'DAYS_14', 'input': ['trade_price'], 'params': [3]},
    # 'trima3_15': {'function': 'TRIMA', 'dataframe': 'DAYS_15', 'input': ['trade_price'], 'params': [3]},
    # 'trima3_16': {'function': 'TRIMA', 'dataframe': 'DAYS_16', 'input': ['trade_price'], 'params': [3]},
    # 'trima3_17': {'function': 'TRIMA', 'dataframe': 'DAYS_17', 'input': ['trade_price'], 'params': [3]},
    # 'trima3_18': {'function': 'TRIMA', 'dataframe': 'DAYS_18', 'input': ['trade_price'], 'params': [3]},
    # 'trima3_19': {'function': 'TRIMA', 'dataframe': 'DAYS_19', 'input': ['trade_price'], 'params': [3]},
    # 'trima3_20': {'function': 'TRIMA', 'dataframe': 'DAYS_20', 'input': ['trade_price'], 'params': [3]},
    # 'trima3_21': {'function': 'TRIMA', 'dataframe': 'DAYS_21', 'input': ['trade_price'], 'params': [3]},
    # 'trima3_22': {'function': 'TRIMA', 'dataframe': 'DAYS_22', 'input': ['trade_price'], 'params': [3]},
    # 'trima3_23': {'function': 'TRIMA', 'dataframe': 'DAYS_23', 'input': ['trade_price'], 'params': [3]},
    #
    # 'trima10_0': {'function': 'TRIMA', 'dataframe': 'DAYS_0', 'input': ['trade_price'], 'params': [10]},
    # 'trima10_1': {'function': 'TRIMA', 'dataframe': 'DAYS_1', 'input': ['trade_price'], 'params': [10]},
    # 'trima10_2': {'function': 'TRIMA', 'dataframe': 'DAYS_2', 'input': ['trade_price'], 'params': [10]},
    # 'trima10_3': {'function': 'TRIMA', 'dataframe': 'DAYS_3', 'input': ['trade_price'], 'params': [10]},
    # 'trima10_4': {'function': 'TRIMA', 'dataframe': 'DAYS_4', 'input': ['trade_price'], 'params': [10]},
    # 'trima10_5': {'function': 'TRIMA', 'dataframe': 'DAYS_5', 'input': ['trade_price'], 'params': [10]},
    # 'trima10_6': {'function': 'TRIMA', 'dataframe': 'DAYS_6', 'input': ['trade_price'], 'params': [10]},
    # 'trima10_7': {'function': 'TRIMA', 'dataframe': 'DAYS_7', 'input': ['trade_price'], 'params': [10]},
    # 'trima10_8': {'function': 'TRIMA', 'dataframe': 'DAYS_8', 'input': ['trade_price'], 'params': [10]},
    # 'trima10_9': {'function': 'TRIMA', 'dataframe': 'DAYS_9', 'input': ['trade_price'], 'params': [10]},
    # 'trima10_10': {'function': 'TRIMA', 'dataframe': 'DAYS_10', 'input': ['trade_price'], 'params': [10]},
    # 'trima10_11': {'function': 'TRIMA', 'dataframe': 'DAYS_11', 'input': ['trade_price'], 'params': [10]},
    # 'trima10_12': {'function': 'TRIMA', 'dataframe': 'DAYS_12', 'input': ['trade_price'], 'params': [10]},
    # 'trima10_13': {'function': 'TRIMA', 'dataframe': 'DAYS_13', 'input': ['trade_price'], 'params': [10]},
    # 'trima10_14': {'function': 'TRIMA', 'dataframe': 'DAYS_14', 'input': ['trade_price'], 'params': [10]},
    # 'trima10_15': {'function': 'TRIMA', 'dataframe': 'DAYS_15', 'input': ['trade_price'], 'params': [10]},
    # 'trima10_16': {'function': 'TRIMA', 'dataframe': 'DAYS_16', 'input': ['trade_price'], 'params': [10]},
    # 'trima10_17': {'function': 'TRIMA', 'dataframe': 'DAYS_17', 'input': ['trade_price'], 'params': [10]},
    # 'trima10_18': {'function': 'TRIMA', 'dataframe': 'DAYS_18', 'input': ['trade_price'], 'params': [10]},
    # 'trima10_19': {'function': 'TRIMA', 'dataframe': 'DAYS_19', 'input': ['trade_price'], 'params': [10]},
    # 'trima10_20': {'function': 'TRIMA', 'dataframe': 'DAYS_20', 'input': ['trade_price'], 'params': [10]},
    # 'trima10_21': {'function': 'TRIMA', 'dataframe': 'DAYS_21', 'input': ['trade_price'], 'params': [10]},
    # 'trima10_22': {'function': 'TRIMA', 'dataframe': 'DAYS_22', 'input': ['trade_price'], 'params': [10]},
    # 'trima10_23': {'function': 'TRIMA', 'dataframe': 'DAYS_23', 'input': ['trade_price'], 'params': [10]},
    #
    # 'trima20_0': {'function': 'TRIMA', 'dataframe': 'DAYS_0', 'input': ['trade_price'], 'params': [20]},
    # 'trima20_1': {'function': 'TRIMA', 'dataframe': 'DAYS_1', 'input': ['trade_price'], 'params': [20]},
    # 'trima20_2': {'function': 'TRIMA', 'dataframe': 'DAYS_2', 'input': ['trade_price'], 'params': [20]},
    # 'trima20_3': {'function': 'TRIMA', 'dataframe': 'DAYS_3', 'input': ['trade_price'], 'params': [20]},
    # 'trima20_4': {'function': 'TRIMA', 'dataframe': 'DAYS_4', 'input': ['trade_price'], 'params': [20]},
    # 'trima20_5': {'function': 'TRIMA', 'dataframe': 'DAYS_5', 'input': ['trade_price'], 'params': [20]},
    # 'trima20_6': {'function': 'TRIMA', 'dataframe': 'DAYS_6', 'input': ['trade_price'], 'params': [20]},
    # 'trima20_7': {'function': 'TRIMA', 'dataframe': 'DAYS_7', 'input': ['trade_price'], 'params': [20]},
    # 'trima20_8': {'function': 'TRIMA', 'dataframe': 'DAYS_8', 'input': ['trade_price'], 'params': [20]},
    # 'trima20_9': {'function': 'TRIMA', 'dataframe': 'DAYS_9', 'input': ['trade_price'], 'params': [20]},
    # 'trima20_10': {'function': 'TRIMA', 'dataframe': 'DAYS_10', 'input': ['trade_price'], 'params': [20]},
    # 'trima20_11': {'function': 'TRIMA', 'dataframe': 'DAYS_11', 'input': ['trade_price'], 'params': [20]},
    # 'trima20_12': {'function': 'TRIMA', 'dataframe': 'DAYS_12', 'input': ['trade_price'], 'params': [20]},
    # 'trima20_13': {'function': 'TRIMA', 'dataframe': 'DAYS_13', 'input': ['trade_price'], 'params': [20]},
    # 'trima20_14': {'function': 'TRIMA', 'dataframe': 'DAYS_14', 'input': ['trade_price'], 'params': [20]},
    # 'trima20_15': {'function': 'TRIMA', 'dataframe': 'DAYS_15', 'input': ['trade_price'], 'params': [20]},
    # 'trima20_16': {'function': 'TRIMA', 'dataframe': 'DAYS_16', 'input': ['trade_price'], 'params': [20]},
    # 'trima20_17': {'function': 'TRIMA', 'dataframe': 'DAYS_17', 'input': ['trade_price'], 'params': [20]},
    # 'trima20_18': {'function': 'TRIMA', 'dataframe': 'DAYS_18', 'input': ['trade_price'], 'params': [20]},
    # 'trima20_19': {'function': 'TRIMA', 'dataframe': 'DAYS_19', 'input': ['trade_price'], 'params': [20]},
    # 'trima20_20': {'function': 'TRIMA', 'dataframe': 'DAYS_20', 'input': ['trade_price'], 'params': [20]},
    # 'trima20_21': {'function': 'TRIMA', 'dataframe': 'DAYS_21', 'input': ['trade_price'], 'params': [20]},
    # 'trima20_22': {'function': 'TRIMA', 'dataframe': 'DAYS_22', 'input': ['trade_price'], 'params': [20]},
    # 'trima20_23': {'function': 'TRIMA', 'dataframe': 'DAYS_23', 'input': ['trade_price'], 'params': [20]},
    #
    'wma5_0': {'function': 'WMA', 'dataframe': 'DAYS_0', 'input': ['trade_price'], 'params': [5]},
    'wma5_1': {'function': 'WMA', 'dataframe': 'DAYS_1', 'input': ['trade_price'], 'params': [5]},
    'wma5_2': {'function': 'WMA', 'dataframe': 'DAYS_2', 'input': ['trade_price'], 'params': [5]},
    'wma5_3': {'function': 'WMA', 'dataframe': 'DAYS_3', 'input': ['trade_price'], 'params': [5]},
    'wma5_4': {'function': 'WMA', 'dataframe': 'DAYS_4', 'input': ['trade_price'], 'params': [5]},
    'wma5_5': {'function': 'WMA', 'dataframe': 'DAYS_5', 'input': ['trade_price'], 'params': [5]},
    'wma5_6': {'function': 'WMA', 'dataframe': 'DAYS_6', 'input': ['trade_price'], 'params': [5]},
    'wma5_7': {'function': 'WMA', 'dataframe': 'DAYS_7', 'input': ['trade_price'], 'params': [5]},
    'wma5_8': {'function': 'WMA', 'dataframe': 'DAYS_8', 'input': ['trade_price'], 'params': [5]},
    'wma5_9': {'function': 'WMA', 'dataframe': 'DAYS_9', 'input': ['trade_price'], 'params': [5]},
    'wma5_10': {'function': 'WMA', 'dataframe': 'DAYS_10', 'input': ['trade_price'], 'params': [5]},
    'wma5_11': {'function': 'WMA', 'dataframe': 'DAYS_11', 'input': ['trade_price'], 'params': [5]},
    'wma5_12': {'function': 'WMA', 'dataframe': 'DAYS_12', 'input': ['trade_price'], 'params': [5]},
    'wma5_13': {'function': 'WMA', 'dataframe': 'DAYS_13', 'input': ['trade_price'], 'params': [5]},
    'wma5_14': {'function': 'WMA', 'dataframe': 'DAYS_14', 'input': ['trade_price'], 'params': [5]},
    'wma5_15': {'function': 'WMA', 'dataframe': 'DAYS_15', 'input': ['trade_price'], 'params': [5]},
    'wma5_16': {'function': 'WMA', 'dataframe': 'DAYS_16', 'input': ['trade_price'], 'params': [5]},
    'wma5_17': {'function': 'WMA', 'dataframe': 'DAYS_17', 'input': ['trade_price'], 'params': [5]},
    'wma5_18': {'function': 'WMA', 'dataframe': 'DAYS_18', 'input': ['trade_price'], 'params': [5]},
    'wma5_19': {'function': 'WMA', 'dataframe': 'DAYS_19', 'input': ['trade_price'], 'params': [5]},
    'wma5_20': {'function': 'WMA', 'dataframe': 'DAYS_20', 'input': ['trade_price'], 'params': [5]},
    'wma5_21': {'function': 'WMA', 'dataframe': 'DAYS_21', 'input': ['trade_price'], 'params': [5]},
    'wma5_22': {'function': 'WMA', 'dataframe': 'DAYS_22', 'input': ['trade_price'], 'params': [5]},
    'wma5_23': {'function': 'WMA', 'dataframe': 'DAYS_23', 'input': ['trade_price'], 'params': [5]},

    'wma3_0': {'function': 'WMA', 'dataframe': 'DAYS_0', 'input': ['trade_price'], 'params': [3]},
    'wma3_1': {'function': 'WMA', 'dataframe': 'DAYS_1', 'input': ['trade_price'], 'params': [3]},
    'wma3_2': {'function': 'WMA', 'dataframe': 'DAYS_2', 'input': ['trade_price'], 'params': [3]},
    'wma3_3': {'function': 'WMA', 'dataframe': 'DAYS_3', 'input': ['trade_price'], 'params': [3]},
    'wma3_4': {'function': 'WMA', 'dataframe': 'DAYS_4', 'input': ['trade_price'], 'params': [3]},
    'wma3_5': {'function': 'WMA', 'dataframe': 'DAYS_5', 'input': ['trade_price'], 'params': [3]},
    'wma3_6': {'function': 'WMA', 'dataframe': 'DAYS_6', 'input': ['trade_price'], 'params': [3]},
    'wma3_7': {'function': 'WMA', 'dataframe': 'DAYS_7', 'input': ['trade_price'], 'params': [3]},
    'wma3_8': {'function': 'WMA', 'dataframe': 'DAYS_8', 'input': ['trade_price'], 'params': [3]},
    'wma3_9': {'function': 'WMA', 'dataframe': 'DAYS_9', 'input': ['trade_price'], 'params': [3]},
    'wma3_10': {'function': 'WMA', 'dataframe': 'DAYS_10', 'input': ['trade_price'], 'params': [3]},
    'wma3_11': {'function': 'WMA', 'dataframe': 'DAYS_11', 'input': ['trade_price'], 'params': [3]},
    'wma3_12': {'function': 'WMA', 'dataframe': 'DAYS_12', 'input': ['trade_price'], 'params': [3]},
    'wma3_13': {'function': 'WMA', 'dataframe': 'DAYS_13', 'input': ['trade_price'], 'params': [3]},
    'wma3_14': {'function': 'WMA', 'dataframe': 'DAYS_14', 'input': ['trade_price'], 'params': [3]},
    'wma3_15': {'function': 'WMA', 'dataframe': 'DAYS_15', 'input': ['trade_price'], 'params': [3]},
    'wma3_16': {'function': 'WMA', 'dataframe': 'DAYS_16', 'input': ['trade_price'], 'params': [3]},
    'wma3_17': {'function': 'WMA', 'dataframe': 'DAYS_17', 'input': ['trade_price'], 'params': [3]},
    'wma3_18': {'function': 'WMA', 'dataframe': 'DAYS_18', 'input': ['trade_price'], 'params': [3]},
    'wma3_19': {'function': 'WMA', 'dataframe': 'DAYS_19', 'input': ['trade_price'], 'params': [3]},
    'wma3_20': {'function': 'WMA', 'dataframe': 'DAYS_20', 'input': ['trade_price'], 'params': [3]},
    'wma3_21': {'function': 'WMA', 'dataframe': 'DAYS_21', 'input': ['trade_price'], 'params': [3]},
    'wma3_22': {'function': 'WMA', 'dataframe': 'DAYS_22', 'input': ['trade_price'], 'params': [3]},
    'wma3_23': {'function': 'WMA', 'dataframe': 'DAYS_23', 'input': ['trade_price'], 'params': [3]},

    'wma10_0': {'function': 'WMA', 'dataframe': 'DAYS_0', 'input': ['trade_price'], 'params': [10]},
    'wma10_1': {'function': 'WMA', 'dataframe': 'DAYS_1', 'input': ['trade_price'], 'params': [10]},
    'wma10_2': {'function': 'WMA', 'dataframe': 'DAYS_2', 'input': ['trade_price'], 'params': [10]},
    'wma10_3': {'function': 'WMA', 'dataframe': 'DAYS_3', 'input': ['trade_price'], 'params': [10]},
    'wma10_4': {'function': 'WMA', 'dataframe': 'DAYS_4', 'input': ['trade_price'], 'params': [10]},
    'wma10_5': {'function': 'WMA', 'dataframe': 'DAYS_5', 'input': ['trade_price'], 'params': [10]},
    'wma10_6': {'function': 'WMA', 'dataframe': 'DAYS_6', 'input': ['trade_price'], 'params': [10]},
    'wma10_7': {'function': 'WMA', 'dataframe': 'DAYS_7', 'input': ['trade_price'], 'params': [10]},
    'wma10_8': {'function': 'WMA', 'dataframe': 'DAYS_8', 'input': ['trade_price'], 'params': [10]},
    'wma10_9': {'function': 'WMA', 'dataframe': 'DAYS_9', 'input': ['trade_price'], 'params': [10]},
    'wma10_10': {'function': 'WMA', 'dataframe': 'DAYS_10', 'input': ['trade_price'], 'params': [10]},
    'wma10_11': {'function': 'WMA', 'dataframe': 'DAYS_11', 'input': ['trade_price'], 'params': [10]},
    'wma10_12': {'function': 'WMA', 'dataframe': 'DAYS_12', 'input': ['trade_price'], 'params': [10]},
    'wma10_13': {'function': 'WMA', 'dataframe': 'DAYS_13', 'input': ['trade_price'], 'params': [10]},
    'wma10_14': {'function': 'WMA', 'dataframe': 'DAYS_14', 'input': ['trade_price'], 'params': [10]},
    'wma10_15': {'function': 'WMA', 'dataframe': 'DAYS_15', 'input': ['trade_price'], 'params': [10]},
    'wma10_16': {'function': 'WMA', 'dataframe': 'DAYS_16', 'input': ['trade_price'], 'params': [10]},
    'wma10_17': {'function': 'WMA', 'dataframe': 'DAYS_17', 'input': ['trade_price'], 'params': [10]},
    'wma10_18': {'function': 'WMA', 'dataframe': 'DAYS_18', 'input': ['trade_price'], 'params': [10]},
    'wma10_19': {'function': 'WMA', 'dataframe': 'DAYS_19', 'input': ['trade_price'], 'params': [10]},
    'wma10_20': {'function': 'WMA', 'dataframe': 'DAYS_20', 'input': ['trade_price'], 'params': [10]},
    'wma10_21': {'function': 'WMA', 'dataframe': 'DAYS_21', 'input': ['trade_price'], 'params': [10]},
    'wma10_22': {'function': 'WMA', 'dataframe': 'DAYS_22', 'input': ['trade_price'], 'params': [10]},
    'wma10_23': {'function': 'WMA', 'dataframe': 'DAYS_23', 'input': ['trade_price'], 'params': [10]},

    'wma20_0': {'function': 'WMA', 'dataframe': 'DAYS_0', 'input': ['trade_price'], 'params': [20]},
    'wma20_1': {'function': 'WMA', 'dataframe': 'DAYS_1', 'input': ['trade_price'], 'params': [20]},
    'wma20_2': {'function': 'WMA', 'dataframe': 'DAYS_2', 'input': ['trade_price'], 'params': [20]},
    'wma20_3': {'function': 'WMA', 'dataframe': 'DAYS_3', 'input': ['trade_price'], 'params': [20]},
    'wma20_4': {'function': 'WMA', 'dataframe': 'DAYS_4', 'input': ['trade_price'], 'params': [20]},
    'wma20_5': {'function': 'WMA', 'dataframe': 'DAYS_5', 'input': ['trade_price'], 'params': [20]},
    'wma20_6': {'function': 'WMA', 'dataframe': 'DAYS_6', 'input': ['trade_price'], 'params': [20]},
    'wma20_7': {'function': 'WMA', 'dataframe': 'DAYS_7', 'input': ['trade_price'], 'params': [20]},
    'wma20_8': {'function': 'WMA', 'dataframe': 'DAYS_8', 'input': ['trade_price'], 'params': [20]},
    'wma20_9': {'function': 'WMA', 'dataframe': 'DAYS_9', 'input': ['trade_price'], 'params': [20]},
    'wma20_10': {'function': 'WMA', 'dataframe': 'DAYS_10', 'input': ['trade_price'], 'params': [20]},
    'wma20_11': {'function': 'WMA', 'dataframe': 'DAYS_11', 'input': ['trade_price'], 'params': [20]},
    'wma20_12': {'function': 'WMA', 'dataframe': 'DAYS_12', 'input': ['trade_price'], 'params': [20]},
    'wma20_13': {'function': 'WMA', 'dataframe': 'DAYS_13', 'input': ['trade_price'], 'params': [20]},
    'wma20_14': {'function': 'WMA', 'dataframe': 'DAYS_14', 'input': ['trade_price'], 'params': [20]},
    'wma20_15': {'function': 'WMA', 'dataframe': 'DAYS_15', 'input': ['trade_price'], 'params': [20]},
    'wma20_16': {'function': 'WMA', 'dataframe': 'DAYS_16', 'input': ['trade_price'], 'params': [20]},
    'wma20_17': {'function': 'WMA', 'dataframe': 'DAYS_17', 'input': ['trade_price'], 'params': [20]},
    'wma20_18': {'function': 'WMA', 'dataframe': 'DAYS_18', 'input': ['trade_price'], 'params': [20]},
    'wma20_19': {'function': 'WMA', 'dataframe': 'DAYS_19', 'input': ['trade_price'], 'params': [20]},
    'wma20_20': {'function': 'WMA', 'dataframe': 'DAYS_20', 'input': ['trade_price'], 'params': [20]},
    'wma20_21': {'function': 'WMA', 'dataframe': 'DAYS_21', 'input': ['trade_price'], 'params': [20]},
    'wma20_22': {'function': 'WMA', 'dataframe': 'DAYS_22', 'input': ['trade_price'], 'params': [20]},
    'wma20_23': {'function': 'WMA', 'dataframe': 'DAYS_23', 'input': ['trade_price'], 'params': [20]},

}
