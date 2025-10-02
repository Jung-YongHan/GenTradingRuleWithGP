from bt4.strategy.Strategy import AbstractNettingStrategy


class BuyNHoldStrategy(AbstractNettingStrategy):
    def __init__(self):
        super(BuyNHoldStrategy, self).__init__()

    def set_params(self, am, report_storage, markets, params):
        super(BuyNHoldStrategy, self).set_params(am, report_storage, markets, params)

    def load_tai_params(self, params) :

        pass

    def __is_rebalance_time__(self, time_dt) :
        return True if time_dt.hour == 8 and time_dt.minute == 59 else False

    def __isBuySignal__(self, mkt_tais, tmgr, market, price, time_dt):
        return True, f"@Buy At the first time"

    def __isSellSignal__(self, mkt_tais, tmgr, market, price, time_dt):
        return False, f"@Keep"

    def extract_tai(self, tmgr):
        return {}
