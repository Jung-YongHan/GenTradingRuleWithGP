from bt4.Constants import CandleType, QItem
from bt4.utils.market_utils import pick_market_unary_tais
from bt4.utils.misc_utils import rearrange_market_tais
from bt4.utils.mylog import init_log
from bt4.utils.python_utils import split_hour_min, is_the_time, to_curr_unit_str2
from bt4.utils.tai_utils import get_unary_tai, get_nary_tai
from bt4.strategy.Strategy import AbstractNettingStrategy, AbstractHedgingStrategy

log = init_log()

######################################################
## Common functions in SWS
def signal_buy_pos(mas_list, price):
    buySignal = True
    for ma in mas_list:
        if price <= ma:
            buySignal = False
            break
    return buySignal

def signal_sell_pos(mas_list, price):
    sellSignal = False
    for ma in mas_list:
        if price <= ma:
            sellSignal = True
            break
    return sellSignal

def get_mas_str2(ma_prefix_list, tf_hour, mas_list):
    mas_str = '{'
    for i, ma_prefix in enumerate(ma_prefix_list):
        mas_str = mas_str + f'{ma_prefix}{tf_hour}({to_curr_unit_str2(mas_list[i], None)}),'
    return mas_str[0:-1] + '}'

def get_mas_str(mas_list):
    mas_str = '['
    for i, ma in enumerate(mas_list):
        mas_str = mas_str + f'{ma:3.1f}'
        if i < len(mas_list) - 1:
            mas_str = mas_str + ','
    mas_str = mas_str + ']'
    return mas_str

@DeprecationWarning
def pick_up_mas_from_ta_indicators(ta_indicators, ma_name_list):
    market_mas = {}

    market_ma_list = []
    for ma_name in ma_name_list:
        market_ma = pick_market_unary_tais(ta_indicators, ma_name)
        market_ma_list.append(market_ma)

    for market in ta_indicators:
        market_mas[market] = []
        for market_ma in market_ma_list:
            market_mas[market].append(market_ma[market])
    return market_mas

def pick_up_mas_from_ta_indicators3(tmgr, tai_ma_list):
    market_mas = {}

    market_ma_list = []
    for tai_ma in tai_ma_list:
        market_ma = get_unary_tai(tmgr, tai_ma)
        market_ma_list.append(market_ma)

    quote = tmgr.get_quote()
    market_ticks = quote.get_market_ticks(tmgr.ex_type)
    for market in market_ticks:
        market_mas[market] = []
        for market_ma in market_ma_list:
            market_mas[market].append(market_ma[market])
    return market_mas

@DeprecationWarning
def pick_up_mas_from_ta_indicators2(tmgr, market_ticks, candle_type, ma_period_list):
    market_mas = {}

    market_ma_list = []
    for ma_period in ma_period_list:
        market_ma = tmgr.get_unary('sma', [ma_period], candle_type, [QItem.close])
        market_ma_list.append(market_ma)

    for market in market_ticks:
        market_mas[market] = []
        for market_ma in market_ma_list:
            market_mas[market].append(market_ma[market])
    return market_mas


class SuperWinningSession_Day(AbstractNettingStrategy):

    def __init__(self):
        super(SuperWinningSession_Day, self).__init__()

    def set_params(self, am, report_storage, markets, params):
        super(SuperWinningSession_Day, self).set_params(am, report_storage, markets, params)
        self.__sig__ = "sws"

    def load_tai_params(self, params) :
        self.base_time = params['base_time']
        self.base_hour, self.base_minute = split_hour_min(self.base_time)
        self.sell_time = params['sell_time']
        self.sell_hour, self.sell_minute = split_hour_min(self.sell_time)
        self.tai_ma1 = params['tai_ma1']
        self.tai_ma2 = params['tai_ma2']
        self.tai_ma3 = params['tai_ma3']
        self.tai_ma4 = params['tai_ma4']

    def __is_rebalance_time__(self, time_dt) :
        return True if time_dt.hour == 8 and time_dt.minute == 59 else False

    def __isBuySignal__(self, market_tai, tmgr, market, tick, time_dt):
        price = tick.close
        is_base_time = is_the_time(time_dt, self.base_hour, self.base_minute)

        ma0 = market_tai[f"{market}_{self.__sig__}"]['ma0']
        ma1 = market_tai[f"{market}_{self.__sig__}"]['ma1']
        ma2 = market_tai[f"{market}_{self.__sig__}"]['ma2']
        ma3 = market_tai[f"{market}_{self.__sig__}"]['ma3']
        ma_list = [ma0, ma1, ma2, ma3]
        tai_signal = signal_buy_pos(ma_list, price)
        return is_base_time and tai_signal, f"(@{self.base_time}) price({price}) > mas({get_mas_str(ma_list)})"

    def __isSellSignal__(self, market_tai, tmgr, market, tick, time_dt):
        price = tick.close
        is_sell_time = is_the_time(time_dt, self.sell_hour, self.sell_minute)

        ma0 = market_tai[f"{market}_{self.__sig__}"]['ma0']
        ma1 = market_tai[f"{market}_{self.__sig__}"]['ma1']
        ma2 = market_tai[f"{market}_{self.__sig__}"]['ma2']
        ma3 = market_tai[f"{market}_{self.__sig__}"]['ma3']
        ma_list = [ma0, ma1, ma2, ma3]
        tai_signal = signal_sell_pos(ma_list, price)
        return is_sell_time and tai_signal, f"@{self.sell_time} price({price}) < mas({get_mas_str(ma_list)})"

    def extract_tai(self, tmgr):
        tai_ma_list = [self.tai_ma1, self.tai_ma2, self.tai_ma3, self.tai_ma4]
        market_mas_list = []
        ma_prefix_list = []
        for tai_ma in tai_ma_list:
            market_ma = get_unary_tai(tmgr, tai_ma)
            market_mas_list.append(market_ma)
            ma_prefix = f"{tai_ma[0]}{tai_ma[1][0]}"
            ma_prefix_list.append(ma_prefix)

        quote = tmgr.get_quote()
        market_ticks = quote.get_market_ticks(tmgr.ex_type)

        market_mas = {}
        for market in market_ticks:
            market_mas[f"{market}_{self.__sig__}"] = {}
            ma_list = []
            for idx, mas in enumerate(market_mas_list):
                market_mas[f"{market}_{self.__sig__}"][f"ma{idx}"] = mas[market]
                ma_list.append(mas[market])
        return market_mas


