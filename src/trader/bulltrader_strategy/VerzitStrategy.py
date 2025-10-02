from abc import abstractmethod, ABCMeta
from copy import deepcopy

from bt4.Constants import CandleType
from bt4.utils.mylog import init_log
from bt4.utils.tai_utils import get_unary_tai, get_nary_tai
from bt4.strategy.Strategy import AbstractNettingStrategy

import pandas as pd
from enum import IntEnum

from bulltrader_strategy.SuperWinningSessionStrategy import signal_buy_pos, signal_sell_pos, SuperWinningSession_4H

log = init_log()

class Signal(IntEnum):
    BUY = 1
    SELL = -1
    HOLD = 0

class VerzitStrategy(AbstractNettingStrategy):
    def __init__(self):
        super(VerzitStrategy, self).__init__()
        self.__sig__ = "vzt"

    def set_params(self, am, report_storage, markets, params):
        super(VerzitStrategy, self).set_params(am, report_storage, markets, params)
        self.sig_gen = SignalGenerator()

    def load_tai_params(self, params) :
        self.tr_idx_threshold = params['tr_idx_threshold']
        self.tai_candles = params['tai_candles']
        self.tai_ma_periods = params['tai_ma_periods']
        self.tai_ma = params['tai_ma']
        self.tai_bb_close = params['tai_bb_close']
        self.tai_psar = params['tai_psar']
        self.tai_cci = params['tai_cci']
        self.tai_macd = params['tai_macd']

    def __is_rebalance_time__(self, time_dt) :
        return True if time_dt.hour == 8 and time_dt.minute == 59 else False

    def __isBuySignal__(self, tmgr, market, price, time_dt, market_tai_values):
        sig_book_df = self.mkt_tais[f"{market}_{self.__sig__}"]
        tr_idx = sig_book_df["tr_idx"][-1]

        buy_signal = False
        if tr_idx > self.tr_idx_threshold:
            buy_signal = True
        return buy_signal, f" tr_idx({tr_idx:.2f}) > threshold({self.tr_idx_threshold})"

    def __isSellSignal__(self, tmgr, market, price, time_dt, market_tai_values):
        sig_book_df = self.mkt_tais[f"{market}_{self.__sig__}"]
        tr_idx = sig_book_df["tr_idx"][-1]

        sell_signal = False
        if tr_idx < self.tr_idx_threshold:
            sell_signal = True

        return sell_signal,  f" tr_idx({tr_idx:.2f}) < threshold({self.tr_idx_threshold})"

    def extract_tai(self, tmgr):
        tai_ma_template = deepcopy(self.tai_ma)
        tai_bb_template = deepcopy(self.tai_bb_close)
        tai_psar_template = deepcopy(self.tai_psar)
        tai_cci_template = deepcopy(self.tai_cci)
        tai_macd_template = deepcopy(self.tai_macd)

        quote = tmgr.get_quote()
        markets = quote.get_markets(self.ex_type)
        market_sig_books = {}

        cdl_tai_cache = {}
        for market in markets:
            market_sig_book_df = pd.DataFrame(data={}, index=self.sig_gen.idx)

            for cdl in self.tai_candles:
                if cdl not in cdl_tai_cache:
                    cdl_tai_cache[cdl] = {}

                col_name = cdl.name
                tai_list = {}
                for ma_period in self.tai_ma_periods:
                    tai_ma_template[1] = [ma_period]
                    tai_ma_template[2] = cdl
                    tai_key = f"ma{ma_period}"
                    if tai_key not in cdl_tai_cache:
                        cdl_tai_cache[cdl][tai_key] = get_unary_tai(tmgr, tai_ma_template)
                    tai_list[tai_key] = cdl_tai_cache[cdl][tai_key][market]

                tai_bb_template[2] = tai_psar_template[2] = tai_cci_template[2] = tai_macd_template[2] = cdl
                if "bb" not in cdl_tai_cache:
                    cdl_tai_cache[cdl]["bb"] = get_nary_tai(tmgr, tai_bb_template)
                tai_list["bb"] = cdl_tai_cache[cdl]["bb"][market]

                if "psar" not in cdl_tai_cache :
                    cdl_tai_cache[cdl]["psar"] = get_unary_tai(tmgr, tai_psar_template)
                tai_list["psar"] = cdl_tai_cache[cdl]["psar"][market]

                if "cci" not in cdl_tai_cache :
                    cdl_tai_cache[cdl]["cci"] = get_unary_tai(tmgr, tai_cci_template)
                tai_list["cci"] = cdl_tai_cache[cdl]["cci"][market]

                if "macd" not in cdl_tai_cache :
                    cdl_tai_cache[cdl]["macd"] = get_nary_tai(tmgr, tai_macd_template)
                tai_list["macd"] = cdl_tai_cache[cdl]["macd"][market]

                market_tick = tmgr.get_quote().get_market_ticks(self.ex_type)[market]
                sig_ser = self.sig_gen.generate_signal(market_tick.close, tai_list)
                market_sig_book_df[col_name] = sig_ser

            market_sig_book_df['tr_idx'] = market_sig_book_df.sum(axis = 1) / len(market_sig_book_df.columns)
            market_sig_books[f"{market}_{self.__sig__}"] = market_sig_book_df
        return market_sig_books


