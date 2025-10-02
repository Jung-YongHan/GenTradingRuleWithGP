import copy

from bt4.Constants import Ary
from bt4.utils.misc_utils import rearrange_market_tais
from bt4.utils.tai_utils import get_nary_tai, get_unary_tai
from bt4.strategy.Strategy import AbstractNettingStrategy


class TAICombStrategy(AbstractNettingStrategy):
    def __init__(self):
        super(TAICombStrategy, self).__init__()

    def set_params(self, am, report_storage, markets, params):
        super(TAICombStrategy, self).set_params(am, report_storage, markets, params)

    def load_tai_params(self, params) :
        self.candle_type = params["candle_type"]
        self.tai_macd    = params["tai_macd"]
        self.tai_ic1    = params["tai_ic1"]
        self.tai_ic = params["tai_ic"]
        self.tai_cmf = params["tai_cmf"]

    def __is_rebalance_time__(self, time_dt) :
        remainder = time_dt.minute % self.candle_type.value         # Rebalance every candle time
        if remainder == (self.candle_type.value - 1) :
            return True
        return False

    def __is_settlement_time__(self, time_dt):
        return True if time_dt.hour == 8 and time_dt.minute == 59 else False

    def __isBuySignal__(self, mkt_tais, tmgr, market, tick, time_dt):
        price = tick.close
        desc = ""
        ic1_signal = False
        ic1 = mkt_tais[market]["tai_ic1"]
        if price > ic1:
            ic1_signal = True # True to enable, False for disable
            desc += f"ic1({ic1_signal}) price({price}) > ic1({ic1}), "

        ic_signal =  False # True to enable, False for disable
        ic = mkt_tais[market]["tai_ic"]
        if price > ic:
            ic_signal = True
            desc += f"ic({ic_signal}) price({price}) > ic({ic}), "

        cmf_signal = True  # True for disable, False for enable
        cmf = mkt_tais[market]["tai_cmf"]
        if cmf > 0:
            cmf_signal = True
            desc += f"cmf({cmf_signal}) cmf({cmf}) > 0, "

        macd_signal = True  # True for disable, False for enable
        macd,_,_ = mkt_tais[market]["tai_macd"]
        if macd > 0:
            macd_signal = True
            desc += f"macd({cmf_signal}) macd({macd}) > 0, "

        return ic1_signal and ic_signal and cmf_signal and macd_signal, desc

    def __isSellSignal__(self, mkt_tais, tmgr, market, tick, time_dt):
        price = tick.close
        desc = ""
        ic1_signal = False
        ic1 = mkt_tais[market]["tai_ic1"]
        if price < ic1 :
            ic1_signal = True
            desc += f"ic1({ic1_signal}) price({price}) < ic1({ic1}), "

        ic_signal = False
        ic = mkt_tais[market]["tai_ic"]
        if price < ic :
            ic_signal = False  # True to enable, False for disable
            desc += f"ic({ic_signal}) price({price}) < ic({ic}), "

        cmf_signal = False
        cmf = mkt_tais[market]["tai_cmf"]
        if cmf < 0 :
            cmf_signal =  False  # True to enable, False for disable
            desc += f"cmf({cmf_signal}) cmf({cmf}) < 0, "

        macd_signal = False
        macd, _, _ = mkt_tais[market]["tai_macd"]
        if macd < 0 :
            macd_signal =  False  # True to enable, False for disable
            desc += f"macd({cmf_signal}) macd({macd}) > 0, "

        return ic1_signal or ic_signal or cmf_signal or macd_signal, desc

    def extract_tai(self, tmgr):
        quote = tmgr.get_quote()
        markets = quote.get_markets(self.ex_type)

        tai_holder = {}
        rearrange_market_tais(markets, tai_holder, "tai_macd", get_nary_tai(tmgr, self.tai_macd))
        rearrange_market_tais(markets, tai_holder, "tai_ic1", get_unary_tai(tmgr, self.tai_ic1))
        rearrange_market_tais(markets, tai_holder, "tai_ic", get_unary_tai(tmgr, self.tai_ic))
        rearrange_market_tais(markets, tai_holder, "tai_cmf", get_unary_tai(tmgr, self.tai_cmf))

        return tai_holder


class TAIRuleStrategy(AbstractNettingStrategy):
    def __init__(self):
        super(TAIRuleStrategy, self).__init__()

    def set_params(self, am, report_storage, markets, params):
        super(TAIRuleStrategy, self).set_params(am, report_storage, markets, params)

    def load_tai_params(self, params) :
        self.tai_rules = {}
        for tai in params:
            if tai == "rebalance":
                self.rebal_cdl = params["rebalance"]
            elif tai.endswith("_rule"):
                if params[tai]["enable"] == True:
                    self.tai_rules[tai] = params[tai]

    def __is_rebalance_time__(self, time_dt) :
        remainder = time_dt.minute % self.rebal_cdl.value         # Rebalance every candle time
        if remainder == (self.rebal_cdl.value - 1) :
            return True
        return False

    def __is_settlement_time__(self, time_dt):
        return True if time_dt.hour == 8 and time_dt.minute == 59 else False

    def __isBuySignal__(self, mkt_tais, tmgr, market, tick, time_dt):
        desc = ""
        buy_signal = True
        for tai_r_name in self.tai_rules :
            tai_rule = self.tai_rules[tai_r_name]
            long_func = tai_rule["l_fc"]
            enable = tai_rule["enable"]
            if long_func is not None and enable:
                tai_buy_signal, tai_desc = long_func(mkt_tais, tmgr, market, tick, time_dt)
                desc += tai_desc
                if tai_buy_signal == False:
                    buy_signal = False

        return buy_signal, desc

    def __isSellSignal__(self, mkt_tais, tmgr, market, tick, time_dt):
        desc = ""
        sell_signal = False
        for tai_r_name in self.tai_rules :
            tai_rule = self.tai_rules[tai_r_name]
            short_func = tai_rule["s_fc"]
            enable = tai_rule["enable"]
            if short_func is not None and enable:
                tai_sell_signal, tai_desc = short_func(mkt_tais, tmgr, market, tick, time_dt)
                desc += tai_desc
                if tai_sell_signal == True:
                    sell_signal = True

        return sell_signal, desc

    def extract_tai(self, tmgr):
        quote = tmgr.get_quote()
        markets = quote.get_markets(self.ex_type)

        tai_holder = {}
        for tai_r_name in self.tai_rules:
            tai_rule = self.tai_rules[tai_r_name]
            tais = tai_rule["tai"]
            for tai in tais:
                tai_params = tais[tai]
                cdl_type = tai_rule["cdl"]
                tai_params[2] = cdl_type
                cloned_tai_params = copy.copy(tai_params)
                ary = cloned_tai_params.pop()
                if ary == Ary.Unary:
                    rearrange_market_tais(markets, tai_holder, tai, get_unary_tai(tmgr, cloned_tai_params))
                else:
                    rearrange_market_tais(markets, tai_holder, tai, get_nary_tai(tmgr, cloned_tai_params))

        return tai_holder
