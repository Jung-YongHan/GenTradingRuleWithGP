from bt4.Constants import CandleType
from bt4.utils.mylog import init_log
from bt4.utils.tai_utils import get_unary_tai, get_nary_tai
from bt4.strategy.Strategy import AbstractNettingStrategy, AbstractHedgingStrategy
from bt4.utils.misc_utils import rearrange_market_tais

log = init_log()

class MACrossOverStrategy(AbstractNettingStrategy):

    def __init__(self):
        super(MACrossOverStrategy, self).__init__()

    def load_tai_params(self, params) :
        self.candle_type    = params['candle_type']
        self.tai_arrow_ma   = params['tai_arrow_ma']
        self.tai_target_ma  = params['tai_target_ma']
        self.tai_trb        = params['tai_trb']

        if 'band' in params:
            self.band = params['band'] if 'band' in params else None

    # def __is_rebalance_time__(self, time_dt) :
    #     _, is_day_close_timing = self.__is_close_update_timing(self.candle_type, time_dt)
    #     return is_day_close_timing
    def __is_rebalance_time__(self, time_dt) :
        return True if time_dt.hour == 8 and time_dt.minute == 59 else False

    def __is_trading_timing(self, candle_type, time_dt):
        current_hour = time_dt.hour
        current_minute = time_dt.minute

        if candle_type == CandleType.DAYS:
            if current_hour == 8 and current_minute == 59:
                return True
        elif candle_type == CandleType.HOUR4:
            if current_hour % 4 == 0 and current_minute == 59:
                return True
        elif candle_type == CandleType.HOUR:
            if current_minute == 59:
                return True
        elif candle_type == CandleType.MINUTES_1:
            return True
        else:
            return False

    def __is_close_update_timing(self, candle_type, cur_date_time):
        current_hour = cur_date_time.hour
        current_minute = cur_date_time.minute

        if candle_type == CandleType.DAYS:
            if current_hour == 8 and current_minute == 59:
                return True, True
        elif candle_type == CandleType.HOUR4:  ## Update for each 1,5,9,13,17,21H : 00M
            if current_hour % 4 == 0 and current_minute == 59:
                return True, False
        elif candle_type == CandleType.HOUR:
            if current_minute == 59:
                return True, False
        elif candle_type == CandleType.MINUTES_1:
            if current_hour == 8 and current_minute == 59:
                return True, True

        return False, False

    def __isBuySignal__(self, mkt_tais, tmgr, market, tick, time_dt):
        price = tick.close
        is_trading_timing = self.__is_trading_timing(self.candle_type, time_dt)

        if not is_trading_timing:
            return False, f"Not Trade Timing"

        arrow_ma = mkt_tais[market]['arr_ma']
        target_ma = mkt_tais[market]['tgt_ma']

        buy_conditions = arrow_ma > target_ma
        desc = f"arrow_ma({arrow_ma}) > tgt_ma({target_ma})"
        if self.band is not None :
            buy_band_condition = arrow_ma > target_ma * (1 + self.band)
            desc = desc + f', and band({buy_band_condition})=(ma5({arrow_ma:.2f}) > target_ma({target_ma}) * (1+self.band({self.band})))'
            buy_conditions = buy_conditions and buy_band_condition

        if self.tai_trb is not None :
            trb_h = mkt_tais[market]['trb'][0]
            buy_trb_condition = price > trb_h
            desc1 = desc + f', and trb({buy_trb_condition})=(price({price}) > trb_h({trb_h}))'
            if self.band is not None :
                buy_trb_condition = price > trb_h * (1 + self.band)
                desc1 = desc + f', and trb({buy_trb_condition})=(price({price}) > trb_h({trb_h})*(1+{self.band}))'
            buy_conditions = buy_conditions and buy_trb_condition
            desc = desc1

        return buy_conditions, desc

    def __isSellSignal__(self, mkt_tais, tmgr, market, tick, time_dt):
        price = tick.close
        is_trading_timing = self.__is_trading_timing(self.candle_type, time_dt)

        if not is_trading_timing:
            return False, f"Not Trade Timing"

        arrow_ma = mkt_tais[market]['arr_ma']
        target_ma = mkt_tais[market]['tgt_ma']

        sell_conditions = arrow_ma < target_ma
        desc = f'-- ma5({arrow_ma:.2f}) < ma20({target_ma:.2f})'
        if self.band is not None :
            sell_conditions = arrow_ma < target_ma * (1 - self.band)
            desc = f'-- ma5({arrow_ma:.2f}) < ma20({target_ma:.2f})*(1-band({self.band}))'

        if self.tai_trb is not None :
            trb_l = mkt_tais[market]['trb'][1]
            sell_trb_condition = price < trb_l
            desc1 = desc + f', and (price({price}) < trb_l({trb_l}))'
            if self.band is not None :
                sell_trb_condition = price < trb_l * (1 - self.band)
                desc1 = desc + f', and (price({price}) < trb_l({trb_l})*(1-{self.band}))'
            sell_conditions = sell_conditions and sell_trb_condition
            desc = desc1

        return sell_conditions, desc

    def extract_tai(self, tmgr):
        quote = tmgr.get_quote()
        markets = quote.get_markets(self.ex_type)

        tai_holder = {}
        rearrange_market_tais(markets, tai_holder, "arr_ma", get_unary_tai(tmgr, self.tai_arrow_ma))
        rearrange_market_tais(markets, tai_holder, "tgt_ma", get_unary_tai(tmgr, self.tai_target_ma))
        rearrange_market_tais(markets, tai_holder, "trb", get_nary_tai(tmgr, self.tai_trb))
        return tai_holder