class SuperWinningSession(AbstractNettingStrategy):

    def __init__(self):
        super(SuperWinningSession, self).__init__()

    def set_params(self, am, report_storage, markets, params):
        super(SuperWinningSession, self).set_params(am, report_storage, markets, params)
        self.__sig__ = "sws"

    def load_tai_params(self, params) :
        self.candle_type = params['candle_type']
        self.tai_ma1 = params['tai_ma1']
        self.tai_ma2 = params['tai_ma2']
        self.tai_ma3 = params['tai_ma3']
        self.tai_ma4 = params['tai_ma4']

    def __is_rebalance_time__(self, time_dt) :
        remainder = time_dt.minute % self.candle_type.value         # Rebalance every candle time
        if remainder == (self.candle_type.value - 1) :
            return True
        return False

    def __is_settlement_time__(self, time_dt):
        return True if time_dt.hour == 8 and time_dt.minute == 59 else False

    def __isBuySignal__(self, market_tai, tmgr, market, tick, time_dt):
        price = tick.close
        ma0 = market_tai[f"{market}_{self.__sig__}"]['ma0']
        ma1 = market_tai[f"{market}_{self.__sig__}"]['ma1']
        ma2 = market_tai[f"{market}_{self.__sig__}"]['ma2']
        ma3 = market_tai[f"{market}_{self.__sig__}"]['ma3']
        ma_list = [ma0, ma1, ma2, ma3]
        tai_signal = signal_buy_pos(ma_list, price)
        return tai_signal, f"price({price}) > mas({get_mas_str(ma_list)})"

    def __isSellSignal__(self, market_tai, tmgr, market, tick, time_dt):
        price = tick.close
        ma0 = market_tai[f"{market}_{self.__sig__}"]['ma0']
        ma1 = market_tai[f"{market}_{self.__sig__}"]['ma1']
        ma2 = market_tai[f"{market}_{self.__sig__}"]['ma2']
        ma3 = market_tai[f"{market}_{self.__sig__}"]['ma3']
        ma_list = [ma0, ma1, ma2, ma3]
        tai_signal = signal_sell_pos(ma_list, price)
        return tai_signal, f"price({price}) < mas({get_mas_str(ma_list)})"

    def extract_tai(self, tmgr):
        tai_ma_list = [self.tai_ma1, self.tai_ma2, self.tai_ma3, self.tai_ma4]
        market_mas_list = []
        ma_prefix_list = []
        for tai_ma in tai_ma_list:
            market_ma = get_unary_tai(tmgr, tai_ma)
            market_mas_list.append(market_ma)
            ma_prefix = f"{tai_ma[0]}{tai_ma[1][0]}"
            ma_prefix_list.append(ma_prefix)

        quote = tmgr.get_quote()
        market_ticks = quote.get_market_ticks(tmgr.ex_type)

        market_mas = {}
        for market in market_ticks:
            market_mas[f"{market}_{self.__sig__}"] = {}
            ma_list = []
            for idx, mas in enumerate(market_mas_list):
                market_mas[f"{market}_{self.__sig__}"][f"ma{idx}"] = mas[market]
                ma_list.append(mas[market])
        return market_mas

class SuperWinningSessionPoweredByMACrossOver_Day(SuperWinningSession_Day):
    def __init__(self, ):
        super(SuperWinningSessionPoweredByMACrossOver_Day, self).__init__()

    def set_params(self, am, report_storage, markets, params):
        super(SuperWinningSessionPoweredByMACrossOver_Day, self).set_params(am, report_storage, markets, params)
        self.arrow_tai_ma = params['arrow_tai_ma']
        self.target_tai_ma = params['target_tai_ma']

    def __isBuySignal__(self, market_tai, tmgr, market, tick, time_dt):
        price = tick.close
        super_winning_session_buy_signal, buy_log = super(SuperWinningSessionPoweredByMACrossOver_Day, self).\
            __isBuySignal__(market_tai, tmgr, market, tick, time_dt)

        ma1 = market_tai[f"{market}_{self.__sig__}"]['ma1']
        ma3 = market_tai[f"{market}_{self.__sig__}"]['ma3']

        # self.mass[1] = MA(5), self.mass[3] = MA(20)
        ma_cross_over_buy_signal = False
        if ma1 >= ma3 :
            ma_cross_over_buy_signal = True
        buy_log += f", ma1({ma1}) > ma3({ma3})"
        return super_winning_session_buy_signal and ma_cross_over_buy_signal, buy_log

    def __isSellSignal__(self, market_tai, tmgr, market, tick, time_dt):
        price = tick.close
        super_winning_session_sell_signal, sell_log = super(SuperWinningSessionPoweredByMACrossOver_Day, self). \
            __isSellSignal__(market_tai, tmgr, market, tick, time_dt)

        ma1 = market_tai[f"{market}_{self.__sig__}"]['ma1']
        ma3 = market_tai[f"{market}_{self.__sig__}"]['ma3']
        # self.mass[1] = MA(5), self.mass[3] = MA(20)
        ma_cross_over_sell_signal = False
        if ma1 < ma3:
            ma_cross_over_sell_signal = True

        sell_log += f", ma1({ma1}) < ma3({ma3})"
        return super_winning_session_sell_signal or ma_cross_over_sell_signal, sell_log


class SuperWinningSession_4H(AbstractNettingStrategy):
    def __init__(self, ):
        super(SuperWinningSession_4H, self).__init__()
        self.__sig__ = "sws4h"

    def set_params(self, am, report_storage, markets, params):
        params['rebal_time'] = '08:59'
        super(SuperWinningSession_4H, self).set_params(am, report_storage, markets, params)
        self.trading_hour = 4

    def load_tai_params(self, params) :
        self.tai_ma1 = params['tai_ma1']
        self.tai_ma2 = params['tai_ma2']
        self.tai_ma3 = params['tai_ma3']
        self.tai_ma4 = params['tai_ma4']

    def __is_rebalance_time__(self, time_dt) :
        # return True if time_dt.hour % self.trading_hour == 0 and time_dt.minute == 59 else False
        return True if time_dt.hour == 8 and time_dt.minute == 59 else False

    def __isBuySignal__(self, market_tai, tmgr, market, tick, time_dt):
        price = tick.close
        is_trading_time = True if time_dt.hour % self.trading_hour == 0 and time_dt.minute == 59 else False

        ma0 = market_tai[f"{market}_{self.__sig__}"]['ma0']
        ma1 = market_tai[f"{market}_{self.__sig__}"]['ma1']
        ma2 = market_tai[f"{market}_{self.__sig__}"]['ma2']
        ma3 = market_tai[f"{market}_{self.__sig__}"]['ma3']
        ma_list = [ma0, ma1, ma2, ma3]

        tai_signal = signal_buy_pos(ma_list, price)
        return is_trading_time and tai_signal, f"(@{is_trading_time}) price({price}) > mas({get_mas_str(ma_list)})"

    def __isSellSignal__(self, market_tai, tmgr, market, tick, time_dt):
        price = tick.close
        is_trading_time = True if time_dt.hour % self.trading_hour == 0 and time_dt.minute == 59 else False

        ma0 = market_tai[f"{market}_{self.__sig__}"]['ma0']
        ma1 = market_tai[f"{market}_{self.__sig__}"]['ma1']
        ma2 = market_tai[f"{market}_{self.__sig__}"]['ma2']
        ma3 = market_tai[f"{market}_{self.__sig__}"]['ma3']
        ma_list = [ma0, ma1, ma2, ma3]
        tai_signal = signal_sell_pos(ma_list, price)
        return is_trading_time and tai_signal, f"@{is_trading_time} price({price}) < mas({get_mas_str(ma_list)})"

    def extract_tai(self, tmgr):
        tai_ma_list = [self.tai_ma1, self.tai_ma2, self.tai_ma3, self.tai_ma4]
        market_mas_list = []
        ma_prefix_list = []
        for tai_ma in tai_ma_list:
            market_ma = get_unary_tai(tmgr, tai_ma)
            market_mas_list.append(market_ma)
            ma_prefix = f"{tai_ma[0]}{tai_ma[1][0]}"
            ma_prefix_list.append(ma_prefix)

        quote = tmgr.get_quote()
        market_ticks = quote.get_market_ticks(tmgr.ex_type)

        market_mas = {}
        for market in market_ticks:
            market_mas[f"{market}_{self.__sig__}"] = {}
            for idx, mas in enumerate(market_mas_list):
                market_mas[f"{market}_{self.__sig__}"][f"ma{idx}"] = mas[market]
        return market_mas