class Verzit_SWS_Strategy(VerzitStrategy):

    def __init__(self):
        super(Verzit_SWS_Strategy, self).__init__()
        self.sws = SuperWinningSession_4H()
        self.sws.trading_hour = 1

    def set_params(self, am, report_storage, markets, params):
        super(Verzit_SWS_Strategy, self).set_params(am, report_storage, markets, params)
        self.sws.set_params(am, report_storage, markets, params)

    def load_tai_params(self, params):
        super(Verzit_SWS_Strategy, self).load_tai_params(params)
        self.sws.load_tai_params(params)

    def __isBuySignal__(self, tmgr, market, price, time_dt, market_tai_values):
        sws_buy_signal, desc1 = self.sws.__isBuySignal__(tmgr, market, price, time_dt, market_tai_values)
        vrz_buy_signal, desc2 = super(Verzit_SWS_Strategy, self).__isBuySignal__(tmgr, market, price, time_dt, market_tai_values)

        return sws_buy_signal and vrz_buy_signal, desc1 + "," + desc2

    def __isSellSignal__(self, tmgr, market, price, time_dt, market_tai_values):
        sws_sell_signal, desc1 = self.sws.__isSellSignal__(tmgr, market, price, time_dt, market_tai_values)
        vrz_sell_signal, desc2 = super(Verzit_SWS_Strategy, self).__isSellSignal__(tmgr, market, price, time_dt, market_tai_values)

        return sws_sell_signal and vrz_sell_signal, desc1 + "," + desc2

    def extract_tai(self, tmgr):
        market_sig_books = super(Verzit_SWS_Strategy, self).extract_tai(tmgr)
        market_sws_sigs = self.sws.extract_tai(tmgr)
        market_sig_books.update(market_sws_sigs)

        return market_sig_books

# class Verzit_SWS_Strategy(VerzitStrategy):
#
#     def __init__(self):
#         super(Verzit_SWS_Strategy, self).__init__()
#
#     def load_tai_params(self, params) :
#         super(Verzit_SWS_Strategy, self).load_tai_params(params)
#         self.tai_ma1 = params['tai_ma1']
#         self.tai_ma2 = params['tai_ma2']
#         self.tai_ma3 = params['tai_ma3']
#         self.tai_ma4 = params['tai_ma4']
#
#
#     def __isBuySignal__(self, tmgr, market, price, time_dt):
#         mas_list = self.market_tai_values[f"{market}_mas"]
#
#         sws_buy_signal = signal_buy_pos(mas_list, price)
#         desc = f"BUY:{sws_buy_signal=},"
#         if sws_buy_signal:
#             tr_buy_signal, desc = super(Verzit_SWS_Strategy, self).__isBuySignal__(tmgr, market, price, time_dt)
#             if tr_buy_signal:
#                 desc += desc
#                 return True, desc
#
#         return False, desc
#
#     def __isSellSignal__(self, tmgr, market, price, time_dt):
#         mas_list = self.market_tai_values[f"{market}_mas"]
#         sws_sell_signal = signal_sell_pos(mas_list, price)
#         desc = f"SELL:{sws_sell_signal=},"
#
#         if sws_sell_signal:
#             tr_sell_signal, desc = super(Verzit_SWS_Strategy, self).__isSellSignal__(tmgr, market, price, time_dt)
#             if tr_sell_signal :
#                 desc += desc
#                 return True, desc
#
#         return False, desc
#
#     def extract_tai(self, tmgr):
#         market_sig_books = super(Verzit_SWS_Strategy, self).extract_tai(tmgr)
#
#         tai_ma_list = [self.tai_ma1, self.tai_ma2, self.tai_ma3, self.tai_ma4]
#         market_mas_list = []
#         for tai_ma in tai_ma_list :
#             market_ma = get_unary_tai(tmgr, tai_ma)
#             market_mas_list.append(market_ma)
#
#         quote = tmgr.get_quote()
#         market_ticks = quote.get_market_ticks(tmgr.ex_type)
#
#         market_mas = {}
#         for market in market_ticks :
#             market_mas[market] = {}
#             ma_list = []
#             for idx, mas in enumerate(market_mas_list) :
#                 market_mas[market][f"ma{idx}"] = mas[market]
#                 ma_list.append(mas[market])
#
#             market_sig_books[f"{market}_mas"] = ma_list
#         return market_sig_books


