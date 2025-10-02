from bt4.utils.market_utils import pick_market_unary_tais, pick_market_nary_tais
from bt4.Constants import CandleType
from bt4.utils.mylog import init_log
from bt4.strategy.Strategy import AbstractStrategy

log = init_log()

## No Rebalancing
class FRL_Price_Strategy(AbstractStrategy):

    def __init__(self):
        super(FRL_Price_Strategy, self).__init__()

    def set_params(self, am, report_storage, markets, params):
        super(FRL_Price_Strategy, self).set_params(am, report_storage, markets)
        self.candle_type = params['candle_type']
        self.trading_type = params['trading_type']

        self.buy_tai_key = params['buy_tai']
        self.sell_tai_key = params['sell_tai']
        if self.candle_type == CandleType.HOUR4:
            self.buy_tai_key = f'{self.buy_tai_key}_4h'
            self.sell_tai_key = f'{self.sell_tai_key}_4h'
        elif self.candle_type == CandleType.HOUR:
            self.buy_tai_key = f'{self.buy_tai_key}_1h'
            self.sell_tai_key = f'{self.sell_tai_key}_1h'

    def initialize_right_before_trading(self, time_dt, market_ticks, ta_indicators):
        return super(FRL_Price_Strategy, self).initialize_right_before_trading(time_dt, market_ticks,
                                                                                    ta_indicators)

    def __is_trading_timing(self, candle_type, time_dt):
        current_hour = time_dt.hour
        current_minute = time_dt.minute

        if candle_type == CandleType.DAYS:
            if current_hour == 8 and current_minute == 59:
                return True, '08:59'
        elif candle_type == CandleType.HOUR4:
            if current_hour % 4 == 0 and current_minute == 59:
                return True, 'Each (H%4==0):59'
        elif candle_type == CandleType.HOUR:
            if current_minute == 59:
                return True, 'Each HH:59'
        elif candle_type == CandleType.MINUTES_1:
            return True, 'Every Min'

        return False, ''

    def is_buy_condition(self, *args):
        tick = args[0]
        market = args[1]
        buy_tai_key = args[2]
        ta_indicators = args[3]

        price_bases = pick_market_unary_tais(ta_indicators, buy_tai_key)
        market_price_base = price_bases[market]

        buy_condition = True if tick.trade_price > market_price_base else False
        desc = f'price({tick.trade_price:,}) > {buy_tai_key}({market_price_base})'
        return buy_condition, desc

    def is_sell_condition(self, *args):
        tick = args[0]
        market = args[1]
        sell_tai_key = args[2]
        ta_indicators = args[3]

        price_bases = pick_market_unary_tais(ta_indicators, sell_tai_key)
        market_price_base = price_bases[market]

        sell_condition = True if tick.trade_price < market_price_base else False
        desc = f'price({tick.trade_price:,}) < {sell_tai_key}({market_price_base})'
        return sell_condition, desc

    def perform(self, time_dt, market_ticks, ta_indicators):
        is_trading_timing, trading_time_str = self.__is_trading_timing(self.trading_type, time_dt)

        if not is_trading_timing:
            return

        for market in market_ticks:
            tick = market_ticks[market]

            buy_trade_result = self.asset_mgmt.get_opened_buy_position(market)
            if buy_trade_result is None:
                buy_conditions, desc = self.is_buy_condition(tick, market, self.buy_tai_key, ta_indicators)
                log.info(
                    f'[{tick.candle_date_time_kst}] {tick.market} Time Check for BUY Order(@{trading_time_str})::' + desc)

                if buy_conditions:
                    super(FRL_Price_Strategy, self).process_enter_long_position(market, tick, tick.trade_price, desc)

            if buy_trade_result is not None and buy_trade_result.date != tick.candle_date_time_kst:
                sell_conditions, desc = self.is_sell_condition(tick, market, self.sell_tai_key, ta_indicators)

                log.info(f'[{tick.candle_date_time_kst}] {tick.market} Check:checking for SELL Order(@{trading_time_str}):: ' + desc)

                if sell_conditions:
                        super(FRL_Price_Strategy, self).process_exit_long_position(buy_trade_result, market, tick,
                                                                                   tick.trade_price, desc)

        if is_trading_timing:
            if self.enable_asset_rebalance:
                self.asset_mgmt.rebalance(market_ticks)
            super(FRL_Price_Strategy, self).process_settle(time_dt, market_ticks)