# class MACrossOverStrategy(AbstractStrategy):
#
#     def __init__(self):
#         super(MACrossOverStrategy, self).__init__()
#
#     def set_params(self, am, report_storage, markets, params):
#         self.ex_type = params['quote_provider']
#         super(MACrossOverStrategy, self).set_params(am, report_storage, markets, self.ex_type)
#
#         self.candle_type    = params['candle_type']
#         self.tai_arrow_ma   = params['tai_arrow_ma']
#         self.tai_target_ma  = params['tai_target_ma']
#         self.tai_trb        = params['tai_trb']
#
#         self.band = None
#         self.trb_func = None
#         if 'band' in params:
#             self.band = params['band']
#
#
#     def init_trading(self, quote):
#         return super(MACrossOverStrategy, self).init_trading(quote)
#
#     def __is_trading_timing(self, candle_type, time_dt):
#         current_hour = time_dt.hour
#         current_minute = time_dt.minute
#
#         if candle_type == CandleType.DAYS:
#             if current_hour == 8 and current_minute == 59:
#                 return True
#         elif candle_type == CandleType.HOUR4:
#             if current_hour % 4 == 0 and current_minute == 59:
#                 return True
#         elif candle_type == CandleType.HOUR:
#             if current_minute == 59:
#                 return True
#         elif candle_type == CandleType.MINUTES_1:
#             return True
#         else:
#             return False
#
#     def __is_close_update_timing(self, candle_type, cur_date_time):
#         current_hour = cur_date_time.hour
#         current_minute = cur_date_time.minute
#
#         if candle_type == CandleType.DAYS:
#             if current_hour == 8 and current_minute == 59:
#                 return True, True
#         elif candle_type == CandleType.HOUR4:  ## Update for each 1,5,9,13,17,21H : 00M
#             if current_hour % 4 == 0 and current_minute == 59:
#                 return True, False
#         elif candle_type == CandleType.HOUR:
#             if current_minute == 59:
#                 return True, False
#         elif candle_type == CandleType.MINUTES_1:
#             if current_hour == 8 and current_minute == 59:
#                 return True, True
#
#         return False, False
#
#     def perform(self, quote):
#         super(MACrossOverStrategy, self).perform(quote)
#         if self.is_paused:
#             return
#         time_dt = quote.get_time()
#
#         tmgr = TAIMgr(quote, self.ex_type)
#         market_ticks = quote.get_market_ticks(self.ex_type)
#         ####################################################################
#         is_trading_timing = self.__is_trading_timing(self.candle_type, time_dt)
#         is_close_update_timing, is_day_close_timing = self.__is_close_update_timing(self.candle_type, time_dt)
#
#         ## Update Daily Data for Asset Management
#         if is_day_close_timing:
#             market_vol5 = compute_vol5(quote, tmgr, self.ex_type)
#             self.asset_mgmt.append_supplements(market_vol5)
#             if self.enable_asset_rebalance:
#                 self.asset_mgmt.rebalance(market_ticks)
#
#         # If it's not trading timing, this strategy will be terminated immediately.
#         if not is_trading_timing:
#             return
#
#         arrow_mas  = get_unary_tai(tmgr, self.tai_arrow_ma)
#         target_mas = get_unary_tai(tmgr, self.tai_target_ma)
#         trbs       = get_nary_tai(tmgr, self.tai_trb)
#
#         for market in market_ticks:
#             tick = market_ticks[market]
#             arrow_ma = arrow_mas[market]
#             target_ma = target_mas[market]
#
#             buy_trade_result = self.asset_mgmt.get_opened_buy_position(market)
#             if buy_trade_result is None:
#                 basic_ma_condition = arrow_ma > target_ma
#                 buy_conditions = basic_ma_condition
#                 desc = f'-- ma5({arrow_ma:.2f}) > ma20({target_ma:.2f})'
#
#                 if self.band is not None:
#                     buy_band_condition = arrow_ma > target_ma * (1 + self.band)
#                     desc = desc + f', and band({buy_band_condition})=(ma5({arrow_ma:.2f}) > target_ma({target_ma}) * (1+self.band({self.band})))'
#                     buy_conditions = buy_conditions and buy_band_condition
#
#                 if self.tai_trb is not None:
#                     trb_h = trbs[market][0]
#                     buy_trb_condition = tick.close > trb_h
#                     desc1 = desc + f', and trb({buy_trb_condition})=(price({tick.close}) > trb_h({trb_h}))'
#                     if self.band is not None:
#                         buy_trb_condition = tick.close > trb_h * (1+self.band)
#                         desc1 = desc + f', and trb({buy_trb_condition})=(price({tick.close}) > trb_h({trb_h})*(1+{self.band}))'
#                     buy_conditions = buy_conditions and buy_trb_condition
#                     desc = desc1
#
#                 log.info(f'[{tick.datetime}] {tick.market} Check for BUY Order:: '+ desc +
#                          f',Market Bal({self.asset_mgmt.get_market_cash_balance(market):.2f})..')
#
#                 if buy_conditions:
#                     super(MACrossOverStrategy, self).process_enter_long_position(market, tick, tick.close, desc)
#
#
#             if buy_trade_result is not None and buy_trade_result.date != tick.datetime:
#
#                 sell_conditions = arrow_ma < target_ma
#                 desc = f'-- ma5({arrow_ma:.2f}) < ma20({target_ma:.2f})'
#                 if self.band is not None:
#                     sell_conditions = arrow_ma < target_ma * (1 - self.band)
#                     desc = f'-- ma5({arrow_ma:.2f}) < ma20({target_ma:.2f})*(1-band({self.band}))'
#
#                 if self.tai_trb is not None:
#                     trb_l = trbs[market][1]
#                     sell_trb_condition = tick.close < trb_l
#                     desc1 = desc + f', and (price({tick.close}) < trb_l({trb_l}))'
#                     if self.band is not None:
#                         sell_trb_condition = tick.close < trb_l * (1-self.band)
#                         desc1 = desc + f', and (price({tick.close}) < trb_l({trb_l})*(1-{self.band}))'
#                     sell_conditions =  sell_conditions and sell_trb_condition
#                     desc = desc1
#
#                 log.info(f'[{tick.datetime}] {tick.market} Check:checking for SELL Order:: ' + desc)
#
#                 if sell_conditions:
#                         super(MACrossOverStrategy, self).process_exit_long_position(buy_trade_result, market, tick,
#                                                                                     tick.close, desc)
#
#         if is_trading_timing:
#             super(MACrossOverStrategy, self).process_settle(time_dt, market_ticks)



