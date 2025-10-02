from bt4.Constants import Operation_Type, ExType, TradeResultStorageType


class BtCommonConfig:
    def __init__(self):
        pass

    def load_params(self, r, params):
        params[r.OP.OP] = Operation_Type.BACK_TESTOR

        params[r.EX.EX_ACCOUNT] = 'simulator'

        ## File Storage Type
        # params[r.RS.RS_TYPE] = TradeResultStorageType.FILE
        params[r.RS.RS_TYPE] = TradeResultStorageType.PSQL
        params[r.RS.RS_VISUALIZE] = True