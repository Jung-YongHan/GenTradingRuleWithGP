import json
import uuid

from bt4.Constants import Operation_Type
from bt4.model.trade_object import Trade
import bt4.GlobalProperties as global_prop
from bt4.model.state_mgr import StateStorage
from bt4.utils.mylog import init_log
import time
from abc import *
log = init_log()

'''
For Two Trade Operation Types
 - Netting : Only one trade at a time
 - Hedging : Many trades at a time
'''
class TradeMgr(metaclass=ABCMeta):

    def __init__(self, op_type):
        self.op_type = op_type

    @abstractmethod
    def initialize(self, markets, timeframes = None) -> None:
        self.markets = markets
        self.trade_recover_mgr = TradeStateRecoverMgr()

    @abstractmethod
    def synchronize_trade_states2(self, account, ex_type, am, quote) -> bool:
        pass

    @abstractmethod
    def exist_open_positions(self, market) -> bool:
        pass

    def handle_buy_position(self, buy_trade_result, timeframe_str = None) -> None:
        # The following code has been blocked due to the migration from file based into mongodb based trade statements.

        # if buy_trade_result.is_processed and self.op_type.value == Operation_Type.REAL_TRADING.value:
        #     self.trade_recover_mgr.store_trade_state(buy_trade_result, timeframe_str)
        pass

    @abstractmethod
    def get_opened_buy_position(self, market, timeframe_str = None) -> Trade:
        pass

    def handle_sell_position(self, sell_trade_result, timeframe_str = None) -> None:
        # The following code has been blocked due to the migration from file based into mongodb based trade statements.

        # if sell_trade_result.is_processed and self.op_type.value == Operation_Type.REAL_TRADING.value:
        #     self.trade_recover_mgr.resolve_trade_state(sell_trade_result, timeframe_str)
        pass

    def reset_trade_state(self, account, ex_type, tid):
        StateStorage.instance().remove_trade_states(account, ex_type, tid)


class NettingTradeMgr(TradeMgr):

    def __init__(self, op_type):
        super(NettingTradeMgr, self).__init__(op_type)

    def initialize(self, markets, timeframes=None) -> None:
        super(NettingTradeMgr, self).initialize(markets)
        self.opened_buy_tradings = {}
        for market in self.markets:
            self.opened_buy_tradings[market] = None

    def synchronize_trade_states2(self, account, ex_type, am, quote) -> bool:
        init_time_dt = quote.get_time()
        init_market_ticks = quote.get_market_ticks(ex_type)
        if self.op_type.value == Operation_Type.LIVE_TRADING.value or \
            self.op_type.value == Operation_Type.FORWARD_TESTING.value :
            for market in init_market_ticks:
                tick = init_market_ticks[market]
                buy_position = self.trade_recover_mgr.load_init_trade_states(account, ex_type, am, tick)
                if buy_position is not None:
                    self.opened_buy_tradings[market] = buy_position
        return True


    def handle_buy_position(self, buy_trade_result, timeframe_str = None) -> None:
        if buy_trade_result.is_processed:
            self.opened_buy_tradings[buy_trade_result.market] = buy_trade_result

        super(NettingTradeMgr, self).handle_buy_position(buy_trade_result, timeframe_str)

    def exist_open_positions(self, market) -> bool:
        trade = self.get_opened_buy_position(market)
        return True if trade is not None else False

    def get_opened_buy_position(self, market, timeframe_str = None) -> Trade:
        return self.opened_buy_tradings[market]

    def handle_sell_position(self, sell_trade_result, timeframe_str = None) -> None:
        self.opened_buy_tradings[sell_trade_result.market] = None
        super(NettingTradeMgr, self).handle_sell_position(sell_trade_result, timeframe_str)

