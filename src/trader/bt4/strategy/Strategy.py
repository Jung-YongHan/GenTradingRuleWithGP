
from bt4 import GlobalProperties
from bt4.Constants import R, ExType, CandleType

from bt4.common.AdminCtrlReq import RebalanceReq, PauseTradingReq, ResumeTradingReq, StopTradingReq, ForceEnterLongReq, \
    ForceExitLongReq, ForceSettleReq
from bt4.common.ResultAnalyzer import analyze_result
from bt4.model.state_mgr import StateStorage
from bt4.quote.TAIMgr import TAIMgr
from bt4.model.trade_object import Trade
from bt4.core.ReportSupport import Report
from bt4.utils.market_utils import compute_vol5, compute_sell_timeframes, match_time_frame
from bt4.utils.memory_profiler import MemoryProfiler
from bt4.utils.python_utils import dt2str, to_curr_unit_str2, split_hour_min, now_str
from bt4.utils.mylog import init_log
from abc import *
import uuid
import pandas as pd

log = init_log()

class AbstractStrategy(metaclass=ABCMeta):
    def __init__(self):
        pass

    def set_params(self, am, report_storage, markets, tgt_ex_type):
        self.report = Report(report_storage)
        self.asset_mgmt = am
        self.markets = markets
        self.account = None
        self.result_df = None

        self.is_init_trading = False
        self.enable_asset_rebalance = True

        self.ex_type = tgt_ex_type
        self.admin_req_list = []
        self.is_paused = False
        self.tid = GlobalProperties.tid

        ## for keeping trade states
        self.trade_states_id = None

        ##########################
        ## Stop loss / trailing stop / take profit
        self.stop_loss_param = None
        self.trailing_stop_params = None
        self.take_profit_params = None
        self.ts_max_prices = {}


    def setup(self, context):
        if self.enable_asset_rebalance:
            self.asset_mgmt.rebalance()
        self.before_evaluate_balance = self.asset_mgmt.get_evaluated_balance()
        r = R()
        self.context = context

        if r.STGY.STOP_LOSS in context.ctx_params :
            self.stop_loss_param = context.ctx_params[r.STGY.STOP_LOSS]
        if r.STGY.TRAILING_STOP in context.ctx_params :
            self.trailing_stop_params = context.ctx_params[r.STGY.TRAILING_STOP]
        if r.STGY.TAKE_PROFIT in context.ctx_params :
            self.take_profit_params = context.ctx_params[r.STGY.TAKE_PROFIT]

        if context.stgy_live_trader is not None:
            self.account = context.ctx_params[r.EX.EX_USR_ID]
            self.trade_states_id = StateStorage.instance().get_trade_states_ids(self.account, self.ex_type, self.tid)

    def init_trading(self, quote):
        print(f'######################## init_trading')

        ###################################################
        ## Init AssetMgmt
        tmgr = TAIMgr(quote, self.ex_type)
        tai = self.asset_mgmt.get_ta_indicator()
        if tai is not None:
            if tai == 'vol5':
                market_vol5 = compute_vol5(quote, tmgr, self.ex_type)
                self.asset_mgmt.initialize(market_vol5)

        ###################################################
        ## Validate Balance States - compare balance state of postgresql and that of Exchange
        if self.context.stgy_live_trader is not None:
            if not GlobalProperties.reset_trades:
                ## When not forcing resetting trades, the balance states from database and exchange should be synchronized.
                is_balance_valid, invalid_balance_msg = self.asset_mgmt.validate_balance_state(self.account, self.ex_type, self.tid, quote)
                if not is_balance_valid:
                    err_msg = f"######## FAILURE in Validating Balance Process. {invalid_balance_msg}. Check Update of Balance of Exchange...!"
                    log.error(err_msg)
                    raise RuntimeError(err_msg)

        ###################################################
        ## Handle POST
        if self.context.stgy_live_trader is not None and not GlobalProperties.is_post_done :
            is_post_success = self.asset_mgmt.perform_post2(self.ex_type, quote)
            if not is_post_success :
                err_msg = "######## FAILURE in POST Process. Check Network and Protocol to Exchange...!"
                log.error(err_msg)
                raise RuntimeError(err_msg)
            else :
                GlobalProperties.is_post_done = True
                post_mkt = self.asset_mgmt.ex_conn.get_post_market()
                if post_mkt not in self.markets:
                    quote.remove_markets(self.ex_type, [post_mkt])

        ###################################################
        ## Recover Trade States
        if self.context.stgy_live_trader is not None:
            ## Not synchronize trade state when reset_trade_flag is set to be true.
            if GlobalProperties.reset_trades :
                self.asset_mgmt.reset_trade_state(self.account, self.ex_type, self.tid)
                log.info("Reset Previous Trade States...")
            else:
                self.asset_mgmt.synchronize_trade_states2(self.account, self.ex_type, quote)
                log.info("Recover Previous Previous Trade States...")


        ###################################################
        ## Initialize Trading List and Rebalance
        if self.enable_asset_rebalance:
            desc = ''
            _uuid = str(uuid.uuid4())

            if self.report.trading_list is None :
                date_time_as_string = dt2str(quote.get_time())
                settle = Trade(True, "SETT", date_time_as_string, 'SETT', 0, 0, 0,
                           0, 0, self.before_evaluate_balance, 0,
                           self.before_evaluate_balance, desc, _uuid, _uuid)
                self.report.append(settle)
            else:
                log.info(f"{len(self.report.trading_list)} trading list has been recovered.")

            self.asset_mgmt.rebalance(quote.get_market_ticks(self.ex_type))

        return True

    def perform(self, quote) :
        if self.context.stgy_live_trader is None :
            return

        if self.is_paused:
            log.info(f'The strategy is paused! Request resume for resuming the trading.')
            return

    def process_admin_ctrl(self, quote):
        if len(self.admin_req_list) == 0 :
            return

        while len(self.admin_req_list) > 0 :
            admin_req = self.admin_req_list.pop(0)
            admin_ex_type_str = admin_req.ex_type
            admin_ex_type = ExType(admin_ex_type_str)
            if self.ex_type != admin_ex_type :  ## The following is only for the targeting ex_type
                continue

            self.handle_admin_request(admin_req, quote)

    def post_admin_request(self, admin_req_obj):
        log.info(f'Strategy:: admin_control message has been posted : {admin_req_obj.__dict__}')
        self.admin_req_list.append(admin_req_obj)

    def handle_admin_request(self, admin_req, quote):
        market_ticks = quote.get_market_ticks(self.ex_type)

        ############################################################
        ## Force Enter Long
        if isinstance(admin_req, ForceEnterLongReq) :
            tick = market_ticks[admin_req.market]
            if admin_req.ent_long_tf != "":
                desc = f'Admin Control(force_buy - mkt({admin_req.market}) tf({admin_req.ent_long_tf}), ' \
                       f'price({tick.close})) has been requested.'
            else:
                desc = f"Admin Control(force_buy - mkt({admin_req.market}), " \
                       f'price({tick.close})) has been requested.'

            log.info(desc)

            if tick is not None :
                self.process_enter_long_position(admin_req.market, tick, tick.close, f', {desc}')

        ############################################################
        ## Force Exit Long
        if isinstance(admin_req, ForceExitLongReq) :
            tick = market_ticks[admin_req.market]
            if admin_req.exit_long_tf != "":
                desc = f'Admin Control(force_sell - mkt({admin_req.market}) of sell_tf({admin_req.exit_long_tf})' \
                       f' matched buy_tf({admin_req.matched_enter_long_tf}), ' \
                       f'price({tick.close})) has been requested.'

                log.info(desc)
                if tick is not None :
                    matched_buy_trade_result = self.asset_mgmt.get_opened_buy_position(admin_req.market,
                                                                                       admin_req.matched_enter_long_tf)
                    if matched_buy_trade_result is not None :
                        self.process_exit_long_position(matched_buy_trade_result, admin_req.market, tick,
                                                        tick.close, desc, admin_req.matched_enter_long_tf)
            else:
                desc = f'Admin Control(force_sell - mkt({admin_req.market}), ' \
                       f'price({tick.close})) has been requested.'
                log.info(desc)
                if tick is not None :
                    buy_trade_result = self.asset_mgmt.get_opened_buy_position(admin_req.market)
                    if buy_trade_result is not None :
                        self.process_exit_long_position(buy_trade_result, admin_req.market, tick, tick.close, desc)


        if isinstance(admin_req, RebalanceReq):
            msg = f'Admin Control(rebalance) for a user {self.account} of {self.ex_type.value} has been requested.'
            log.info(msg)
            self.asset_mgmt.rebalance(quote.get_market_ticks(self.ex_type))

        if isinstance(admin_req, PauseTradingReq):
            msg = f'Admin Control(pause trading) for a user {self.account} of {self.ex_type.value} has been requested.'
            log.info(msg)

            if self.is_paused == True:
                msg2 = f'Strategy is already paused. The request (resume trading) will be ignored.!'
            else:
                self.is_paused = True
                msg2 = f'The trading will be paused in a minute.'
            log.info(msg2)

        if isinstance(admin_req, ResumeTradingReq):
            msg = f'Admin Control(resume trading) for a user {self.account} of {self.ex_type.value} has been requested.'
            log.info(msg)
            msg2 = ''
            if self.is_paused == True:
                self.is_paused = False
                self.asset_mgmt.rebalance(quote.get_market_ticks(self.ex_type))
                msg2 = f'The trading will be resumed in a minute.'
            else:
                msg2 = f'Strategy is not paused now. The request (resume trading) will be ignored.!'
            log.info(msg2)

        if isinstance(admin_req, StopTradingReq):
            msg = f'Stop Trading for a user {self.account} of {self.ex_type.value} has been requested.' \
                  f'The strategy for a user {self.account} of {self.ex_type.value} will be terminated!!'
            log.info(msg)
            raise RuntimeError("This Thread has been killed!")

        if isinstance(admin_req, ForceSettleReq):
            msg = f'Force Settle for a user {self.account} of {self.ex_type.value} has been requested.'
            log.info(msg)
            self.process_settle(quote.time_dt, quote.get_market_ticks(self.ex_type))

    def finish(self):
        self.report.close()

    def process_enter_long_position(self, market, tick, price, description, expected_timeframe_str = None):

        opend_trade = self.asset_mgmt.get_opened_buy_position(market, expected_timeframe_str)
        if opend_trade is not None:
            log.warning(f'There already exists opened buy position({opend_trade.__str__()}). The requested buy order is cancelled({market=}, {expected_timeframe_str=}).')
            return

        buy_trade_result = self.asset_mgmt.enter_long(market, price, tick, expected_timeframe_str)
        # buy_trade_result.desc = buy_trade_result.desc + description
        buy_trade_result.desc = description

        log.info(f'[{tick.datetime}] BUY ORDER:: {tick.market} price:{buy_trade_result.settled_price}, '
                 f'vol:{buy_trade_result.settled_vol}, market evaluated market bal: {buy_trade_result.evaluated_market_balance}')
        if buy_trade_result.is_processed:
            # self.opened_buy_tradings[market] = buy_trade_result
            self.report.append(buy_trade_result)

            if self.context.stgy_live_trader is not None:
                self.context.ctx_params["bt_end_date"] = now_str()
                self.__update_trade_summary__()


    def process_exit_long_position(self, buy_trade_result, market, tick, price, description, expected_timeframe_str = None):
        sell_trade_result = self.asset_mgmt.exit_long(buy_trade_result, market, price, tick, expected_timeframe_str)
        sell_trade_result.desc = sell_trade_result.desc + description

        log.info(
            f'[{tick.datetime}] SELL ORDER:: {sell_trade_result.market} price:{sell_trade_result.settled_price}, '
            f'vol:{sell_trade_result.settled_vol}, market cash bal:{sell_trade_result.market_cash_bal}')

        if sell_trade_result.is_processed:
            self.report.append(sell_trade_result)

            if self.context.stgy_live_trader is not None:
                self.context.ctx_params["bt_end_date"] = now_str()
                self.__update_trade_summary__()

    def process_settle(self, time_dt, market_ticks):
        after_evaluated_balance, desc = self.asset_mgmt.compute_evaluated_balance(market_ticks)
        # time_str = dt2str(time_dt)
        time_str = str(time_dt)
        log.info(f'[{time_str}] SETTLE-profit:: {after_evaluated_balance - self.before_evaluate_balance}, - balance: {after_evaluated_balance}')
        profit = after_evaluated_balance - self.before_evaluate_balance
        _uuid = str(uuid.uuid4())
        settle = Trade(True, "SETT", time_str, 'SETT', 0, 0, 0, 0, 0,
                       self.asset_mgmt.get_cash_balance(), profit, after_evaluated_balance, desc, _uuid, _uuid)
        self.report.append(settle)
        self.before_evaluate_balance = after_evaluated_balance

        if self.context.stgy_live_trader is not None:
            base_cur = self.context.exchange.get_base_currency()
            print("sett-1.1")
            StateStorage.instance().upsert_balance_states(self.account, self.ex_type, self.tid, time_dt, base_cur,
                                                          self.asset_mgmt.make_balance_state(self.ex_type, market_ticks,
                                                                                    after_evaluated_balance))
            print("sett-1.2 ")
            self.context.ctx_params["bt_end_date"] = now_str()
            self.__update_trade_summary__()

    def update_trade_n_balance_states_hdging(self, time_dt, market_ticks, buy_timeframes, buy_sell_tf, sell_buy_tf):
        ## The following steps should be executed in the real-trading mode
        if self.context.stgy_live_trader is None:
            return

        after_evaluated_balance, desc = self.asset_mgmt.compute_evaluated_balance(market_ticks)

        self.__update_balances_states__(time_dt, market_ticks, after_evaluated_balance)

        ########################################
        ## Trade States
        future_past_trade_list = []
        for market in market_ticks:
            tick = market_ticks[market]

            for buy_elem_tf in buy_timeframes:
                buy_trade_result = self.asset_mgmt.get_opened_buy_position(market, buy_elem_tf)

                sell_tf = buy_sell_tf[buy_elem_tf]
                buy_sell_tf_str = f'(B){buy_elem_tf}/(S){sell_tf}'
                if buy_trade_result is None:
                    _uuid = str(uuid.uuid4())
                    future_trade = Trade(False, 'BUY', dt2str(time_dt), market, self.asset_mgmt.get_market_vol(market) *  tick.close,
                                   tick.close, 0, 0, self.asset_mgmt.get_market_cash_balance(market, buy_elem_tf),
                                   self.asset_mgmt.get_cash_balance(), 0, after_evaluated_balance, buy_sell_tf_str, _uuid, _uuid)

                    future_past_trade_list.append(future_trade)
                else:
                    if buy_trade_result.desc is None or buy_trade_result.desc == "":
                        buy_trade_result.desc = buy_sell_tf_str + "*" + buy_trade_result.desc
                    future_past_trade_list.append(buy_trade_result)

            for sell_elem_tf in sell_buy_tf:
                matched_buy_timeframe_str = sell_buy_tf[sell_elem_tf]
                matched_buy_trade_result = self.asset_mgmt.get_opened_buy_position(market, matched_buy_timeframe_str)

                if matched_buy_trade_result is not None and matched_buy_trade_result.date != dt2str(time_dt):
                    should_be_returned = tick.close * matched_buy_trade_result.settled_vol - matched_buy_trade_result.fee
                    buy_settle = matched_buy_trade_result.evaluated_market_balance
                    sell_settle = should_be_returned
                    profit = sell_settle - buy_settle

                    _uuid = str(uuid.uuid4())
                    future_trade = Trade(False, 'SELL', dt2str(time_dt), market, matched_buy_trade_result.settled_vol *  tick.close,
                                    tick.close, matched_buy_trade_result.settled_vol, matched_buy_trade_result.fee,
                                    self.asset_mgmt.get_market_cash_balance(market, matched_buy_timeframe_str), self.asset_mgmt.get_cash_balance(),
                                        profit, after_evaluated_balance, f'(S){sell_elem_tf}/(B){matched_buy_timeframe_str}',
                                         _uuid, matched_buy_trade_result.id)
                    future_past_trade_list.append(future_trade)

        ## bt4
        self.trade_states_id = StateStorage.instance().upsert_trade_states(self.account, self.ex_type, self.tid, future_past_trade_list, self.trade_states_id)

    def __update_balances_states__(self, time_dt, market_ticks, after_evaluated_balance):
        print("4.__update_balances_states__")
        balance_state = self.asset_mgmt.make_balance_state(self.ex_type, market_ticks, after_evaluated_balance)
        base_cur = self.context.exchange.get_base_currency()
        StateStorage.instance().upsert_balance_states(self.account, self.ex_type, self.tid, time_dt, base_cur,
                                                      balance_state)

    def update_trade_n_balance_states_netting(self, time_dt, market_ticks):
        if self.context.stgy_live_trader is None:
            return

        after_evaluated_balance, desc = self.asset_mgmt.compute_evaluated_balance(market_ticks)

        print(f"3.update_trade_n_balance_states_netting - {time_dt}")
        self.__update_balances_states__(time_dt, market_ticks, after_evaluated_balance)
        print(f"5. {after_evaluated_balance}")

        ########################################
        future_past_trade_list = []
        for market in market_ticks :
            tick = market_ticks[market]

            buy_trade_result = self.asset_mgmt.get_opened_buy_position(market)
            if buy_trade_result is None :
                _uuid = str(uuid.uuid4())
                future_trade = Trade(False, 'BUY', dt2str(time_dt), market,
                                     self.asset_mgmt.get_market_vol(market) * tick.close,
                                     tick.close, 0, 0, self.asset_mgmt.get_market_cash_balance(market),
                                     self.asset_mgmt.get_cash_balance(), 0, after_evaluated_balance,
                                     "", _uuid, _uuid)

                future_past_trade_list.append(future_trade)
            else:
                future_past_trade_list.append(buy_trade_result)
                should_be_returned = tick.close * buy_trade_result.settled_vol - buy_trade_result.fee
                buy_settle = buy_trade_result.evaluated_market_balance
                sell_settle = should_be_returned
                profit = sell_settle - buy_settle

                _uuid = str(uuid.uuid4())
                future_trade = Trade(False, 'SELL', dt2str(time_dt), market,
                                     buy_trade_result.settled_vol * tick.close,
                                     tick.close, buy_trade_result.settled_vol, buy_trade_result.fee,
                                     self.asset_mgmt.get_market_cash_balance(market),
                                     self.asset_mgmt.get_cash_balance(),
                                     profit, after_evaluated_balance, "",
                                     _uuid, buy_trade_result.id)
                future_past_trade_list.append(future_trade)

        ## bt4
        self.trade_states_id = StateStorage.instance().upsert_trade_states(self.account, self.ex_type, self.tid,
                                                                           future_past_trade_list, self.trade_states_id)


    def log_evaluated_balance(self, time_dt, market_ticks):
        evaluated_val, desc = self.asset_mgmt.compute_evaluated_balance(market_ticks)
        eval_bal_desc = f'[{dt2str(time_dt)}] Evaluated balance :: {to_curr_unit_str2(evaluated_val, self.ex_type)}'
        if desc is not None and desc.strip() != '':
            eval_bal_desc = eval_bal_desc + f' {desc}'
        log.info(eval_bal_desc)


    def __handle_stop_loss__(self, matched_buy_trade_result, tmgr, market, cur_price, sell_elem_tf_hour=None):
        quote = tmgr.get_quote()
        low_price_time = ""

        enter_price = matched_buy_trade_result.settled_price
        stop_loss_price = enter_price * (1 + self.stop_loss_param[0])

        if self.context.stgy_live_trader is None:
            cdl_type = CandleType.MINUTES_1
            search_start_pdt = matched_buy_trade_result.date + pd.Timedelta(minutes = 1)
            ohlcv_df = quote.get_candle_types(self.ex_type)[cdl_type][market][search_start_pdt:]
            low_price_of_range = ohlcv_df["low"].min()

            if low_price_of_range < stop_loss_price:
                low_range_list = ohlcv_df["low"].tolist()
                low_range_time = ohlcv_df.index.tolist()

                for low, low_time in zip(low_range_list, low_range_time):
                    if low < stop_loss_price:
                        low_time_str = low_time.strftime("%Y-%m-%d %H:%M:%S")
                        return True, low, f"*[STOP LOSS] = True :: ({matched_buy_trade_result.date}~{low_time_str}) low_price_of_range({low}) < stop_loss_price limit({stop_loss_price})"

            return False, -1, f"*[STOP LOSS] = False :: price({low_price_of_range}) < stop_loss_price limit({stop_loss_price})"
        else:
            low_price_of_range = cur_price
            low_price_time = tmgr.get_quote().get_market_ticks(self.ex_type)[market].datetime

            if low_price_of_range < stop_loss_price:
                return True, low_price_of_range, f"*[STOP LOSS] = True :: ({matched_buy_trade_result.date}~{low_price_time}) low_price_of_range({low_price_of_range}) < stop_loss_price limit({stop_loss_price})"
            else:
                return False, -1, f"*[STOP LOSS] = False :: price({low_price_of_range}) < stop_loss_price limit({stop_loss_price})"

    def __handle_take_profit__(self, matched_buy_trade_result, tmgr, market, cur_price, sell_elem_tf_hour=None):

        enter_price = matched_buy_trade_result.settled_price
        tp_limit = enter_price * (1+ self.take_profit_params[0])

        if self.context.stgy_live_trader is None:
            quote = tmgr.get_quote()
            cdl_type = CandleType.MINUTES_1
            check_start_date = matched_buy_trade_result.date + pd.Timedelta(minutes = 1)
            ohlcv_df = quote.get_candle_types(self.ex_type)[cdl_type][market][check_start_date:]
            high_price_of_range = ohlcv_df["high"].max()

            if high_price_of_range > tp_limit:
                high_range_list = ohlcv_df["high"].tolist()
                high_range_time = ohlcv_df.index.tolist()

                for high, high_time in zip(high_range_list, high_range_time) :
                    if high > tp_limit :
                        high_time_str = high_time.strftime("%Y-%m-%d %H:%M:%S")
                        return True, high, f"*[TAKE PROFIT] = True :: ({high_time_str}) = close({high}) > take_profit limit ({tp_limit})"

            return False, -1, f"*[TAKE PROFIT] = False :: price({high_price_of_range}) > take_profit limit({tp_limit})"
        else:
            high_price_of_range = cur_price

            if high_price_of_range > tp_limit:
                return True, high_price_of_range, f"*[TAKE PROFIT] = True :: high_price_of_range({high_price_of_range}) > take_profit limit ({tp_limit})"
            else:
                return False, -1, f"*[TAKE PROFIT] = False :: price({high_price_of_range}) > take_profit limit({tp_limit})"


    def __handle_tailing_stop__(self, matched_buy_trade_result, tmgr, market, cur_price, matched_buy_timeframe_str = None):

        quote = tmgr.get_quote()
        if self.context.stgy_live_trader is None :  ## Backtesting
            cdl_type = CandleType.MINUTES_1
            min_ohlcv_df = quote.get_candle_types(self.ex_type)[cdl_type][market][matched_buy_trade_result.date :]
            min_max = min_ohlcv_df["close"].max()

            ts_start_price = matched_buy_trade_result.settled_price * (1-self.trailing_stop_params[0])
            if min_max > ts_start_price: # TS Starts
                min_range_list = min_ohlcv_df["close"].tolist()
                min_range_time = min_ohlcv_df.index.tolist()
                prev_max = -1
                for min_close, min_time in zip(min_range_list, min_range_time):
                    if prev_max < min_close:
                        prev_max = min_close
                    ts_price = prev_max * (1+self.trailing_stop_params[0])
                    ts_condition = prev_max > ts_start_price and min_close < ts_price
                    if ts_condition:
                        min_time_str = min_time.strftime("%Y-%m-%d %H:%M:%S")
                        return True, min_close, f"*[TRAILING STOP] = True :: ({matched_buy_trade_result.date}~{min_time_str}) prev_max({prev_max}) > ts_start_price({ts_start_price}) and min_close({min_close}) < ts_price({ts_price})"

                return False, -1, f"*[TRAILING STOP] = False :: True(min_max({min_max}) >  ts_start_price({ts_start_price})) but Not Reached to the cur_price({cur_price}) < trailing_stop{prev_max * (1+self.trailing_stop_params[0])}"
            else:
                return False, -1, f"*[TRAILING STOP] = False :: min_max({min_max}) >  ts_start_price({ts_start_price})"

        else:  ## Live Trading
            if matched_buy_timeframe_str is not None:  ## Hedging
                if market not in self.ts_max_prices:
                    self.ts_max_prices[market] = {}

                if matched_buy_timeframe_str not in self.ts_max_prices[market]:
                    self.ts_max_prices[market][matched_buy_timeframe_str] = cur_price
                else:
                    prev_max = self.ts_max_prices[market][matched_buy_timeframe_str]
                    if cur_price > prev_max:
                        self.ts_max_prices[market][matched_buy_timeframe_str] = cur_price

                max_price = self.ts_max_prices[market][matched_buy_timeframe_str]
            else:
                if market not in self.ts_max_prices:
                    self.ts_max_prices[market] = cur_price

                prev_max = self.ts_max_prices[market]
                if cur_price > prev_max :
                    self.ts_max_prices[market] = cur_price

                max_price = self.ts_max_prices[market]

            gap_rate = (cur_price - max_price) / max_price
            if gap_rate < self.trailing_stop_params[0]:
                if matched_buy_timeframe_str is not None:
                    self.ts_max_prices[market].pop(matched_buy_timeframe_str)
                else:
                    self.ts_max_prices.pop(market)
                return True, cur_price, f"*[TRAILING STOP] == True :: ({matched_buy_trade_result.date}~{quote.get_time()}) gap_rate({gap_rate}) < trailing_stop_limit ({self.trailing_stop_params[0]})"
            else:
                return False, -1, ""


    def __handle_stop_loss_in_bulk__(self, matched_buy_trade_result, from_buy_to_now_df, _1m_start_time, _1m_before_time):
        low_price = from_buy_to_now_df["close"].min()

        enter_price = matched_buy_trade_result.settled_price
        stop_loss_price = enter_price * (1 + self.stop_loss_param[0])
        if low_price < stop_loss_price:
            low_range_list = from_buy_to_now_df["close"].tolist()
            low_range_time = from_buy_to_now_df.index.tolist()

            for low, low_time in zip(low_range_list, low_range_time) :
                if low < stop_loss_price :
                    low_time_str = low_time.strftime("%Y-%m-%d %H:%M:%S")
                    return True, low, f"*[STOP LOSS] = True :: ({_1m_start_time}~{low_time_str}) low_price_of_range({low}) < stop_loss_price limit({stop_loss_price})"

        return False, -1, f"*[STOP LOSS] = False :: price({low_price}) < stop_loss_price limit({stop_loss_price})"

    def __handle_take_profit_in_bulk__(self, matched_buy_trade_result, from_buy_to_now_df, _1m_start_time, _1m_before_time):
        high_price_of_range = from_buy_to_now_df["high"].max()

        enter_price = matched_buy_trade_result.settled_price
        tp_limit = enter_price * (1 + self.take_profit_params[0])
        if high_price_of_range > tp_limit :
            high_range_list = from_buy_to_now_df["high"].tolist()
            high_range_time = from_buy_to_now_df.index.tolist()

            for high, high_time in zip(high_range_list, high_range_time) :
                if high > tp_limit:
                    high_time_str = high_time.strftime("%Y-%m-%d %H:%M:%S")
                    return True, high, f"*[TAKE PROFIT] = True :: ({high_time_str}) = close({high}) > take_profit limit ({tp_limit})"

        return False, -1, f"*[TAKE PROFIT] = False :: price({high_price_of_range}) > take_profit limit({tp_limit})"

    def __handle_tailing_stop_in_bulk__(self, matched_buy_trade_result, from_buy_to_now_df, _1m_start_time, _1m_before_time, cur_price):
        min_max = from_buy_to_now_df["close"].max()
        _1m_before_time_str = _1m_before_time.strftime("%Y-%m-%d %H:%M:%S")
        ts_start_price = matched_buy_trade_result.settled_price * (1 - self.trailing_stop_params[0])
        if min_max > ts_start_price :  # TS Starts
            min_range_list = from_buy_to_now_df["close"].tolist()
            min_range_time = from_buy_to_now_df.index.tolist()
            prev_max = -1
            for min_close, min_time in zip(min_range_list, min_range_time) :
                if prev_max < min_close :
                    prev_max = min_close
                ts_price = prev_max * (1 + self.trailing_stop_params[0])
                ts_condition = prev_max > ts_start_price and min_close < ts_price
                if ts_condition :
                    min_time_str = min_time.strftime("%Y-%m-%d %H:%M:%S")
                    return True, min_close, f"*[TRAILING STOP] = True :: ({_1m_start_time}~{min_time_str}) prev_max({prev_max}) > ts_start_price({ts_start_price}) and min_close({min_close}) < ts_price({ts_price})"

            return False, -1, f"*[TRAILING STOP] = False :: True(min_max({min_max}) >  ts_start_price({ts_start_price})) but Not Reached to the cur_price({cur_price}) < trailing_stop{prev_max * (1 + self.trailing_stop_params[0])}"
        else :
            return False, -1, f"*[TRAILING STOP] = False :: min_max({min_max}) >  ts_start_price({ts_start_price})"

    def __clean_trailing_stop_max_price__(self, market, matched_buy_timeframe_str = None):
        if self.trailing_stop_params is not None and \
                self.context.stgy_live_trader is not None :
            if matched_buy_timeframe_str is not None:
                if market in self.ts_max_prices :
                    self.ts_max_prices[market].pop(matched_buy_timeframe_str)
            else:
                self.ts_max_prices.pop(market)

    def __update_trade_summary__(self):
        r = R()
        df = self.report.toDataFrame()
        stgy_name = self.context.ctx_params[r.STGY.NAME]
        analyze_result(df, stgy_name, self.context, self.context.report_storage)
        self.report.result_storage.update_intermediate(df)

    def __get_total_tai_row_in_bulk__(self, base_cdl_dfs) :
        total_row = 0
        for market in base_cdl_dfs :
            market_df = base_cdl_dfs[market]

            filter_out_hour_min = self.get_filter_hour_min_in_base_cdl(market_df)
            if filter_out_hour_min is not None :
                market_df = market_df.loc[filter_out_hour_min]

            total_row = len(market_df)
            break
        return total_row

    @abstractmethod
    def update_trade_n_balance_state(self, time_pdt, market_ticks):
        pass

    @abstractmethod
    def process_bulk_quote(self, bulk_quote_loader, start_pdt, end_pdt):
        pass

