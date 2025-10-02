from bt3.Constants import AssetMgrType, CandleType


class Config:
    def __init__(self):
        pass

    def load_params(self, r, parameters):
        # parameters[r.OP.MARKET] = ('KRW-BTC', 'KRW-ETH', 'KRW-XRP')
        parameters[r.OP.MARKET] = ('KRW-BTC',)
        parameters[r.OP.BT.CANDLE_TYPE] = CandleType.DAYS
        parameters[r.OP.BT.TIME] = []

        # parameters[r.OP.sim.SIMUL_TA_INDICATORS] = ['ma3_3m', 'ma5_3m', 'ma10_3m', 'ma20_3m', 'ma60_3m', 'ma120_3m', 'sar_3m' ,'macd_3m', 'cci_3m','bb_3m']
        parameters[r.OP.BT.TA_INDICATORS] = []

        parameters[r.OP.BT.START] = '2021-04-17T09:00:00'
        parameters[r.OP.BT.END] = '2022-03-06T09:00:00'

        parameters[r.AM.AM_TYPE] = AssetMgrType.FIXED
        parameters[r.AM.AM_FIXED_TRADE_RATIO] = 0.4  #### Changed

        parameters[r.STGY.NAME] = 'LabeledStrategySimulator'
        parameters[r.STGY.MODULE] = 'LabeledStrategySimulator'
        parameters[r.RS.RS_FILE_NAME] = parameters[r.STGY.NAME]
        parameters[r.STGY.PARAMS] = {
            # 'simul_data': './data_labeled_strategy/220613_arima_bitcoin.csv',
            # 'simul_data': './data_labeled_strategy/220613_arima_bitcoin_(buy 0.5, sell -0.2).csv',
            # 'simul_data': './data_labeled_strategy/220613_arima_bitcoin_(buy 1, sell -0.2).csv',
            # 'simul_data': './data_labeled_strategy/220613_arima_bitcoin_(buy 0.2, sell -0.2).csv',
            # 'simul_data': './data_labeled_strategy/220613_arima_bitcoin_(buy 0.2, sell -0.1).csv',
            'simul_data': './data_labeled_strategy/220613_arima_bitcoin_(buy 0.5, sell -0.5)_reverse.csv',


        }