class VerzitStrategy2(VerzitStrategy):
    def __init__(self):
        super(VerzitStrategy2, self).__init__()

    def load_tai_params(self, params) :
        super(VerzitStrategy2, self).load_tai_params(params)
        self.tr_idx_lt_threshold = params['tr_idx_lt_threshold']
        self.tr_idx_st_threshold = params['tr_idx_st_threshold']

    def __isBuySignal__(self, tmgr, market, price, time_dt):
        sig_book_df = self.mkt_tais[market]

        lt_tr_idx_cdls = [CandleType.HOUR, CandleType.HOUR4, CandleType.DAYS]
        lt_tr_idx_cols = [x.name for x in lt_tr_idx_cdls]
        lt_tr_idx = self.__compute_term_tr_idx__(sig_book_df, lt_tr_idx_cols)
        tr_signal = False

        desc = ""
        if lt_tr_idx > self.tr_idx_lt_threshold:
            st_tr_idx_cdls = list(set(self.tai_candles) - set(lt_tr_idx_cdls))
            st_tr_idx_cols = [x.name for x in st_tr_idx_cdls]
            if len(st_tr_idx_cols) > 0:
                st_tr_idx = self.__compute_term_tr_idx__(sig_book_df, st_tr_idx_cols)

                if st_tr_idx > self.tr_idx_st_threshold:
                    desc += f" long_tr_idx({lt_tr_idx:.2f}) > threshold({self.tr_idx_lt_threshold}) and short_tr_idx({st_tr_idx:.2f}) > threshold({self.tr_idx_st_threshold}) "
                    tr_signal = True
                else:
                    desc += f" long_tr_idx({lt_tr_idx:.2f}) > threshold({self.tr_idx_lt_threshold}) satisfied, " \
                            f"but short_tr_idx({st_tr_idx:.2f}) > threshold({self.tr_idx_st_threshold}) is not satisfied for buying."
            else:
                desc += "ERROR: short term indexes are empty!"
                log.error(desc)
                return False, desc
        else:
            desc += f" long_tr_idx({lt_tr_idx:.2f}) > threshold({self.tr_idx_lt_threshold}) is not satisfied for buying."

        return tr_signal, desc

    def __compute_term_tr_idx__(self, sig_book_df, tr_idx_cols):
        lt_sig_book_df = sig_book_df[tr_idx_cols].copy(deep=True)
        lt_sig_book_df["tr_idx"] = lt_sig_book_df.sum(axis = 1) / len(lt_sig_book_df.columns)
        return lt_sig_book_df["tr_idx"].mean()

    def __isSellSignal__(self, tmgr, market, price, time_dt):
        sig_book_df = self.mkt_tais[market]

        lt_tr_idx_cdls = [CandleType.HOUR, CandleType.HOUR4, CandleType.DAYS]
        lt_tr_idx_cols = [x.name for x in lt_tr_idx_cdls]
        lt_tr_idx = self.__compute_term_tr_idx__(sig_book_df, lt_tr_idx_cols)
        sell_signal = False

        desc = ""
        if lt_tr_idx < self.tr_idx_lt_threshold :
            sell_signal = True
            desc += f" long_tr_idx({lt_tr_idx:.2f}) < threshold({self.tr_idx_lt_threshold}), for selling. "
        else :
            st_tr_idx_cdls = list(set(self.tai_candles) - set(lt_tr_idx_cols))
            st_tr_idx_cols = [x.name for x in st_tr_idx_cdls]
            if len(st_tr_idx_cols) > 0:
                st_tr_idx = self.__compute_term_tr_idx__(sig_book_df, st_tr_idx_cols)

                if st_tr_idx < self.tr_idx_st_threshold :
                    desc += f" long_tr_idx({lt_tr_idx:.2f}) < threshold({self.tr_idx_lt_threshold}) and short_tr_idx({st_tr_idx:.2f}) < threshold({self.tr_idx_st_threshold}) "
                    sell_signal = True
                else:
                    desc += f" keep! the position!"
            else:
                desc += "ERROR: short term indexes are empty!"
                log.error(desc)
                return False, desc

        return sell_signal,  desc



