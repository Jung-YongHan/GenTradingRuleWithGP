from bt4.Constants import CandleType
from bt4.quote.TAIMgr import TAIMgr
from bt4.utils.market_utils import match_time_frame, compute_vol5
from bt4.utils.mylog import init_log
from bt4.utils.python_utils import split_hour_min, is_the_time
from bt4.utils.tai_utils import get_unary_tai
from bt4.strategy.Strategy import AbstractNettingStrategy, AbstractHedgingStrategy

log = init_log()


class SWKimStrategy1(AbstractNettingStrategy):

    def __init__(self):
        super(SWKimStrategy1, self).__init__()

    def load_tai_params(self, params) :
        self.base_time = params['base_time']
        self.base_hour, self.base_minute = split_hour_min(self.base_time)
        self.tai_plus_di  = params['tai_plus_di']
        self.tai_minus_di = params['tai_minus_di']

    def __is_rebalance_time__(self, time_dt) :
        return True if time_dt.hour == self.base_hour \
                       and time_dt.minute == self.base_minute\
            else False

    def __isBuySignal__(self, market_tai, tmgr, market, price, time_dt):
        is_base_time = is_the_time(time_dt, self.base_hour, self.base_minute)

        pdi = market_tai[market]['pdi']
        mdi = market_tai[market]['mdi']

        tai_signal = False
        if pdi > mdi:
            tai_signal = True

        return is_base_time and tai_signal, f"(@{self.base_time}) pdi({pdi}) > mdi({mdi})"

    def __isSellSignal__(self, market_tai, tmgr, market, price, time_dt):
        is_sell_time = is_the_time(time_dt, self.base_hour, self.base_minute)

        pdi = market_tai[market]['pdi']
        mdi = market_tai[market]['mdi']

        tai_sell_signal = False
        if pdi < mdi:
            tai_sell_signal = True

        return is_sell_time and tai_sell_signal, f"(@{self.base_time}) pdi({pdi}) < mdi({mdi})"

    def extract_tai(self, tmgr):
        mkt_pdi = get_unary_tai(tmgr, self.tai_plus_di)
        mkt_mdi = get_unary_tai(tmgr, self.tai_minus_di)

        quote = tmgr.get_quote()
        market_ticks = quote.get_market_ticks(tmgr.ex_type)

        market_tais = {}
        for market in market_ticks:
            market_tais[market] = {}
            market_tais[market]['pdi'] = mkt_pdi[market]
            market_tais[market]['mdi'] = mkt_mdi[market]
        return market_tais


class SWKimStrategy1_4H(SWKimStrategy1):

    def __init__(self):
        super(SWKimStrategy1_4H, self).__init__()

    def __isBuySignal__(self, market_tai, tmgr, market, price, time_dt):
        is_trading_hour = self.is_trading_hour(time_dt)

        pdi = market_tai[market]['pdi']
        mdi = market_tai[market]['mdi']

        tai_signal = False
        if pdi > mdi:
            tai_signal = True

        return is_trading_hour and tai_signal, f"(@{time_dt}) pdi({pdi}) > mdi({mdi})"

    def is_trading_hour(self, time_dt):
        trading_hours = ['00:59', '04:59', '08:59', '12:59', '16:59', '20:59']
        for th in trading_hours:
            hour, min = split_hour_min(th)
            if is_the_time(time_dt, hour, min):
                return True
        return False

    def __isSellSignal__(self, market_tai, tmgr, market, price, time_dt):
        is_sell_time = self.is_trading_hour(time_dt)

        pdi = market_tai[market]['pdi']
        mdi = market_tai[market]['mdi']

        tai_sell_signal = False
        if pdi < mdi:
            tai_sell_signal = True

        return is_sell_time and tai_sell_signal, f"(@{time_dt}) pdi({pdi}) < mdi({mdi})"



