class Context:
    def __init__(self, backtestor, stgy_live_trader, markets, data_type, ex, am, rs, strategy, ctx_params):
        self.__backtestor = backtestor
        self.__stgy_live_trader = stgy_live_trader
        self.__markets = markets
        self.__candle_type = data_type
        self.__exchange = ex
        self.__asset_mgmt = am
        self.__report_storage = rs
        self.__strategy = strategy
        self.__ctx_params = ctx_params

    @property
    def stgy_live_trader(self):
        return self.__stgy_live_trader

    @stgy_live_trader.setter
    def stgy_live_trader(self, new_live_trader):
        self.__stgy_live_trader = new_live_trader

    @property
    def backtestor(self):
        return self.__backtestor

    @backtestor.setter
    def backtestor(self, new_bt):
        self.__backtestor = new_bt

    @property
    def markets(self):
        return self.__markets

    @markets.setter
    def markets(self, markets):
        self.__markets = markets

    @property
    def candle_type(self):
        return self.__candle_type

    @candle_type.setter
    def candle_type(self, candle_type):
        self.__candle_type = candle_type

    @property
    def exchange(self):
        return self.__exchange

    @exchange.setter
    def exchange(self, exchange):
        self.__exchange = exchange

    @property
    def asset_mgmt(self):
        return self.__asset_mgmt

    @asset_mgmt.setter
    def asset_mgmt(self, asset_mgmt):
        self.__asset_mgmt = asset_mgmt

    @property
    def report_storage(self):
        return self.__report_storage

    @report_storage.setter
    def report_storage(self, report_storage):
        self.__report_storage = report_storage

    @property
    def strategy(self):
        return self.__strategy

    @strategy.setter
    def strategy(self, strategy):
        self.__strategy = strategy

    @property
    def ctx_params(self):
        return self.__ctx_params

    @ctx_params.setter
    def ctx_params(self, ctx_params):
        self.__ctx_params = ctx_params