class SuperWinningSession_Hedge(AbstractHedgingStrategy):
    def __init__(self, ):
        super(SuperWinningSession_Hedge, self).__init__()

    def load_tai_params(self, params):
        self.tai_ma1_tf = params['tai_ma1_tf']
        self.tai_ma2_tf = params['tai_ma2_tf']
        self.tai_ma3_tf = params['tai_ma3_tf']
        self.tai_ma4_tf = params['tai_ma4_tf']

    def __isBuySignal__(self, mkt_buy_tais, tmgr, market, tick, time_dt, tf_hour):
        price = tick.close
        ma_list = []
        ma_list.append(mkt_buy_tais[market]['ma0'])
        ma_list.append(mkt_buy_tais[market]['ma1'])
        ma_list.append(mkt_buy_tais[market]['ma2'])
        ma_list.append(mkt_buy_tais[market]['ma3'])

        ma_prefix_list = ['ma1_', 'ma2_', 'ma3_', 'ma4_']
        buy_log = f"price({to_curr_unit_str2(price, None)}) > {get_mas_str2(ma_prefix_list, tf_hour, ma_list)}"
        return signal_buy_pos(ma_list, price), buy_log

    def __isSellSignal__(self, mkt_sell_tais, tmgr, market, tick, time_dt, tf_hour) :
        price = tick.close
        ma_list = []
        ma_list.append(mkt_sell_tais[market]['ma0'])
        ma_list.append(mkt_sell_tais[market]['ma1'])
        ma_list.append(mkt_sell_tais[market]['ma2'])
        ma_list.append(mkt_sell_tais[market]['ma3'])

        ma_prefix_list = ['ma1_', 'ma2_', 'ma3_', 'ma4_']
        sell_log = f"price({to_curr_unit_str2(price, None)}) < {get_mas_str2(ma_prefix_list, tf_hour, ma_list)}"
        return signal_sell_pos(ma_list, price), sell_log

    def extract_tai(self, tmgr, timeframe_hour):
        tai_ma_list = [self.tai_ma1_tf, self.tai_ma2_tf, self.tai_ma3_tf, self.tai_ma4_tf]
        market_mas_list = []
        for tai_ma in tai_ma_list:
            ma_key = f'DAYS_{timeframe_hour}'  # it should be matched with that of euote dispatcher
            cdl_type = CandleType[ma_key]
            tai_ma[2] = cdl_type
            market_ma = get_unary_tai(tmgr, tai_ma)
            market_mas_list.append(market_ma)

        quote = tmgr.get_quote()
        market_ticks = quote.get_market_ticks(tmgr.ex_type)

        market_mas = {}
        for market in market_ticks:
            market_mas[market] = {}
            ma_list = []
            for idx, mas in enumerate(market_mas_list):
                market_mas[market][f"ma{idx}"] = mas[market]
                ma_list.append(mas[market])

        return market_mas