class SWKimStrategy1_Hdge(AbstractHedgingStrategy):

    def __init__(self):
        super(SWKimStrategy1_Hdge, self).__init__()

    def load_tai_params(self, params):
        self.tai_plus_di_tf  = params['tai_plus_di_tf']
        self.tai_minus_di_tf = params['tai_minus_di_tf']

    def __isBuySignal__(self, mkt_buy_tais, tmgr, market, price, time_dt, tf_hour):
        pdi = mkt_buy_tais[market]['pdi']
        mdi = mkt_buy_tais[market]['mdi']
        tai_signal = False
        if pdi > mdi:
            tai_signal = True
        return tai_signal, f"(@{time_dt}) pdi({pdi}) > mdi({mdi})"

    def __isSellSignal__(self, mkt_sell_tais, tmgr, market, price, time_dt, tf_hour) :
        pdi = mkt_sell_tais[market]['pdi']
        mdi = mkt_sell_tais[market]['mdi']
        tai_sell_signal = False
        if pdi < mdi:
            tai_sell_signal = True
        return tai_sell_signal, f"(@{time_dt}) pdi({pdi}) < mdi({mdi})"

    def extract_tai(self, tmgr, timeframe_hour):
        self.tai_plus_di_tf[2] = CandleType[f'DAYS_{timeframe_hour}']
        self.tai_minus_di_tf[2] = CandleType[f'DAYS_{timeframe_hour}']

        mkt_pdi = get_unary_tai(tmgr, self.tai_plus_di_tf)
        mkt_mdi = get_unary_tai(tmgr, self.tai_minus_di_tf)

        quote = tmgr.get_quote()
        market_ticks = quote.get_market_ticks(tmgr.ex_type)

        market_tai = {}
        for market in market_ticks:
            market_tai[market] = {}
            market_tai[market]['pdi'] = mkt_pdi[market]
            market_tai[market]['mdi'] = mkt_mdi[market]

        return market_tai


    def perform(self, quote):
        super(SWKimStrategy1_Hdge, self).perform(quote)
        if self.is_paused:
            return
        time_dt = quote.get_time()
        tmgr = TAIMgr(quote, self.ex_type)
        market_ticks = quote.get_market_ticks(self.ex_type)
        #########################################################################
        is_vol_update_time = is_the_time(time_dt, 8, 59)
        is_buy_time, expected_buy_timeframe_str, buy_tf_hour = match_time_frame(time_dt, self.buy_timeframes)
        is_sell_time, expected_sell_timeframe_str, sell_tf_hour = match_time_frame(time_dt, self.sell_timeframes)

        if is_vol_update_time:      ## Rebalance only once a day!
            market_vol5 = compute_vol5(quote, tmgr, self.ex_type)
            self.asset_mgmt.append_supplements(market_vol5)
            if self.enable_asset_rebalance:
                self.asset_mgmt.rebalance(market_ticks)

        # if is_buy_time or is_sell_time:
        for market in market_ticks:
            tick = market_ticks[market]

            #######################################################
            ## Processing Buy

            market_buy_tf_key = f'DAYS_{buy_tf_hour}'
            cdl_type = CandleType[market_buy_tf_key]
            self.tai_plus_di_tf[2] = cdl_type
            sell_market_plus_di = get_unary_tai(tmgr, self.tai_plus_di_tf)
            self.tai_minus_di_tf[2] = cdl_type
            sell_market_minus_di = get_unary_tai(tmgr, self.tai_minus_di_tf)

            p_di = sell_market_plus_di[market]
            m_di = sell_market_minus_di[market]

            buy_trade_result = self.asset_mgmt.get_opened_buy_position(market, expected_buy_timeframe_str)
            if buy_trade_result is None:
                log.info(
                    f'[{tick.datetime}] {tick.market} Time Check for BUY Order(@{expected_buy_timeframe_str}):: '
                    f'price({tick.close}),p_di({p_di:.2f}) > m_di({m_di:.2f}), '
                    f'Market Bal({self.asset_mgmt.get_market_cash_balance(market):.2f})..')
                if is_buy_time and p_di > m_di:  ## Buy Signal (At 9 AM)
                    super(SWKimStrategy1_Hdge, self).process_enter_long_position(market, tick, tick.close,
                                                                     f', p_di({p_di:.2f}) > m_di({m_di:.2f})', expected_buy_timeframe_str)

            market_sell_tf_key = f'DAYS_{sell_tf_hour}'
            cdl_type = CandleType[market_sell_tf_key]
            self.tai_plus_di_tf[2] = cdl_type
            sell_market_plus_di = get_unary_tai(tmgr, self.tai_plus_di_tf)
            self.tai_minus_di_tf[2] = cdl_type
            sell_market_minus_di = get_unary_tai(tmgr, self.tai_minus_di_tf)

            p_di = sell_market_plus_di[market]
            m_di = sell_market_minus_di[market]

            matched_buy_timeframe_str = self.sell_buy_tf[expected_sell_timeframe_str]
            matched_buy_trade_result = self.asset_mgmt.get_opened_buy_position(market, matched_buy_timeframe_str)

            if matched_buy_trade_result is not None and matched_buy_trade_result.date != tick.datetime:
                log.info(
                    f'[{tick.datetime}] {tick.market} Time Check:checking '
                    f'for SELL Order(sell time ({expected_sell_timeframe_str}) for buy tf({matched_buy_timeframe_str}):: '
                    f'price({tick.close}),p_di({p_di:.2f}) < m_di({m_di:.2f}) ')

                if is_sell_time and p_di < m_di:  ## Sell Signal (Next days' close price is under MA(5))
                    super(SWKimStrategy1_Hdge, self).process_exit_long_position(matched_buy_trade_result, market, tick,
                                                                                tick.close,
                                                                      f', p_di({p_di:.2f}) < m_di({m_di:.2f})', matched_buy_timeframe_str)

        if is_vol_update_time:
            super(SWKimStrategy1_Hdge, self).process_settle(time_dt, market_ticks)
