from abc import ABCMeta, abstractmethod

from bt4 import GlobalProperties as global_prop
from bt4.Constants import ExType
from bt4.model.state_mgr import StateStorage
from bt4.trade.TradeMgr import POSTMgr, log
from bt4.model.trade_object import Trade
from bt4.utils.exchange_filter import ExFilterFactory
from bt4.utils.python_utils import to_int_str
from bt4.utils.strings import split_source_target_markets
import pandas as pd
import uuid

class AssetMgr(metaclass=ABCMeta):
    def __init__(self):
        pass

    def set_params(self, ex_connector, markets, trade_mgr):
        self.ex_conn = ex_connector
        self.markets = markets
        self.fee_ratio = ex_connector.get_fee_ratio()
        self.cash_balance, self.market_vol = self.refresh_balance()
        self.market_cash_balance = {}
        for market in self.markets:
            self.market_cash_balance[market] = 0

        self.evaluated_balance = self.cash_balance
        self.trade_mgr = trade_mgr
        self.post_mgr = POSTMgr(ex_connector)
        self.initialized_with_market_ticks = False

    def validate_balance_state(self, usr_uuid, ex_type, tid, quote):
        base_cur = self.ex_conn.get_base_currency()
        bal_state_from_db, _ = StateStorage.instance().get_balance_states(usr_uuid, ex_type, tid, base_cur)
        bal_state_from_ex, _ = self.__load_balances_from_exchange__()

        ## The strategy starting for the first time, nothing has been stored in the database.
        if len(bal_state_from_db) == 0:
            return True, ""

        is_balance_valid = True
        invalid_balance_msg = ""
        for cur in bal_state_from_ex:
            ex_bal = bal_state_from_ex[cur]
            if cur in bal_state_from_db:
                db_bal = bal_state_from_db[cur]
            else:
                if f"{base_cur}-{cur}" in bal_state_from_db:
                    db_bal = ExFilterFactory.instance().get(ex_type).filter_volume(bal_state_from_db[f"{base_cur}-{cur}"])
                else:
                    db_bal = None

            if ex_bal != db_bal:
                is_balance_valid = False
                invalid_balance_msg = invalid_balance_msg + f"{cur} of Exchange ({ex_bal}) != {cur} of Balance State ({db_bal})" + "\r\n"

        return is_balance_valid, invalid_balance_msg

    def make_balance_state(self, ex_type, market_ticks, after_evaluated_balance):
        balance_state = {}
        balance_state['Total'] = after_evaluated_balance
        base_cur = self.ex_conn.get_base_currency()
        balance_state[base_cur] = self.get_cash_balance()
        for market in market_ticks:
            if ex_type == ExType.upbit:
                currency = market.replace('KRW-','')
            else:
                currency = market.replace(f'/{base_cur}', '')
            balance_state[currency] = self.get_market_vol(market)
            balance_state[currency +'_price'] = market_ticks[market].close
        return balance_state

    def synchronize_trade_states2(self, account, ex_type, quote) -> None:
        self.trade_mgr.synchronize_trade_states2(account, ex_type, self, quote)

    def reset_trade_state(self, account, ex_type, tid) -> None:
        self.trade_mgr.reset_trade_state(account, ex_type, tid)

    def compute_cash_for_rebalance(self, market_ticks = None):
        cash_for_rebalance = 0
        if market_ticks is not None:
            evaluated_bal,_ = self.compute_evaluated_balance(market_ticks)
            cash_for_rebalance = evaluated_bal * global_prop.utility_rate_for_trading
        else:
            cash_for_rebalance = self.cash_balance
        return cash_for_rebalance

    def initialize(self, init_tais):
        pass

    def perform_post2(self, extype, quote) -> bool:
        return self.post_mgr.perform_post2(extype, quote)

    def refresh_balance(self):
        base_currency = self.ex_conn.get_base_currency()
        cur_bal_state, mkt_bal_state = self.__load_balances_from_exchange__()

        self.cash_balance = cur_bal_state[base_currency]
        self.market_vol = mkt_bal_state
        return self.cash_balance, self.market_vol

    def __load_balances_from_exchange__(self):
        '''
        balance_states['KRW'] = 10000
        balance_states['BTC'] = 0.1111
        balance_states['ETH'] = 0.1111
        balance_states['XRP'] = 0.1111
        :return:
        '''
        balance_states = {}
        mkt_bal_state = {}
        self.ex_conn.fetch_balances()
        base_currency = self.ex_conn.get_base_currency()
        balance_states[base_currency] = int(self.ex_conn.get_balance(base_currency))

        for market in self.markets :
            _, target_cur = split_source_target_markets(market)
            balance_states[target_cur] = self.ex_conn.get_balance(target_cur)
            mkt_bal_state[market] = self.ex_conn.get_balance(target_cur)

        return balance_states, mkt_bal_state


    def get_ta_indicator(self):
        pass

    def exist_open_positions(self,market):
        return self.trade_mgr.exist_open_positions(market)

    def get_opened_buy_position(self, market, timeframe_str=None) -> Trade:
        return self.trade_mgr.get_opened_buy_position(market, timeframe_str)

    def get_cash_balance(self, timeframe = None):
        return self.cash_balance

    def get_market_vol(self, market):
        return self.market_vol[market]

    def get_market_cash_balance(self, market, timeframe = None):
        return self.market_cash_balance[market]

    def get_evaluated_balance(self):
        return self.evaluated_balance

    def compute_evaluated_balance(self, market_ticks, compute_fee=True):
        desc = ''
        self.evaluated_balance = self.cash_balance
        for market in market_ticks:
            price = market_ticks[market].close

            if compute_fee:
                self.evaluated_balance = self.evaluated_balance + self.market_vol[market] * price * (1 - self.fee_ratio)
            else:
                self.evaluated_balance = self.evaluated_balance + self.market_vol[market] * price

            try:
                market_krw = int(price * self.market_vol[market])
            except ValueError:
                market_krw = 0

            if market_krw > 10:
                desc = desc +f'({market}:{market_krw:,}(={price:.1f}x{self.market_vol[market]:.3f})),'

        ## Compute minimum_volumn_krw_limit_for_rebalance to consider the minimal volumn of a specific market
        min_limit = self.evaluated_balance * 0.0003
        min_base_amount_for_rebalance = self.ex_conn.get_minimum_base_amount_for_rebalance()
        min_rebal_limit =  min_base_amount_for_rebalance if min_limit < min_base_amount_for_rebalance else min_limit
        self.ex_conn.set_min_rebalance_limit(min_rebal_limit)
        # log.debug(f'min_rebal_limit : {min_rebal_limit}')
        return self.evaluated_balance, desc[0:-1]

    def append_supplements(self, supplements):
        pass

    def rebalance(self, market_ticks=None):
        pass

    def get_markets(self):
        return self.markets

    def get_minumum_base_amount_for_rebalance(self):
        return self.ex_conn.get_minimum_base_amount_for_rebalance()

    @abstractmethod
    def compute_wish_to_buy_vol(self, market, tick, expected_timeframe_str=None) -> float:
        pass

    def enter_long(self, market, buy_price, tick=None, expected_timeframe_str=None):
        if tick is not None:
            buy_price = tick.close
        _uuid= str(uuid.uuid4())
        trade_result = Trade(False, 'BUY', tick.datetime, tick.market,
                             -1, -1, self.market_vol[market], -1,
                             self.market_cash_balance[market], self.cash_balance, 0, self.evaluated_balance, '', _uuid, _uuid)

        ### Validate if there is no cache or no market cash balance.
        wish_to_buy_vol = self.compute_wish_to_buy_vol(market, buy_price, tick, expected_timeframe_str)
        is_valid = self.validate_buy_position(market, buy_price, wish_to_buy_vol)
        if not is_valid:
            return trade_result

        trade_result = self.process_buy_position(market, buy_price, trade_result, tick, expected_timeframe_str)
        if trade_result.is_processed:
            self.trade_mgr.handle_buy_position(trade_result, expected_timeframe_str)
        else:
            log.warning(f'AssetMgmt: Buy Order Failure: ({market=}, {buy_price=}, {wish_to_buy_vol}, {expected_timeframe_str=})')
        return trade_result

    def validate_buy_position(self, market, buy_price, wish_to_buy_vol):
        trading_krw = buy_price * wish_to_buy_vol

        if self.cash_balance <= 0:
            log.warning(f'No CASH!: No Cash in Balance({self.cash_balance})')
            return False
        elif self.market_cash_balance[market] < trading_krw:
            log.info(f'Small CASH!: Cash in market cash balance({self.market_cash_balance[market]:.2f}) is smaller than wish_to_buy({trading_krw:.2f}=buy_price({buy_price:.2f}) x buy_vol({wish_to_buy_vol:.5f})). Total Remaining Cash State: {self.cash_balance:.2f}')
            return False
        elif trading_krw < self.ex_conn.get_min_rebalance_limit():
            log.info(f'TOO SMALL TRADING REQUEST: Amount of Cash for trading ({trading_krw}) is smaller than '
                     f'system\'s minimum value for trading({self.ex_conn.get_min_rebalance_limit()})')
            return False
        else:
            return True

    @abstractmethod
    def process_buy_position(self, market, buy_price, trade_result, tick = None, expected_timeframe_str=None):
        pass

    @abstractmethod
    def process_after_sell_position(self,buy_trade_result, market, sell_price, tick,
                                    is_processed, settled_price, settled_volume, payed_fee, expected_timeframe_str=None):
        pass

    def exit_long(self, buy_trade_result, market, sell_price, tick, expected_timeframe_str=None):
        evaluated_bal_before_sell_position = self.get_evaluated_balance()
        _uuid = str(uuid.uuid4())
        trade_result = Trade(False, 'SELL', tick.datetime, tick.market,
                             -1, -1, self.market_vol[market], -1,
                             self.market_cash_balance[market], self.cash_balance, 0, self.evaluated_balance, '', _uuid, buy_trade_result.id)

        market_vol_with_fee = buy_trade_result.settled_vol
        market_vol_without_fee = market_vol_with_fee * (1-self.fee_ratio)
        is_processed, settled_price, settled_volume, payed_fee = self.ex_conn.exit_long(market, market_vol_without_fee, sell_price)

        if is_processed:
            should_be_returned = settled_price * settled_volume - payed_fee
            self.cash_balance = self.cash_balance + should_be_returned
            self.market_vol[market] = self.market_vol[market] - settled_volume
            self.evaluated_balance = self.evaluated_balance - payed_fee
            self.market_cash_balance[market] = self.market_cash_balance[market] + should_be_returned

            self.process_after_sell_position(buy_trade_result, market, sell_price, tick,
                                        is_processed, settled_price, settled_volume, payed_fee,
                                        expected_timeframe_str)

            #############################################################
            buy_settle = buy_trade_result.evaluated_market_balance
            sell_settle = should_be_returned
            profit = sell_settle - buy_settle
            profit_ratio = profit / evaluated_bal_before_sell_position
            self.evaluated_balance = self.get_evaluated_balance() + profit

            trade_result = Trade(is_processed, 'SELL', tick.datetime, tick.market,
                                 should_be_returned, settled_price, settled_volume, payed_fee,
                                 self.market_cash_balance[market], self.cash_balance, profit, self.evaluated_balance,'',
                                 _uuid, buy_trade_result.id)
            self.trade_mgr.handle_sell_position(trade_result, expected_timeframe_str)
        else:
            log.warning(f'AssetMgmt: Sell Order Failure:({market=}, {sell_price=}, {market_vol_without_fee=})')
        return trade_result


    def reset_market_bal_vol(self, market_index):
        self.market_cash_balance[market_index] = 0
        self.market_vol[market_index] = 0

    def rebalance_of_market(self, market_index):
        pass


