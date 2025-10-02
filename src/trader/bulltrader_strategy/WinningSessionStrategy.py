import pandas as pd
import talib
import numpy as np
import math
from statsmodels.tsa.seasonal import seasonal_decompose
from bt4.Constants import CandleType
from bt4.utils.misc_utils import rearrange_market_tais
from bt4.utils.mylog import init_log
from bt4.utils.python_utils import split_hour_min, is_the_time
from bt4.utils.stat.stats import TTest
from bt4.utils.tai_utils import get_unary_tai, get_nary_tai
from bt4.optim.AdaptiveWSParamOptim import AdaptiveWSParamOptim
from bt4.strategy.Strategy import AbstractNettingStrategy, AbstractHedgingStrategy

log = init_log()


class WinningSession_Day(AbstractNettingStrategy):
    def __init__(self):
        super(WinningSession_Day, self).__init__()

    def set_params(self, am, report_storage, markets, params):
        super(WinningSession_Day, self).set_params(am, report_storage, markets, params)

    def load_tai_params(self, params) :
        self.base_time = params['base_time']
        self.base_hour, self.base_minute = split_hour_min(self.base_time)
        self.sell_time = params['sell_time']
        self.sell_hour, self.sell_minute = split_hour_min(self.sell_time)
        self.tai_ma = params['tai_ma']

    def __is_rebalance_time__(self, time_dt) :
        return True if time_dt.hour == 8 and time_dt.minute == 59 else False

    def __isBuySignal__(self, mkt_tais, tmgr, market, tick, time_dt):
        price = tick.close

        is_base_time = is_the_time(time_dt, self.base_hour, self.base_minute)
        ma = mkt_tais[market]
        tai_signal = True if ma > 0 and price > ma else False
        return is_base_time and tai_signal, f"(@{self.base_time}) price({price}) > mas({ma})"

    def __isSellSignal__(self, mkt_tais, tmgr, market, tick, time_dt):
        price = tick.close

        is_sell_time = is_the_time(time_dt, self.sell_hour, self.sell_minute)
        ma = mkt_tais[market]
        tai_signal = True if ma > 0 and price < ma else False
        return is_sell_time and tai_signal, f"@{self.sell_time} price({price}) < mas({ma})"

    def extract_tai(self, tmgr):
        market_ma = get_unary_tai(tmgr, self.tai_ma)
        return market_ma


class WinningSession_4H(WinningSession_Day):
    def __init__(self):
        super(WinningSession_4H, self).__init__()

    def load_tai_params(self, params) :
        self.trading_hour = 4
        self.tai_ma = params['tai_ma']

    def __is_rebalance_time__(self, time_dt) :
        # return True if time_dt.hour % self.trading_hour == 0 and time_dt.minute == 59 else False
        return True if time_dt.hour == 8 and time_dt.minute == 59 else False

    def __isBuySignal__(self, mkt_tais, tmgr, market, tick, time_dt):
        price = tick.close
        is_trading_time = True if time_dt.hour % self.trading_hour == 0 and time_dt.minute == 59 else False

        ma = mkt_tais[market]
        tai_signal = True if ma > 0 and price > ma else False
        return is_trading_time and tai_signal, f"(@{is_trading_time}) price({price}) > mas({ma})"

    def __isSellSignal__(self, mkt_tais, tmgr, market, tick, time_dt):
        price = tick.close
        is_trading_time = True if time_dt.hour % self.trading_hour == 0 and time_dt.minute == 59 else False

        ma = mkt_tais[market]
        tai_signal = True if ma > 0 and price < ma else False
        return is_trading_time and tai_signal, f"@{is_trading_time} price({price}) < mas({ma})"


