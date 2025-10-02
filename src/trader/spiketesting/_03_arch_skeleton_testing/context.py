from bt4.exec.BullTraderMain import Context


class V4Context(Context):
    def __init__(self, simulator, auto_trader, markets,
                 data_type, ex, am, rs, strategy, ctx_params):
        super(V4Context, self).__init__(simulator, auto_trader, markets, data_type, ex, am, rs, strategy, ctx_params)
        self.attributes = {}

    @classmethod
    def from_context(cls, context):
        return V4Context(context.backtestor, context.stgy_live_trader,
                         context.markets, context.candle_type, context.exchange,
                         context.asset_mgmt, context.report_storage, context.strategy,
                         context.ctx_params)

    def set_attribute(self, key, value):
        self.attributes[key] = value

    def get_attribute(self, key):
        return self.attributes[key]