class FixedRatioAssetMgr(AssetMgr):
    def __init__(self):
        super(FixedRatioAssetMgr, self).__init__()

    def set_params(self, ex_connector, trade_ratio, markets, trade_mgr) :
        super(FixedRatioAssetMgr, self).set_params(ex_connector, markets, trade_mgr)
        self.trade_mgr.initialize(markets)
        self.trade_ratio = trade_ratio

    def rebalance(self, market_ticks=None):
        super(FixedRatioAssetMgr, self).refresh_balance()

        tot_n_mkt = len(self.markets)
        assigned_n_mkt = 0
        for market in self.markets :
            if self.trade_mgr.get_opened_buy_position(market) is not None :
                assigned_n_mkt += 1

        ## 초기 투자금액을 복원하여 여기에서 비율을 정하여 투자금액을 설정 (2025.3.14)
        ## 1. 초기에는 할당된 마켓이 없으므로 assigned_n_mkt=0 이며, recover_proportion = 1이 됨
        ## 2. 이후 투자된 마켓이 있는 경우에 다음의 식(recover_proportion*cash_balance)으로 초기의 투자금액을 복원하고
        ## 3. 여기에서 투자 비율(trade_ratio)과 utility_rate를 곱하여 총액을 구함
        recover_proportion = tot_n_mkt / (
                    tot_n_mkt - self.trade_ratio * global_prop.utility_rate_for_trading * assigned_n_mkt)
        recover_total_cash_bal = recover_proportion * self.cash_balance
        trade_balance = recover_total_cash_bal * self.trade_ratio * global_prop.utility_rate_for_trading

        for market in self.markets:
            if self.trade_mgr.get_opened_buy_position(market) is None:
                self.market_cash_balance[market] = trade_balance / tot_n_mkt
                log.info(f'Prepared Money for {market} - {to_int_str(self.market_cash_balance[market])} of Total Cash Balance: {to_int_str(self.cash_balance)}')


    def compute_wish_to_buy_vol(self, market, buy_price, tick, expected_timeframe_str):
        market_bal = self.market_cash_balance[market]
        buy_vol = market_bal * (1-self.fee_ratio) / buy_price
        return buy_vol

    def process_after_sell_position(self,buy_trade_result, market, sell_price, tick,
                                    is_processed, settled_price, settled_volume, payed_fee, expected_timeframe_str=None):
        pass

    def process_buy_position(self, market, buy_price, trade_result, tick=None, expected_timeframe_str=None):
        # market_bal = self.market_cash_balance[market]
        # buy_vol = market_bal * (1-self.fee_ratio) / buy_price
        buy_vol = self.compute_wish_to_buy_vol(market, buy_price, tick, expected_timeframe_str)

        is_processed, settled_price, settled_volume, payed_fee = self.ex_conn.enter_long(market, buy_price, buy_vol)

        if is_processed:
            self.market_vol[market] = settled_volume
            should_be_payed = settled_price * settled_volume + payed_fee
            self.cash_balance = self.cash_balance - should_be_payed
            self.evaluated_balance = self.evaluated_balance - payed_fee
            self.market_cash_balance[market] = self.market_cash_balance[market] - should_be_payed

            trade_result = Trade(is_processed, 'BUY', tick.datetime, tick.market,
                  settled_volume * settled_price, settled_price, settled_volume, payed_fee,
                  self.market_cash_balance[market], self.cash_balance, 0, self.evaluated_balance, '', trade_result.id, trade_result.id)
        else:
            log.warning(f'AssetMgmt: Buy Order Failure: ({market=}, {buy_price=}, {expected_timeframe_str=},'
                      f'{settled_price=}, {settled_volume=}, {payed_fee=})')

        return trade_result



