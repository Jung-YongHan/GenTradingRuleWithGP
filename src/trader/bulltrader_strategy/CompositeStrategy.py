
from bt4.Constants import R
from bt4.quote.TAIMgr import TAIMgr
from bt4.model.trade_object import Trade
from bt4.utils.misc_utils import load_bt3_config
from bt4.utils.python_utils import load_class_from_module, dt2str, is_the_time
from bt4.utils.market_utils import match_time_frame, compute_sell_timeframes, compute_vol5
from bt4.utils.mylog import init_log
# from bulltrader_strategy.Strategy2 import NettingStrategy, AbstractStrategy, HedgingStrategy
from bt4.strategy.Strategy import AbstractStrategy

log = init_log()

def load_stgy_n_params(config_name, am, report_storage, markets, composite_params) -> AbstractStrategy:

    r = R()
    params = load_bt3_config(config_name)

    ## Load Strategy Config
    # config = load_class_from_module(config_name, 'Config')
    # config.load_params(r, params)

    ## Update Markets for Each Internal-Strategy
    params[r.OP.MARKET] = markets

    strategy_name = params[r.STGY.NAME]
    module_name = params[r.STGY.MODULE]
    strategy_package_name = "bulltrader_strategy."
    strategy = load_class_from_module(strategy_package_name + module_name, strategy_name)
    s_params = params[r.STGY.PARAMS]

    ## Load Common Config
    # exchange = config_name.split('.')[1]
    # comm_cfg_module = f'bt3_config.{exchange}.bt_{exchange}_common_conf'
    # comm_cls = f'Bt_{exchange}_CommonConfig'
    # common_config = load_class_from_module(comm_cfg_module, comm_cls)
    # common_config.load_params(r, params)

    if 'timeframes' in composite_params:
        s_params['timeframes'] = composite_params['timeframes']

    if 'timegap' in composite_params:
        s_params['timegap'] = composite_params['timegap']

    strategy.set_params(am, report_storage, markets, s_params)
    return strategy


class BBStgyMgr:
    BULL_MARKET = 'Bull'   # Market Type
    BEAR_MARKET = 'Bear'

    def __init__(self):
        pass

    def load_strategies(self, am, rs, markets, params):
        self.markets = markets
        self.params = params
        self.mkt_stgies = {}
        self.mkt_stgy_confs = {}

        for market in markets:
            self.mkt_stgies[market] = {}
            self.mkt_stgy_confs[market] = {}
            ## Load Bull Strategy and call set_params
            bull_mkt_stgy = load_stgy_n_params(params['bull_mkt_conf'], am, rs, (market,), params)
            bull_mkt_stgy.enable_asset_rebalance = False
            self.mkt_stgies[market][BBStgyMgr.BULL_MARKET] = bull_mkt_stgy
            self.mkt_stgy_confs[market][BBStgyMgr.BULL_MARKET] = params['bull_mkt_conf']

            ## Load Bear Strategy and call set_params
            bear_mkt_stgy = load_stgy_n_params(params['bear_mkt_conf'], am, rs, (market,), params)
            bear_mkt_stgy.enable_asset_rebalance = False
            self.mkt_stgies[market][BBStgyMgr.BEAR_MARKET] = bear_mkt_stgy
            self.mkt_stgy_confs[market][BBStgyMgr.BEAR_MARKET] = params['bear_mkt_conf']

    def call_setup(self, context):
        for market in self.markets:
            for market_type in self.mkt_stgies[market]:
                self.mkt_stgies[market][market_type].setup(context)

    def get_market_stgy_n_conf(self, market, m_type):
        return self.mkt_stgies[market][m_type], self.mkt_stgy_confs[market][m_type]

    def get_stgy_conf(self, market, m_type):
        return self.mkt_stgy_confs[market][m_type]

    def get_strategy(self, market, m_type):
        return self.mkt_stgies[market][m_type]


