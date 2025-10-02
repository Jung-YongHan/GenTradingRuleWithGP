from bt3.Constants import AssetMgrType, CandleType


class Config:
    def __init__(self):
        pass

    def load_params(self, r, parameters):

        parameters[r.OP.MARKET] = ('KRW-ETH',)
        parameters[r.OP.BT.START] = '2018-10-01T01:00:00'
        # parameters[r.OP.sim.SIMUL_START] = '2021-06-01T08:59:00'  ## V2
        parameters[r.OP.BT.END] = '2022-02-28T23:59:00'  ## V2

        parameters[r.OP.BT.CANDLE_TYPE] = CandleType.HOUR
        parameters[r.OP.BT.TIME] = ['1:59', '2:59', '3:59', '4:59', '5:59', '6:59', '7:59', '8:59', '9:59', '10:59', '11:59', '12:59',
                                           '13:59','14:59','15:59','16:59','17:59','18:59','19:59','20:59','21:59','22:59','23:59','0:59']
        parameters[r.OP.BT.TA_INDICATORS] = [
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
                                                    'trb10' ,'trb20', 'trb30', 'trb40' ,'trb50',

                                                    ## MACD
                                                    'macd_1h', 'macd_4h', 'macd',
                                                    'macd_s_1h', 'macd_s_4h', 'macd_s',

                                                    ## RSI
                                                    'rsi14_1h', 'rsi28_1h', 'rsi42_1h',
                                                    'rsi14_4h', 'rsi28_4h', 'rsi42_4h',
                                                    'rsi14',    'rsi28',    'rsi42',

                                                    ### Plus_di, Minus_di
                                                    'plus_di_14', 'plus_di_14_1h', 'plus_di_14_4h', 'plus_di_28', 'plus_di_28_1h', 'plus_di_28_4h',
                                                    'plus_di_42', 'plus_di_42_1h', 'plus_di_42_4h',
                                                    'minus_di_14', 'minus_di_14_1h', 'minus_di_14_4h', 'minus_di_28', 'minus_di_28_1h', 'minus_di_28_4h',
                                                    'minus_di_42', 'minus_di_42_1h', 'minus_di_42_4h'
            ]

        parameters[r.AM.AM_TYPE] = AssetMgrType.FIXED
        parameters[r.AM.AM_FIXED_TRADE_RATIO] = 0.4

        parameters[r.STGY.NAME] = 'FRL_PLUS_MINUS_DI_Strategy'
        parameters[r.STGY.MODULE] = 'FRL_2022_Strategy'
        parameters[r.RS.RS_FILE_NAME] = parameters[r.STGY.NAME]
        parameters[r.RS.RS_VISUALIZE] = True
        parameters[r.STGY.PARAMS] = {
                                    'candle_type' : CandleType.HOUR4,
                                    'trading_type' : CandleType.HOUR4,
                                    # 'candle_type': DataType.MINUTES_1,
                                    # 'price_base_tai' : 'ma3',
                                    'buy_tai' : 'plus_di_42',
                                    'sell_tai': 'minus_di_42',
                                    }
