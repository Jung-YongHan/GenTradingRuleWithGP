from bt4.Constants import Operation_Type, ExType, TradeResultStorageType
from bt4_cfg.bt_common_conf import BtCommonConfig


class Bt_upbit_CommonConfig(BtCommonConfig):
    def __init__(self):
        pass

    def load_params(self, r, params):
        super(Bt_upbit_CommonConfig, self).load_params(r, params)

        params[r.OP.QUOTE_PROVIDERS] = [ExType.upbit]

        params[r.EX.EX_TYPE] = ExType.dummy_upbit
        params[r.EX.EX_DUMMY_INITIAL_RATIO] = 10000000
        params[r.EX.EX_DUMMY_FEE_SLIPPAGE] = 0.0008

        # if r.STGY.PARAMS not in params:
        #     params[r.STGY.PARAMS] = {}
        # params[r.STGY.PARAMS]['quote_provider'] = params[r.OP.QUOTE_PROVIDERS][0]