class FRL_MACD_Strategy(FRL_Price_Strategy):

    def __init__(self):
        super(FRL_Price_Strategy, self).__init__()

    def is_buy_condition(self, *args):
        tick = args[0]
        market = args[1]
        buy_tai_key = args[2]
        ta_indicators = args[3]

        macd_bases = pick_market_nary_tais(ta_indicators, buy_tai_key)
        market_macd_bases = macd_bases[market]
        market_macd = market_macd_bases[0]
        market_signal = market_macd_bases[1]

        buy_condition = True if market_macd > market_signal else False
        desc = f'macd({market_macd}) > signal({market_signal})'
        return buy_condition, desc

    def is_sell_condition(self, *args):
        tick = args[0]
        market = args[1]
        sell_tai_key = args[2]
        ta_indicators = args[3]

        macd_bases = pick_market_nary_tais(ta_indicators, sell_tai_key)
        market_macd_bases = macd_bases[market]
        market_macd = market_macd_bases[0]
        market_signal = market_macd_bases[1]

        sell_condition = True if market_macd < market_signal else False
        desc = f'macd({market_macd}) < signal({market_signal})'
        return sell_condition, desc


class FRL_RSI_Strategy(FRL_Price_Strategy):

    def __init__(self):
        super(FRL_RSI_Strategy, self).__init__()
        self.UPPER = 70
        self.LOWER = 30

    def is_buy_condition(self, *args):
        tick = args[0]
        market = args[1]
        buy_tai_key = args[2]
        ta_indicators = args[3]

        rsi_bases = pick_market_unary_tais(ta_indicators, buy_tai_key)
        market_rsi = rsi_bases[market]

        buy_condition = True if market_rsi < self.LOWER else False
        desc = f'rsi({market_rsi}) < LOWER({self.LOWER})'
        return buy_condition, desc

    def is_sell_condition(self, *args):
        tick = args[0]
        market = args[1]
        buy_tai_key = args[2]
        ta_indicators = args[3]

        rsi_bases = pick_market_unary_tais(ta_indicators, buy_tai_key)
        market_rsi = rsi_bases[market]

        sell_condition = True if market_rsi > self.UPPER else False
        desc = f'rsi({market_rsi}) > UPPER({self.UPPER})'
        return sell_condition, desc


class FRL_PLUS_MINUS_DI_Strategy(FRL_Price_Strategy):

    def __init__(self):
        super(FRL_PLUS_MINUS_DI_Strategy, self).__init__()

    def is_buy_condition(self, *args):
        tick = args[0]
        market = args[1]
        ta_indicators = args[3]

        plui_di_bases = pick_market_unary_tais(ta_indicators, self.buy_tai_key)
        market_plus_di = plui_di_bases[market]

        minus_di_bases = pick_market_unary_tais(ta_indicators, self.sell_tai_key)
        market_minus_di = minus_di_bases[market]

        buy_condition = True if market_plus_di > market_minus_di else False
        desc = f'plus_di({market_plus_di}) > minus_di({market_minus_di})'
        return buy_condition, desc

    def is_sell_condition(self, *args):
        tick = args[0]
        market = args[1]
        ta_indicators = args[3]

        plui_di_bases = pick_market_unary_tais(ta_indicators, self.buy_tai_key)
        market_plus_di = plui_di_bases[market]

        minus_di_bases = pick_market_unary_tais(ta_indicators, self.sell_tai_key)
        market_minus_di = minus_di_bases[market]

        sell_condition = True if market_plus_di < market_minus_di else False
        desc = f'plus_di({market_plus_di}) < minus_di({market_minus_di})'
        return sell_condition, desc