class SuperWinningSession_Asym_Hedge(SuperWinningSession_Hedge):
    def __init__(self, ):
        super(SuperWinningSession_Asym_Hedge, self).__init__()

    def load_tai_params(self, params):
        self.tai_bb_close_tf = params['tai_bb_close_tf'] if 'tai_bb_close_tf' in params else None
        self.tai_vwap_tf = params['tai_vwap_tf'] if 'tai_vwap_tf' in params else None
        self.tai_macd_tf = params['tai_macd_tf'] if 'tai_macd_tf' in params else None
        self.tai_cci_tf = params['tai_ccl_tf'] if 'tai_ccl_tf' in params else None
        self.tai_ma5_tf = params['tai_ma5_tf'] if 'tai_ma5_tf' in params else None
        super(SuperWinningSession_Asym_Hedge, self).load_tai_params(params)

    def __isBuySignal__(self, mkt_buy_tais, tmgr, market, tick, time_dt, tf_hour):
        price = tick.close
        desc = ""
        ma0 = mkt_buy_tais[market]['ma0']
        ma1 = mkt_buy_tais[market]['ma1']
        ma2 = mkt_buy_tais[market]['ma2']
        ma3 = mkt_buy_tais[market]['ma3']

        system1 = price > ma0
        system2 = price > ma1
        system3 = price > ma2
        system4 = price > ma3

        desc = desc + f"\r\n *[ma0] = {system1} :: price({price}) > ma0({ma0})"
        desc = desc + f"\r\n *[ma1] = {system2} :: price({price}) > ma1({ma1})"
        desc = desc + f"\r\n *[ma2] = {system3} :: price({price}) > ma2({ma2})"
        desc = desc + f"\r\n *[ma3] = {system4} :: price({price}) > ma3({ma3})"

        signal = False
        if  system1 and system2 and system3 and system4:
            signal = True

        return signal, desc

    def __isSellSignal__(self, mkt_sell_tais, tmgr, market, tick, time_dt, tf_hour) :
        price = tick.close
        desc = ""
        ma0 = mkt_sell_tais[market]['ma0']
        # ma1 = mkt_sell_tais[market]['ma1']
        # ma2 = mkt_sell_tais[market]['ma2']
        # ma3 = mkt_sell_tais[market]['ma3']
        # bband_upper = mkt_sell_tais[market]['bband'][0]
        # vwap = mkt_sell_tais[market]['vwap']
        # macd = mkt_sell_tais[market]['macd']  # [0]macd, [1] macd_signal, [2] macd_hist
        # cci = mkt_sell_tais[market]['cci']
        # ma5 = mkt_sell_tais[market]['ma5']

        system1 = price < ma0
        # system2 = price < ma1
        # system3 = price < ma2
        # system4 = price < ma3
        # system_bband = price > bband_upper
        # system_vwap = price < vwap
        # system_macd = macd[0] < macd[1]
        # system_cci = cci < 0
        # system_ma5 = price < ma5

        desc = desc + f"\r\n *[ma0] = {system1} :: price({price}) < ma0({ma0})"
        # desc = desc + f"\r\n *[ma1] = {system2} :: price({price}) < ma1({ma1})"
        # desc = desc + f"\r\n *[ma2] = {system3} :: price({price}) < ma2({ma2})"
        # desc = desc + f"\r\n *[ma3] = {system4} :: price({price}) < ma3({ma3})"
        # desc = desc + f"\r\n *[bband_upper] = {system_bband} :: price({price}) > bband_upper({bband_upper})"
        # desc = desc + f"\r\n *[vwap] = {system_vwap} :: price({price}) < vwap({vwap})"
        # desc = desc + f"\r\n *[macd] = {system_macd} :: macd({macd[0]}) < macd_sig({macd[1]})"
        # desc = desc + f"\r\n *[cci] = {system_cci} :: cci({cci}) < 0"
        # desc = desc + f"\r\n *[ma5] = {system_ma5} :: price({price}) < {ma5}"

        signal = False
        # if system1 or (system_macd and system_cci):
        if (system1) :
            signal = True
        return signal, desc
        # return system1 or system_bband or system_vwap, desc
        # return system_bband or system_vwap, desc


    def extract_tai(self, tmgr, timeframe_hour) :
        market_tai = super(SuperWinningSession_Asym_Hedge, self).extract_tai(tmgr, timeframe_hour)

        quote = tmgr.get_quote()
        market_ticks = quote.get_market_ticks(tmgr.ex_type)
        markets = quote.get_markets(self.ex_type)

        ma_key = f'DAYS_{timeframe_hour}'
        if self.tai_bb_close_tf is not None :
            self.tai_bb_close_tf[2] = CandleType[ma_key]
            rearrange_market_tais(markets, market_tai, "bband", get_nary_tai(tmgr, self.tai_bb_close_tf))

        if self.tai_vwap_tf is not None:
            self.tai_vwap_tf[2] = CandleType[ma_key]
            rearrange_market_tais(markets, market_tai, "vwap", get_unary_tai(tmgr, self.tai_vwap_tf))

        if self.tai_macd_tf is not None:
            self.tai_macd_tf[2] = CandleType[ma_key]
            rearrange_market_tais(markets, market_tai, "macd", get_nary_tai(tmgr, self.tai_macd_tf))

        if self.tai_cci_tf is not None:
            self.tai_cci_tf[2] = CandleType[ma_key]
            rearrange_market_tais(markets, market_tai, "cci", get_unary_tai(tmgr, self.tai_cci_tf))

        if self.tai_ma5_tf is not None:
            self.tai_ma5_tf[2] = CandleType[ma_key]
            rearrange_market_tais(markets, market_tai, "ma5", get_unary_tai(tmgr, self.tai_ma5_tf))


        return market_tai



class SuperWinningSession_EMA_Hedge(AbstractHedgingStrategy):
    def __init__(self, ):
        super(SuperWinningSession_EMA_Hedge, self).__init__()

    def load_tai_params(self, params):
        self.tai_ema1_tf = params['tai_ema1_tf']
        self.tai_ema2_tf = params['tai_ema2_tf']
        self.tai_ema3_tf = params['tai_ema3_tf']
        self.tai_ema4_tf = params['tai_ema4_tf']

    def __isBuySignal__(self, mkt_buy_tais, tmgr, market, tick, time_dt, tf_hour) :
        price = tick.close
        ema_list = []
        ema_list.append(mkt_buy_tais[market]['ema0'])
        ema_list.append(mkt_buy_tais[market]['ema1'])
        ema_list.append(mkt_buy_tais[market]['ema2'])
        ema_list.append(mkt_buy_tais[market]['ema3'])

        ma_prefix_list = ['ema1_', 'ema2_', 'ema3_', 'ema4_']
        buy_log = f"price({to_curr_unit_str2(price, None)}) > {get_mas_str2(ma_prefix_list, tf_hour, ema_list)}"
        return signal_buy_pos(ema_list, price), buy_log

    def __isSellSignal__(self, mkt_sell_tais, tmgr, market, tick, time_dt, tf_hour) :
        price = tick.close
        ema_list = []
        ema_list.append(mkt_sell_tais[market]['ema0'])
        ema_list.append(mkt_sell_tais[market]['ema1'])
        ema_list.append(mkt_sell_tais[market]['ema2'])
        ema_list.append(mkt_sell_tais[market]['ema3'])

        ma_prefix_list = ['ema1_', 'ema2_', 'ema3_', 'ema4_']
        sell_log = f"price({to_curr_unit_str2(price, None)}) < {get_mas_str2(ma_prefix_list, tf_hour, ema_list)}"
        return signal_sell_pos(ema_list, price), sell_log

    def extract_tai(self, tmgr, timeframe_hour):
        tai_ema_list = [self.tai_ema1_tf, self.tai_ema2_tf, self.tai_ema3_tf, self.tai_ema4_tf]

        market_mas_list = []
        for tai_ema in tai_ema_list:
            ma_key = f'DAYS_{timeframe_hour}'  # it should be matched with that of euote dispatcher
            cdl_type = CandleType[ma_key]
            tai_ema[2] = cdl_type
            market_ma = get_unary_tai(tmgr, tai_ema)
            market_mas_list.append(market_ma)

        quote = tmgr.get_quote()
        market_ticks = quote.get_market_ticks(tmgr.ex_type)

        market_mas = {}
        for market in market_ticks:
            market_mas[market] = {}
            ma_list = []
            for idx, mas in enumerate(market_mas_list):
                market_mas[market][f"ema{idx}"] = mas[market]
                ma_list.append(mas[market])
        return market_mas


