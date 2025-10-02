from bt4.Constants import ExType
from bt4_cfg.lt_common_conf import LiveTradingCommonConfig

class Lt_bithumb_CommonConfig (LiveTradingCommonConfig):
    def __init__(self):
        pass

    def load_params(self, r, params):
        super(Lt_bithumb_CommonConfig, self).load_params(r, params)

        ## Exchange Mode
        params[r.EX.EX_TYPE] = ExType.bithumb

        # if r.STGY.PARAMS not in params:
        #     params[r.STGY.PARAMS] = {}
        # params[r.STGY.PARAMS]['quote_provider'] = params[r.EX.EX_TYPE]