class HedgingTradeMgr(TradeMgr):
    def __init__(self, op_type):
        super(HedgingTradeMgr, self).__init__(op_type)

    def initialize(self, markets, timeframes=None) -> None:
        super(HedgingTradeMgr, self).initialize(markets)
        if timeframes is None:
            return
        self.timeframes = timeframes

        # self.opened_buy_tradings[market] has already been created by calling the super.
        if timeframes is None or len(self.timeframes) == 0:
            err_msg = 'ERROR: Timeframes should be given for HedgingStrategy!'
            log.error(err_msg)
            raise RuntimeError(err_msg)

        self.opened_buy_tradings = {}
        for market in self.markets:
            self.opened_buy_tradings[market] = {}  ## Change Dic to manage multiple timeframes
            for timeframe in self.timeframes:
                self.opened_buy_tradings[market][timeframe] = None

    ## TODO: Should be tested (stkim: 2023-01-05)
    def synchronize_trade_states2(self, account, ex_type, am, quote) -> bool:
        init_time_dt = quote.get_time()
        init_market_ticks = quote.get_market_ticks(ex_type)
        for market in init_market_ticks:
            tick = init_market_ticks[market]

            for timeframe in self.timeframes:
                buy_position = self.trade_recover_mgr.load_init_trade_states(account, ex_type, am, tick, timeframe)
                self.opened_buy_tradings[market][timeframe] = buy_position
        return True


    def handle_buy_position(self, buy_trade_result, expected_timeframe_str) -> None:
        if buy_trade_result.is_processed:
            self.opened_buy_tradings[buy_trade_result.market][expected_timeframe_str] = buy_trade_result

        # super(HedgingTradeMgr, self).handle_buy_position(buy_trade_result, expected_timeframe_str)

    def exist_open_positions(self, market) -> bool:
        is_exist = False
        for timeframe_str in self.opened_buy_tradings[market]:
            trade = self.get_opened_buy_position(market,timeframe_str)
            if trade is not None:
                is_exist = True
                break

        return is_exist

    def get_opened_buy_position(self, market, timeframe_str = None) -> Trade:
        return self.opened_buy_tradings[market][timeframe_str]

    def handle_sell_position(self, sell_trade_result, expected_timeframe_str) -> None:
        self.opened_buy_tradings[sell_trade_result.market][expected_timeframe_str] = None
        super(HedgingTradeMgr, self).handle_sell_position(sell_trade_result, expected_timeframe_str)

class TradeStateRecoverMgr:

    def __init__(self):
        self.trade_states = {}

    def load_init_trade_states(self, account, ex_type, am, init_market_tick, timeframe_str=None):
        market = init_market_tick.market
        evaluated_holding_market_bal = init_market_tick.close * am.get_market_vol(market)

        if len(self.trade_states) == 0:
            tid = global_prop.tid
            self.trade_states = StateStorage.instance().get_bought_trade_states(account, ex_type, tid)

        if timeframe_str is None:
            key = f'{market}'
            if key in self.trade_states:
                buy_trade_result = self.trade_states[key]
            else:
                if evaluated_holding_market_bal > global_prop.minimum_volumn_krw_limit_for_rebalance:
                    _uuid = str(uuid.uuid4())
                    buy_trade_result = Trade(True, "BUY", init_market_tick.datetime, init_market_tick.market,
                                             evaluated_holding_market_bal, init_market_tick.close,
                                             am.get_market_vol(market), 0,
                                             am.get_market_cash_balance(market),
                                             am.get_cash_balance(), 0,
                                             am.get_evaluated_balance(), 'RECOVERED FROM EXCHANGE', _uuid, _uuid)
                else:
                    buy_trade_result = None
            return buy_trade_result
        else:
            key = f'{market}_{timeframe_str}'
            if key in self.trade_states:
                return self.trade_states[key]
            else:
                log.debug(f'Trade state for {market}_{timeframe_str} does not exist in the trade state {self.trade_states.keys()}.')
        return None

    def load_init_trade_states0(self, am, init_time_dt, init_market_tick, timeframe_str=None):
        market = init_market_tick.market
        evaluated_holding_market_bal = init_market_tick.close * am.get_market_vol(market)

        trade_states = self.__read_trade_states()
        if timeframe_str is None:
            key = f'{market}'
            if key in trade_states:
                buy_trade_result = Trade.from_json(trade_states[key])
            else:
                if evaluated_holding_market_bal > global_prop.minimum_volumn_krw_limit_for_rebalance:
                    _uuid = str(uuid.uuid4())
                    buy_trade_result = Trade(True, "BUY", init_market_tick.datetime, init_market_tick.market,
                                             evaluated_holding_market_bal, init_market_tick.close,
                                             am.get_market_vol(market), 0,
                                             am.get_market_cash_balance(market),
                                             am.get_cash_balance(), 0,
                                             am.get_evaluated_balance(), 'RECOVERED FROM EXCHANGE', _uuid, _uuid)
                else:
                    buy_trade_result = None
            return buy_trade_result
        else:
            key = f'{market}_{timeframe_str}'
            if key in trade_states:
                buy_trade_result = Trade.from_json(trade_states[key])
                return buy_trade_result
            else:
                log.debug(f'Trade state for {market}-{timeframe_str} does not exist in the trade state {trade_states.keys()}.')
        return None

    def __read_trade_states(self):
        return

    def __read_trade_states00(self):
        trade_states = {}
        with open(self.__state_file_name, mode='r') as state_file:
            trade_states = json.load(state_file)
        return trade_states

    def __write_trade_states(self, trade_states):
        with open(self.__state_file_name, mode='w') as state_file:
            state_file.write(json.dumps(trade_states, indent=2))

    def store_trade_state(self, buy_trade_result, timeframe_str):
        trade_states = self.__read_trade_states()
        if timeframe_str is None:
            key = buy_trade_result.market
        else:
            key = f'{buy_trade_result.market}_{timeframe_str}'
        trade_states[key] = buy_trade_result.to_json()
        log.debug(f'Store_trade_state :: store {key} ==> {trade_states.keys()}')
        self.__write_trade_states(trade_states)

    def resolve_trade_state(self, sell_trade_result, timeframe_str):
        trade_states = self.__read_trade_states()

        if timeframe_str is None:
            key = sell_trade_result.market
        else:
            key = f'{sell_trade_result.market}_{timeframe_str}'

        if key in trade_states:
            trade_states.pop(key)
        else:
            err_msg = f"########## ERROR, while trying to remove {key} in the trade states {trade_states.keys()}."
            log.error(err_msg)
            raise RuntimeError(err_msg)
        log.debug(f'Resolve_trade_state :: remove {key} ==> {trade_states.keys()}')
        self.__write_trade_states(trade_states)