class WinningSessionAltStrategy(AbstractNettingStrategy):
    def __init__(self):
        super(WinningSessionAltStrategy, self).__init__()

    def set_params(self, am, report_storage, markets, params):
        super(WinningSessionAltStrategy, self).set_params(am, report_storage, markets, params)

    def load_tai_params(self, params) :
        self.tai_ma1_3 = params["tai_ma1_3"]
        self.tai_ma1_5 = params["tai_ma1_5"]
        self.tai_ma1_10 = params["tai_ma1_10"]
        self.tai_ma1_20 = params["tai_ma1_20"]
        self.tai_ma3_10 = params["tai_ma3_10"]
        self.tai_ma3_20 = params["tai_ma3_20"]
        self.tai_ma5_10 = params["tai_ma5_10"]
        self.tai_ma5_20 = params["tai_ma5_20"]
        self.tai_ma15_10 = params["tai_ma15_10"]
        self.tai_ma15_20 = params["tai_ma15_20"]
        self.tai_ma30_10 = params["tai_ma30_10"]
        self.tai_ma30_20 = params["tai_ma30_20"]
        self.tai_vol1_3 = params["tai_vol1_3"]

    def __is_rebalance_time__(self, time_dt) :
        return True if time_dt.hour == 8 and time_dt.minute == 59 else False

    def __isBuySignal__(self, mkt_tais, tmgr, market, tick, time_dt):
        price = tick.close

        price_signal = False
        ma1_3 = mkt_tais[market]["tai_ma1_3"]
        ma1_5 = mkt_tais[market]["tai_ma1_5"]
        ma1_10 = mkt_tais[market]["tai_ma1_10"]
        ma1_20 = mkt_tais[market]["tai_ma1_20"]
        if price > ma1_3 and \
            price > ma1_5 and \
            price > ma1_10 and \
            price > ma1_20:
            price_signal = True

        ma3_signal = True
        ma3_10 = mkt_tais[market]["tai_ma3_10"]
        ma3_20 = mkt_tais[market]["tai_ma3_20"]
        if ma3_10 > ma3_20:
            ma3_signal = True

        ma5_signal = True # disable ma5, to enable make it False
        ma5_10 = mkt_tais[market]["tai_ma5_10"]
        ma5_20 = mkt_tais[market]["tai_ma5_20"]
        if ma5_10 > ma5_20:
            ma5_signal = True

        ma30_signal = False # disable ma5, to enable make it False
        ma30_10 = mkt_tais[market]["tai_ma30_10"]
        ma30_20 = mkt_tais[market]["tai_ma30_20"]
        if ma30_10 > ma30_20:
            ma30_signal = True

        price_signal2 = False
        if price > ma30_10 and \
            price > ma30_20 :
            price_signal2 = True

        bb_upper = mkt_tais[market]["tai_vol1_3"]
        quote = tmgr.get_quote()
        market_ticks = quote.get_market_ticks(self.ex_type)
        vol_signal = True
        if market_ticks[market].volume > bb_upper[0]:
            vol_signal = True

        return price_signal & ma3_signal & ma5_signal & ma30_signal & price_signal2 & vol_signal, f"price({price}) > mas({ma1_3}, {ma1_5}, {ma1_10}, {ma1_20}) and vol({market_ticks[market].volume}) > bb_upper({bb_upper[0]})"

    def __isSellSignal__(self, mkt_tais, tmgr, market, tick, time_dt):
        price = tick.close

        ma30_sell_signal = False
        ma30_10 = mkt_tais[market]["tai_ma30_10"]
        ma30_20 = mkt_tais[market]["tai_ma30_20"]
        if ma30_10 < ma30_20:
            ma30_sell_signal = True

        price_signal = False
        if price < ma30_10 and \
            price < ma30_20 :
            price_signal = False

        ma5_sell_signal = False
        ma5_10 = mkt_tais[market]["tai_ma5_10"]
        ma5_20 = mkt_tais[market]["tai_ma5_20"]
        if ma5_10 < ma5_20:
            ma5_sell_signal = False # disable ma5, to enable make it True

        return ma30_sell_signal or ma5_sell_signal or price_signal, f"ma30_10({ma30_10}) < ma30_20({ma30_20}) or ma5_10({ma5_10}) < ma5_20({ma5_20})"

    def extract_tai(self, tmgr):
        quote = tmgr.get_quote()
        markets = quote.get_markets(self.ex_type)

        tai_holder = {}
        rearrange_market_tais(markets, tai_holder, "tai_ma1_3", get_unary_tai(tmgr, self.tai_ma1_3))
        rearrange_market_tais(markets, tai_holder, "tai_ma1_5", get_unary_tai(tmgr, self.tai_ma1_5))
        rearrange_market_tais(markets, tai_holder, "tai_ma1_10", get_unary_tai(tmgr, self.tai_ma1_10))
        rearrange_market_tais(markets, tai_holder, "tai_ma1_20", get_unary_tai(tmgr, self.tai_ma1_20))
        rearrange_market_tais(markets, tai_holder, "tai_ma3_10", get_unary_tai(tmgr, self.tai_ma3_10))
        rearrange_market_tais(markets, tai_holder, "tai_ma3_20", get_unary_tai(tmgr, self.tai_ma3_20))
        rearrange_market_tais(markets, tai_holder, "tai_ma5_10", get_unary_tai(tmgr, self.tai_ma5_10))
        rearrange_market_tais(markets, tai_holder, "tai_ma5_20", get_unary_tai(tmgr, self.tai_ma5_20))
        rearrange_market_tais(markets, tai_holder, "tai_ma15_10", get_unary_tai(tmgr, self.tai_ma15_10))
        rearrange_market_tais(markets, tai_holder, "tai_ma15_20", get_unary_tai(tmgr, self.tai_ma15_20))
        rearrange_market_tais(markets, tai_holder, "tai_ma30_10", get_unary_tai(tmgr, self.tai_ma30_10))
        rearrange_market_tais(markets, tai_holder, "tai_ma30_20", get_unary_tai(tmgr, self.tai_ma30_20))
        rearrange_market_tais(markets, tai_holder, "tai_vol1_3", get_nary_tai(tmgr, self.tai_vol1_3))

        return tai_holder