class Verzit2_SWS_Strategy(VerzitStrategy2):

    def __init__(self):
        super(Verzit2_SWS_Strategy, self).__init__()

    def load_tai_params(self, params) :
        super(Verzit2_SWS_Strategy, self).load_tai_params(params)
        self.tai_ma1 = params['tai_ma1']
        self.tai_ma2 = params['tai_ma2']
        self.tai_ma3 = params['tai_ma3']
        self.tai_ma4 = params['tai_ma4']


    def __isBuySignal__(self, tmgr, market, price, time_dt):
        mas_list = self.mkt_tais[f"{market}_mas"]

        sws_buy_signal = signal_buy_pos(mas_list, price)
        desc = f"BUY:{sws_buy_signal=},"
        if sws_buy_signal:
            tr_buy_signal, desc = super(Verzit2_SWS_Strategy, self).__isBuySignal__(tmgr, market, price, time_dt)
            if tr_buy_signal:
                desc += desc
                return True, desc

        return False, desc

    def __isSellSignal__(self, tmgr, market, price, time_dt):
        mas_list = self.mkt_tais[f"{market}_mas"]
        sws_sell_signal = signal_sell_pos(mas_list, price)
        desc = f"SELL:{sws_sell_signal=},"

        if sws_sell_signal:
            tr_sell_signal, desc = super(Verzit2_SWS_Strategy, self).__isSellSignal__(tmgr, market, price, time_dt)
            if tr_sell_signal :
                desc += desc
                return True, desc

        return False, desc

    def extract_tai(self, tmgr):
        market_sig_books = super(Verzit2_SWS_Strategy, self).extract_tai(tmgr)

        tai_ma_list = [self.tai_ma1, self.tai_ma2, self.tai_ma3, self.tai_ma4]
        market_mas_list = []
        for tai_ma in tai_ma_list :
            market_ma = get_unary_tai(tmgr, tai_ma)
            market_mas_list.append(market_ma)

        quote = tmgr.get_quote()
        market_ticks = quote.get_market_ticks(tmgr.ex_type)

        market_mas = {}
        for market in market_ticks :
            market_mas[market] = {}
            ma_list = []
            for idx, mas in enumerate(market_mas_list) :
                market_mas[market][f"ma{idx}"] = mas[market]
                ma_list.append(mas[market])

            market_sig_books[f"{market}_mas"] = ma_list
        return market_sig_books

############################################################################################
class SignalGenerator :
    def __init__(self) :

        self.sig_gen_units = {}
        self.sig_gen_units["ma3-ma5"] = MASigGenUnit("ma3", "ma5")
        self.sig_gen_units["ma5-ma10"] = MASigGenUnit("ma5", "ma10")
        self.sig_gen_units["ma10-ma20"] = MASigGenUnit("ma10", "ma20")
        self.sig_gen_units["ma20-ma60"] = MASigGenUnit("ma20", "ma60")
        self.sig_gen_units["ma60-ma120"] = MASigGenUnit("ma60", "ma120")
        self.sig_gen_units["ma60"] = MASigGenUnit("ma60", None)
        self.sig_gen_units["macd"] = MACDSigGenUnit()
        self.sig_gen_units["bb"] = BBSigGenUnit()
        self.sig_gen_units["cci"] = CCISigGenUnit()
        self.sig_gen_units["psar"] = PSARSigGenUnit()
        self.idx = list(self.sig_gen_units.keys())
        self.idx.append('tr_idx')

    def generate_signal(self, price, tai) :
        list_of_sigs = []

        for sig_gen in self.sig_gen_units :
            sig, desc = self.sig_gen_units[sig_gen].gen(price, tai)
            list_of_sigs.append(sig)
        tr_idx = sum(list_of_sigs) / len(list_of_sigs)
        list_of_sigs.append(tr_idx)
        sig_ser = pd.Series(list_of_sigs, index = self.idx)
        return sig_ser

class AbstractSigGenUnit(metaclass = ABCMeta) :
    def __init__(self, tai_name) :
        self.tai_name = tai_name

    def get_tai_name(self) :
        return self.tai_name

    @abstractmethod
    def gen(self, price, tai) :
        pass

