import os
import unittest
from os.path import dirname, join

from bt4.Constants import CandleType, ExType, AssetMgrType, Operation_Type, TradeResultStorageType
from bt4.exec.BullTraderMain import Context
from bt4.utils.misc_utils import calibrate_simul_env
from bt4.utils.python_utils import load_class_from_module
from spiketesting._03_arch_skeleton_testing.context import V4Context
from spiketesting._03_arch_skeleton_testing.backtestor.backtestor import BackTestor
from spiketesting._03_arch_skeleton_testing.factory import ExecutionMode


class MyTestCase(unittest.TestCase):

    def test_backtestor(self):

        import bt4.utils.mylog as log_module
        log_module.log_mode = Operation_Type.BACK_TESTOR.value

        from bt4.Constants import R
        r = R()
        params = {}

        params[r.OP.OP] = Operation_Type.BACK_TESTOR

        params[r.OP.BT.START] = '2018-10-01T08:59:00'
        params[r.OP.MARKET] = ('KRW-BTC', 'KRW-ETH', 'KRW-XRP')
        params[r.OP.BT.CANDLE_TYPE] = CandleType.HOUR
        params[r.OP.BT.TA_INDICATORS] = ['vol', 'vol5', 'ma5_', 'ma3_', 'ma10_', 'ma20_']
        params[r.OP.BT.TIME] = ['08:59', '12:59', '16:59', '20:59']

        params[r.EX.EX_TYPE] = ExType.dummy_upbit
        params[r.EX.EX_DUMMY_INITIAL_RATIO] = 10000000
        params[r.EX.EX_DUMMY_FEE_SLIPPAGE] = 0.0008

        params[r.AM.AM_TYPE] = AssetMgrType.VOLATILITY_HDGE
        params[r.AM.AM_VOL_TARGET] = 0.04
        params[r.AM.AM_VOL_TAI] = 'vol5'
        params[r.AM.AM_TIMEFRAMES] = ['08:59', '17:59']

        params[r.RS.RS_TYPE] = TradeResultStorageType.FILE
        params[r.STGY.NAME] = 'SuperWinningSession_Hedge'
        params[r.STGY.MODULE] = 'SuperWinningSessionStrategy'
        params[r.RS.RS_FILE_NAME] = params[r.STGY.NAME]

        params[r.STGY.PARAMS] = {'timeframes': params[r.AM.AM_TIMEFRAMES],
                                     'timegap': 1}

        calibrate_simul_env(r, params)

        log_module.log_strategy = params[r.STGY.NAME]
        from bt4.utils.mylog import init_log
        log = init_log()
        ###########################################################################

        markets = params[r.OP.MARKET]
        simul_start = params[r.OP.BT.START]
        simul_end = params[r.OP.BT.END] if r.OP.BT.END in params else None
        simul_times = params[r.OP.BT.TIME]
        simul_ta_indicators = params[r.OP.BT.TA_INDICATORS]
        data_type = params[r.OP.BT.CANDLE_TYPE]
        strategy_name = params[r.STGY.NAME]
        ########################
        ## Newly Added Code
        context = self.__create_strategy(r, params)

        v3_context = V4Context.from_context(context)
        v3_context.ctx_params['account'] = 'stkim'
        v3_context.ctx_params[r.OP.BT.CANDLE_TYPE] = params[r.OP.BT.CANDLE_TYPE]
        v3_context.ctx_params[r.OP.BT.TA_INDICATORS] = params[r.OP.BT.TA_INDICATORS]

        v3_context.set_attribute("Execution_Mode", ExecutionMode.BackTesting_Mode)

        backtestor = BackTestor(v3_context, markets=markets, start=simul_start, end=simul_end,
                                   data_type=data_type, simul_times=simul_times,
                                   simul_tais=simul_ta_indicators)


        # core.setup(context)
        # Temp Code
        v3_context.strategy.setup(context)
        v3_context.backtestor = backtestor

        ########################
        ## start
        backtestor.simulate(v3_context.strategy)
        df = v3_context.strategy.report.toDataFrame()
        if len(df) > 0:
            df.sort_values(by='date', ascending=True, inplace=True)
            root_dir = dirname(dirname(dirname(__file__)))  ## parent of parent of directory of simulator.py
            file_name = join(root_dir, f'report/{strategy_name}_BeforeRefactoring_{os.getpid()}.csv')
            df.to_csv(file_name)

            from bt4.core.ResultAnalyzer import analyze_result
            analyze_result(df, strategy_name, v3_context.report_storage)
            v3_context.report_storage.store('=========================================================')


    def __create_strategy(self, r, params):
        simulator = None
        auto_trader = None
        markets = params[r.OP.MARKET]
        data_type = params[r.OP.BT.CANDLE_TYPE]
        op_type = params[r.OP.OP]

        ######################################################
        ### Exchange
        ex_type = params[r.EX.EX_TYPE]
        core_package_name = "bt4.exec."
        ex = load_class_from_module(core_package_name + "ExchangeConnector",
                                         ex_type.value + 'ExchangeConnector')

        from bt4.Constants import ExType
        if ex_type == ExType.dummy_upbit:
            initial_budget = params[r.EX.EX_DUMMY_INITIAL_RATIO]
            fee_ratio = params[r.EX.EX_DUMMY_FEE_SLIPPAGE]
            ex.set_params(initial_budget, fee_ratio)
        elif ex_type == ExType.upbit:  ## Currently Not Reach here!
            access_key = params[r.EX.EX_ACCESS_KEY]
            secret_key = params[r.EX.EX_SECRET_KEY]
            ex.set_params(access_key, secret_key)
            ex.is_live_trade = True

        ######################################################
        ### Asset Management
        core_package_name = "bt4.exec."
        am_type = params[r.AM.AM_TYPE]
        am = load_class_from_module(core_package_name + "AssetManagement", am_type.value)
        from bt4.Constants import AssetMgrType
        from bt4.trade import NettingTradeMgr, HedgingTradeMgr
        if am_type == AssetMgrType.FIXED:                  ## Not Reach here!
            fixed_trade_ratio = params[r.AM.AM_FIXED_TRADE_RATIO]
            am.set_params(ex, fixed_trade_ratio, markets, NettingTradeMgr(op_type))
        elif am_type == AssetMgrType.VOLATILITY:      ## Not Reach here!
            target_volatility_ratio = params[r.AM.AM_VOL_TARGET]
            volatility_tai = params[r.AM.AM_VOL_TAI]
            am.set_params(ex, target_volatility_ratio, volatility_tai, markets,
                               NettingTradeMgr(op_type))
        if am_type == AssetMgrType.FIXED_HDGE:        ## Not Reach here!
            fixed_trade_ratio = params[r.AM.AM_FIXED_TRADE_RATIO]
            timeframes = params[r.AM.AM_TIMEFRAMES]
            am.set_params(ex, fixed_trade_ratio, markets, timeframes, HedgingTradeMgr(op_type))
        if am_type == AssetMgrType.VOLATILITY_HDGE:   ## Will be executed here!
            target_volatility_ratio = params[r.AM.AM_VOL_TARGET]
            volatility_tai = params[r.AM.AM_VOL_TAI]
            timeframes = params[r.AM.AM_TIMEFRAMES]
            am.set_params(ex, target_volatility_ratio, volatility_tai, markets, timeframes,
                               HedgingTradeMgr(op_type))

        core_package_name = "bt4.exec."
        ######################################################
        ### Report Storage
        rs_type = params[r.RS.RS_TYPE]
        rs = load_class_from_module(core_package_name + "SimulationSupport", rs_type.value)
        from bt4.Constants import TradeResultStorageType
        if rs_type == TradeResultStorageType.FILE:
            file_name = params[r.RS.RS_FILE_NAME]
            visualize_support = params[r.RS.RS_VISUALIZE] if r.RS.RS_VISUALIZE in params else True
            rs.set_params(file_name, visualize_support)
        elif rs_type == TradeResultStorageType.MONGO:  ## Only For AutoTrading
            pass

        ######################################################
        ### Strategy
        strategy_name = params[r.STGY.NAME]
        module_name = params[r.STGY.MODULE]
        strategy_package_name = "bulltrader_strategy."
        strategy = load_class_from_module(strategy_package_name + module_name, strategy_name)
        s_params = params[r.STGY.PARAMS]
        strategy.set_params(am, rs, markets, s_params)

        return Context(simulator, auto_trader, markets, data_type, ex, am, rs,
                       strategy, params)


if __name__ == '__main__':
    unittest.main()