class WSAlt_Price_Residual_Strategy(AbstractNettingStrategy):
    def __init__(self):
        super(WSAlt_Price_Residual_Strategy, self).__init__()

    def set_params(self, am, report_storage, markets, params):
        super(WSAlt_Price_Residual_Strategy, self).set_params(am, report_storage, markets, params)

    def load_tai_params(self, params) :
        self.residual_sigma_lower = params["residual_sigma_lower"]
        self.residual_sigma_upper = params["residual_sigma_upper"]
        self.candle_type = params["candle_type"]
        self.seasonal_decomp_period = params["seasonal_decomp_period"]
        self.tai_ma = params['tai_ma']
        self.tai_ma15_10 = params["tai_ma15_10"]
        self.tai_ma15_20 = params["tai_ma15_20"]
        self.tai_cci = params["tai_cci"]

        self.prev_rma1 = {}
        self.residual_buf = {}
        self.prev_rrma = {}
        for market in self.markets:
            self.prev_rma1[market] = -1000
            self.residual_buf[market] = []
            self.prev_rrma[market] = -1000

        self.residual_buf_size = 10

    def __is_rebalance_time__(self, time_dt) :
        remainder = time_dt.minute % self.candle_type.value         # Rebalance every candle time
        if remainder == (self.candle_type.value - 1) :
            return True
        return False

    def __is_settlement_time__(self, time_dt):
        return True if time_dt.hour == 8 and time_dt.minute == 59 else False

    def __padding__(self, candle_df):
        freq_str = f'{self.candle_type.value}min'
        front_padding_start = candle_df.index[0] - pd.Timedelta(
            minutes = self.candle_type.value * (self.seasonal_decomp_period / 2 + 1))
        front_padding_end = candle_df.index[0] - pd.Timedelta(minutes = self.candle_type.value)
        front_padding_idx = pd.date_range(front_padding_start, front_padding_end, freq = freq_str)
        front_padding_df = pd.DataFrame(columns = candle_df.columns, index = front_padding_idx)
        front_padded_candle = pd.concat([front_padding_df, candle_df])
        front_padded_candle = front_padded_candle.fillna(method = "bfill")

        rear_padding_start = candle_df.index[-1] + pd.Timedelta(minutes = self.candle_type.value)
        rear_padding_end = candle_df.index[-1] + pd.Timedelta(
            minutes = self.candle_type.value * self.seasonal_decomp_period / 2 + 1)
        rear_padding_idx = pd.date_range(rear_padding_start, rear_padding_end, freq = freq_str)
        rear_padding_df = pd.DataFrame(columns = candle_df.columns, index = rear_padding_idx)
        padded_candle_df = pd.concat([front_padded_candle, rear_padding_df])
        padded_candle_df = padded_candle_df.fillna(method = "ffill")
        return padded_candle_df

    def __perform_seasonal_decomposition__(self, tmgr, market):
        quote = tmgr.get_quote()

        candle_df = quote.get_candle_types(self.ex_type)[self.candle_type][market]
        past_padded_candle_df = self.__padding__(candle_df)

        dec = seasonal_decompose(past_padded_candle_df["close"], model = 'additive', period = self.seasonal_decomp_period)
        res_mean = dec.resid.mean()
        res_std = dec.resid.std()

        # print(f"candle length: {len(candle_df)}, {res_mean=}, {res_std=}")

        lower_bound = res_mean - self.residual_sigma_lower * res_std
        upper_bound = res_mean + self.residual_sigma_upper * res_std

        residual = dec.resid.dropna()

        return residual, lower_bound, upper_bound

    def __isBuySignal__(self, mkt_tais, tmgr, market, tick, time_dt):
        price = tick.close

        btc_ma5 = mkt_tais[market]['tai_ma']
        desc = ""
        btc_ws_buy_signal = True  # To Enable it, set it False
        btc_price = tmgr.get_quote().get_market_ticks(self.ex_type)[market].close
        if btc_price > btc_ma5:
            btc_ws_buy_signal = True
            desc += f"btc_price({btc_price}) > btc_ma5({btc_ma5}),"

        residual_buy_signal = True # To Enable it, set it False
        residual, lower_bound, _ = self.__perform_seasonal_decomposition__(tmgr, market)
        r_resl = residual[-1]
        if r_resl < lower_bound :
            residual_buy_signal = True
            desc += f"recent_residual({r_resl}) < lower_bound({lower_bound}),"

        rma1 = talib.SMA(residual, 3)[-1]
        rma2 = talib.SMA(residual, 5)[-1]
        rma3 = talib.SMA(residual, 10)[-1]

        residual_divergence_signal = True # To Enable it, set it False
        if residual_buy_signal:
            if rma1 > self.prev_rma1[market]:
                residual_divergence_signal = True
                desc += f"rma1({rma1}) > prev_rma1({self.prev_rma1[market]}),"
        self.prev_rma1[market] = rma1

        residual_sws_signal = True # To Enable it, set it False
        if r_resl > rma1 and r_resl > rma2 and r_resl > rma3 :
            residual_sws_signal = True
            desc += f"residual({r_resl}) > rma1({rma1}) and residual({r_resl}) > rma2({rma2}) and residual({r_resl}) > rma3({rma3})"

        residual_sws_signal2 = True # To Enable it, set it False
        if r_resl < rma1 and r_resl < rma2 and r_resl < rma3 :
            residual_sws_signal2 = True
            desc += f"residual({r_resl}) < rma1({rma1}) and residual({r_resl}) < rma2({rma2}) and residual({r_resl}) < rma3({rma3})"

        ############################################
        ## Gradient
        residual_gradient_signal = False # To Enable it, set it False
        if len(self.residual_buf[market]) < self.residual_buf_size:
            self.residual_buf[market].append(r_resl)
        else:
            self.residual_buf[market].append(r_resl)
            self.residual_buf[market].pop(0)

        rrma = talib.SMA(np.array(self.residual_buf[market]), 3)[-1]
        if not math.isnan(rrma):
            if rrma - self.prev_rrma[market] > 1.5:
                residual_gradient_signal = True
                desc += f"residual gap({rrma - self.prev_rma1[market]}) > 1.5,"
            self.prev_rrma[market] = rrma

        ############################################
        ## CCI
        cci_signal = False
        cci = mkt_tais[market]['tai_cci']
        if cci > 300:
            cci_signal = True

        return btc_ws_buy_signal and residual_buy_signal and residual_sws_signal and \
               residual_sws_signal2 and residual_divergence_signal \
               and residual_gradient_signal and cci_signal, desc

    def __isSellSignal__(self, mkt_tais, tmgr, market, tick, time_dt):
        price = tick.close

        desc = ""
        btc_ws_sell_signal = False
        btc_ma5 = mkt_tais[market]['tai_ma']
        btc_price = tmgr.get_quote().get_market_ticks(self.ex_type)[market].close
        if btc_price < btc_ma5:
            btc_ws_sell_signal = False # to enable make it True
            desc += f"btc_price({btc_price}) < btc_ma5({btc_ma5}), "

        residual_sell_signal = False
        residual, _, upper_bound = self.__perform_seasonal_decomposition__(tmgr, market)
        r_resl = residual[-1]
        if r_resl > upper_bound :
            residual_sell_signal = False # to enable make it True
            desc += f"recent_residual({r_resl}) > upper_bound({upper_bound})"

        ma5_sell_signal = False
        ma15_10 = mkt_tais[market]["tai_ma15_10"]
        ma15_20 = mkt_tais[market]["tai_ma15_20"]
        if ma15_10 < ma15_20 :
            ma5_sell_signal = False  # to enable make it True
            desc += f"ma15_10({ma15_10}) < ma15_20({ma15_20}), "

        rma1 = talib.SMA(residual, 3)[-1]
        rma2 = talib.SMA(residual, 5)[-1]
        rma3 = talib.SMA(residual, 10)[-1]

        residual_divergence_signal = False
        if residual_sell_signal:
            if rma1 < self.prev_rma1[market]:
                residual_divergence_signal = False # to enable make it True
                desc += f"rma1({rma1}) < prev_rma1({self.prev_rma1[market]}),"
        self.prev_rma1[market] = rma1

        residual_sws_signal = False
        if r_resl < rma1 or r_resl < rma2 or r_resl < rma3 :
            residual_sws_signal = False   # to enable make it True
            desc += f"residual({r_resl}) < rma1({rma1}) or residual({r_resl}) < rma2({rma2}) or residual({r_resl}) < rma3({rma3})"

        ##################################################################################
        residual_gradient_signal = False
        if len(self.residual_buf[market]) < self.residual_buf_size:
            self.residual_buf[market].append(r_resl)
        else:
            self.residual_buf[market].append(r_resl)
            self.residual_buf[market].pop(0)

        rrma = talib.SMA(np.array(self.residual_buf[market]), 3)[-1]
        if not math.isnan(rrma) :
            if rrma - self.prev_rma1[market] < -0.5:
                residual_gradient_signal = True # To Enable it, set it True
                desc += f"residual gap({rrma - self.prev_rma1[market]}) < 0.5,"
            self.prev_rrma[market] = rrma

        return btc_ws_sell_signal or (residual_sell_signal and residual_divergence_signal) or \
               ma5_sell_signal or residual_sws_signal or residual_gradient_signal, desc

    def extract_tai(self, tmgr):
        quote = tmgr.get_quote()
        markets = quote.get_markets(self.ex_type)

        tai_holder = {}

        rearrange_market_tais(markets, tai_holder, "tai_ma", get_unary_tai(tmgr, self.tai_ma))
        rearrange_market_tais(markets, tai_holder, "tai_ma15_10", get_unary_tai(tmgr, self.tai_ma15_10))
        rearrange_market_tais(markets, tai_holder, "tai_ma15_20", get_unary_tai(tmgr, self.tai_ma15_20))
        rearrange_market_tais(markets, tai_holder, "tai_cci", get_unary_tai(tmgr, self.tai_cci))

        return tai_holder