class MASigGenUnit(AbstractSigGenUnit) :
    def __init__(self, ma1, ma2) :
        super(MASigGenUnit, self).__init__("ma")
        self.ma1 = ma1
        self.ma2 = ma2
        self.band = 0.0001  # HOLD if the gap exists between upper and lower bands

    def gen(self, price, tai) :
        ma1_val = tai[self.ma1]
        desc = ""

        if self.ma2 is not None :
            ma2_val = tai[self.ma2]
            upper_band = ma2_val * (1 + self.band)
            lower_band = ma2_val * (1 - self.band)
            if ma1_val >= upper_band :
                desc += f"[BUY] {self.ma1}({ma1_val}) >= upper({upper_band})(={self.ma2}({ma2_val})*{1 + self.band})"
                return Signal.BUY, desc
            elif lower_band < ma1_val < upper_band :
                desc += f"[HOLD] lower({lower_band}) < {self.ma1}({ma1_val}) < upper({upper_band})(={self.ma2}({1 + self.band})*{1 + self.band})"
                return Signal.HOLD, desc
            else :
                desc += f"[SELL] {self.ma1}({ma1_val}) < lower({lower_band})(={ma2_val}*({1 - self.band})"
                return Signal.SELL, desc
        else :
            upper_band = ma1_val * (1 + self.band)
            if price >= upper_band :
                desc += f"[BUY] price({price}) >= upper({upper_band})(={self.ma1}({ma1_val})*{1 + self.band})"
                return Signal.BUY, desc
            elif ma1_val < price < upper_band :
                desc += f"[BUY] ma1({ma1_val}) < price({price}) < upper({upper_band})"
                return Signal.HOLD, desc
            else :
                desc += f"[SELL] price({price}) < {self.ma1}({ma1_val})"
                return Signal.SELL, desc

class MACDSigGenUnit(AbstractSigGenUnit) :
    def __init__(self) :
        super(MACDSigGenUnit, self).__init__("macd")

    def gen(self, price, tai) :
        my_tai = tai[self.tai_name]
        macd = my_tai[0]
        signal = my_tai[1]

        desc = ""
        if macd > signal :
            desc += f"[BUY] macd({macd}) > signal({signal})"
            return Signal.BUY, desc
        else :
            desc += f"[SELL] macd({macd}) <= signal({signal})"
            return Signal.SELL, desc

class PSARSigGenUnit(AbstractSigGenUnit) :
    def __init__(self) :
        super(PSARSigGenUnit, self).__init__("psar")

    def gen(self, price, tai) :
        psar = tai[self.tai_name]

        if price > psar :
            return Signal.BUY, f"[BUY] price({price}) > psar({psar})"
        else :
            return Signal.SELL, f"[SELL] price({price}) < psar({psar})"

class CCISigGenUnit(AbstractSigGenUnit) :
    def __init__(self) :
        super(CCISigGenUnit, self).__init__("cci")

    def gen(self, price, tai) :
        cci = tai[self.tai_name]
        desc = ""

        if cci > 100 :
            desc += f"[BUY] cci({cci}) >= 100"
            self.prev_cci = cci
            return Signal.BUY, desc
        elif cci < -100 :
            desc += f"[SELL] cci({cci}) =< -100"
            self.prev_cci = cci
            return Signal.SELL, desc
        else :
            desc += f"[HOLD] -100 < {cci} < 100"
            self.prev_cci = cci
            return Signal.HOLD, desc

class BBSigGenUnit(AbstractSigGenUnit) :
    def __init__(self) :
        super(BBSigGenUnit, self).__init__("bb")
        self.band = 0.05

    def gen(self, price, tai):
        my_tai = tai[self.tai_name]
        bb_low = my_tai[2]
        bb_high = my_tai[0]
        desc = ""
        if bb_low <= price < bb_low * (1 + self.band) :
            desc += f"[BUY] bblow({bb_low}) <= price({price}) < bblow*band({bb_low * (1 + self.band)})"
            return Signal.BUY, desc
        if bb_high <= price < bb_high * (1 + self.band) :
            desc += f"[SELL] bbhigh({bb_high}) <= price({price}) < bbhigh*band({bb_high * (1 + self.band)})"
            return Signal.SELL, desc
        else :
            desc += f"[HOLD] bblow*band({bb_low * (1 + self.band)}) <= price({price}) < bbhigh({bb_high})"
            return Signal.HOLD, desc