class MACrossOver_Hedge(AbstractHedgingStrategy):

    def __init__(self):
        super(MACrossOver_Hedge, self).__init__()

    def load_tai_params(self, params):
        self.tai_arrow_ma_tf  = params['tai_arrow_ma_tf']
        self.tai_target_ma_tf = params['tai_target_ma_tf']

    def __isBuySignal__(self, mkt_buy_tais, tmgr, market, price, time_dt, tf_hour):
       arrow_ma =  mkt_buy_tais[market]['arr_ma']
       target_ma = mkt_buy_tais[market]['tgt_ma']

       ma_signal = False
       if arrow_ma > target_ma:
           ma_signal = True
       return ma_signal, f"arrow_ma({arrow_ma}) > tgt_ma({target_ma})"

    def __isSellSignal__(self, mkt_sell_tais, tmgr, market, price, time_dt, tf_hour) :
        arrow_ma = mkt_sell_tais[market]['arr_ma']
        target_ma = mkt_sell_tais[market]['tgt_ma']

        ma_sell_signal = False
        if arrow_ma < target_ma :
            ma_sell_signal = True
        return ma_sell_signal, f"arrow_ma({arrow_ma}) < tgt_ma({target_ma})"

    def extract_tai(self, tmgr, timeframe_hour):
        quote = tmgr.get_quote()
        markets = quote.get_markets(self.ex_type)

        self.tai_arrow_ma_tf[2] = CandleType[f'DAYS_{timeframe_hour}']
        self.tai_target_ma_tf[2] = CandleType[f'DAYS_{timeframe_hour}']

        tai_holder = {}
        rearrange_market_tais(markets, tai_holder, "arr_ma", get_unary_tai(tmgr, self.tai_arrow_ma_tf))
        rearrange_market_tais(markets, tai_holder, "tgt_ma", get_unary_tai(tmgr, self.tai_target_ma_tf))
        return tai_holder