class WinningSession_Hedge(AbstractHedgingStrategy):
    def __init__(self):
        super(WinningSession_Hedge, self).__init__()

    def load_tai_params(self, params):
        self.tai_ma_tf = params['tai_ma_tf']

    def __isBuySignal__(self, mkt_buy_tais, tmgr, market, tick, time_dt, tf_hour):
        price = tick.close

        buy_signal = False
        buy_ma = mkt_buy_tais[market]
        if price > buy_ma:
            buy_signal = True
        buy_ma5_key = f"ma{self.tai_ma_tf[1][0]}"
        buy_log = f"price({price}) > {buy_ma5_key}({buy_ma:.2f})"
        return buy_signal, buy_log

    def __isSellSignal__(self, mkt_sell_tais, tmgr, market, tick, time_dt, tf_hour) :
        price = tick.close

        sell_signal = False
        sell_ma = mkt_sell_tais[market]
        if price < sell_ma :
            sell_signal = True
        sell_ma_key = f"ma{self.tai_ma_tf[1][0]}"
        sell_log = f"price({price}) < {sell_ma_key}({sell_ma:.2f})"
        return sell_signal, sell_log

    def extract_tai(self, tmgr, timeframe_hour):
        self.tai_ma_tf[2] = CandleType[f'DAYS_{timeframe_hour}']
        return get_unary_tai(tmgr, self.tai_ma_tf)