class FRL_SUPER_PLUS_MINUS_DI_Strategy(AbstractStrategy):

    def __init__(self):
        super(FRL_SUPER_PLUS_MINUS_DI_Strategy, self).__init__()

    def set_params(self, am, report_storage, markets, params):
        super(FRL_SUPER_PLUS_MINUS_DI_Strategy, self).set_params(am, report_storage, markets)
        self.candle_type = params['candle_type']
        self.trading_type = params['trading_type']

        self.buy_tai_keys = params['buy_tais']
        self.sell_tai_keys = params['sell_tais']

        if self.candle_type == CandleType.HOUR4:
            self.buy_tai_keys = self.__make_tai_keys(self.buy_tai_keys, '_4h')
            self.sell_tai_keys = self.__make_tai_keys(self.sell_tai_keys, '_4h')

        elif self.candle_type == CandleType.HOUR:
            self.buy_tai_keys = self.__make_tai_keys(self.buy_tai_keys, '_1h')
            self.sell_tai_keys = self.__make_tai_keys(self.sell_tai_keys, '_1h')

    def __make_tai_keys(self, tai_keys, post_fix):
        tai_key_list = []
        for tai_key in tai_keys:
            tai_key_list.append(f'{tai_key}_4h')
        return tai_key_list


    def initialize_right_before_trading(self, time_dt, market_ticks, ta_indicators):
        return super(FRL_SUPER_PLUS_MINUS_DI_Strategy, self).initialize_right_before_trading(time_dt, market_ticks,
                                                                                    ta_indicators)

    def __is_trading_timing(self, candle_type, time_dt):
        current_hour = time_dt.hour
        current_minute = time_dt.minute

        if candle_type == CandleType.DAYS:
            if current_hour == 8 and current_minute == 59:
                return True, '08:59'
        elif candle_type == CandleType.HOUR4:
            if current_hour % 4 == 0 and current_minute == 59:
                return True, 'Each (H%4==0):59'
        elif candle_type == CandleType.HOUR:
            if current_minute == 59:
                return True, 'Each HH:59'
        elif candle_type == CandleType.MINUTES_1:
            return True, 'Every Min'

        return False, ''

    def __get_tais(self, tai_keys,  market, ta_indicators):
        market_tais = []
        for tai_key in tai_keys:
            price_bases = pick_market_unary_tais(ta_indicators, tai_key)
            market_tais.append(price_bases[market])
        return market_tais

    def is_buy_condition(self, *args):
        tick = args[0]
        market = args[1]
        ta_indicators = args[3]

        market_plus_dis = self.__get_tais(self.buy_tai_keys, market, ta_indicators)
        market_minus_dis = self.__get_tais(self.sell_tai_keys, market, ta_indicators)

        buy_condition = True
        desc = ''
        for market_plus_di, market_minus_di, buy_tai_key, sell_tai_key in zip(market_plus_dis, market_minus_dis, self.buy_tai_keys, self.sell_tai_keys):
            if market_plus_di <= market_minus_di:
                desc = desc + f',{buy_tai_key}({market_plus_di}) < {sell_tai_key}({market_minus_di})'
                buy_condition = False
                break
            else:
                desc = desc + f',{buy_tai_key}({market_plus_di}) > {sell_tai_key}({market_minus_di})'

        return buy_condition, desc

    def is_sell_condition(self, *args):
        tick = args[0]
        market = args[1]
        ta_indicators = args[3]

        market_plus_dis = self.__get_tais(self.buy_tai_keys, market, ta_indicators)
        market_minus_dis = self.__get_tais(self.sell_tai_keys, market, ta_indicators)

        sell_condition = True
        desc = ''
        for market_plus_di, market_minus_di, buy_tai_key, sell_tai_key in zip(market_plus_dis, market_minus_dis,
                                                                                    self.buy_tai_keys,
                                                                                    self.sell_tai_keys):
            if market_plus_di > market_minus_di:
                desc = desc + f',{buy_tai_key}({market_plus_di}) > {sell_tai_key}({market_minus_di})'
                sell_condition = False
                break
            else:
                desc = desc + f',{buy_tai_key}({market_plus_di}) <= {sell_tai_key}({market_minus_di})'

        return sell_condition, desc

    def perform(self, time_dt, market_ticks, ta_indicators):
        is_trading_timing, trading_time_str = self.__is_trading_timing(self.trading_type, time_dt)

        if not is_trading_timing:
            return

        for market in market_ticks:
            tick = market_ticks[market]

            buy_trade_result = self.asset_mgmt.get_opened_buy_position(market)
            if buy_trade_result is None:
                buy_conditions, desc = self.is_buy_condition(tick, market, self.buy_tai_keys, ta_indicators)
                log.info(
                    f'[{tick.candle_date_time_kst}] {tick.market} Time Check for BUY Order(@{trading_time_str})::' + desc)

                if buy_conditions:
                    super(FRL_SUPER_PLUS_MINUS_DI_Strategy, self).process_enter_long_position(market, tick, tick.trade_price, desc)

            if buy_trade_result is not None and buy_trade_result.date != tick.candle_date_time_kst:
                sell_conditions, desc = self.is_sell_condition(tick, market, self.sell_tai_keys, ta_indicators)

                log.info(f'[{tick.candle_date_time_kst}] {tick.market} Check:checking for SELL Order(@{trading_time_str}):: ' + desc)

                if sell_conditions:
                        super(FRL_SUPER_PLUS_MINUS_DI_Strategy, self).process_exit_long_position(buy_trade_result, market, tick,
                                                                                                 tick.trade_price, desc)

        if is_trading_timing:
            if self.enable_asset_rebalance:
                self.asset_mgmt.rebalance(market_ticks)
            super(FRL_SUPER_PLUS_MINUS_DI_Strategy, self).process_settle(time_dt, market_ticks)

