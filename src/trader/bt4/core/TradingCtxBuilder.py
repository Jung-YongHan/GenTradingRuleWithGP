from bt4 import GlobalProperties
from bt4.Constants import R, Operation_Type
from bt4.core.Context import Context
from bt4.resource_path_mgr import RPath
from bt4.trade.ExchangeConnector import ExConnFactory
from bt4.utils.market_utils import handle_dummy_ex
from bt4.utils.mylog import init_log
from bt4.utils.python_utils import load_class_from_module
from bt4.Constants import ExType

log = init_log()

r = R()
class TradingContextBuilder:

    def __init__(self, conf_params):
        self.params = conf_params

        self.op_type = self.params[r.OP.OP]
        self.backtestor = None
        self.stgy_live_trader = None
        self.markets = self.params[r.OP.MARKET]
        self.candle_type = self.params[r.OP.BT.CANDLE_TYPE]

        self.context = Context(self.backtestor, self.stgy_live_trader, self.markets, self.candle_type, None, None,
                       None, None, self.params)

    def build_trading_system(self):

        if self.op_type.value == Operation_Type.BACK_TESTOR.value:
            self.op_type = Operation_Type.BACK_TESTOR ## Issue: I don't know why the enum instance is different depending on bat and pycharm execution
            markets = self.params[r.OP.MARKET]
            bt_start = self.params[r.OP.BT.START]
            bt_end = self.params[r.OP.BT.END] if r.OP.BT.END in self.params else None
            tr_times = self.params[r.OP.BT.TIME]

            bt_cdl_types_needed = None if r.OP.BT.CDL_TYPES_NEEDED not in self.params else self.params[r.OP.BT.CDL_TYPES_NEEDED]

            from bt4.core.Backtestor import Backtestor
            quote_providers = self.params[r.OP.QUOTE_PROVIDERS]

            backtestor = Backtestor(markets=markets, start_str= bt_start, end_str= bt_end,
                                    candle_type= self.candle_type, tr_times = tr_times,
                                    quote_providers = quote_providers,
                                    cld_type_needed=bt_cdl_types_needed)
            self.context.backtestor = backtestor
            return backtestor

        elif self.op_type.value == Operation_Type.LIVE_TRADING.value or self.op_type.value == Operation_Type.FORWARD_TESTING.value:
            from bt4.core.StrategyLiveTrader import StrategyLiveTrader
            quote_mode = self.params[r.OP.live.QUOTE_MODE]
            usr_id = self.params[r.EX.EX_USR_ID]
            tr_times = self.params[r.OP.BT.TIME]
            stgy_live_trader = StrategyLiveTrader(usr_id, self.markets, self.candle_type, tr_times, quote_mode)
            self.context.stgy_live_trader = stgy_live_trader
            return stgy_live_trader

    def build_exchange(self):
        ex_type = self.params[r.EX.EX_TYPE]

        if (ex_type == ExType.dummy_upbit) or (ex_type == ExType.dummy_bithumb) or \
                (ex_type == ExType.dummy_binance) or (ex_type == ExType.dummy_binanceusdm) :
            ex = ExConnFactory.instance().get_ex_conn(ex_type)
            initial_budget = self.params[r.EX.EX_DUMMY_INITIAL_RATIO]
            fee_ratio = self.params[r.EX.EX_DUMMY_FEE_SLIPPAGE]
            ex.set_params(initial_budget, fee_ratio)

        elif (ex_type == ExType.upbit) or (ex_type == ExType.bithumb) or \
             (ex_type == ExType.binance) or (ex_type == ExType.binanceusdm):   ## Only For LiveTrading
            access_key = self.params[r.EX.EX_ACCESS_KEY]
            secret_key = self.params[r.EX.EX_SECRET_KEY]

            if ex_type == ExType.binanceusdm:
                ex = ExConnFactory.instance().get_ex_conn(ex_type, access_key,
                                                          secret_key, self.markets)
            else:
                ex = ExConnFactory.instance().get_ex_conn(ex_type, access_key,
                                                          secret_key)

            ex.is_live_trade = True

        self.context.exchange = ex
        return ex


    def build_asset_mgmt(self):
        core_package_name = "bt4.trade."
        # self.__extend_trade_mgr_config__(self.params)

        am_type = self.params[r.AM.AM_TYPE]
        am = load_class_from_module(core_package_name + "AssetMgr", am_type.value)
        from bt4.Constants import AssetMgrType
        from bt4.trade.TradeMgr import NettingTradeMgr, HedgingTradeMgr
        if am_type == AssetMgrType.FIXED:
            fixed_trade_ratio = self.params[r.AM.AM_FIXED_TRADE_RATIO]
            am.set_params(self.context.exchange, fixed_trade_ratio, self.markets, NettingTradeMgr(self.op_type))
        elif am_type == AssetMgrType.WEIGHTED:
            top_n_weights = self.params[r.AM.AM_WGHT_TOP_N]
            am.set_params(self.context.exchange, top_n_weights, self.markets, NettingTradeMgr(self.op_type))
        elif am_type == AssetMgrType.VOLATILITY:  ## Only For AutoTrading
            target_volatility_ratio = self.params[r.AM.AM_VOL_TARGET]
            volatility_tai = self.params[r.AM.AM_VOL_TAI]
            am.set_params(self.context.exchange, target_volatility_ratio, volatility_tai, self.markets,
                               NettingTradeMgr(self.op_type))
        if am_type == AssetMgrType.FIXED_HDGE:
            fixed_trade_ratio = self.params[r.AM.AM_FIXED_TRADE_RATIO]
            timeframes = self.params[r.AM.AM_TIMEFRAMES]
            am.set_params(self.context.exchange, fixed_trade_ratio, self.markets, timeframes, HedgingTradeMgr(self.op_type))
        if am_type == AssetMgrType.VOLATILITY_HDGE:
            target_volatility_ratio = self.params[r.AM.AM_VOL_TARGET]
            volatility_tai = self.params[r.AM.AM_VOL_TAI]
            timeframes = self.params[r.AM.AM_TIMEFRAMES]
            am.set_params(self.context.exchange, target_volatility_ratio, volatility_tai, self.markets, timeframes,
                               HedgingTradeMgr(self.op_type))
        self.context.asset_mgmt = am
        return am

    def build_report_storage(self):
        core_package_name = "bt4.core."
        rs_type = self.params[r.RS.RS_TYPE]
        rs = load_class_from_module(core_package_name + "ReportSupport", rs_type.value)
        from bt4.Constants import TradeResultStorageType
        if rs_type == TradeResultStorageType.FILE:
            file_name = self.params[r.RS.RS_FILE_NAME]
            visualize_support = self.params[r.RS.RS_VISUALIZE] if r.RS.RS_VISUALIZE in self.params else True
            rs.set_params(file_name, visualize_support)
        elif rs_type == TradeResultStorageType.MONGO:  ## Only For AutoTrading
            pass
        elif rs_type == TradeResultStorageType.PSQL:
            tid = self.params[r.OP.tid]
            bt_start = self.params[r.OP.BT.START]
            bt_end = self.params[r.OP.BT.END] if r.OP.BT.END in self.params else None
            rs.set_params(tid, bt_start, bt_end, self.params[r.OP.OP], self.markets)
        self.context.report_storage = rs
        return rs

    def build_strategy(self):
        strategy_name = self.params[r.STGY.NAME]
        module_name = self.params[r.STGY.MODULE]
        extype = handle_dummy_ex(self.params[r.EX.EX_TYPE])
        stgy_root = RPath.instance().stgy_root_module()
        if GlobalProperties.__VERSION__ == "bt3":
            strategy_package_name = f"{stgy_root}."
        elif GlobalProperties.__VERSION__ == "bt4":
            strategy_package_name = f"{stgy_root}.{extype.value}."

        strategy = load_class_from_module(strategy_package_name + module_name, strategy_name)
        s_params = self.params[r.STGY.PARAMS]
        strategy.set_params(self.context.asset_mgmt, self.context.report_storage, extype, self.markets, s_params)
        self.context.strategy = strategy
        return strategy

    def get_context(self):
        return self.context

    def get_op_type(self):
        return self.op_type

    # def __extend_trade_mgr_config__(self, params):
    #     from bt3_config.trade_mgmt_config import trade_tactic
    #     if r.Tm.TM_TACTIC in params:
    #         ttactic = params[r.Tm.TM_TACTIC]
    #         ttactic_cfg_dic = trade_tactic[ttactic]
    #         if 'overide_from' in ttactic_cfg_dic:
    #             ovg_from_tactic = ttactic_cfg_dic['overide_from']
    #             if ovg_from_tactic in trade_tactic:
    #                 ttactic_cfg_dic.update(trade_tactic[ovg_from_tactic])
    #             else:
    #                 log.debug(f'Error! override_from tactic({ovg_from_tactic}) does not exist in trade_tactics({trade_tactic.keys()})')
    #             ttactic_cfg_dic.pop('overide_from', None)
    #
    #         params.update(ttactic_cfg_dic)
    #     return params