class WinningSession_Volume_Hedge(AbstractHedgingStrategy):
    def __init__(self):
        super(WinningSession_Volume_Hedge, self).__init__()

    def load_tai_params(self, params):
        self.tai_ma_tf = params["tai_ma_tf"]
        self.tai_vol_ma_tf = params["tai_vol_ma_tf"]

    def __isBuySignal__(self, mkt_tais, tmgr, market, tick, time_dt, tf_hour):
        price = tick.close

        buy_signal = False
        quote = tmgr.get_quote()
        market_df = quote.get_candle_types(self.ex_type)[CandleType[f'DAYS_{tf_hour}']][market]
        cur_vol = market_df.tail(1)["vol"].item()

        price_ma = mkt_tais[market]['price_ma']
        vol_ma = mkt_tais[market]['vol_ma']

        if (price > price_ma) and (cur_vol > vol_ma):
            buy_signal = True

        buy_ma5_key = f"ma{self.tai_ma_tf[1][0]}"
        buy_vol_ma_key = f"vol_ma{self.tai_vol_ma_tf[1][0]}"
        buy_log = f"price({price}) > {buy_ma5_key}({price_ma:.2f}) and vol({cur_vol}) > {buy_vol_ma_key}({vol_ma:.2f})"
        return buy_signal, buy_log

    def __isSellSignal__(self, mkt_tais, tmgr, market, tick, time_dt, tf_hour) :
        price = tick.close
        sell_signal = False

        quote = tmgr.get_quote()
        market_df = quote.get_candle_types(self.ex_type)[CandleType[f'DAYS_{tf_hour}']][market]
        cur_vol = market_df.tail(1)["vol"].item()

        price_ma = mkt_tais[market]['price_ma']
        vol_ma = mkt_tais[market]['vol_ma']

        if (price < price_ma) or (cur_vol < vol_ma) :
            sell_signal = True

        sell_ma_key = f"ma{self.tai_ma_tf[1][0]}"
        sell_vol_ma_key = f"vol_ma{self.tai_vol_ma_tf[1][0]}"
        sell_log = f"price({price}) < {sell_ma_key}({price_ma:.2f}) or vol({cur_vol}) > {sell_vol_ma_key}({vol_ma:.2f})"
        return sell_signal, sell_log

    def extract_tai(self, tmgr, timeframe_hour):
        quote = tmgr.get_quote()
        markets = quote.get_markets(self.ex_type)

        self.tai_ma_tf[2] = CandleType[f'DAYS_{timeframe_hour}']
        self.tai_vol_ma_tf[2] = CandleType[f'DAYS_{timeframe_hour}']

        tai_holder = {}
        rearrange_market_tais(markets, tai_holder, "price_ma", get_unary_tai(tmgr, self.tai_ma_tf))
        rearrange_market_tais(markets, tai_holder, "vol_ma", get_unary_tai(tmgr, self.tai_vol_ma_tf))
        return tai_holder


