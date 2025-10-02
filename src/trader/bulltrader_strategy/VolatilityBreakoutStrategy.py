from bt4.Constants import CandleType
from bt4.quote.TAIMgr import TAIMgr
from bt4.utils.market_utils import match_time_frame, compute_vol5
from bt4.utils.python_utils import dt2str
from bt4.utils.mylog import init_log
from bt4.utils.python_utils import split_hour_min, is_the_time
from bt4.strategy.Strategy import AbstractStrategy

log = init_log()

def get_ma(tmgr, tai_ma):
    return tmgr.get_unary(tai_ma[0], tai_ma[1], tai_ma[2], tai_ma[3])


class VolatilityBreakoutStrategy(AbstractStrategy):
    def __init__(self):
        super(VolatilityBreakoutStrategy, self).__init__()

    def set_params(self, am, report_storage, markets, params):
        self.ex_type = params['quote_provider']
        super(VolatilityBreakoutStrategy, self).set_params(am, report_storage, markets, self.ex_type)
        self.k = params['k']
        self.base_time = params['base_time']
        self.base_hour, self.base_minute = split_hour_min(self.base_time)
        self.sell_time = params['sell_time']
        self.sell_hour, self.sell_minute = split_hour_min(self.sell_time)
        self.buy_base_price = {}
        self.tai_range = params['range']

    def init_trading(self, quote):
        return super(VolatilityBreakoutStrategy, self).init_trading(quote)

    def get_list_of_indicators_for_vbt(self, market, tick, buy_base_price, tmgr):
        return [tick.close, buy_base_price[market]]

    def signal_buy(self, *args):
        if len(args) != 2:
            return False

        close = args[0]
        base_price = args[1]
        return True if close > base_price else False

    def perform(self, quote):
        super(VolatilityBreakoutStrategy, self).perform(quote)
        if self.is_paused:
            return
        time_dt = quote.get_time()
        tmgr = TAIMgr(quote, self.ex_type)
        market_ticks = quote.get_market_ticks(self.ex_type)
        #########################################################################
        # NeedToPostProcessing = False

        is_base_time = is_the_time(time_dt, self.base_hour, self.base_minute)
        is_sell_time = is_the_time(time_dt, self.sell_hour, self.sell_minute)

        evaluated_balance, _ = self.asset_mgmt.compute_evaluated_balance(market_ticks)
        if evaluated_balance < self.asset_mgmt.get_minumum_base_amount_for_rebalance():
            log.info(f'No Cash!! {evaluated_balance} Simulation will be terminated!')
            return

        if is_base_time:
            market_range = tmgr.get_unary(self.tai_range[0], self.tai_range[1], self.tai_range[2], self.tai_range[3])
            market_vol5 = compute_vol5(quote, tmgr, self.ex_type)
            self.asset_mgmt.append_supplements(market_vol5)
            if self.enable_asset_rebalance:
                self.asset_mgmt.rebalance(market_ticks)

            for market in market_ticks:
                tick = market_ticks[market]
                today_open = tick.open
                yesterday_range = market_range[market]
                self.buy_base_price[market] = today_open + self.k * yesterday_range

        for market in market_ticks:
            tick = market_ticks[market]
            base_price = self.buy_base_price[market]

            # for simulation boosting
            buy_trade_result = self.asset_mgmt.get_opened_buy_position(market)
            if self.context.backtestor is not None and buy_trade_result \
                    is not None and not is_sell_time:
                continue

            if buy_trade_result is None:
                log.info(f'[{tick.datetime}] {tick.market} Time Check for BUY Order:: '
                         f'price({tick.close}) > base_price({base_price:.2f}), '
                         f'Market Bal({self.asset_mgmt.get_market_cash_balance(market):.2f})..')

                signal_indicator_list = self.get_list_of_indicators_for_vbt(market, tick, self.buy_base_price, tmgr)

                if self.signal_buy(*signal_indicator_list):
                    desc = f', base:{base_price} at {dt2str(time_dt)}'
                    super(VolatilityBreakoutStrategy, self).process_enter_long_position(market, tick, tick.close, desc)

            # When it turns 8:59, it perform sell order if the buy order exists.
            if buy_trade_result != None and buy_trade_result.date != tick.datetime:
                log.info(f'[{tick.datetime}] {tick.market} Time Check:checking for SELL Order:: '
                         f'price({tick.close})...')

                if is_sell_time:
                    super(VolatilityBreakoutStrategy, self).process_exit_long_position(buy_trade_result, market, tick, tick.close, '')
                    # NeedToPostProcessing = True

        if is_base_time:
            super(VolatilityBreakoutStrategy, self).process_settle(time_dt, market_ticks)