class POSTMgr:
    def __init__(self, ex_connector):
        self.ex_connector = ex_connector

    def perform_post2(self, ex_type, quote):
        market_ticks = quote.get_market_ticks(ex_type)
        ##############################
        post_market = self.ex_connector.get_post_market()
        tick = market_ticks[post_market]
        post_price = tick.close

        post_amount = self.ex_connector.get_post_amount()
        post_buy_vol = post_amount * (1 - self.ex_connector.get_fee_ratio()) / post_price

        log.info(f'POST: Try to check BUY_POSITION of {post_market} with price({post_price})')
        is_processed, avg_price, total_vol, paid_fee = self.ex_connector.enter_long(post_market, post_price, post_buy_vol)
        if is_processed:
            log.info(f'POST: Okay! BUY_POSITION works well!(market({post_market}), avg_price({avg_price}), total_vol({total_vol}),paid_fee({paid_fee}))')
        else:
            log.error(f'POST: Failure while trying to execute buy position in POST. Need to check the network states for Exchange')
            return False

        time.sleep(2)   # After Two Seconds

        market_vol_without_fee = total_vol * (1 - self.ex_connector.get_fee_ratio())
        log.info(f'POST: Try to check SELL_POSITION of {post_market} with vol({market_vol_without_fee})')
        is_processed, avg_price, total_vol, paid_fee = self.ex_connector.exit_long(post_market, market_vol_without_fee, post_price)
        if is_processed:
            log.info(f'POST: Okay! SELL_POSITION works well!(market({post_market}), avg_price({avg_price}), total_vol({total_vol}),paid_fee({paid_fee}))')
        else:
            log.error(f'POST: Failure while trying to execute sell position in POST. Need to check the network states for Exchange')
            return False

        return True

    ## TODO: Depreciated in V3, should be removed after testing post (stkim: 2023-01-05)
    def perform_post(self, time_dt, market_ticks, ta_indicators):
        post_market = 'KRW-BTC'
        post_price = 0
        for market in market_ticks:
            tick = market_ticks[market]
            post_market = market
            post_price = tick.close
            break

        post_min_krw = 5100
        post_buy_vol = post_min_krw * (1 - self.ex_connector.get_fee_ratio()) / post_price

        log.info(f'POST: Try to check BUY_POSITION of {post_market} with price({post_price})')
        is_processed, avg_price, total_vol, paid_fee = self.ex_connector.enter_long(post_market, post_price, post_buy_vol)
        if is_processed:
            log.info(f'POST: Okay! BUY_POSITION works well!(market({post_market}), avg_price({avg_price}), total_vol({total_vol}),paid_fee({paid_fee}))')
        else:
            log.error(f'POST: Failure while trying to execute buy position in POST. Need to check the network states for Exchange')
            return False

        time.sleep(2)   # After Two Seconds

        market_vol_without_fee = total_vol * (1 - self.ex_connector.get_fee_ratio())
        log.info(f'POST: Try to check SELL_POSITION of {post_market} with vol({market_vol_without_fee})')
        is_processed, avg_price, total_vol, paid_fee = self.ex_connector.exit_long(post_market, market_vol_without_fee)
        if is_processed:
            log.info(f'POST: Okay! SELL_POSITION works well!(market({post_market}), avg_price({avg_price}), total_vol({total_vol}),paid_fee({paid_fee}))')
        else:
            log.error(f'POST: Failure while trying to execute sell position in POST. Need to check the network states for Exchange')
            return False

        return True