class WinningSession_Adaptive_ParamOptim_Volume_Hedge(WinningSession_Volume_Hedge):
    def __init__(self):
        super(WinningSession_Adaptive_ParamOptim_Volume_Hedge, self).__init__()
        self.windows = 30

    def set_params(self, am, report_storage, markets, params):
        super(WinningSession_Adaptive_ParamOptim_Volume_Hedge, self).set_params(am, report_storage, markets, params)
        self.market = markets[0]

    def init_trading(self, quote) :
        recent_market_day_df = quote.get_candle_types(self.ex_type)[CandleType.DAYS][self.market]
        # 1. (Init) 첫 30일의 Volume정보를 로딩하여 저장함
        self.recent_mkt_day_vols = recent_market_day_df.tail(30)["vol"]
        return super(WinningSession_Adaptive_ParamOptim_Volume_Hedge, self).init_trading(quote)

    def load_tai_params(self, params) :
        super(WinningSession_Adaptive_ParamOptim_Volume_Hedge, self).load_tai_params(params)
        # 2. (Init) 그리고 price_ma_period와 volume_ma_period도 저장해 놓기
        self.price_ma_period = self.tai_ma_tf[1][0]
        self.volume_ma_period = self.tai_vol_ma_tf[1][0]

    def __isBuySignal__(self, mkt_tais, tmgr, market, tick, time_dt, tf_hour) :
        price = tick.close
        return super(WinningSession_Adaptive_ParamOptim_Volume_Hedge, self).__isBuySignal__(mkt_tais, tmgr, market, tick, time_dt, tf_hour)
    def __isSellSignal__(self, mkt_tais, tmgr, market, tick, time_dt, tf_hour) :
        price = tick.close
        return super(WinningSession_Adaptive_ParamOptim_Volume_Hedge, self).__isSellSignal__(mkt_tais, tmgr, market, tick, time_dt, tf_hour)

    def extract_tai(self, tmgr, timeframe_hour) :
        return super(WinningSession_Adaptive_ParamOptim_Volume_Hedge, self).extract_tai(tmgr, timeframe_hour)

    def perform(self, quote) :
        ##
        # 3. (perform) 매일 9시에 전 30일과 비교하여 T-Test 수행

        time_pdt = quote.get_time()
        if time_pdt.hour == 8 and time_pdt.minute == 59:
            log.info(f"##(( {time_pdt} ))################################# RECALCULATE!! MEANS")

            todays_day_df = quote.get_candle_types(self.ex_type)[CandleType.DAYS][self.market]
            todays_day_vols = todays_day_df.tail(self.windows)["vol"]
            ttest = TTest()

            base_start = self.recent_mkt_day_vols.index[0].strftime('%Y-%m-%d %X')
            base_end   = self.recent_mkt_day_vols.index[self.windows-1].strftime('%Y-%m-%d %X')
            base_mean = np.mean(self.recent_mkt_day_vols)
            base_stdev = np.std(self.recent_mkt_day_vols)
            print(f"## base : {base_start} ~ {base_end}, mean:{base_mean}, stdev:{base_stdev}")

            recent_start = todays_day_vols.index[0].strftime('%Y-%m-%d %X')
            recent_end = todays_day_vols.index[self.windows - 1].strftime('%Y-%m-%d %X')
            recent_mean = np.mean(todays_day_vols)
            recent_stdev = np.std(todays_day_vols)
            print(f"## recent : {recent_start} ~ {recent_end}, mean:{recent_mean}, stdev:{recent_stdev}")
            is_same_mean, reason = ttest.perform(self.recent_mkt_day_vols.to_numpy(), todays_day_vols.to_numpy())
            print(is_same_mean, reason)
            if not is_same_mean:
                self.recent_mkt_day_vols = todays_day_vols

                awso = AdaptiveWSParamOptim()
                simul_start = base_start
                simul_end = recent_end
                market = tuple(self.markets)
                malist = [3, 5, 10, 20]

                optimal_params = awso.getOptimalParameters(simul_start, simul_end, market, malist)

                current_pma_period = self.price_ma_period
                current_vma_period = self.volume_ma_period
                self.price_ma_period = optimal_params["tai_ma_tf"]
                self.volume_ma_period = optimal_params["tai_vol_ma_tf"]

                log.info (f"### Parameter Change:: price ma period {current_pma_period} => {self.price_ma_period}, "
                          f"voluma ma period {current_vma_period} => {self.volume_ma_period}")
                self.tai_ma_tf[1][0] = self.price_ma_period
                self.tai_vol_ma_tf[1][0] = self.volume_ma_period


        super(WinningSession_Adaptive_ParamOptim_Volume_Hedge, self).perform(quote)