class VolBout_WS(VolatilityBreakoutStrategy):
    def __init__(self):
        super(VolBout_WS, self).__init__()

    def set_params(self, am, report_storage, markets, params):
        super(VolBout_WS, self).set_params(am, report_storage, markets, params)
        self.tai_ma = params['ma']

    def get_list_of_indicators_for_vbt(self, market, tick, buy_base_price, tmgr):
        ma = tmgr.get_unary(self.tai_ma[0], self.tai_ma[1], self.tai_ma[2], self.tai_ma[3])
        return [tick.close, buy_base_price[market], ma[market]]

    def signal_buy(self, *args):
        if len(args) != 3:
            return False

        close = args[0]
        base_price = args[1]
        ma5 = args[2]
        return True if (close > base_price) and (close > ma5) else False


class VolBout_SWS(VolatilityBreakoutStrategy):
    def __init__(self):
        super(VolBout_SWS, self).__init__()

    def set_params(self, am, report_storage, markets, params):
        super(VolBout_SWS, self).set_params(am, report_storage, markets, params)
        self.tai_ma1 = params['ma1']
        self.tai_ma2 = params['ma2']
        self.tai_ma3 = params['ma3']
        self.tai_ma4 = params['ma4']

    def get_list_of_indicators_for_vbt(self, market, tick, buy_base_price, tmgr):
        ma1 = self.__get_ma__(tmgr, self.tai_ma1)
        ma2 = self.__get_ma__(tmgr, self.tai_ma2)
        ma3 = self.__get_ma__(tmgr, self.tai_ma3)
        ma4 = self.__get_ma__(tmgr, self.tai_ma4)
        return [tick.close, buy_base_price[market], ma1[market], ma2[market], ma3[market], ma4[market]]

    def __get_ma__(self, tmgr, tai_ma):
        return tmgr.get_unary(tai_ma[0], tai_ma[1], tai_ma[2], tai_ma[3])

    def signal_buy(self, *args):
        if len(args) != 6:
            return False

        close = args[0]
        base_price = args[1]
        ma3 = args[2]
        ma5 = args[3]
        ma10= args[4]
        ma20= args[5]
        result = True if (close > base_price) and (close > ma3) \
                   and (close > ma5)        and (close > ma10)\
                   and (close > ma20)       else False
        return result

class HdgeVBoutBasePriceMgr:
    def __init__(self, markets, timeframes, k, tai_rng_tf):
        self.buy_base_price = {}
        self.markets = markets
        self.timeframes = timeframes
        self.k = k
        self.tai_rng_tf = tai_rng_tf

        for market in self.markets:
            self.buy_base_price[market] = {}        # for maintaining market timeframes
            for timeframe in self.timeframes:
                self.buy_base_price[market][timeframe] = 0

    def update_market_base_price_for_timeframe(self, time_dt, expected_timeframe_str, market_h_range):
        for market in self.markets:
            yesterday_range = market_h_range[market][0]  # Range
            yesterday_close = market_h_range[market][1]  # close
            # base_price = today_open + self.k * yesterday_range  ## 이슈: 9:00의 시가로 해야하는데, 8:59분 종가로 open을 맞춰줌 약간의 오차 발생함
            base_price = yesterday_close + self.k * yesterday_range
            self.buy_base_price[market][expected_timeframe_str] = base_price
            log.info(f'[{dt2str(time_dt)}] Cal. BasePrice {market}-{expected_timeframe_str} : base_price({base_price}) = yes_clo({yesterday_close}) + '
                     f' k({self.k}) * yes_rage({yesterday_range})')

    def init_all_base_prices(self, quote, tmgr):
        time_dt = quote.get_time()

        for timeframe in self.timeframes:
            tf_hour, _ = split_hour_min(timeframe)
            timeframe_hour = tf_hour + 1
            if timeframe_hour == 24:
                timeframe_hour = 0
            h_range_key = f'DAYS_{timeframe_hour}'  # it should be matched with that of euote dispatcher
            cdl_type = CandleType[h_range_key]
            market_h_range = tmgr.get_nary(self.tai_rng_tf[0], self.tai_rng_tf[1],
                                                      cdl_type, self.tai_rng_tf[3])
            self.update_market_base_price_for_timeframe(time_dt, timeframe, market_h_range)

    def get_base_price(self, market, timeframe):
        return self.buy_base_price[market][timeframe]