class SuperWinningSession_MACD_Hedge(AbstractHedgingStrategy):
    def __init__(self, ):
        super(SuperWinningSession_MACD_Hedge, self).__init__()

    def load_tai_params(self, params):
        self.tai_macd1_tf = params['tai_macd1_tf']
        self.tai_macd2_tf = params['tai_macd2_tf']
        self.tai_macd3_tf = params['tai_macd3_tf']
        self.tai_macd4_tf = params['tai_macd4_tf']

    def __isBuySignal__(self, mkt_buy_tai, tmgr, market, tick, time_dt, tf_hour) :
        price = tick.close
        macd1 = mkt_buy_tai[market]['macd0']
        macd2 = mkt_buy_tai[market]['macd1']
        macd3 = mkt_buy_tai[market]['macd2']
        macd4 = mkt_buy_tai[market]['macd3']

        market_tai_str = f"[{[macd1], [macd2], [macd3], [macd4]}]"
        buy_log = f"{market_tai_str}"

        return (macd1[0] > macd1[1]) and (macd2[0] > macd2[1]) and \
                (macd3[0] > macd3[1]) and (macd4[0] > macd4[1]), buy_log

    def __isSellSignal__(self, mkt_sell_tai, tmgr, market, tick, time_dt, tf_hour) :
        price = tick.close
        macd1 = mkt_sell_tai[market]['macd0']
        macd2 = mkt_sell_tai[market]['macd1']
        macd3 = mkt_sell_tai[market]['macd2']
        macd4 = mkt_sell_tai[market]['macd3']

        market_tai_str = f"[{[macd1], [macd2], [macd3], [macd4]}]"
        sell_log = f"{market_tai_str}"

        return (macd1[0] < macd1[1]) or (macd2[0] < macd2[1]) or \
                (macd3[0] < macd3[1]) or (macd4[0] < macd4[1]), sell_log

    def extract_tai(self, tmgr, timeframe_hour):
        tai_macd_list = [self.tai_macd1_tf, self.tai_macd2_tf, self.tai_macd3_tf, self.tai_macd4_tf]

        market_macd_list = []
        for tai_macd in tai_macd_list:
            ma_key = f'DAYS_{timeframe_hour}'  # it should be matched with that of euote dispatcher
            cdl_type = CandleType[ma_key]
            tai_macd[2] = cdl_type
            market_ma = get_nary_tai(tmgr, tai_macd)
            market_macd_list.append(market_ma)

        quote = tmgr.get_quote()
        market_ticks = quote.get_market_ticks(tmgr.ex_type)

        market_macds = {}
        for market in market_ticks:
            market_macds[market] = {}
            for idx, macds in enumerate(market_macd_list):
                market_macds[market][f"macd{idx}"] = macds[market]

        return market_macds


class SuperWinningSessionPoweredByMACrossOver_Hdge(SuperWinningSession_Hedge):
    def __init__(self, ):
        super(SuperWinningSessionPoweredByMACrossOver_Hdge, self).__init__()

    def set_params(self, am, report_storage, markets, params):
        super(SuperWinningSessionPoweredByMACrossOver_Hdge, self).set_params(am, report_storage, markets, params)
        self.arrow_tai_ma  = params['arrow_tai_ma']
        self.target_tai_ma = params['target_tai_ma']

    def __isBuySignal__(self, mkt_buy_tais, tmgr, market, tick, time_dt, tf_hour) :
        price = tick.close
        super_winning_session_buy_signal, buy_log = super(SuperWinningSessionPoweredByMACrossOver_Hdge, self).\
            __isBuySignal__(mkt_buy_tais, tmgr, market, tick, time_dt, tf_hour)
        # self.mass[1] = MA(5), self.mass[3] = MA(20)
        ma_cross_over_buy_signal = False
        ma1 = mkt_buy_tais[market]['ma1']
        ma3 = mkt_buy_tais[market]['ma3']
        if ma1 >= ma3:
            ma_cross_over_buy_signal = True

        buy_log += f" ma1({ma1}) >= ma3({ma3})"
        return super_winning_session_buy_signal and ma_cross_over_buy_signal, buy_log

    def __isSellSignal__(self, mkt_sell_tais, tmgr, market, tick, time_dt, tf_hour) :
        price = tick.close
        super_winning_session_sell_signal, sell_log = super(SuperWinningSessionPoweredByMACrossOver_Hdge, self). \
            __isSellSignal__(mkt_sell_tais, tmgr, market, tick, time_dt, tf_hour)

        # self.mass[1] = MA(5), self.mass[3] = MA(20)
        ma_cross_over_sell_signal = False
        ma1 = mkt_sell_tais[market]['ma1']
        ma3 = mkt_sell_tais[market]['ma3']
        if ma1  < ma3:
            ma_cross_over_sell_signal = True
        sell_log += f" ma1({ma1}) < ma3({ma3})"
        return super_winning_session_sell_signal or ma_cross_over_sell_signal, sell_log

class SuperWinningSessionForBitHolders_Hdge(SuperWinningSession_Hedge):
    def __init__(self, ):
        super(SuperWinningSessionForBitHolders_Hdge, self).__init__()

    def __isBuySignal__(self, mkt_buy_tais, tmgr, market, tick, time_dt, tf_hour) :
        price = tick.close
        ma1 = mkt_buy_tais[market]['ma0']
        ma2 = mkt_buy_tais[market]['ma1']
        ma3 = mkt_buy_tais[market]['ma2']
        ma4 = mkt_buy_tais[market]['ma3']

        buy_signal = False
        if (price >= ma1) or (price >= ma2) or (price >= ma3) or (price >= ma4):
            buy_signal = True

        buy_log = f"(price({price}) >= ma1({ma1})) or ({price} >= ma2({ma2})) or ({price} >= ma3({ma3})) or ({price} >= ma4({ma4}))"
        return buy_signal, buy_log

    def __isSellSignal__(self, mkt_sell_tais, tmgr, market, tick, time_dt, tf_hour) :
        price = tick.close
        ma1 = mkt_sell_tais[market]['ma0']
        ma2 = mkt_sell_tais[market]['ma1']
        ma3 = mkt_sell_tais[market]['ma2']
        ma4 = mkt_sell_tais[market]['ma3']

        sell_signal = False
        if (price < ma1) and (price < ma2) and (price < ma3) and (price < ma4):
            sell_signal = True

        sell_log = f"(price({price}) < ma1({ma1})) and ({price} < ma2({ma2})) and ({price} < ma3({ma3})) and ({price} < ma4({ma4}))"
        return sell_signal, sell_log