class WinningSession_MMA_Hedge(AbstractHedgingStrategy):
    def __init__(self):
        super(WinningSession_MMA_Hedge, self).__init__()

    def load_tai_params(self, params):
        self.tai_ma_tf1 = params['tai_ma_tf1']
        self.tai_ma_tf2 = params['tai_ma_tf2']

    def __isBuySignal__(self, mkt_buy_tais, tmgr, market, tick, time_dt, tf_hour):
        price = tick.close
        buy_ma1 = mkt_buy_tais[market]["ma1"]
        buy_ma2 = mkt_buy_tais[market]["ma2"]

        buy_signal = False
        if price > buy_ma1 and price > buy_ma2:
            buy_signal = True

        buy_ma1_key = f"ma{self.tai_ma_tf1[1][0]}"
        buy_ma2_key = f"ma{self.tai_ma_tf2[1][0]}"
        buy_log = f"price({price}) > {buy_ma1_key}({buy_ma1:.2f}), and "+\
                  f"price({price}) > {buy_ma2_key}({buy_ma2:.2f}),"
        return buy_signal, buy_log

    def __isSellSignal__(self, mkt_sell_tais, tmgr, market, tick, time_dt, tf_hour) :
        price = tick.close
        sell_ma1 = mkt_sell_tais[market]["ma1"]
        sell_ma2 = mkt_sell_tais[market]["ma2"]

        sell_signal = False
        if price < sell_ma1 or price < sell_ma2 :
            sell_signal = True

        sell_ma1_key = f"ma{self.tai_ma_tf1[1][0]}"
        sell_ma2_key = f"ma{self.tai_ma_tf2[1][0]}"
        sell_log = f"price({price}) < {sell_ma1_key}({sell_ma1:.2f}), or " + \
                  f"price({price}) < {sell_ma2_key}({sell_ma2:.2f}),"
        return sell_signal, sell_log

    def extract_tai(self, tmgr, timeframe_hour):
        self.tai_ma_tf1[2] = CandleType[f'DAYS_{timeframe_hour}']
        self.tai_ma_tf2[2] = CandleType[f'DAYS_{timeframe_hour}']

        mkt_ma1 = get_unary_tai(tmgr, self.tai_ma_tf1)
        mkt_ma2 = get_unary_tai(tmgr, self.tai_ma_tf2)

        quote = tmgr.get_quote()
        market_ticks = quote.get_market_ticks(tmgr.ex_type)

        market_mas = {}
        for market in market_ticks:
            market_mas[market] = {}
            market_mas[market]["ma1"] = mkt_ma1[market]
            market_mas[market]["ma2"] = mkt_ma2[market]
        return market_mas