# class MACrossOver_Hedge(AbstractStrategy):
#
#     def __init__(self):
#         super(MACrossOver_Hedge, self).__init__()
#
#     def set_params(self, am, report_storage, markets, params):
#         self.ex_type = params['quote_provider']
#         super(MACrossOver_Hedge, self).set_params(am, report_storage, markets, self.ex_type)
#         self.buy_timeframes   = params['timeframes']
#         self.buy_sell_time_gap = params['timegap']
#         self.buy_sell_tf, self.sell_buy_tf, self.sell_timeframes = compute_sell_timeframes(self.buy_timeframes,
#                                                                                            self.buy_sell_time_gap)
#         self.tai_arrow_ma_tf  = params['tai_arrow_ma_tf']
#         self.tai_target_ma_tf = params['tai_target_ma_tf']
#
#     def init_trading(self, quote):
#         return super(MACrossOver_Hedge, self).init_trading(quote)
#
#     def perform(self, quote):
#         super(MACrossOver_Hedge, self).perform(quote)
#         if self.is_paused:
#             return
#         time_dt = quote.get_time()
#
#         tmgr = TAIMgr(quote, self.ex_type)
#         market_ticks = quote.get_market_ticks(self.ex_type)
#         #########################################################################
#         is_vol_update_time = is_the_time(time_dt, 8, 59)
#         is_buy_time, expected_buy_timeframe_str, buy_tf_hour = match_time_frame(time_dt, self.buy_timeframes)
#         is_sell_time, expected_sell_timeframe_str, sell_tf_hour = match_time_frame(time_dt, self.sell_timeframes)
#
#         ## Update Daily Data for Asset Management
#         if is_vol_update_time:
#             market_vol5 = compute_vol5(quote, tmgr, self.ex_type)
#             self.asset_mgmt.append_supplements(market_vol5)
#             if self.enable_asset_rebalance:
#                 self.asset_mgmt.rebalance(market_ticks)
#
#         # if is_buy_time or is_sell_time:
#         for market in market_ticks:
#             tick = market_ticks[market]
#
#             #######################################################
#             ## Processing Buy
#             arrow_key = f'DAYS_{buy_tf_hour}'  # it should be matched with that of euote dispatcher
#             arrow_cdl_type = CandleType[arrow_key]
#             self.tai_arrow_ma_tf[2] = arrow_cdl_type
#             arrow_mas = get_unary_tai(tmgr, self.tai_arrow_ma_tf)
#
#             tgt_key = f'DAYS_{buy_tf_hour}'  # it should be matched with that of euote dispatcher
#             tgt_cdl_type = CandleType[tgt_key]
#             self.tai_target_ma_tf[2] = tgt_cdl_type
#             target_mas = get_unary_tai(tmgr, self.tai_target_ma_tf)
#
#             arrow_ma = arrow_mas[market]
#             target_ma = target_mas[market]
#
#             buy_trade_result = self.asset_mgmt.get_opened_buy_position(market, expected_buy_timeframe_str)
#
#             if buy_trade_result is None:
#                 desc = f'{arrow_key}({arrow_ma:.2f}) > {tgt_key}({target_ma:.2f})'
#                 log.info(f'[{tick.datetime}] {tick.market} Check for BUY Order(@{expected_buy_timeframe_str}):: '
#                          f'price({tick.close}), {desc},'
#                          f'Market Bal({self.asset_mgmt.get_market_cash_balance(market):.2f})..')
#
#                 if is_buy_time and arrow_ma > target_ma:
#                     log.info(f'### BUY POSITION ({dt2str(time_dt)})(@{expected_buy_timeframe_str}):{market} '
#                              f'price({tick.close}),{desc}')
#                     super(MACrossOver_Hedge, self).process_enter_long_position(market, tick, tick.close, desc,
#                                                                                expected_buy_timeframe_str)
#
#             #######################################################
#             ## Processing Sell
#             arrow_key = f'DAYS_{sell_tf_hour}'  # it should be matched with that of euote dispatcher
#             arrow_cdl_type = CandleType[arrow_key]
#             self.tai_arrow_ma_tf[2] = arrow_cdl_type
#             arrow_mas = get_unary_tai(tmgr, self.tai_arrow_ma_tf)
#
#             tgt_key = f'DAYS_{sell_tf_hour}'  # it should be matched with that of euote dispatcher
#             tgt_cdl_type = CandleType[tgt_key]
#             self.tai_target_ma_tf[2] = tgt_cdl_type
#             target_mas = get_unary_tai(tmgr, self.tai_target_ma_tf)
#
#             arrow_ma = arrow_mas[market]
#             target_ma = target_mas[market]
#             matched_buy_timeframe_str = self.sell_buy_tf[expected_sell_timeframe_str]
#             matched_buy_trade_result = self.asset_mgmt.get_opened_buy_position(market, matched_buy_timeframe_str)
#
#             if matched_buy_trade_result is not None \
#                 and matched_buy_trade_result.date != dt2str(time_dt):
#
#                 desc = f'{arrow_key}({arrow_ma:.2f}) < {tgt_key}({target_ma:.2f})'
#                 log.info(f'[{tick.datetime}] {tick.market} Check:checking '
#                          f'for SELL Order(sell time ({expected_sell_timeframe_str}) for buy tf({matched_buy_timeframe_str}):: '
#                      f'price({tick.close}), {desc}...')
#
#                 if is_sell_time and arrow_ma < target_ma:
#                     super(MACrossOver_Hedge, self).process_exit_long_position(matched_buy_trade_result, market,
#                                                                               tick, tick.close, f', {desc}',
#                                                                               matched_buy_timeframe_str)
#
#         if is_vol_update_time:
#             super(MACrossOver_Hedge, self).process_settle(time_dt, market_ticks)