class CompositeStgy_Support:
    def __init__(self):
        self.trading_list = []

    def set_params_0(self, am, report_storage, markets, params, report, ex_type):
        self.asset_mgmt = am
        self.report = report
        self.markets = markets
        self.ex_type = ex_type

        self.bb_stg_mgr = BBStgyMgr()
        self.bb_stg_mgr.load_strategies(am, report_storage, markets, params)

        self.tai_decision = params['tai_decision']

        self.cur_mkt_stgy = {}
        self.cur_mkt_type = {}
        self.before_evaluate_balance = self.asset_mgmt.get_evaluated_balance()

    def setup_0(self, context):
        self.context = context
        self.bb_stg_mgr.call_setup(context)

    def init_trading_0(self, quote):
        time_dt = quote.get_time()

        tmgr = TAIMgr(quote, self.ex_type)
        market_ticks = quote.get_market_ticks(self.ex_type)
        ###########################################################
        market_decision_ma = tmgr.get_unary(self.tai_decision[0], self.tai_decision[1],
                                            self.tai_decision[2], self.tai_decision[3])

        init_settle = self.report.get_trading_list()[-1]
        self.trading_list.append(init_settle)

        for market in self.markets:
            tick = market_ticks[market]
            ma = market_decision_ma[market]
            if tick.close >= ma:
                self.cur_mkt_stgy[market], bull_strategy_conf = self.bb_stg_mgr.get_market_stgy_n_conf(market, BBStgyMgr.BULL_MARKET)
                self.cur_mkt_type[market] = BBStgyMgr.BULL_MARKET
                log.info(f'## {market} Market::Bull Strategy ({bull_strategy_conf}) has been initially selected!!')
            else:
                self.cur_mkt_stgy[market], bear_strategy_conf = self.bb_stg_mgr.get_market_stgy_n_conf(market, BBStgyMgr.BEAR_MARKET)
                self.cur_mkt_type[market] = BBStgyMgr.BEAR_MARKET
                log.info(f'## {market} Market::Bear Strategy ({bear_strategy_conf}) has been initially selected!!')

            # mkt_quote = quote.pick_market(self.ex_type, market)
            mkt_quote = quote
            init_strategy_result = self.cur_mkt_stgy[market].init_trading(mkt_quote)
            if not init_strategy_result:
                return False
        return True

    def perform_0(self, quote, is_rebalance_time,
                  is_buy_time, expected_buy_timeframe_str, is_sell_time, expected_sell_timeframe_str):
        time_dt = quote.get_time()
        tmgr = TAIMgr(quote, self.ex_type)
        market_ticks = quote.get_market_ticks(self.ex_type)
        ########################################################################
        is_59_minute = True if time_dt.minute == 59 else False

        if self.context.backtestor is not None:    # In Simulation Mode, return immediately when it's not a trading hour for fast processing.
            if not(is_rebalance_time or is_buy_time or is_sell_time or is_59_minute):
                return

        if is_rebalance_time:
            market_vol5 = compute_vol5(quote, tmgr, self.ex_type)
            self.asset_mgmt.append_supplements(market_vol5)
            self.asset_mgmt.rebalance(market_ticks)

        # if is_buy_time or is_sell_time:
        market_decision_ma = tmgr.get_unary(self.tai_decision[0], self.tai_decision[1],
                                            self.tai_decision[2], self.tai_decision[3])
        for market in market_ticks:
            tick = market_ticks[market]
            decision_ma = market_decision_ma[market]

            # if is_buy_time or is_sell_time:
            stgy_conf = self.bb_stg_mgr.get_stgy_conf(market, self.cur_mkt_type[market])

            is_trade_exist = self.asset_mgmt.exist_open_positions(market)
            log.info(f'[{dt2str(time_dt)}] {market} ({self.cur_mkt_type[market]}:{stgy_conf}): '
                 f'[strategy update] price ({tick.close}) > {self.tai_decision[0]}{self.tai_decision[1]}'
                     f'({decision_ma:.2f}) and check trade exists ({is_trade_exist}) of {market} market.')

            mkt_quote = quote.pick_market(self.ex_type, market)

            if tick.close >= decision_ma:
                if not is_trade_exist: # if there is no buy order
                    if self.cur_mkt_stgy[market] == self.bb_stg_mgr.get_strategy(market, BBStgyMgr.BEAR_MARKET):
                        next_strategy = self.bb_stg_mgr.get_strategy(market, BBStgyMgr.BULL_MARKET)
                        self.cur_mkt_type[market] = BBStgyMgr.BULL_MARKET
                        bull_strategy_conf = self.bb_stg_mgr.get_stgy_conf(market, BBStgyMgr.BULL_MARKET)
                        log.info(f'## {market} Market::Bull Strategy ({bull_strategy_conf}) has been selected!!')

                        next_strategy.init_trading(mkt_quote)
                        self.cur_mkt_stgy[market] = next_strategy
            else:
                if not is_trade_exist: # if there is no buy order
                    if self.cur_mkt_stgy[market] == self.bb_stg_mgr.get_strategy(market, BBStgyMgr.BULL_MARKET):
                        next_strategy = self.bb_stg_mgr.get_strategy(market, BBStgyMgr.BEAR_MARKET)
                        self.cur_mkt_type[market] = BBStgyMgr.BEAR_MARKET
                        bear_strategy_conf = self.bb_stg_mgr.get_stgy_conf(market, BBStgyMgr.BEAR_MARKET)
                        log.info(f'## {market} Market::Bear Strategy ({bear_strategy_conf}) has been selected!!')

                        next_strategy.init_trading(mkt_quote)
                        self.cur_mkt_stgy[market] = next_strategy

            trading_list_len_before_trading = len(self.cur_mkt_stgy[market].report.trading_list)
            self.cur_mkt_stgy[market].perform(mkt_quote)

            trading_list_len_after_trading = len(self.cur_mkt_stgy[market].report.trading_list)
            if trading_list_len_after_trading > trading_list_len_before_trading:
                updated_trading_list = self.cur_mkt_stgy[market].report.trading_list[-(trading_list_len_after_trading - trading_list_len_before_trading):]
                for trade in updated_trading_list:
                    if trade.order != 'SETT':
                        self.trading_list.append(trade)
                self.report.set_trading_list(self.trading_list)

        if is_rebalance_time:  ## Hedge
            after_evaluated_balance, desc = self.asset_mgmt.compute_evaluated_balance(market_ticks)
            time_str = dt2str(time_dt)
            log.info(f'[{time_str}] SETTLE-profit:: {after_evaluated_balance - self.before_evaluate_balance}, - balance: {after_evaluated_balance}')
            profit = after_evaluated_balance - self.before_evaluate_balance
            settle = Trade(True, "SETT", time_str, 'SETT', 0, 0, 0, 0, 0,
                           self.asset_mgmt.get_cash_balance(), profit, after_evaluated_balance, desc)
            self.report.append(settle)
            self.before_evaluate_balance = after_evaluated_balance

        log.info(f'[{dt2str(time_dt)}] Evaluated balance :: {self.asset_mgmt.get_evaluated_balance()}')