class FixedHdgeAssetMgr(FixedRatioAssetMgr):

    def __init__(self):
        super(FixedHdgeAssetMgr, self).__init__()

    def set_params(self, ex_connector, trade_ratio, markets, timeframes, trade_mgr):
        super(FixedHdgeAssetMgr, self).set_params(ex_connector, trade_ratio, markets, trade_mgr)
        self.trade_mgr.initialize(markets, timeframes)
        self.time_frame_len = len(timeframes)
        self.timeframes = timeframes
        self.mkt_reserved_tf_cash_bal = {}

        for mkt in markets:
            self.mkt_reserved_tf_cash_bal[mkt] = {}
            for tf in self.timeframes:
                self.mkt_reserved_tf_cash_bal[mkt][tf] = 0

    def rebalance(self, market_ticks=None):
        super(FixedHdgeAssetMgr, self).refresh_balance()

        tot_n_mkt_tfs = len(self.markets) * len(self.timeframes)
        assigned_n_mkt_tfs = 0
        for market in self.markets :
            for tf in self.timeframes :
                if self.trade_mgr.get_opened_buy_position(market, tf) is not None :
                    assigned_n_mkt_tfs += 1

        ## 초기 투자금액을 복원하여 여기에서 비율을 정하여 투자금액을 설정 (2025.3.14)
        ## 1. 초기에는 할당된 마켓이 없으므로 assigned_n_mkt=0 이며, recover_proportion = 1이 됨
        ## 2. 이후 투자된 마켓이 있는 경우에 다음의 식(recover_proportion*cash_balance)으로 초기의 투자금액을 복원하고
        ## 3. 여기에서 투자 비율(trade_ratio)과 utility_rate를 곱하여 총액을 구함
        recover_proportion = tot_n_mkt_tfs / (
                    tot_n_mkt_tfs - self.trade_ratio * global_prop.utility_rate_for_trading * assigned_n_mkt_tfs)
        recover_total_cash_bal = recover_proportion * self.cash_balance
        trade_balance = recover_total_cash_bal * self.trade_ratio * global_prop.utility_rate_for_trading

        for market in self.markets :
            self.market_cash_balance[market] = 0
            for tf in self.timeframes:
                trade = self.trade_mgr.get_opened_buy_position(market, tf)
                if trade is None :
                    self.mkt_reserved_tf_cash_bal[market][tf] = trade_balance / tot_n_mkt_tfs
                    self.market_cash_balance[market] += self.mkt_reserved_tf_cash_bal[market][tf]
                log.info(f"Prepared Money for {market}-tf({tf}):: mkt_rsv_tf_cash_bal({to_int_str(self.mkt_reserved_tf_cash_bal[market][tf])})")

    def compute_wish_to_buy_vol(self, market, buy_price, tick, expected_timeframe_str):
        market_bal = self.mkt_reserved_tf_cash_bal[market][expected_timeframe_str]
        buy_vol = market_bal * (1 - self.fee_ratio) / buy_price
        return buy_vol

    def process_buy_position(self, market, buy_price, trade_result, tick=None, expected_timeframe_str=None):
        buy_vol = self.compute_wish_to_buy_vol(market, buy_price, tick, expected_timeframe_str)

        is_processed, settled_price, settled_volume, payed_fee = self.ex_conn.enter_long(market, buy_price,
                                                                                         buy_vol)
        if is_processed:
            self.market_vol[market] = self.market_vol[market] + settled_volume
            should_be_payed = settled_price * settled_volume + payed_fee
            self.cash_balance = self.cash_balance - should_be_payed
            self.evaluated_balance = self.evaluated_balance - payed_fee
            self.market_cash_balance[market] = self.market_cash_balance[market] - should_be_payed
            self.mkt_reserved_tf_cash_bal[market][expected_timeframe_str] -= should_be_payed

            trade_result = Trade(is_processed, 'BUY', tick.datetime, tick.market,
                                 settled_volume * settled_price, settled_price, settled_volume,
                                 payed_fee, self.market_cash_balance[market], self.cash_balance, 0, self.evaluated_balance, '',
                                 trade_result.id, trade_result.id)
        else:
            log.warning(f'AssetMgmt: Buy Order Failure: ({market=}, {buy_price=}, {expected_timeframe_str=},'
                      f'{settled_price=}, {settled_volume=}, {payed_fee=})')

        return trade_result

    def process_after_sell_position(self,buy_trade_result, market, sell_price, tick,
                                    is_processed, settled_price, settled_volume, payed_fee, expected_timeframe_str=None):
        should_be_returned = settled_price * settled_volume - payed_fee
        self.mkt_reserved_tf_cash_bal[market][expected_timeframe_str] += should_be_returned



