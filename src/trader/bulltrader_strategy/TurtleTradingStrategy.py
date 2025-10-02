from bt4.utils.misc_utils import rearrange_market_tais
from bt4.utils.mylog import init_log
from bt4.utils.tai_utils import get_nary_tai, get_unary_tai
from bt4.strategy.Strategy import AbstractHedgingStrategy, AbstractNettingStrategy

log = init_log()

class TurtleTrading(AbstractNettingStrategy):

    def __init__(self):
        super(TurtleTrading, self).__init__()

    def load_tai_params(self, params) :
        self.tai_trb1 = params['tai_trb1']
        self.tai_trb2 = params['tai_trb2']
        self.tai_ema1 = params['tai_ema1']
        self.tai_ema2 = params['tai_ema2']
        self.tai_ema3 = params['tai_ema3']

    def __is_rebalance_time__(self, time_dt) :
        return True if time_dt.hour == 8 and time_dt.minute == 59 else False

    def __isBuySignal__(self, market_tai, tmgr, market, tick, time_dt) :
        price = tick.close
        ema4h_100 = market_tai[market]["ema4h_100s"]
        ema4h_60 = market_tai[market]["ema4h_60s"]
        ema4h_30 = market_tai[market]["ema4h_30s"]
        trb4h_24_h = market_tai[market]["trb4h_24s"][0]
        trb4h_24_l = market_tai[market]["trb4h_24s"][1]
        trb4h_48_h = market_tai[market]["trb4h_48s"][0]
        trb4h_48_l = market_tai[market]["trb4h_48s"][1]

        buy_system1 = (price > ema4h_100) and (ema4h_30 > ema4h_60) and (price > trb4h_24_h)
        # buy_system1 = (price > trb4h_24_h)
        buy_system1_log = f'(price({price}) > ema4h_100({ema4h_100})) and ' \
                          f'(ema4h_30({ema4h_30}) > ema4h_60({ema4h_60})) and (price({price}) > trb4h_24_h({trb4h_24_h}))'

        buy_system2 = (price > ema4h_100) and (ema4h_30 > ema4h_60) and (price > trb4h_48_h)
        # buy_system2 = (price > trb4h_48_h)
        buy_system2_log = f'(price({price}) > ema4h_100({ema4h_100})) and ' \
                          f'(ema4h_30({ema4h_30}) > ema4h_60({ema4h_60})) and (price({price}) > trb4h_48_h({trb4h_48_h}))'

        return buy_system1 or buy_system2, f', system1({buy_system1})={buy_system1_log}, system2({buy_system2})={buy_system2_log}'

    def __isSellSignal__(self, market_tai, tmgr, market, tick, time_dt) :
        price = tick.close
        trb4h_24_h = market_tai[market]["trb4h_24s"][0]
        trb4h_24_l = market_tai[market]["trb4h_24s"][1]
        trb4h_48_h = market_tai[market]["trb4h_48s"][0]
        trb4h_48_l = market_tai[market]["trb4h_48s"][1]

        sell_system1 = price < trb4h_24_l
        sell_system1_log = f'(price({price}) < trb4h_24_l({trb4h_24_l}))'
        sell_system2 = price < trb4h_48_l
        sell_system2_log = f'(price({price}) > trb4h_48_l({trb4h_48_l}))'

        return sell_system1 or sell_system2, f'sell_system1({sell_system1})={sell_system1_log}, sell_system2({sell_system2})={sell_system2_log}'

    def extract_tai(self, tmgr) :
        quote = tmgr.get_quote()
        markets = quote.get_markets(self.ex_type)

        tai_holder = {}
        rearrange_market_tais(markets, tai_holder, "trb4h_24s", get_nary_tai(tmgr, self.tai_trb1))
        rearrange_market_tais(markets, tai_holder, "trb4h_48s", get_nary_tai(tmgr, self.tai_trb2))
        rearrange_market_tais(markets, tai_holder, "ema4h_100s", get_unary_tai(tmgr, self.tai_ema3))
        rearrange_market_tais(markets, tai_holder, "ema4h_60s", get_unary_tai(tmgr, self.tai_ema2))
        rearrange_market_tais(markets, tai_holder, "ema4h_30s", get_unary_tai(tmgr, self.tai_ema1))

        return tai_holder


