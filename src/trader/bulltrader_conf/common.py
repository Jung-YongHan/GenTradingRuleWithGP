
from bt3.Constants import ExType, TradeResultStorageType, QUOTE_MODE, Operation_Type
# from bt3.trade.AccountManagement import AccountMgmt

@DeprecationWarning
class AbstractCommonConfig:
    def __init__(self):
        pass

    def load_params(self, r, parameters):
        pass


@DeprecationWarning
class BacktestorCommonConfig(AbstractCommonConfig):
    def __init__(self):
        pass


    def load_params(self, r, parameters):
        super(BacktestorCommonConfig, self).load_params(r, parameters)

        ## Operation Mode
        parameters[r.OP.OP] = Operation_Type.BACK_TESTOR
        ## Exchange Mode
        parameters[r.EX.EX_TYPE] = ExType.dummy_upbit
        parameters[r.EX.EX_DUMMY_INITIAL_RATIO] = 10000000
        parameters[r.EX.EX_DUMMY_FEE_SLIPPAGE] = 0.0008
        # parameters[r.EX.EX_DUMMY_FEE_RATIO] = 0.0005

        parameters[r.EX.EX_ACCOUNT] = 'simulator'

        ## File Storage Type
        parameters[r.RS.RS_TYPE] = TradeResultStorageType.FILE
#
# @DeprecationWarning
# class LiveTradingCommonConfig(AbstractCommonConfig):
#     def __init__(self, account_alias):
#         self.account_mgmt = AccountMgmt(account_alias)
#
#     def load_params(self, r, parameters):
#         super(LiveTradingCommonConfig, self).load_params(r, parameters)
#
#         ## Operation Mode
#         parameters[r.OP.OP] = Operation_Type.LIVE_TRADING
#         parameters[r.OP.live.QUOTE_MODE] = QUOTE_MODE.KAFKA
#         # parameters[bulltrader.exec.Constants.QUOTE_MODE] = QUOTE_MODE.SELF
#
#         ## Exchange Mode
#         parameters[r.EX.EX_TYPE] = ExType.upbit
#         # parameters[r.EX.EX_TYPE] = ExchangeType.DUMMY
#         # parameters[r.EX.EX_DUMMY_INITIAL_RATIO] = 10000000
#         # parameters[r.EX.EX_DUMMY_FEE_RATIO] = 0.0005
#
#         parameters[r.EX.EX_ACCOUNT]  = self.account_mgmt.get_account().alias
#         parameters[r.EX.EX_ACCESS_KEY] = self.account_mgmt.get_account().access_key
#         parameters[r.EX.EX_SECRET_KEY] = self.account_mgmt.get_account().secrete_key
#
#         ## File Storage Type
#         parameters[r.RS.RS_TYPE] = TradeResultStorageType.MONGO