class CompositeBullBearStrategy(AbstractStrategy):
    def __init__(self):
        super(CompositeBullBearStrategy, self).__init__()
        self.composite_support = CompositeStgy_Support()

    def set_params(self, am, report_storage, markets, params):
        self.ex_type = params['quote_provider']
        super(CompositeBullBearStrategy, self).set_params(am, report_storage, markets, self.ex_type)
        self.composite_support.set_params_0(am, report_storage, markets, params, self.report, self.ex_type)

    def setup(self, context):
        super(CompositeBullBearStrategy, self).setup(context)
        self.composite_support.setup_0(context)

    def init_trading(self, quote):
        super(CompositeBullBearStrategy, self).init_trading(quote)
        return self.composite_support.init_trading_0(quote)

    def perform(self, quote):
        super(CompositeBullBearStrategy, self).perform(quote)
        if self.is_paused:
            return
        time_dt = quote.get_time()
        #################################################################################

        current_hour = time_dt.hour
        is_59_minute = True if time_dt.minute == 59 else False
        is_8oclock_sell_time = True if current_hour == 7 and is_59_minute else False
        is_9oclock_buy_time = True if current_hour == 8 and is_59_minute else False

        return self.composite_support.perform_0(quote, is_9oclock_buy_time,
                                                is_9oclock_buy_time, None, is_8oclock_sell_time, None)   # pass method of this class


class CompositeBullBearStrategy_Hdge(AbstractStrategy):
    def __init__(self):
        super(CompositeBullBearStrategy_Hdge, self).__init__()
        self.composite_support = CompositeStgy_Support()

    def set_params(self, am, report_storage, markets, params):
        self.ex_type = params['quote_provider']
        super(CompositeBullBearStrategy_Hdge, self).set_params(am, report_storage, markets, self.ex_type)
        self.buy_timeframes = params['timeframes']
        self.buy_sell_time_gap = params['timegap']
        self.composite_support.set_params_0(am, report_storage, markets, params, self.report, self.ex_type)
        self.buy_sell_tf, self.sell_buy_tf, self.sell_timeframes = compute_sell_timeframes(self.buy_timeframes,
                                                                                           self.buy_sell_time_gap)

    def setup(self, context):
        super(CompositeBullBearStrategy_Hdge, self).setup(context)
        self.composite_support.setup_0(context)

    def init_trading(self, quote):
        super(CompositeBullBearStrategy_Hdge, self).init_trading(quote)
        return self.composite_support.init_trading_0(quote)

    def perform(self, quote):
        super(CompositeBullBearStrategy_Hdge, self).perform(quote)
        time_dt = quote.get_time()

        current_hour = time_dt.hour
        is_59_minute = True if time_dt.minute == 59 else False

        is_vol_update_time = is_the_time(time_dt, 8, 59)
        is_buy_time, expected_buy_timeframe_str, buy_tf_hour = match_time_frame(time_dt, self.buy_timeframes)
        is_sell_time, expected_sell_timeframe_str, sell_tf_hour = match_time_frame(time_dt, self.sell_timeframes)

        return self.composite_support.perform_0(quote, is_vol_update_time, is_buy_time,
                                                expected_buy_timeframe_str, is_sell_time,
                                                expected_sell_timeframe_str)