class VolatilityBreakoutStrategy_Hdge(AbstractStrategy):
    def __init__(self):
        super(VolatilityBreakoutStrategy_Hdge, self).__init__()

    def set_params(self, am, report_storage, markets, params):
        self.ex_type = params['quote_provider']
        super(VolatilityBreakoutStrategy_Hdge, self).set_params(am, report_storage, markets, self.ex_type)
        self.k = params['k']
        self.timeframes = params['timeframes']
        self.tai_rng_tf = params['rng_tf']
        self.base_price_mgr = HdgeVBoutBasePriceMgr(markets, self.timeframes, self.k, self.tai_rng_tf)

    def init_trading(self, quote):
        tmgr = TAIMgr(quote, self.ex_type)
        self.base_price_mgr.init_all_base_prices(quote, tmgr)
        return super(VolatilityBreakoutStrategy_Hdge, self).init_trading(quote)

    def get_list_of_indicators_for_vbt(self, market, tick, base_price, tmgr):
        return [tick.close, base_price]

    def signal_buy(self, *args):
        if len(args) != 2:
            return False

        close = args[0]
        base_price = args[1]
        return True if close > base_price else False

    def perform(self, quote):
        super(VolatilityBreakoutStrategy_Hdge, self).perform(quote)
        if self.is_paused:
            return
        time_dt = quote.get_time()
        tmgr = TAIMgr(quote, self.ex_type)
        market_ticks = quote.get_market_ticks(self.ex_type)
        #########################################################################

        is_vol_update_time = is_the_time(time_dt, 8, 59)
        is_matched, expected_timeframe_str, timeframe_hour = match_time_frame(time_dt, self.timeframes)

        evaluated_balance, _ = self.asset_mgmt.compute_evaluated_balance(market_ticks)
        if evaluated_balance < self.asset_mgmt.get_minumum_base_amount_for_rebalance():
            log.info(f'No Cash!! {evaluated_balance} Simulation will be terminated!')
            return

        if is_vol_update_time:  ## Rebalance only once a day!
            market_vol5 = compute_vol5(quote, tmgr, self.ex_type)
            self.asset_mgmt.append_supplements(market_vol5)
            if self.enable_asset_rebalance:
                self.asset_mgmt.rebalance(market_ticks)

        # Update market base price for this timeframe
        if is_matched:
            h_range_key = f'DAYS_{timeframe_hour}'  # it should be matched with that of euote dispatcher
            cdl_type = CandleType[h_range_key]
            market_h_range = tmgr.get_nary(self.tai_rng_tf[0], self.tai_rng_tf[1],
                                                     cdl_type, self.tai_rng_tf[3])
            self.base_price_mgr.update_market_base_price_for_timeframe(time_dt, expected_timeframe_str, market_h_range)

        ## For Buying based on the base price for each timeframe
        for market in market_ticks:
            tick = market_ticks[market]

            for timeframe in self.timeframes:
                base_price = self.base_price_mgr.get_base_price(market, timeframe)

                # for simulation boosting
                buy_trade_result = self.asset_mgmt.get_opened_buy_position(market, timeframe)
                if self.context.backtestor is not None and buy_trade_result is not None:
                    continue

                if buy_trade_result is None:
                    log.info(f'[{tick.datetime}] {tick.market} Time Check for BUY Order:: '
                             f'price({tick.close}) > base_price({base_price:.2f}), '
                             f'Market Bal({self.asset_mgmt.get_market_cash_balance(market):.2f}) for timeframe({timeframe}).')

                    signal_indicator_list = self.get_list_of_indicators_for_vbt(market, tick, base_price, tmgr)

                    if self.signal_buy(*signal_indicator_list):
                        desc = f', price({tick.close}) > base_price({base_price:.2f}) for timeframe({timeframe}) at {dt2str(time_dt)}'
                        super(VolatilityBreakoutStrategy_Hdge, self).process_enter_long_position(market, tick, tick.close, desc, timeframe)

        ## For Selling based on the base price for each timeframe
        if is_matched:
            for market in market_ticks:
                tick = market_ticks[market]
                buy_trade_result = self.asset_mgmt.get_opened_buy_position(market, expected_timeframe_str)
                if buy_trade_result is not None:
                    desc = f', volume({buy_trade_result.settled_vol}), timeframe({timeframe}) at {buy_trade_result.date}.'
                    super(VolatilityBreakoutStrategy_Hdge, self).process_exit_long_position(buy_trade_result, market, tick, tick.close, desc, expected_timeframe_str)
                    NeedToPostProcessing = True

            super(VolatilityBreakoutStrategy_Hdge, self).process_settle(time_dt, market_ticks)
        else:
            for market in market_ticks:
                tick = market_ticks[market]
                for timeframe in self.timeframes:
                    buy_trade_result = self.asset_mgmt.get_opened_buy_position(market, timeframe)
                    if buy_trade_result is not None:
                        log.info(f'[{tick.datetime}] {buy_trade_result.market} Time Check:checking for SELL Order:: '
                             f'volume({buy_trade_result.settled_vol}), timeframe({timeframe}) bought at {buy_trade_result.date}.')