class VolatilityAssetMgr(AssetMgr):
    def __init__(self):
        super(VolatilityAssetMgr, self).__init__()

    def set_params(self, ex_connector, target_volatility, volatility_tai, markets, trade_mgr):
        super(VolatilityAssetMgr, self).set_params(ex_connector, markets, trade_mgr)
        self.trade_mgr.initialize(markets)
        self.target_volatility = target_volatility
        self.volatilities = {}
        self.volatility_tai = volatility_tai
        self.cash_for_each_mkt = 0

        for market in self.markets:
            self.volatilities[market] = 0

        # self.rebalance_logic = "MARKET_WALL"
        self.rebalance_logic = "REMAINED_CASH"


    def initialize(self, init_vols):
        for market in self.markets:
            self.volatilities[market] = init_vols[market]

    def get_ta_indicator(self):
        return self.volatility_tai

    def get_evaluated_holding_markets_val(self, market_ticks):
        sum_of_holding_market_cash = 0
        for market in self.markets:
            if market_ticks is not None and self.market_vol[market] > 0:
                close_price = market_ticks[market].close
                evaluated_holding_market_bal = self.market_vol[market] * close_price
            else:
                evaluated_holding_market_bal = 0

            if evaluated_holding_market_bal > self.ex_conn.get_min_rebalance_limit():  ## If evaluated asset is under 10000 KRW
                sum_of_holding_market_cash = sum_of_holding_market_cash + evaluated_holding_market_bal

        return sum_of_holding_market_cash

    def rebalance(self, market_ticks=None) :
        if self.rebalance_logic == "MARKET_WALL":
            self.rebalance_mkt_wall(market_ticks)
        else: # self.rebalance_logic = "REMAINED_CASH"
            self.rebalance_remained_cash(market_ticks)

    def rebalance_mkt_wall(self, market_ticks = None):
        super(VolatilityAssetMgr, self).refresh_balance()

        tot_n_mkt = len(self.markets)
        assigned_n_mkt = 0
        for market in self.markets:
            if self.trade_mgr.get_opened_buy_position(market) is not None:
                assigned_n_mkt += 1

        ## market에 모든 거래가 없을때 현금보유량/Market수로 배분 금액(cash_for_each_mkt)을 계산 유지함
        if assigned_n_mkt == 0:
            self.cash_for_each_mkt = (self.cash_balance * global_prop.utility_rate_for_trading) / tot_n_mkt

        should_assign_mkt = tot_n_mkt - assigned_n_mkt
        ## 분배 대상 금액을 계산
        should_assign_tot_bal = self.cash_balance * global_prop.utility_rate_for_trading
        for market in self.markets:
            trade = self.trade_mgr.get_opened_buy_position(market)
            ## 거래가 되고 있는 경우 self.cash_balance에는 volatility때문에 각 Market별로 할당되지 않고 남은 금액이 있음
            ## 그 금액을 제외하고, Market별로 할당해야함
            if trade is not None:
                origin_mkt_assigned_cash = trade.settled_price * trade.settled_vol + trade.market_cash_bal  # Market별로 할당된 cash를 계산하기 (origin_mkt_assigned_cash)
                prev_should_assign_tot_bal = should_assign_tot_bal
                if origin_mkt_assigned_cash > self.cash_for_each_mkt:                       ## 이경우는 비정상적인 상황임, 보통은 origin_mkt_assigned_cash는 Market배분 금액을 넘을수 없음
                    origin_mkt_assigned_cash = self.cash_for_each_mkt
                should_assign_tot_bal -= (self.cash_for_each_mkt - origin_mkt_assigned_cash)## 전체 cash중에서 거래가 있는 경우 거래에 사용된 금액을 제외한 남은 금액들로, 전체 Market에 할당되고 남은 Cash를 계산함 ==> 이렇게 해야 특정 Market에 과도하게 남은 잔액이 할당되는 문제를 해결할수 있음
                log.info(f'Prepared Money - {market} => should_assign_tot_bal({to_int_str(should_assign_tot_bal)}) = should_assign_tot_bal({to_int_str(prev_should_assign_tot_bal)}) - (({self.cash_for_each_mkt=}) - ({origin_mkt_assigned_cash=}))')

        for market in self.markets:
            if self.trade_mgr.get_opened_buy_position(market) is None:
                current_volatility = self.volatilities[market]
                if current_volatility != 0 :
                    ## 변동성을 고려하여 Market에 할당
                    self.market_cash_balance[market] = should_assign_tot_bal * (min(1, ( self.target_volatility / current_volatility)) / should_assign_mkt)
                    log.info(f'[{self.rebalance_logic}] Prepared Money :: {market} - market_cash_bal({to_int_str(self.market_cash_balance[market])}) = should_assign_tot_bal({to_int_str(should_assign_tot_bal)} *'
                            f' target_vol({self.target_volatility})/cur_vol({current_volatility:.5f}) / should_assign_mkt({should_assign_mkt})')


    def rebalance_remained_cash(self, market_ticks = None):
        super(VolatilityAssetMgr, self).refresh_balance()

        cash_for_rebalance = super(VolatilityAssetMgr, self).compute_cash_for_rebalance(market_ticks)

        market_should_be_rebalanced = []
        sum_of_reserved_market_cash = 0
        for market in self.markets:
            # current_volatility = self.volatilities[market]
            # if current_volatility != -1 and current_volatility != 0:
            if market_ticks is not None and self.market_vol[market] > 0:
                close_price = market_ticks[market].close
                evaluated_holding_market_bal = self.market_vol[market] * close_price
            else:
                evaluated_holding_market_bal = 0

            if evaluated_holding_market_bal < self.ex_conn.get_min_rebalance_limit():  ## If evaluated asset is under 10000 KRW
                market_should_be_rebalanced.append(market)
            else:
                sum_of_reserved_market_cash = sum_of_reserved_market_cash + \
                                              self.market_cash_balance[market] + evaluated_holding_market_bal

        num_of_market_for_rebalancing =  len(market_should_be_rebalanced)
        remained_cash = cash_for_rebalance - sum_of_reserved_market_cash

        for market in market_should_be_rebalanced:
            current_volatility = self.volatilities[market]
            if current_volatility != 0:
                self.market_cash_balance[market] = remained_cash * \
                                                   (min(1, (self.target_volatility / current_volatility)) / num_of_market_for_rebalancing)
                log.info(f'[{self.rebalance_logic}] Prepared Money :: {market} - market_cash_bal({to_int_str(self.market_cash_balance[market])}) = remained_cash({to_int_str(remained_cash)} *'
                    f' target_vol({self.target_volatility})/cur_vol({current_volatility:.5f}) / num of market rebalce({num_of_market_for_rebalancing})')


    def process_after_sell_position(self,buy_trade_result, market, sell_price, tick,
                                    is_processed, settled_price, settled_volume, payed_fee, expected_timeframe_str=None):
        pass


    def __arrange_low_volatility(self, volatility):
        arranged_vol = volatility
        if arranged_vol < self.target_volatility:  # Remove *2
            arranged_vol = self.target_volatility
        return arranged_vol

    def append_supplements(self, supplements):
        for market in self.markets:
            self.volatilities[market] = supplements[market]

    def compute_wish_to_buy_vol(self, market, buy_price, tick, expected_timeframe_str):
        market_bal = self.market_cash_balance[market]
        buy_vol = market_bal * (1 - self.fee_ratio) / buy_price
        return buy_vol

    def process_buy_position(self, market, buy_price, trade_result, tick=None, expected_timeframe_str=None):
        current_volatility = self.volatilities[market]
        market_bal = 0
        if current_volatility != -1:
            # market_bal = self.market_cash_balance[market]
            # buy_vol = market_bal * (1 - self.fee_ratio) / buy_price
            buy_vol = self.compute_wish_to_buy_vol(market, buy_price, tick, expected_timeframe_str)

            is_processed, settled_price, settled_volume, payed_fee = self.ex_conn.enter_long(
                market, buy_price, buy_vol)

            if is_processed:
                self.market_vol[market] = settled_volume
                should_be_payed = settled_price * settled_volume + payed_fee
                self.cash_balance = self.cash_balance - should_be_payed
                self.evaluated_balance = self.evaluated_balance - payed_fee ## When buying, only payed fee should be extracted from evaluated balance
                self.market_cash_balance[market] = self.market_cash_balance[market] - should_be_payed

                trade_result = Trade(is_processed, 'BUY', tick.datetime, tick.market,
                                     settled_volume * settled_price, settled_price, settled_volume,
                                     payed_fee,
                                     self.market_cash_balance[market], self.cash_balance, 0, self.evaluated_balance,
                                     f'prop: {((self.target_volatility / current_volatility) / len(self.markets)):3.3f},vola: {current_volatility:3.4f}',
                                     trade_result.id, trade_result.id)
            else:
                log.warning(f'AssetMgmt: Buy Order Failure:  ({market=}, {buy_price=}, {expected_timeframe_str=},'
                    f'{settled_price=}, {settled_volume=}, {payed_fee=})')

        return trade_result