class SuperWinningSession_TAI_Hedge(SuperWinningSession_Hedge):
    def __init__(self, ):
        super(SuperWinningSession_TAI_Hedge, self).__init__()

    def load_tai_params(self, params):
        super(SuperWinningSession_TAI_Hedge, self).load_tai_params(params)
        self.tai_macd_tf = params['tai_macd_tf'] if 'tai_macd_tf' in params else None
        self.tai_cci_tf = params['tai_ccl_tf'] if 'tai_ccl_tf' in params else None
        self.tai_pdi_tf = params['tai_pdi_tf'] if 'tai_pdi_tf' in params else None
        self.tai_mdi_tf = params['tai_mdi_tf'] if 'tai_mdi_tf' in params else None
        self.tai_bb_close_tf = params['tai_bb_close_tf'] if 'tai_bb_close_tf' in params else None
        self.tai_psar_tf = params['tai_psar_tf'] if 'tai_psar_tf' in params else None
        self.tai_rsi_tf = params['tai_rsi_tf'] if 'tai_rsi_tf' in params else None
        self.tai_vol_tf = params['tai_vol_tf'] if 'tai_vol_tf' in params else None
        self.tai_vol_ma_tf = params['tai_vol_ma_tf'] if 'tai_vol_ma_tf' in params else None


    def __isBuySignal__(self, mkt_buy_tais, tmgr, market, tick, time_dt, tf_hour) :
        price = tick.close
        super_winning_session_buy_signal, buy_log = super(SuperWinningSession_TAI_Hedge, self).\
            __isBuySignal__(mkt_buy_tais, tmgr, market, tick, time_dt, tf_hour)

        desc = f"\r\n *[sws] = {super_winning_session_buy_signal} :: {buy_log}"
        buy_log = ""
        buy_log += desc + ",  "
        # log.info(desc)

        #################################################################
        if self.tai_macd_tf is None:
            macd_buy_signal = True
        else:
            macd = mkt_buy_tais[market]['macd']  # [0]macd, [1] macd_signal, [2] macd_hist
            macd_buy_signal = False
            if macd[0] > macd[1] :
                macd_buy_signal = True
            desc = f"\r\n *[macd] = {macd_buy_signal} :: macd({macd[0]}) > macd_sig({macd[1]})"
            # log.info(desc)
            buy_log += desc + ",  "
        #################################################################
        if self.tai_cci_tf is None:
            cci_buy_signal = True
        else:
            cci = mkt_buy_tais[market]['cci']
            cci_buy_signal = False
            if cci > 0 :
                cci_buy_signal = True
            desc = f"\r\n *[cci] = {cci_buy_signal} :: cci({cci}) > 0"
            # log.info(desc)
            buy_log += desc + ",  "
        #################################################################
        if (self.tai_pdi_tf is None) or (self.tai_mdi_tf is None):
            di_signal = True
        else:
            pdi = mkt_buy_tais[market]['pdi']
            mdi = mkt_buy_tais[market]['mdi']
            di_signal = False
            if pdi > mdi :
                di_signal = True
            desc = f"\r\n *[di] = {di_signal} :: pdi({pdi}) > mdi({mdi})"
            # log.info(desc)
            buy_log += desc + ",  "
        #################################################################
        if self.tai_bb_close_tf is None:
            bband_buy_signal = True
        else:
            bbands = mkt_buy_tais[market]['bband']  # [0] upper, [1] middle, [2] lower
            bband_buy_signal = False
            if price > bbands[2] :
                bband_buy_signal = True
            desc = f"\r\n *[bband] = {bband_buy_signal} :: price({price}) > bb_low({bbands[2]})"
            # log.info(desc)
            buy_log += desc + ",  "
        #################################################################
        if self.tai_psar_tf is None:
            psar_buy_signal = True
        else:
            psar = mkt_buy_tais[market]['psar']
            psar_buy_signal = False
            if price > psar :
                psar_buy_signal = True
            desc = f"\r\n *[psar] = {psar_buy_signal} :: price({price}) > psar({psar})"
            # log.info(desc)
            buy_log += desc + ",  "
        #################################################################
        if self.tai_rsi_tf is None:
            rsi_buy_signal = True
        else:
            rsi = mkt_buy_tais[market]['rsi']
            rsi_buy_signal = False

            if rsi > 30 :
                rsi_buy_signal = True
            desc = f"\r\n *[rsi] = {rsi_buy_signal} :: rsi({rsi}) > 30"
            # log.info(desc)
            buy_log += desc + ",  "
        #################################################################
        if (self.tai_vol_tf is None) or (self.tai_vol_ma_tf is None):
            vol_ma_buy_signal = True
        else:
            vol = mkt_buy_tais[market]['vol']
            vol_ma = self.mkt_buy_tais[market]['vol_ma']
            vol_ma_buy_signal = False

            if vol > vol_ma :
                vol_ma_buy_signal = True
            desc = f"\r\n *[vol_ma] = {vol_ma_buy_signal} :: vol({vol}) > vol_ma({vol_ma})"
            # log.info(desc)
            buy_log += desc + "  "

        return super_winning_session_buy_signal and macd_buy_signal and cci_buy_signal and \
               di_signal and bband_buy_signal and psar_buy_signal and rsi_buy_signal and vol_ma_buy_signal, buy_log


    def __isSellSignal__(self, mkt_sell_tais, tmgr, market, tick, time_dt, tf_hour) :
        price = tick.close
        super_winning_session_sell_signal, sell_log = super(SuperWinningSession_TAI_Hedge, self). \
            __isSellSignal__(mkt_sell_tais, tmgr, market, tick, time_dt, tf_hour)

        desc = f"\r\n *[sws] = {super_winning_session_sell_signal} :: {sell_log}"
        sell_log = ""
        sell_log += desc + ",  "

        #################################################################
        if self.tai_macd_tf is None:
            macd_sell_signal = False
        else:
            macd = mkt_sell_tais[market]['macd']  # [0]macd, [1] macd_signal, [2] macd_hist
            macd_sell_signal = False
            if macd[0] < macd[1] :
                macd_sell_signal = True
            desc = f"\r\n *[macd] = {macd_sell_signal} :: macd({macd[0]}) < macd_sig({macd[1]})"
            # log.info(desc)
            sell_log += desc + ",  "
        #################################################################
        if self.tai_cci_tf is None:
            cci_sell_signal = False
        else:
            cci = mkt_sell_tais[market]['cci']
            cci_sell_signal = False
            if cci < 0 :
                cci_sell_signal = True
            desc = f"\r\n *[cci] = {cci_sell_signal} :: cci({cci}) < 0"
            # log.info(desc)
            sell_log += desc + ",  "
        #################################################################
        if (self.tai_pdi_tf is None) or (self.tai_mdi_tf is None):
            di_sell_signal = False
        else:
            pdi = mkt_sell_tais[market]['pdi']
            mdi = mkt_sell_tais[market]['mdi']
            di_sell_signal = False
            if pdi < mdi :
                di_sell_signal = True
            desc = f"\r\n *[di] = {di_sell_signal} :: pdi({pdi}) < mdi({mdi})"
            # log.info(desc)
            sell_log += desc + ",  "
        #################################################################
        if self.tai_bb_close_tf is None:
            bband_sell_signal = False
        else:
            bbands = mkt_sell_tais[market]['bband']  # [0] upper, [1] middle, [2] lower
            bband_sell_signal = False
            if price > bbands[0] :
                bband_sell_signal = True
            desc = f"\r\n *[bband] = {bband_sell_signal} :: price({price}) > bb_upper({bbands[0]})"
            # log.info(desc)
            sell_log += desc + ",  "
        #################################################################
        if self.tai_psar_tf is None:
            psar_sell_signal = False
        else:
            psar = mkt_sell_tais[market]['psar']
            psar_sell_signal = False
            if price < psar :
                psar_sell_signal = True
            desc = f"\r\n *[psar] = {psar_sell_signal} :: price({price}) < psar({psar})"
            # log.info(desc)
            sell_log += desc + ",  "
        #################################################################
        if self.tai_rsi_tf is None:
            rsi_sell_signal = False
        else:
            rsi = mkt_sell_tais[market]['rsi']
            rsi_sell_signal = False
            if rsi > 90 :
                rsi_sell_signal = True
            desc = f"\r\n *[rsi] = {rsi_sell_signal} :: rsi({rsi}) > 70"
            # log.info(desc)
            sell_log += desc + ",  "
        #################################################################
        if (self.tai_vol_tf is None) or (self.tai_vol_ma_tf is None):
            vol_ma_sell_signal = False
        else:
            vol = mkt_sell_tais[market]['vol']
            vol_ma = mkt_sell_tais[market]['vol_ma']
            vol_ma_sell_signal = False
            if vol < vol_ma :
                vol_ma_sell_signal = True

            desc = f"\r\n *[vol_ma] = {vol_ma_sell_signal} :: vol({vol}) < vol_ma({vol_ma})"
            # log.info(desc)
            sell_log += desc + "  "

        return super_winning_session_sell_signal or macd_sell_signal or cci_sell_signal or di_sell_signal \
               or bband_sell_signal or psar_sell_signal or rsi_sell_signal or vol_ma_sell_signal, sell_log

    def extract_tai(self, tmgr, timeframe_hour):
        market_tai = super(SuperWinningSession_TAI_Hedge, self).extract_tai(tmgr, timeframe_hour)

        quote = tmgr.get_quote()
        market_ticks = quote.get_market_ticks(tmgr.ex_type)

        ma_key = f'DAYS_{timeframe_hour}'  # it should be matched with that of euote dispatcher
        if self.tai_macd_tf is not None:
            self.tai_macd_tf[2] = CandleType[ma_key]
            market_macd = get_nary_tai(tmgr, self.tai_macd_tf)

            for market in market_ticks:
                market_tai[market]['macd'] = market_macd[market]

        if self.tai_cci_tf is not None:
            self.tai_cci_tf[2] = CandleType[ma_key]
            market_cci = get_unary_tai(tmgr, self.tai_cci_tf)
            for market in market_ticks:
                market_tai[market]['cci'] = market_cci[market]

        if self.tai_pdi_tf is not None:
            self.tai_pdi_tf[2] = CandleType[ma_key]
            market_pdi = get_unary_tai(tmgr, self.tai_pdi_tf)
            for market in market_ticks:
                market_tai[market]['pdi'] = market_pdi[market]

        if self.tai_mdi_tf is not None :
            self.tai_mdi_tf[2] = CandleType[ma_key]
            market_mdi = get_unary_tai(tmgr, self.tai_mdi_tf)
            for market in market_ticks:
                market_tai[market]['mdi'] = market_mdi[market]

        if self.tai_bb_close_tf is not None :
            self.tai_bb_close_tf[2] = CandleType[ma_key]
            bbands = get_nary_tai(tmgr, self.tai_bb_close_tf)
            for market in market_ticks:
                market_tai[market]['bband'] = bbands[market]

        if self.tai_psar_tf is not None:
            self.tai_psar_tf[2] = CandleType[ma_key]
            psar = get_unary_tai(tmgr, self.tai_psar_tf)
            for market in market_ticks:
                market_tai[market]['psar'] = psar[market]

        if self.tai_rsi_tf is not None :
            self.tai_rsi_tf[2] = CandleType[ma_key]
            rsi = get_unary_tai(tmgr, self.tai_rsi_tf)
            for market in market_ticks:
                market_tai[market]['rsi'] = rsi[market]

        if self.tai_vol_tf is not None :
            self.tai_vol_tf[2] = CandleType[ma_key]
            vol = get_unary_tai(tmgr, self.tai_vol_tf)
            for market in market_ticks:
                market_tai[market]['vol'] = vol[market]

        if self.tai_vol_ma_tf is not None :
            self.tai_vol_ma_tf[2] = CandleType[ma_key]
            vol_ma = get_unary_tai(tmgr, self.tai_vol_ma_tf)
            for market in market_ticks:
                market_tai[market]['vol_ma'] = vol_ma[market]

        return market_tai