class AbstractNettingStrategy(AbstractStrategy):
    def __init__(self, ):
        super(AbstractNettingStrategy, self).__init__()

    def set_params(self, am, report_storage, ex_type, markets, params):
        self.ex_type = ex_type
        super(AbstractNettingStrategy, self).set_params(am, report_storage, markets, self.ex_type)
        self.load_tai_params(params)

    @abstractmethod
    def load_tai_params(self, params) :
        pass

    @abstractmethod
    def __is_rebalance_time__(self, time_dt) :
        pass

    def __is_settlement_time__(self, time_dt) :
        return self.__is_rebalance_time__(time_dt)

    @abstractmethod
    def __isBuySignal__(self, mkt_tais, tmgr, market, price, time_dt):
        pass

    @abstractmethod
    def __isSellSignal__(self, mkt_tais, tmgr, market, price, time_dt):
        pass

    def perform(self, quote):
        super(AbstractNettingStrategy, self).perform(quote)

        if self.ex_type not in quote.ex_quote.keys():
            log.error(f"{self.ex_type.name} does not exist in {quote.ex_quote.keys()} from ExchangeQuoteDispatcher.")
            return

        if self.is_paused:
            return

        time_dt = quote.get_time()

        tmgr = TAIMgr(quote, self.ex_type)
        market_ticks = quote.get_market_ticks(self.ex_type)
        ################################################################

        if self.__is_rebalance_time__(time_dt):
            market_vol5 = compute_vol5(quote, tmgr, self.ex_type)
            self.asset_mgmt.append_supplements(market_vol5)
            if self.enable_asset_rebalance:
                self.asset_mgmt.rebalance(market_ticks)

        self.mkt_tais = self.extract_tai(tmgr)

        for market in market_ticks:
            tick = market_ticks[market]
            price = tick.close
            buy_trade_result = self.asset_mgmt.get_opened_buy_position(market)

            if buy_trade_result is None:
                is_buy_signal, buy_log = self.__isBuySignal__(self.mkt_tais, tmgr, market, tick, time_dt)
                log.info(f'[{tick.datetime}] {tick.market} Time Check:checking for BUY Order:{buy_log} '
                    f'Market Bal({self.asset_mgmt.get_market_cash_balance(market):.2f})..')

                if is_buy_signal:
                    super(AbstractNettingStrategy, self).process_enter_long_position(market, tick, tick.close,f",{buy_log},")

            if buy_trade_result is not None and buy_trade_result.date != tick.datetime:

                ### Handle Stop_loss
                stop_loss_signal = False
                if self.stop_loss_param is not None :
                    stop_loss_signal, sl_price, sl_log = \
                        super(AbstractNettingStrategy, self).__handle_stop_loss__(buy_trade_result, tmgr,
                                                                                  market, price)

                    if stop_loss_signal:
                        super(AbstractNettingStrategy, self).process_exit_long_position(buy_trade_result, market, tick,
                                                                                        sl_price, f', {sl_log}')

                take_profit_signal = False
                if self.take_profit_params is not None :
                    take_profit_signal, ts_price, ts_log = \
                        super(AbstractNettingStrategy, self).__handle_take_profit__(buy_trade_result, tmgr,
                                                                                    market, price)
                if take_profit_signal :
                    super(AbstractNettingStrategy, self).process_exit_long_position(buy_trade_result,
                                                                                    market, tick,
                                                                                    tick.close, f', {ts_log}')
                # ### Handle Trailing_stop
                trailing_stop_signal = False
                if self.trailing_stop_params is not None :
                    trailing_stop_signal, ts_price, ts_log = \
                        super(AbstractNettingStrategy, self).__handle_tailing_stop__(buy_trade_result, tmgr,
                                                                                     market, price)
                if trailing_stop_signal :
                    super(AbstractNettingStrategy, self).process_exit_long_position(buy_trade_result,
                                                                                    market, tick,
                                                                                    ts_price, f', {ts_log}')

                if stop_loss_signal or take_profit_signal or trailing_stop_signal:
                    continue

                is_sell_signal, sell_log = self.__isSellSignal__(self.mkt_tais, tmgr, market, tick, time_dt)
                log.info(
                    f'[{tick.datetime}] {tick.market} Time Check:checking for SELL Order:{sell_log}')

                if is_sell_signal:
                    super(AbstractNettingStrategy, self).process_exit_long_position(buy_trade_result, market, tick,
                                                                                        tick.close, f", {sell_log}")
                    super(AbstractNettingStrategy, self).__clean_trailing_stop_max_price__(market)

        ## TODO: STKIM : Need to update for Netting in live trading if the netting strategy is deployed for service.
        print("1")
        self.update_trade_n_balance_state(time_dt, market_ticks)
        print("6")
        if self.__is_settlement_time__(time_dt):
            print("sett-1") #sett - 1.1, sett - 1.2
            super(AbstractNettingStrategy, self).process_settle(time_dt, market_ticks)
            print("sett-2")
        else:
            self.update_trade_n_balance_state(time_dt, market_ticks)

        super(AbstractNettingStrategy, self).log_evaluated_balance(time_dt, market_ticks)

    def update_trade_n_balance_state(self, time_pdt, market_ticks):
        print("2")
        super(AbstractNettingStrategy, self).update_trade_n_balance_states_netting(time_pdt, market_ticks)

    @abstractmethod
    def extract_tai(self, tmgr):
        '''

        :param tmgr:
        :return: tai and tai_str for each market
        '''
        pass

    def process_bulk_quote(self, bulk_quote_loader, start_pdt, end_pdt):
        pass