class VolatilityHdgeAssetMgr(VolatilityAssetMgr):
    def __init__(self):
        super(VolatilityHdgeAssetMgr, self).__init__()

    def set_params(self, ex_connector, target_volatility_ratio, volatility_tai, markets, timeframes, trade_mgr):
        super(VolatilityHdgeAssetMgr, self).set_params(ex_connector, target_volatility_ratio, volatility_tai, markets, trade_mgr)
        self.trade_mgr.initialize(markets, timeframes)
        self.time_frame_len = len(timeframes)
        self.timeframes = timeframes
        self.cash_for_each_mkt_tfs = 0
        self.market_reserved_tf_cash_bal = {}
        self.market_tf_holding_vol = {}
        for market in markets:
            self.market_reserved_tf_cash_bal[market] = {}
            self.market_tf_holding_vol[market] = {}
            for tf in self.timeframes:
                self.market_reserved_tf_cash_bal[market][tf] = 0
                self.market_tf_holding_vol[market][tf] = 0

        self.rebalance_logic = "REMAINED_CASH"
        # self.rebalance_logic = "MARKET_WALL"

    def get_num_of_not_traded_market_tfs(self):
        num_of_not_traded_market_tf = 0
        for market in self.markets:
            for timeframe in self.timeframes:
                trade = self.trade_mgr.get_opened_buy_position(market, timeframe)
                if trade is None:
                    num_of_not_traded_market_tf = num_of_not_traded_market_tf + 1
        return num_of_not_traded_market_tf

    def rebalance(self, market_ticks=None) :
        if self.rebalance_logic == "MARKET_WALL":
            self.rebalance_mkt_wall(market_ticks)
        else: #self.rebalance_logic = "REMAINED_CASH":
            self.rebalance_remained_cash(market_ticks)

    # 각 Market별로 경계를 주고, 그 이상으로는 할당되지 않게함(2025.3.22)
    def rebalance_mkt_wall(self, market_ticks=None) :
        super(VolatilityHdgeAssetMgr, self).refresh_balance()

        tot_n_mkt_tfs = len(self.markets) * len(self.timeframes)
        assigned_n_mkt_tfs = 0

        for market in self.markets :
            for tf in self.timeframes :
                if self.trade_mgr.get_opened_buy_position(market, tf) is not None :
                    assigned_n_mkt_tfs += 1

        ## market에 모든 거래가 없을때 현금보유량/Market수로 배분 금액(cash_for_each_mkt)을 계산 유지함
        if assigned_n_mkt_tfs == 0:
            self.cash_for_each_mkt_tfs = (self.cash_balance * global_prop.utility_rate_for_trading) / tot_n_mkt_tfs

        log.info(f"CURRENT CASH: {self.cash_balance:,} ")
        ## 분배 대상 금액을 계산
        should_assign_tot_bal = self.cash_balance * global_prop.utility_rate_for_trading
        for market in self.markets :
            for tf in self.timeframes :
                trade = self.trade_mgr.get_opened_buy_position(market, tf)
                ## 거래가 되고 있는 경우 self.cash_balance에는 volatility때문에 각 Market별로 할당되지 않고 남은 금액이 있음
                ## 그 금액을 제외하고, Market별로 할당해야함
                if trade is not None :
                    origin_mkt_assigned_cash = trade.settled_price * trade.settled_vol + trade.market_cash_bal  # Market별로 할당된 cash를 계산하기 (origin_mkt_assigned_cash)
                    prev_should_assign_tot_bal = should_assign_tot_bal
                    if origin_mkt_assigned_cash > self.cash_for_each_mkt_tfs :  ## 이경우는 비정상적인 상황임, 보통은 origin_mkt_assigned_cash는 Market배분 금액을 넘을수 없음
                        origin_mkt_assigned_cash = self.cash_for_each_mkt_tfs
                    should_assign_tot_bal -= (self.cash_for_each_mkt_tfs - origin_mkt_assigned_cash)  ## 전체 cash중에서 거래가 있는 경우 거래에 사용된 금액을 제외한 남은 금액들로, 전체 Market에 할당되고 남은 Cash를 계산함 ==> 이렇게 해야 특정 Market에 과도하게 남은 잔액이 할당되는 문제를 해결할수 있음
                    log.info(f'Prepared Money - {market} => should_assign_tot_bal({to_int_str(should_assign_tot_bal)}) = should_assign_tot_bal({to_int_str(prev_should_assign_tot_bal)}) - (({self.cash_for_each_mkt_tfs=}) - ({origin_mkt_assigned_cash=}))')

        should_assign_mkt_tfs = tot_n_mkt_tfs - assigned_n_mkt_tfs
        for market in self.markets:
            self.market_cash_balance[market] = 0
            for tf in self.timeframes :
                if self.trade_mgr.get_opened_buy_position(market, tf) is None:
                    current_volatility = self.volatilities[market]
                    if current_volatility != 0 :
                        ## 변동성을 고려하여 Market에 할당
                        cash_assigned_in_market_tf = should_assign_tot_bal * (min(1, ( self.target_volatility / current_volatility)) / should_assign_mkt_tfs)
                        self.market_reserved_tf_cash_bal[market][tf] = cash_assigned_in_market_tf
                        self.market_cash_balance[market] += self.market_reserved_tf_cash_bal[market][tf]

                        log.info(f'[{self.rebalance_logic}] Prepared Money for {market}-tf({tf}):: mkt_rsv_tf_cash_bal({to_int_str(cash_assigned_in_market_tf)}))='
                            f'should_assign_tot_bal({to_int_str(should_assign_tot_bal)}) * min(1,tar_vol({self.target_volatility})/cur_vol({current_volatility}))/should_assign_mkt_tfs({should_assign_mkt_tfs}))')


    ## 평가금액 중심의 Rebalance
    def rebalance_remained_cash(self, market_ticks=None):
        super(VolatilityHdgeAssetMgr, self).refresh_balance()

        #########################################################################################
        ## Rebalance for each market and market tf
        cash_for_rebalance = super(VolatilityHdgeAssetMgr, self).compute_cash_for_rebalance(market_ticks)

        num_of_not_traded_market_tf = self.get_num_of_not_traded_market_tfs()
        sum_of_reserved_market_cash = self.get_evaluated_holding_markets_val(market_ticks)
        remained_cash = cash_for_rebalance - sum_of_reserved_market_cash

        market_list = []
        if market_ticks is None:
            market_list = self.markets
        else:
            for market in market_ticks:
                market_list.append(market)

        for market in market_list:
            current_volatility = self.target_volatility if self.volatilities[market] == 0 else self.volatilities[market]
            self.market_cash_balance[market] = 0
            for market_tf in self.timeframes:
                trade = self.trade_mgr.get_opened_buy_position(market, market_tf)
                if trade is None:
                    max_cash_for_market_tf = remained_cash / num_of_not_traded_market_tf
                    adjust_rate_by_volatility = min(1, (self.target_volatility / current_volatility))
                    cash_assigned_in_market_tf = max_cash_for_market_tf * adjust_rate_by_volatility
                    self.market_reserved_tf_cash_bal[market][market_tf] = cash_assigned_in_market_tf
                    self.market_cash_balance[market] = self.market_cash_balance[market] + cash_assigned_in_market_tf

                    log.info(f'[{self.rebalance_logic}] Prepared Money for {market}-tf({market_tf}):: mkt_rsv_tf_cash_bal({to_int_str(self.market_reserved_tf_cash_bal[market][market_tf])}))='
                        f'remained_cash({to_int_str(remained_cash)})/not_traded_market_tf({num_of_not_traded_market_tf})*'
                             f'adjust_rate({adjust_rate_by_volatility}=min(1,tar_vol({self.target_volatility})/cur_vol({current_volatility})))')


    def get_market_cash_balance(self, market, timeframe=None):
        if timeframe is not None:
            return self.market_reserved_tf_cash_bal[market][timeframe]
        else:
            return self.market_cash_balance[market]

    def synchronize_trade_states(self, init_time_dt, init_market_ticks, init_ta_indicators) -> None:
        self.trade_mgr.synchronize_trade_states(self, init_time_dt, init_market_ticks, init_ta_indicators)

    def compute_wish_to_buy_vol(self, market, buy_price, tick, expected_timeframe_str):
        market_reserved_tf_cash = self.market_reserved_tf_cash_bal[market][expected_timeframe_str]
        buy_vol = market_reserved_tf_cash * (1 - self.fee_ratio) / buy_price
        return buy_vol

    def process_buy_position(self, market, buy_price, trade_result, tick=None, expected_timeframe_str=None):
        current_volatility = self.volatilities[market]
        market_reserved_tf_cash = 0
        if current_volatility != -1:
            buy_vol = self.compute_wish_to_buy_vol(market, buy_price, tick, expected_timeframe_str)

            is_processed, settled_price, settled_volume, payed_fee = self.ex_conn.enter_long(market, buy_price, buy_vol)

            if is_processed:
                self.market_vol[market] = self.market_vol[market] + settled_volume
                should_be_payed = settled_price * settled_volume + payed_fee
                self.cash_balance = self.cash_balance - should_be_payed
                self.evaluated_balance = self.evaluated_balance - payed_fee ## When buying, only payed fee should be extracted from evaluated balance
                self.market_cash_balance[market] = self.market_cash_balance[market] - should_be_payed

                self.market_reserved_tf_cash_bal[market][expected_timeframe_str] \
                    = self.market_reserved_tf_cash_bal[market][expected_timeframe_str] - should_be_payed
                self.market_tf_holding_vol[market][expected_timeframe_str] = settled_volume

                trade_result = Trade(is_processed, 'BUY', tick.datetime, tick.market,
                                     settled_volume * settled_price, settled_price, settled_volume,
                                     payed_fee,
                                     self.market_reserved_tf_cash_bal[market][expected_timeframe_str], self.cash_balance, 0, self.evaluated_balance,
                                     f'prop: {((self.target_volatility / current_volatility) / len(self.markets)):3.3f},vola: {current_volatility:3.4f}',
                                     trade_result.id, trade_result.id)
            else:
                log.warning(
                    f'AssetMgmt: Buy Order Failure: ({market=}, {buy_price=}, {expected_timeframe_str=},'
                    f'{settled_price=}, {settled_volume=}, {payed_fee=})')

        return trade_result

    def process_after_sell_position(self,buy_trade_result, market, sell_price, tick,
                                    is_processed, settled_price, settled_volume, payed_fee, expected_timeframe_str=None):
        should_be_returned = settled_price * settled_volume - payed_fee
        self.market_reserved_tf_cash_bal[market][expected_timeframe_str] \
            = self.market_reserved_tf_cash_bal[market][expected_timeframe_str] + should_be_returned
        self.market_tf_holding_vol[market][expected_timeframe_str] = \
            self.market_tf_holding_vol[market][expected_timeframe_str] - settled_volume


