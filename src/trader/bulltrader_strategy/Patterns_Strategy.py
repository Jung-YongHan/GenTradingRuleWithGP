from bt4.utils.market_utils import pick_market_unary_tais
from bt4.Constants import CandleType
from bt4.utils.mylog import init_log
from bt4.strategy.Strategy import AbstractStrategy

log = init_log()

class Patterns_Strategy(AbstractStrategy):

    def __init__(self):
        super(Patterns_Strategy, self).__init__()

    def set_params(self, am, report_storage, markets, params):
        super(Patterns_Strategy, self).set_params(am, report_storage, markets)
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
        return super(Patterns_Strategy, self).initialize_right_before_trading(time_dt, market_ticks,
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

        market_engulfing_for_buys = self.__get_tais(self.buy_tai_keys, market, ta_indicators)
        market_engulfing_for_sells = self.__get_tais(self.sell_tai_keys, market, ta_indicators)

        buy_condition = True
        desc = ''
        for market_engulfing_for_buy, market_engulfing_for_sell, buy_tai_key, sell_tai_key in zip(market_engulfing_for_buys, market_engulfing_for_sells, self.buy_tai_keys, self.sell_tai_keys):
            if market_engulfing_for_buy != 100:
                desc = desc + f',{buy_tai_key}({market_engulfing_for_buy}) != 100'
                buy_condition = False
                break
            else:
                desc = desc + f',{buy_tai_key}({market_engulfing_for_buy}) == 100'

        return buy_condition, desc

    def is_sell_condition(self, *args):
        tick = args[0]
        market = args[1]
        ta_indicators = args[3]

        market_engulfing_for_buys = self.__get_tais(self.buy_tai_keys, market, ta_indicators)
        market_engulfing_for_sells = self.__get_tais(self.sell_tai_keys, market, ta_indicators)

        sell_condition = True
        desc = ''
        for market_engulfing_for_buy, market_engulfing_for_sell, buy_tai_key, sell_tai_key in zip(market_engulfing_for_buys, market_engulfing_for_sells,
                                                                                    self.buy_tai_keys,
                                                                                    self.sell_tai_keys):
            if market_engulfing_for_buy != -100:
                desc = desc + f',{buy_tai_key}({market_engulfing_for_buy}) != 100'
                sell_condition = False
                break
            else:
                desc = desc + f',{buy_tai_key}({market_engulfing_for_buy}) == -100'

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
                    super(Patterns_Strategy, self).process_enter_long_position(market, tick, tick.trade_price, desc)

            if buy_trade_result is not None and buy_trade_result.date != tick.candle_date_time_kst:
                sell_conditions, desc = self.is_sell_condition(tick, market, self.sell_tai_keys, ta_indicators)

                log.info(f'[{tick.candle_date_time_kst}] {tick.market} Check:checking for SELL Order(@{trading_time_str}):: ' + desc)

                if sell_conditions:
                        super(Patterns_Strategy, self).process_exit_long_position(buy_trade_result, market, tick,
                                                                                  tick.trade_price, desc)

        if is_trading_timing:
            if self.enable_asset_rebalance:
                self.asset_mgmt.rebalance(market_ticks)
            super(Patterns_Strategy, self).process_settle(time_dt, market_ticks)

