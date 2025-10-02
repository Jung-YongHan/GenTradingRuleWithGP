from bt4.Constants import ExType
from bt4_cfg.ft_common_conf import ForwardTestingCommonConfig


class Ft_bithumb_CommonConfig(ForwardTestingCommonConfig):
    def __init__(self):
        pass

    def load_params(self, r, params):
        super(Ft_bithumb_CommonConfig, self).load_params(r, params)

        ## Comment/Uncomment for dummy exchange
        params[r.EX.EX_TYPE] = ExType.dummy_bithumb
        params[r.EX.EX_DUMMY_INITIAL_RATIO] = 10000000
        params[r.EX.EX_DUMMY_FEE_SLIPPAGE] = 0.0008

        # if r.STGY.PARAMS not in params:
        #     params[r.STGY.PARAMS] = {}
        # params[r.STGY.PARAMS]['quote_provider'] = ExType.upbit