class WeightedRatioAssetMgr(AssetMgr) :
    def __init__(self) :
        super(WeightedRatioAssetMgr, self).__init__()

    def set_params(self, ex_connector, top_n_weights, markets, trade_mgr) :
        super(WeightedRatioAssetMgr, self).set_params(ex_connector, markets, trade_mgr)
        self.trade_mgr.initialize(markets)
        self.top_n_weights = top_n_weights
        self.adjusted_weights = top_n_weights
        if len(markets) < len(top_n_weights) : # In Case of the number of designated markets is less than the weights
            self.adjusted_weights = top_n_weights[:len(markets)]

        self.market_idx_map = {}
        self.top_n_reserved_cash_balances = [0] * len(self.adjusted_weights)
        self.top_n_hold_market_cash = [0] * len(self.adjusted_weights)

    def rebalance(self, market_ticks=None) :
        super(WeightedRatioAssetMgr, self).refresh_balance()
        total_balance = self.cash_balance
        if market_ticks is not None:
            total_balance, _ = self.compute_evaluated_balance(market_ticks)

        for idx, weight in enumerate(self.adjusted_weights) :
            if idx == 1:
                post_fix = "st"
            elif idx == 2:
                post_fix = "nd"
            else :
                post_fix = "th"

            if self.top_n_hold_market_cash[idx] < self.ex_conn.get_min_rebalance_limit():
                self.top_n_reserved_cash_balances[idx] = total_balance * weight * global_prop.utility_rate_for_trading
                log.info(f'Rebalance:: Money recalculated for {idx}{post_fix} market - {to_int_str(self.top_n_reserved_cash_balances[idx])} of Total Balance: {to_int_str(total_balance)}')

            else:
                log.info(f'Rebalance:: Money has been hold for {idx}{post_fix} market - {to_int_str(self.top_n_hold_market_cash[idx])} of Total Balance: {to_int_str(total_balance)}')


    def compute_wish_to_buy_vol(self, market, buy_price, tick, expected_timeframe_str) :
        for idx, rsved_cash in enumerate(self.top_n_reserved_cash_balances):
            if rsved_cash > self.ex_conn.get_min_rebalance_limit():
                buy_vol = rsved_cash * (1 - self.fee_ratio) / buy_price
                self.market_idx_map[market] = idx
                self.market_cash_balance[market] = rsved_cash
                return buy_vol
        return -1

    def process_after_sell_position(self, buy_trade_result, market, sell_price, tick,
                                    is_processed, settled_price, settled_volume, payed_fee,
                                    expected_timeframe_str=None) :
        pass

    def process_buy_position(self, market, buy_price, trade_result, tick=None, expected_timeframe_str=None) :
        buy_vol = self.compute_wish_to_buy_vol(market, buy_price, tick, expected_timeframe_str)
        if buy_vol == -1:
            log.info("WeightedAssetMgmt: No reserved cash exists for trading. All trades are occupied")
        else:
            is_processed, settled_price, settled_volume, payed_fee = self.ex_conn.enter_long(market, buy_price,
                                                                                             buy_vol)
            if is_processed :
                self.market_vol[market] = settled_volume
                should_be_payed = settled_price * settled_volume + payed_fee
                self.cash_balance = self.cash_balance - should_be_payed
                self.evaluated_balance = self.evaluated_balance - payed_fee

                market_idx = self.market_idx_map[market]
                self.top_n_hold_market_cash[market_idx] = should_be_payed
                self.top_n_reserved_cash_balances[market_idx] = self.top_n_reserved_cash_balances[market_idx] - should_be_payed
                self.market_cash_balance[market] -= should_be_payed

                trade_result = Trade(is_processed, 'BUY', tick.datetime, tick.market,
                                     settled_volume * settled_price, settled_price, settled_volume, payed_fee,
                                     self.top_n_reserved_cash_balances[market_idx], self.cash_balance, 0,
                                     self.evaluated_balance, '', trade_result.id, trade_result.id)
            else :
                log.warning(f'AssetMgmt: Buy Order Failure: ({market=}, {buy_price=}, {expected_timeframe_str=},'
                            f'{settled_price=}, {settled_volume=}, {payed_fee=})')

        return trade_result

    def exit_long(self, buy_trade_result, market, sell_price, tick, expected_timeframe_str=None) :
        evaluated_bal_before_sell_position = self.get_evaluated_balance()
        _uuid = str(uuid.uuid4())
        trade_result = Trade(False, 'SELL', tick.datetime, tick.market,
                             -1, -1, self.market_vol[market], -1,
                             self.market_cash_balance[market], self.cash_balance, 0, self.evaluated_balance, '',
                             _uuid, buy_trade_result.id)

        market_vol_with_fee = buy_trade_result.settled_vol
        market_vol_without_fee = market_vol_with_fee * (1 - self.fee_ratio)
        is_processed, settled_price, settled_volume, payed_fee = self.ex_conn.exit_long(market,
                                                                                        market_vol_without_fee,
                                                                                        sell_price)

        if is_processed :
            should_be_returned = settled_price * settled_volume - payed_fee
            self.cash_balance = self.cash_balance + should_be_returned
            self.market_vol[market] = self.market_vol[market] - settled_volume
            self.evaluated_balance = self.evaluated_balance - payed_fee

            market_idx = self.market_idx_map[market]
            self.top_n_hold_market_cash[market_idx] -= (buy_trade_result.settled_vol*buy_trade_result.settled_price+buy_trade_result.fee)
            self.top_n_reserved_cash_balances[market_idx] += should_be_returned

            buy_settle = buy_trade_result.evaluated_market_balance
            sell_settle = should_be_returned
            profit = sell_settle - buy_settle
            profit_ratio = profit / evaluated_bal_before_sell_position
            self.evaluated_balance = self.get_evaluated_balance() + profit

            _uuid = str(uuid.uuid4())
            trade_result = Trade(is_processed, 'SELL', tick.datetime, tick.market,
                                 should_be_returned, settled_price, settled_volume, payed_fee,
                                 self.market_cash_balance[market], self.cash_balance, profit, self.evaluated_balance,
                                 '', _uuid, buy_trade_result)
            self.trade_mgr.handle_sell_position(trade_result, expected_timeframe_str)
        else :
            log.warning(f'AssetMgmt: Sell Order Failure:({market=}, {sell_price=}, {market_vol_without_fee=})')
        return trade_result