class SuperWinningSessionForBitHolders_TAI_Hedge(SuperWinningSession_TAI_Hedge):
    def __init__(self, ):
        super(SuperWinningSessionForBitHolders_TAI_Hedge, self).__init__()

    def __isBuySignal__(self, mkt_buy_tais, tmgr, market, tick, time_dt, tf_hour):
        price = tick.close
        #################################################################
        ma1 = mkt_buy_tais[market]['ma0']
        ma2 = mkt_buy_tais[market]['ma1']
        ma3 = mkt_buy_tais[market]['ma2']
        ma4 = mkt_buy_tais[market]['ma3']

        ma_buy_signal = False
        buy_log = ""
        if (price >= ma1) or (price >= ma2) or (price >= ma3) or (price >= ma4) :
            ma_buy_signal = True
            buy_log += f"(price({price}) >= ma1({ma1})) or ({price} >= ma2({ma2})) or ({price} >= ma3({ma3})) or ({price} >= ma4({ma4})), "
        ##################################################################
        if self.tai_macd_tf is None:
            macd_buy_signal = False
        else:
            macd = mkt_buy_tais[market]['macd']  # [0]macd, [1] macd_signal, [2] macd_hist
            macd_buy_signal = False
            if macd[0] > macd[1] :
                macd_buy_signal = True
            desc = f"{market=}/{macd_buy_signal=} :: macd({macd[0]}) > macd_sig({macd[1]})"
            log.info(desc)
            buy_log += desc + ",  "
        #################################################################
        if self.tai_cci_tf is None:
            cci_buy_signal = False
        else:
            cci = mkt_buy_tais[market]['cci']
            cci_buy_signal = False
            if cci >= self.tai_cci_tf[5]:
                cci_buy_signal = True
            desc = f"{market=}/{cci_buy_signal=} -> cci({cci}) > {self.tai_cci_tf[5]}"
            log.info(desc)
            buy_log += desc + ",  "
        #################################################################
        if (self.tai_pdi_tf is None) or (self.tai_mdi_tf is None):
            di_signal = False
        else:
            pdi = mkt_buy_tais[market]['pdi']
            mdi = mkt_buy_tais[market]['mdi']
            di_signal = False
            if pdi > mdi :
                di_signal = True
            desc = f"{market=}/{di_signal=} :: pdi({pdi}) > mdi({mdi})"
            log.info(desc)
            buy_log += desc + ",  "
        #################################################################
        if self.tai_bb_close_tf is None:
            bband_buy_signal = False
        else:
            bbands = mkt_buy_tais[market]['bband']  # [0] upper, [1] middle, [2] lower
            bband_buy_signal = False

            if price > bbands[2] :
                bband_buy_signal = True
            desc = f"{market=}/{bband_buy_signal=} :: price({price}) > bb_low({bbands[2]})"
            log.info(desc)
            buy_log += desc + ",  "
        #################################################################
        if self.tai_psar_tf is None:
            psar_buy_signal = False
        else:
            psar = mkt_buy_tais[market]['psar']
            psar_buy_signal = False

            if price > psar :
                psar_buy_signal = True
            desc = f"{market=}/{psar_buy_signal=} :: price({price}) > psar({psar})"
            log.info(desc)
            buy_log += desc + ",  "
        #################################################################
        if self.tai_rsi_tf is None:
            rsi_buy_signal = False
        else:
            rsi = mkt_buy_tais[market]['rsi']
            rsi_buy_signal = False

            if rsi > 30 :
                rsi_buy_signal = True
            desc = f"{market=}/{rsi_buy_signal=} :: rsi({rsi}) > 30"
            log.info(desc)
            buy_log += desc + ",  "
        #################################################################
        if (self.tai_vol_tf is None) or (self.tai_vol_ma_tf is None):
            vol_ma_buy_signal = False
        else:
            vol = mkt_buy_tais[market]['vol']
            vol_ma = mkt_buy_tais[market]['vol_ma']
            vol_ma_buy_signal = False

            if vol > vol_ma :
                vol_ma_buy_signal = True
            desc = f"{market=}/{vol_ma_buy_signal=} :: vol({vol}) > vol_ma({vol_ma})"
            log.info(desc)
            buy_log += desc + ",  "

        # return ma_buy_signal or macd_buy_signal or cci_buy_signal or \
        #        di_signal or bband_buy_signal or psar_buy_signal or rsi_buy_signal or vol_ma_buy_signal, buy_log
        return cci_buy_signal, buy_log

    def __isSellSignal__(self, mkt_sell_tais, tmgr, market, tick, time_dt, tf_hour):
        price = tick.close
        tai_list = self.mkt_sell_tais[market]

        ma1 = mkt_sell_tais[market]['ma0']
        ma2 = mkt_sell_tais[market]['ma1']
        ma3 = mkt_sell_tais[market]['ma2']
        ma4 = mkt_sell_tais[market]['ma3']
        ma_sell_signal = False

        sell_log = ""
        if (price < ma1) and (price < ma2) and (price < ma3) and (price < ma4) :
            ma_sell_signal = True
            sell_log += f"(price({price}) < ma1({ma1})) and ({price} < ma2({ma2})) and ({price} < ma3({ma3})) and ({price} < ma4({ma4})),  "
        #################################################################
        if self.tai_macd_tf is None:
            macd_sell_signal = True
        else:
            macd = mkt_sell_tais[market]['macd']  # [0]macd, [1] macd_signal, [2] macd_hist
            macd_sell_signal = False
            if macd[0] < macd[1] :
                macd_sell_signal = True
            desc = f"{market=}/{macd_sell_signal=} :: macd({macd[0]}) < macd_sig({macd[1]})"
            log.info(desc)
            sell_log += desc + ",  "
        #################################################################
        if self.tai_cci_tf is None:
            cci_sell_signal = True
        else:
            cci = mkt_sell_tais[market]['cci']
            cci_sell_signal = False
            if cci < self.tai_cci_tf[5]:
                cci_sell_signal = True
            desc = f"{market=}/{cci_sell_signal=} :: cci({cci}) < {self.tai_cci_tf[5]}"
            log.info(desc)
            sell_log += desc + ",  "
        #################################################################
        if (self.tai_pdi_tf is None) or (self.tai_mdi_tf is None):
            di_sell_signal = True
        else:
            pdi = mkt_sell_tais[market]['pdi']
            mdi = mkt_sell_tais[market]['mdi']
            di_sell_signal = False
            if pdi < mdi :
                di_sell_signal = True
            desc = f"{market=}/{di_sell_signal=} :: pdi({pdi}) < mdi({mdi})"
            log.info(desc)
            sell_log += desc + ",  "
        #################################################################
        if self.tai_bb_close_tf is None:
            bband_sell_signal = True
        else:
            bbands = mkt_sell_tais[market]['bband']  # [0] upper, [1] middle, [2] lower
            bband_sell_signal = False
            if price > bbands[0] :
                bband_sell_signal = True
            desc = f"{market=}/{bband_sell_signal=} :: price({price}) > bb_upper({bbands[0]})"
            log.info(desc)
            sell_log += desc + ",  "
        #################################################################
        if self.tai_psar_tf is None:
            psar_sell_signal = True
        else:
            psar = mkt_sell_tais[market]['psar']
            psar_sell_signal = False
            if price < psar :
                psar_sell_signal = True
            desc = f"{market=}/{psar_sell_signal=} :: price({price}) < psar({psar})"
            log.info(desc)
            sell_log += desc + ",  "
        #################################################################
        if self.tai_rsi_tf is None:
            rsi_sell_signal = True
        else:
            rsi = mkt_sell_tais[market]['rsi']
            rsi_sell_signal = False
            if rsi > 90 :
                rsi_sell_signal = True
            desc = f"{market=}/{rsi_sell_signal=} :: rsi({rsi}) > 70"
            log.info(desc)
            sell_log += desc + ",  "
        #################################################################
        if (self.tai_vol_tf is None) or (self.tai_vol_ma_tf is None):
            vol_ma_sell_signal = True
        else:
            vol = mkt_sell_tais[market]['vol']
            vol_ma = mkt_sell_tais[market]['vol_ma']
            vol_ma_sell_signal = False
            if vol < vol_ma :
                vol_ma_sell_signal = True
            desc = f"{market=}/{vol_ma_sell_signal=} :: vol({vol}) < vol_ma({vol_ma})"
            log.info(desc)
            sell_log += desc + ",  "
        #################################################################
        # return ma_sell_signal and macd_sell_signal and cci_sell_signal and di_sell_signal \
        #        and bband_sell_signal and psar_sell_signal and rsi_sell_signal and vol_ma_sell_signal, sell_log
        return cci_sell_signal, sell_log