class WinningSession_VWAP_Hedge(AbstractHedgingStrategy):
    def __init__(self):
        super(WinningSession_VWAP_Hedge, self).__init__()

    def load_tai_params(self, params):
        self.vwap_tf = params['vwap_tf']

    def __isBuySignal__(self, mkt_buy_tais, tmgr, market, tick, time_dt, tf_hour):
        price = tick.close
        vwap  = mkt_buy_tais[market]["vwap"]

        buy_signal = False
        if price > vwap:
            buy_signal = True

        vwap_key = f"vwap{self.vwap_tf[1][0]}"
        buy_log = f"price({price}) > {vwap_key}({vwap:.2f})"
        return buy_signal, buy_log

    def __isSellSignal__(self, mkt_sell_tais, tmgr, market, tick, time_dt, tf_hour) :
        price = tick.close
        vwap = mkt_sell_tais[market]["vwap"]

        sell_signal = False
        if price < vwap:
            sell_signal = True

        vwap_key = f"vwap{self.vwap_tf[1][0]}"
        sell_log = f"price({price}) < {vwap_key}({vwap:.2f})"
        return sell_signal, sell_log

    def extract_tai(self, tmgr, timeframe_hour):
        self.vwap_tf[2] = CandleType[f'DAYS_{timeframe_hour}']

        vwap = get_unary_tai(tmgr, self.vwap_tf)

        quote = tmgr.get_quote()
        market_ticks = quote.get_market_ticks(tmgr.ex_type)

        market_mas = {}
        for market in market_ticks:
            market_mas[market] = {}
            market_mas[market]["vwap"] = vwap[market]
        return market_mas