class VolBout_WS_Hdge(VolatilityBreakoutStrategy_Hdge):
    def __init__(self):
        super(VolBout_WS_Hdge, self).__init__()

    def set_params(self, am, report_storage, markets, params):
        super(VolBout_WS_Hdge, self).set_params(am, report_storage, markets, params)
        self.tai_ma = params['ma']

    def get_list_of_indicators_for_vbt(self, market, tick, buy_base_price, tmgr):
        ma = self.__get_ma__(tmgr, self.tai_ma)
        return [tick.close, buy_base_price, ma[market]]

    def __get_ma__(self, tmgr, tai_ma):
        return tmgr.get_unary(tai_ma[0], tai_ma[1], tai_ma[2], tai_ma[3])

    def signal_buy(self, *args):
        if len(args) != 3:
            return False

        close = args[0]
        base_price = args[1]
        ma5 = args[2]
        return True if (close > base_price) and (close > ma5) else False


class VolBout_SWS_Hdge(VolatilityBreakoutStrategy_Hdge):
    def __init__(self):
        super(VolBout_SWS_Hdge, self).__init__()

    def set_params(self, am, report_storage, markets, params):
        super(VolBout_SWS_Hdge, self).set_params(am, report_storage, markets, params)
        self.tai_ma1 = params['ma1']
        self.tai_ma2 = params['ma2']
        self.tai_ma3 = params['ma3']
        self.tai_ma4 = params['ma4']

    def get_list_of_indicators_for_vbt(self, market, tick, buy_base_price, tmgr):
        ma1 = get_ma(tmgr, self.tai_ma1)
        ma2 = get_ma(tmgr, self.tai_ma2)
        ma3 = get_ma(tmgr, self.tai_ma3)
        ma4 = get_ma(tmgr, self.tai_ma4)
        return [tick.close, buy_base_price, ma1[market], ma2[market], ma3[market], ma4[market]]

    def signal_buy(self, *args):
        if len(args) != 6:
            return False

        close = args[0]
        base_price = args[1]
        ma3 = args[2]
        ma5 = args[3]
        ma10= args[4]
        ma20= args[5]
        result = True if (close > base_price) and (close > ma3) \
                   and (close > ma5)        and (close > ma10)\
                   and (close > ma20)       else False
        return result