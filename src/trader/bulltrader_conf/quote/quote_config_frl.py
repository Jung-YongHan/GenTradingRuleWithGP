

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

    #################################################################################################
    ## Timeframe support
    'timeframe_hours' : [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23], # It can be accessed by 'DAY_7', 'DAY_8', 'DAY_...'
    # 'timeframe_hours' : [], # It can be accessed by 'DAY_7', 'DAY_8', 'DAY_...'

    #################################################################################################
    ##### Indicator List for Target Markets
    'ta_indicators' : [
                        'vol', 'vol5',

                        ## SMA
                        'ma3_1h', 'ma5_1h', 'ma10_1h', 'ma20_1h', 'ma60_1h', 'ma120_1h',
                        'ma3_4h', 'ma5_4h', 'ma10_4h', 'ma20_4h', 'ma60_4h', 'ma120_4h',
                        'ma3', 'ma5', 'ma10', 'ma20', 'ma60', 'ma120',

                        ## EMA
                        'ema3_1h', 'ema5_1h', 'ema10_1h', 'ema20_1h', 'ema60_1h', 'ema120_1h',
                        'ema3_4h', 'ema5_4h', 'ema10_4h', 'ema20_4h', 'ema60_4h', 'ema120_4h',
                        'ema3', 'ema5', 'ema10', 'ema20', 'ema60', 'ema120',

                        ## TRB
                        'trb10_1h', 'trb20_1h', 'trb30_1h', 'trb40_1h', 'trb50_1h',
                        'trb10_4h', 'trb20_4h', 'trb30_4h', 'trb40_4h', 'trb50_4h',
                        'trb10','trb20', 'trb30', 'trb40','trb50',

                        ## MACD
                        'macd_1h', 'macd_4h', 'macd',
                        'macd_s_1h', 'macd_s_4h', 'macd_s',

                        ## RSI
                        'rsi14_1h', 'rsi28_1h', 'rsi42_1h',
                        'rsi14_4h', 'rsi28_4h', 'rsi42_4h',
                        'rsi14', 'rsi28', 'rsi42'
                                          
                        ### Plus_di, Minus_di
                        'plus_di_1h',  'minus_di_1h',
                        'plus_di_4h',  'minus_di_4h',
                        'plus_di',  'minus_di' ],

    'vol': {'function': 'vol', 'dataframe': 'DAYS', 'input': ['opening_price', 'high_price', 'low_price'],
            'params': []},  # p[0]: timeperiod
    'vol5': {'function': 'sma', 'dataframe': 'DAYS', 'input': ['vol'], 'params': [5]},  # p[0]: timeperiod

    ##### Indicator Parameters
    ## dataframe : 'DAYS'='DAYS_9', 'HOUR4', 'HOUR', 'DAYS_0',..'DAYS_23'
    ############# SMA
    'ma3_1h': {'function': 'sma', 'dataframe': 'HOUR', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    'ma5_1h': {'function': 'sma', 'dataframe': 'HOUR', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    'ma10_1h': {'function': 'sma', 'dataframe': 'HOUR', 'input': ['trade_price'], 'params': [10]},  # p[0]: timeperiod
    'ma20_1h': {'function': 'sma', 'dataframe': 'HOUR', 'input': ['trade_price'], 'params': [20]},  # p[0]: timeperiod
    'ma60_1h': {'function': 'sma', 'dataframe': 'HOUR', 'input': ['trade_price'], 'params': [60]},  # p[0]: timeperiod
    'ma120_1h': {'function': 'sma', 'dataframe': 'HOUR', 'input': ['trade_price'], 'params': [120]},  # p[0]: timeperiod

    'ma3_4h': {'function': 'sma', 'dataframe': 'HOUR4', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    'ma5_4h': {'function': 'sma', 'dataframe': 'HOUR4', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    'ma10_4h': {'function': 'sma', 'dataframe': 'HOUR4', 'input': ['trade_price'], 'params': [10]},  # p[0]: timeperiod
    'ma20_4h': {'function': 'sma', 'dataframe': 'HOUR4', 'input': ['trade_price'], 'params': [20]},  # p[0]: timeperiod
    'ma60_4h': {'function': 'sma', 'dataframe': 'HOUR4', 'input': ['trade_price'], 'params': [60]},  # p[0]: timeperiod
    'ma120_4h': {'function': 'sma', 'dataframe': 'HOUR4', 'input': ['trade_price'], 'params': [120]},  # p[0]: timeperiod

    'ma3':     {'function': 'sma', 'dataframe': 'DAYS', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    'ma5':     {'function': 'sma', 'dataframe': 'DAYS', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    'ma10':    {'function': 'sma', 'dataframe': 'DAYS', 'input': ['trade_price'], 'params': [10]},  # p[0]: timeperiod
    'ma20':    {'function': 'sma', 'dataframe': 'DAYS', 'input': ['trade_price'], 'params': [20]},  # p[0]: timeperiod
    'ma60':    {'function': 'sma', 'dataframe': 'DAYS', 'input': ['trade_price'], 'params': [60]},  # p[0]: timeperiod
    'ma120':    {'function': 'sma', 'dataframe': 'DAYS', 'input': ['trade_price'], 'params': [120]},  # p[0]: timeperiod

    ############# EMA
    'ema3_1h': {'function': 'ema', 'dataframe': 'HOUR', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    'ema5_1h': {'function': 'ema', 'dataframe': 'HOUR', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    'ema10_1h': {'function': 'ema', 'dataframe': 'HOUR', 'input': ['trade_price'], 'params': [10]},  # p[0]: timeperiod
    'ema20_1h': {'function': 'ema', 'dataframe': 'HOUR', 'input': ['trade_price'], 'params': [20]},  # p[0]: timeperiod
    'ema60_1h': {'function': 'ema', 'dataframe': 'HOUR', 'input': ['trade_price'], 'params': [60]},  # p[0]: timeperiod
    'ema120_1h': {'function': 'ema', 'dataframe': 'HOUR', 'input': ['trade_price'], 'params': [120]},  # p[0]: timeperiod
    'ema240_1h': {'function': 'ema', 'dataframe': 'HOUR', 'input': ['trade_price'], 'params': [240]},  # p[0]: timeperiod

    'ema3_4h': {'function': 'ema', 'dataframe': 'HOUR4', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    'ema5_4h': {'function': 'ema', 'dataframe': 'HOUR4', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    'ema10_4h': {'function': 'ema', 'dataframe': 'HOUR4', 'input': ['trade_price'], 'params': [10]},  # p[0]: timeperiod
    'ema20_4h': {'function': 'ema', 'dataframe': 'HOUR4', 'input': ['trade_price'], 'params': [20]},  # p[0]: timeperiod
    'ema60_4h': {'function': 'ema', 'dataframe': 'HOUR4', 'input': ['trade_price'], 'params': [60]},  # p[0]: timeperiod
    'ema120_4h': {'function': 'ema', 'dataframe': 'HOUR4', 'input': ['trade_price'], 'params': [120]}, # p[0]: timeperiod
    'ema240_4h': {'function': 'ema', 'dataframe': 'HOUR4', 'input': ['trade_price'], 'params': [240]}, # p[0]: timeperiod

    'ema3': {'function': 'ema', 'dataframe': 'DAYS', 'input': ['trade_price'], 'params': [3]},  # p[0]: timeperiod
    'ema5': {'function': 'ema', 'dataframe': 'DAYS', 'input': ['trade_price'], 'params': [5]},  # p[0]: timeperiod
    'ema10': {'function': 'ema', 'dataframe': 'DAYS', 'input': ['trade_price'], 'params': [10]},  # p[0]: timeperiod
    'ema20': {'function': 'ema', 'dataframe': 'DAYS', 'input': ['trade_price'], 'params': [20]},  # p[0]: timeperiod
    'ema60': {'function': 'ema', 'dataframe': 'DAYS', 'input': ['trade_price'], 'params': [60]},  # p[0]: timeperiod
    'ema120': {'function': 'ema', 'dataframe': 'DAYS', 'input': ['trade_price'], 'params': [120]},  # p[0]: timeperiod
    'ema240': {'function': 'ema', 'dataframe': 'DAYS', 'input': ['trade_price'], 'params': [240]},  # p[0]: timeperiod

    ############# TRB
    'trb10_1h': {'function': 'trb', 'dataframe': 'HOUR', 'input': ['high_price', 'low_price'], 'params': [10]}, # p[0]: timeperiod
    'trb20_1h': {'function': 'trb', 'dataframe': 'HOUR', 'input': ['high_price', 'low_price'], 'params': [20]}, # p[0]: timeperiod
    'trb30_1h': {'function': 'trb', 'dataframe': 'HOUR', 'input': ['high_price', 'low_price'], 'params': [30]}, # p[0]: timeperiod
    'trb40_1h': {'function': 'trb', 'dataframe': 'HOUR', 'input': ['high_price', 'low_price'], 'params': [40]}, # p[0]: timeperiod
    'trb50_1h': {'function': 'trb', 'dataframe': 'HOUR', 'input': ['high_price', 'low_price'], 'params': [50]},# p[0]: timeperiod

    'trb10_4h': {'function': 'trb', 'dataframe': 'HOUR4', 'input': ['high_price', 'low_price'], 'params': [10]}, # p[0]: timeperiod
    'trb20_4h': {'function': 'trb', 'dataframe': 'HOUR4', 'input': ['high_price', 'low_price'], 'params': [20]}, # p[0]: timeperiod
    'trb30_4h': {'function': 'trb', 'dataframe': 'HOUR4', 'input': ['high_price', 'low_price'], 'params': [30]}, # p[0]: timeperiod
    'trb40_4h': {'function': 'trb', 'dataframe': 'HOUR4', 'input': ['high_price', 'low_price'], 'params': [40]},# p[0]: timeperiod
    'trb50_4h': {'function': 'trb', 'dataframe': 'HOUR4', 'input': ['high_price', 'low_price'], 'params': [50]},# p[0]: timeperiod

    'trb10': {'function': 'trb', 'dataframe': 'DAYS', 'input': ['high_price', 'low_price'], 'params': [10]},# p[0]: timeperiod
    'trb20': {'function': 'trb', 'dataframe': 'DAYS', 'input': ['high_price', 'low_price'], 'params': [20]},# p[0]: timeperiod
    'trb30': {'function': 'trb', 'dataframe': 'DAYS', 'input': ['high_price', 'low_price'], 'params': [30]},# p[0]: timeperiod
    'trb40': {'function': 'trb', 'dataframe': 'DAYS', 'input': ['high_price', 'low_price'], 'params': [40]},# p[0]: timeperiod
    'trb50': {'function': 'trb', 'dataframe': 'DAYS', 'input': ['high_price', 'low_price'], 'params': [50]},# p[0]: timeperiod

    ############# MACD
    'macd_1h':    {'function': 'macd', 'dataframe': 'HOUR', 'input': ['trade_price'], 'params': [12, 26, 9]}, # p[0] : fastperiod(def=12), p[1] : slowperiod(def=26), p[2]: signalperiod (def=9)
    'macd_4h':    {'function': 'macd', 'dataframe': 'HOUR4', 'input': ['trade_price'], 'params': [12, 26, 9]}, # p[0] : fastperiod(def=12), p[1] : slowperiod(def=26), p[2]: signalperiod (def=9)
    'macd':    {'function': 'macd', 'dataframe': 'DAYS', 'input': ['trade_price'], 'params': [12, 26, 9]}, # p[0] : fastperiod(def=12), p[1] : slowperiod(def=26), p[2]: signalperiod (def=9)

    'macd_s_1h': {'function': 'macd', 'dataframe': 'HOUR', 'input': ['trade_price'], 'params': [19, 39, 9]}, # p[0] : fastperiod(def=12), p[1] : slowperiod(def=26), p[2]: signalperiod (def=9)
    'macd_s_4h': {'function': 'macd', 'dataframe': 'HOUR4', 'input': ['trade_price'], 'params': [19, 39, 9]}, # p[0] : fastperiod(def=12), p[1] : slowperiod(def=26), p[2]: signalperiod (def=9)
    'macd_s': {'function': 'macd', 'dataframe': 'DAYS', 'input': ['trade_price'], 'params': [19, 39, 9]}, # p[0] : fastperiod(def=12), p[1] : slowperiod(def=26), p[2]: signalperiod (def=9)

    ############# RSI
    'rsi14_1h':   {'function': 'rsi', 'dataframe': 'HOUR', 'input': ['trade_price'], 'params': [14]}, # p[0]: timeperiod(def=14)
    'rsi14_4h':   {'function': 'rsi', 'dataframe': 'HOUR4', 'input': ['trade_price'], 'params': [14]}, # p[0]: timeperiod(def=14)
    'rsi14':   {'function': 'rsi', 'dataframe': 'DAYS', 'input': ['trade_price'], 'params': [14]}, # p[0]: timeperiod(def=14)

    'rsi28_1h': {'function': 'rsi', 'dataframe': 'HOUR', 'input': ['trade_price'], 'params': [28]}, # p[0]: timeperiod(def=14)
    'rsi28_4h': {'function': 'rsi', 'dataframe': 'HOUR4', 'input': ['trade_price'], 'params': [28]}, # p[0]: timeperiod(def=14)
    'rsi28': {'function': 'rsi', 'dataframe': 'DAYS', 'input': ['trade_price'], 'params': [28]},# p[0]: timeperiod(def=14)

    'rsi42_1h': {'function': 'rsi', 'dataframe': 'HOUR', 'input': ['trade_price'], 'params': [42]}, # p[0]: timeperiod(def=14)
    'rsi42_4h': {'function': 'rsi', 'dataframe': 'HOUR4', 'input': ['trade_price'], 'params': [42]}, # p[0]: timeperiod(def=14)
    'rsi42': {'function': 'rsi', 'dataframe': 'DAYS', 'input': ['trade_price'], 'params': [42]},# p[0]: timeperiod(def=14)

    ############# PLUS_DI, MINUS_DI
    'plus_di_1h': {'function': 'PLUS_DI', 'dataframe': 'HOUR', 'input': ['high_price', 'low_price', 'trade_price'], 'params': [14]},  # p[0]: timeperiod
    'minus_di_1h': {'function': 'MINUS_DI', 'dataframe': 'HOUR', 'input': ['high_price', 'low_price', 'trade_price'], 'params': [14]},  # p[0]: timeperiod

    'plus_di_4h': {'function': 'PLUS_DI', 'dataframe': 'HOUR4', 'input': ['high_price', 'low_price', 'trade_price'], 'params': [14]},  # p[0]: timeperiod
    'minus_di_4h': {'function': 'MINUS_DI', 'dataframe': 'HOUR4', 'input': ['high_price', 'low_price', 'trade_price'], 'params': [14]},  # p[0]: timeperiod

    'plus_di': {'function': 'PLUS_DI', 'dataframe': 'DAYS', 'input': ['high_price', 'low_price', 'trade_price'], 'params': [14]},  # p[0]: timeperiod
    'minus_di': {'function': 'MINUS_DI', 'dataframe': 'DAYS', 'input': ['high_price', 'low_price', 'trade_price'], 'params': [14]},  # p[0]: timeperiod
}