class AbstractHedgingStrategy(AbstractStrategy):
    def __init__(self, ):
        super(AbstractHedgingStrategy, self).__init__()

        self.mem_profiling = False
        if self.mem_profiling:
            self.mem_profiler = MemoryProfiler()

    def set_params(self, am, report_storage, ex_type, markets, params):
        self.ex_type = ex_type
        super(AbstractHedgingStrategy, self).set_params(am, report_storage, markets, self.ex_type)
        self.buy_timeframes = params['timeframes']
        self.buy_sell_time_gap = params['timegap']
        self.buy_sell_tf, self.sell_buy_tf, self.sell_timeframes = \
            compute_sell_timeframes(self.buy_timeframes, self.buy_sell_time_gap)

        self.mkt_buy_tais = {}
        self.mkt_sell_tais = {}

        self.load_tai_params(params)

    def setup(self, context) :
        super(AbstractHedgingStrategy, self).setup(context)


    @abstractmethod
    def load_tai_params(self, params):
        pass

    def __is_rebalance_time__(self, time_dt) :
        return True if time_dt.hour == 8 and time_dt.minute == 59 else False

    @abstractmethod
    def __isBuySignal__(self, mkt_buy_tais, tmgr, market, tick, time_dt, tf_hour) :
        pass

    @abstractmethod
    def __isSellSignal__(self, mkt_sell_tais, tmgr, market, tick, time_dt, tf_hour):
        pass

    def perform(self, quote):
        super(AbstractHedgingStrategy, self).perform(quote)

        if self.ex_type not in quote.ex_quote.keys():
            log.error(f"{self.ex_type.name} does not exist in {quote.ex_quote.keys()} from ExchangeQuoteDispatcher.")
            return

        if self.is_paused:
            return

        time_pdt = quote.get_time()

        tmgr = TAIMgr(quote, self.ex_type)
        market_ticks = quote.get_market_ticks(self.ex_type)
        ################################################################
        is_buy_time, expected_buy_timeframe_str, buy_tf_hour = match_time_frame(time_pdt, self.buy_timeframes)
        is_sell_time, expected_sell_timeframe_str, sell_tf_hour = match_time_frame(time_pdt, self.sell_timeframes)

        if self.__is_rebalance_time__(time_pdt):
            market_vol5 = compute_vol5(quote, tmgr, self.ex_type)
            self.asset_mgmt.append_supplements(market_vol5)
            if self.enable_asset_rebalance:
                self.asset_mgmt.rebalance(market_ticks)

        self.mkt_buy_tais = self.extract_tai(tmgr, buy_tf_hour)

        for market in market_ticks:
            tick = market_ticks[market]
            price = tick.close
            #######################################################
            ## Processing Buy
            buy_trade_result = self.asset_mgmt.get_opened_buy_position(market, expected_buy_timeframe_str)
            if buy_trade_result is None:
                is_buy_signal, buy_log = self.__isBuySignal__(self.mkt_buy_tais, tmgr, market, tick, time_pdt, buy_tf_hour)

                desc = f'{buy_log} Market Bal for tf({expected_buy_timeframe_str})' \
                       f'({to_curr_unit_str2(self.asset_mgmt.get_market_cash_balance(market, expected_buy_timeframe_str), None)})'

                log.info(f'[{tick.datetime}] [BUY {tick.market}@{expected_buy_timeframe_str} = {is_buy_signal}] ::' + desc)

                if is_buy_time and is_buy_signal:
                    super(AbstractHedgingStrategy, self).process_enter_long_position(market, tick, tick.close,
                                                                                f', {desc}',
                                                                                       expected_buy_timeframe_str)
            #######################################################
            ## Processing Sell
            for sell_elem_tf in self.sell_buy_tf:
                sell_elem_tf_hour, _ = split_hour_min(sell_elem_tf)
                sell_elem_tf_hour = sell_elem_tf_hour + 1
                sell_elem_tf_hour = 0 if sell_elem_tf_hour == 24 else sell_elem_tf_hour

                self.mkt_sell_tais = self.extract_tai(tmgr, sell_elem_tf_hour)

                matched_buy_timeframe_str = self.sell_buy_tf[sell_elem_tf]
                matched_buy_trade_result = self.asset_mgmt.get_opened_buy_position(market, matched_buy_timeframe_str)

                if matched_buy_trade_result is not None and matched_buy_trade_result.date != time_pdt:

                    ### Handle Stop_loss
                    stop_loss_signal = False
                    if self.stop_loss_param is not None:
                        stop_loss_signal, sl_price, sl_log = \
                            super(AbstractHedgingStrategy, self).__handle_stop_loss__(matched_buy_trade_result, tmgr, market, price, sell_elem_tf_hour)

                    if stop_loss_signal:
                        super(AbstractHedgingStrategy, self).process_exit_long_position(matched_buy_trade_result, market, tick,
                                                                                        sl_price, f', {sl_log}', matched_buy_timeframe_str)
                    # ### Handle Trailing_stop
                    trailing_stop_signal = False
                    if self.trailing_stop_params is not None:
                        trailing_stop_signal, ts_price, ts_log = \
                            super(AbstractHedgingStrategy, self).__handle_tailing_stop__(matched_buy_trade_result, tmgr, market, price, matched_buy_timeframe_str)
                    if trailing_stop_signal:
                        super(AbstractHedgingStrategy, self).process_exit_long_position(matched_buy_trade_result, market, tick,
                                                                                        ts_price, f', {ts_log}', matched_buy_timeframe_str)
                    take_profit_signal = False
                    if self.take_profit_params is not None:
                        take_profit_signal, ts_price, ts_log = \
                            super(AbstractHedgingStrategy, self).__handle_take_profit__(matched_buy_trade_result, tmgr, market, price,sell_elem_tf_hour)
                    if take_profit_signal:
                        super(AbstractHedgingStrategy, self).process_exit_long_position(matched_buy_trade_result, market, tick,
                                                                                        tick.close, f', {ts_log}', matched_buy_timeframe_str)

                    if stop_loss_signal or trailing_stop_signal or take_profit_signal:
                        continue

                    is_sell_signal, sell_log = self.__isSellSignal__(self.mkt_sell_tais, tmgr, market, tick, time_pdt, sell_elem_tf_hour)
                    log.info(f'[{tick.datetime}] [SELL {tick.market}@{sell_elem_tf} of '
                             f'B({matched_buy_timeframe_str}) = {is_sell_signal}]:: ' + sell_log)
                    if is_sell_time and sell_elem_tf == expected_sell_timeframe_str and \
                            is_sell_signal:  ## Sell Signal (NEW In WINNING SESSION)
                        super(AbstractHedgingStrategy, self).process_exit_long_position(matched_buy_trade_result, market,
                                                                                          tick,
                                                                                          tick.close, f', {sell_log}',
                                                                                          matched_buy_timeframe_str)
                        super(AbstractHedgingStrategy, self).__clean_trailing_stop_max_price__(market, matched_buy_timeframe_str)

        if self.mem_profiling :
            self.mem_profiler.take_1st_snapshot()

        # self.update_trade_n_balance_state(time_pdt, market_ticks)

        if self.mem_profiling :
            self.mem_profiler.take_2nd_snapshot_and_show_topN(40)
            self.mem_profiler.print_mem_usage()

        if self.__is_rebalance_time__(time_pdt):
            super(AbstractHedgingStrategy, self).process_settle(time_pdt, market_ticks)
        else:
            self.update_trade_n_balance_state(time_pdt, market_ticks)

        super(AbstractHedgingStrategy, self).log_evaluated_balance(time_pdt, market_ticks)

    def update_trade_n_balance_state(self, time_pdt, market_ticks):
        super(AbstractHedgingStrategy, self).update_trade_n_balance_states_hdging(time_pdt, market_ticks,
                                                                                  self.buy_timeframes,
                                                                                  self.buy_sell_tf, self.sell_buy_tf)


    def extract_tai(self, tmgr, timeframe_hour):
        pass

    def process_bulk_quote(self, bulk_quote_loader, start_pdt, end_pdt):
        pass