class TurtleTrading_Origin(AbstractNettingStrategy):

    def __init__(self):
        super(TurtleTrading_Origin, self).__init__()

    def load_tai_params(self, params) :
        self.tai_trb1 = params['tai_trb1']
        self.tai_trb2 = params['tai_trb2']
        self.tai_trb5 = params['tai_trb5']
        self.tai_atr  = params['tai_atr']

    def init_trading(self, quote):
        self.stop_prices = {}
        market_ticks = quote.get_market_ticks(self.ex_type)
        for market in market_ticks:
            self.stop_prices[market] = market_ticks[market].close
        return super(TurtleTrading_Origin, self).init_trading(quote)

    def __is_rebalance_time__(self, time_dt) :
        return True if time_dt.hour == 8 and time_dt.minute == 59 else False

    def __isBuySignal__(self, market_tai, tmgr, market, tick, time_dt):
        price = tick.close
        trb10_h = market_tai[market]["trb10s"][0]
        trb10_l = market_tai[market]["trb10s"][1]
        trb20_h = market_tai[market]["trb20s"][0]
        trb20_l = market_tai[market]["trb20s"][1]
        trb55_h = market_tai[market]["trb55s"][0]
        trb55_l = market_tai[market]["trb55s"][1]

        buy_system1 = (price > trb20_h)
        buy_system1_log = f'(price({price}) > trb20s_h({trb20_h}))'

        buy_system2 = (price > trb55_h)
        buy_system2_log = f'(price({price}) > trb55s_h({trb55_h}))'

        return buy_system1 or buy_system2, f', system1({buy_system1})={buy_system1_log}, system2({buy_system2})={buy_system2_log}'

    def __isSellSignal__(self, market_tai, tmgr, market, tick, time_dt):
        price = tick.close
        trb10_h = market_tai[market]["trb10s"][0]
        trb10_l = market_tai[market]["trb10s"][1]
        trb20_h = market_tai[market]["trb20s"][0]
        trb20_l = market_tai[market]["trb20s"][1]
        trb55_h = market_tai[market]["trb55s"][0]
        trb55_l = market_tai[market]["trb55s"][1]
        atr = market_tai[market]["atrs"]

        sell_system1 = price < trb10_l
        sell_system1_log = f'(price({price}) < trb10_l({trb10_l}))'
        sell_system2 = price < trb20_l
        sell_system2_log = f'(price({price}) < trb20_l({trb20_l}))'
        self.stop_prices[market] = self.stop_prices[market] - 2 * atr
        cut_loss = price < self.stop_prices[market]
        cut_loss_log = f'(price({price}) < stop({self.stop_prices[market]}))'
        
        return sell_system1 or sell_system2 or cut_loss, f'sell_system1({sell_system1})={sell_system1_log}, sell_system2({sell_system2})={sell_system2_log}, cut_loss({cut_loss})={cut_loss_log}'

    def extract_tai(self, tmgr):
        quote = tmgr.get_quote()
        markets = quote.get_markets(self.ex_type)\

        tai_holder = {}
        rearrange_market_tais(markets, tai_holder, "trb10s", get_nary_tai(tmgr, self.tai_trb1))
        rearrange_market_tais(markets, tai_holder, "trb20s", get_nary_tai(tmgr, self.tai_trb2))
        rearrange_market_tais(markets, tai_holder, "trb55s", get_nary_tai(tmgr, self.tai_trb5))
        rearrange_market_tais(markets, tai_holder, "atrs", get_unary_tai(tmgr, self.tai_atr))

        return tai_holder


class TurtleTrading_Hdg(AbstractHedgingStrategy):

    def __init__(self):
        super(TurtleTrading_Hdg, self).__init__()

    def load_tai_params(self, params):
        self.tai_trb1 = params['tai_trb1']
        self.tai_trb2 = params['tai_trb2']
        self.tai_ema1 = params['tai_ema1']
        self.tai_ema2 = params['tai_ema2']
        self.tai_ema3 = params['tai_ema3']


    def __isBuySignal__(self, mkt_buy_tais, tmgr, market, tick, time_dt, tf_hour):
        price = tick.close
        ema4h_100 = mkt_buy_tais[market]["ema4h_100s"]
        ema4h_60 = mkt_buy_tais[market]["ema4h_60s"]
        ema4h_30 = mkt_buy_tais[market]["ema4h_30s"]
        trb4h_24_h = mkt_buy_tais[market]["trb4h_24s"][0]
        trb4h_48_h = mkt_buy_tais[market]["trb4h_48s"][0]

        buy_system1 = (price > ema4h_100) and (ema4h_30 > ema4h_60) and (price > trb4h_24_h)
        buy_system1_log = f'(price({price}) > ema4h_100({ema4h_100})) and ' \
                          f'(ema4h_30({ema4h_30}) > ema4h_60({ema4h_60})) and (price({price}) > trb4h_24_h({trb4h_24_h}))'

        buy_system2 = (price > ema4h_100) and (ema4h_30 > ema4h_60) and (price > trb4h_48_h)
        buy_system2_log = f'(price({price}) > ema4h_100({ema4h_100})) and ' \
                          f'(ema4h_30({ema4h_30}) > ema4h_60({ema4h_60})) and (price({price}) > trb4h_48_h({trb4h_48_h}))'

        return (buy_system1 or buy_system2), f'buy_system1({buy_system1})={buy_system1_log}, buy_system2({buy_system2})={buy_system2_log}, '

    def __isSellSignal__(self, mkt_sell_tais, tmgr, market, tick, time_dt, tf_hour) :
        price = tick.close
        trb4h_24_l = mkt_sell_tais[market]["trb4h_24s"][1]
        trb4h_48_l = mkt_sell_tais[market]["trb4h_48s"][1]

        sell_system1 = price < trb4h_24_l
        sell_system1_log = f'(price({price}) < trb4h_24_l({trb4h_24_l}))'
        sell_system2 = price < trb4h_48_l
        sell_system2_log = f'(price({price}) > trb4h_48_l({trb4h_48_l}))'

        return (sell_system1 or sell_system2), f'sell_system1({sell_system1})={sell_system1_log}, sell_system2({sell_system2})={sell_system2_log}'

    def extract_tai(self, tmgr, timeframe_hour):
        quote = tmgr.get_quote()
        markets = quote.get_markets(self.ex_type)\

        tai_holder = {}
        rearrange_market_tais(markets, tai_holder, "trb4h_24s", get_nary_tai(tmgr, self.tai_trb1))
        rearrange_market_tais(markets, tai_holder, "trb4h_48s", get_nary_tai(tmgr, self.tai_trb2))

        rearrange_market_tais(markets, tai_holder, "ema4h_100s", get_unary_tai(tmgr, self.tai_ema3))
        rearrange_market_tais(markets, tai_holder, "ema4h_60s", get_unary_tai(tmgr, self.tai_ema2))
        rearrange_market_tais(markets, tai_holder, "ema4h_30s", get_unary_tai(tmgr, self.tai_ema1))

        return tai_holder
