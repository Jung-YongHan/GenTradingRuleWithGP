import unittest

from bt4 import GlobalProperties
from bt4.model.storage_mgr import StrategyStorage
import pandas as pd
import warnings

from bt4_test._00_bt_test._00_BTTestHelper import proceed_backtest_with_tid

warnings.filterwarnings("ignore", category=DeprecationWarning)

pd.set_option('display.max_columns', None)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('max_colwidth', None)

GlobalProperties.__VERSION__ = "bt4"
class WinningSession_upbit(unittest.TestCase):

    ## 1425: 시장변화감지 탄력 투자금 결정 투자
    def test_ws_day_hdg_with_id(self):
        is_same = proceed_backtest_with_tid(1425)
        self.assertEqual(is_same, True)

    def test_ws_day_vol_pair_trading_ga_optim(self):
        sid = StrategyStorage.instance().get_trading_id_of_stgyname("bt", "ws_day_vol_pair_trading_ga_optim")
        is_same = proceed_backtest_with_tid(sid)
        self.assertEqual(is_same, True)
    def test_ws_day_hdg_vol_wo_sell_only_stoploss(self):
        sid = StrategyStorage.instance().get_trading_id_of_stgyname("bt", "ws_day_hdg_vol_wo_sell_only_stoploss")
        is_same = proceed_backtest_with_tid(sid)
        self.assertEqual(is_same, True)

    def test_ws_day_vol_wo_sell_only_stoploss(self) :
        sid = StrategyStorage.instance().get_trading_id_of_stgyname("bt", "ws_day_vol_wo_sell_only_stoploss")
        is_same = proceed_backtest_with_tid(sid)
        self.assertEqual(is_same, True)

    def test_ws_ga_result_test(self):
        sid = StrategyStorage.instance().get_trading_id_of_stgyname("bt", "ws_ga_result_test")
        is_same = proceed_backtest_with_tid(sid)
        self.assertEqual(is_same, True)

    # def test_ws_day_hdg_with_id(self):
    #     is_same = proceed_backtest_with_tid(519)
    #     self.assertEqual(is_same, True)

    def test_ws_day_hdg_vol_cascade_tais(self):
        sid = StrategyStorage.instance().get_trading_id_of_stgyname("bt", "ws_day_hdg_vol_cascade_tais")
        is_same = proceed_backtest_with_tid(sid)
        self.assertEqual(is_same, True)

    def test_ws_day_vol_cascade_tais(self):
        sid = StrategyStorage.instance().get_trading_id_of_stgyname("bt", "ws_day_vol_cascade_tais")
        is_same = proceed_backtest_with_tid(sid)
        self.assertEqual(is_same, True)

    def test_ws_day_hdg_vol_bt4(self):
        sid = StrategyStorage.instance().get_trading_id_of_stgyname("bt", "ws_day_hdg_vol")
        is_same = proceed_backtest_with_tid(sid)
        self.assertEqual(is_same, True)

    # @unittest.skip("Tested")
    def test_ws_day_fixed_bt4(self):
        sid = StrategyStorage.instance().get_trading_id_of_stgyname("bt", "ws_day_fixed")
        is_same = proceed_backtest_with_tid(sid)
        self.assertEqual(is_same, True)


    def test_ws_day_hdg_vol_vwap_bt4(self):
        sid = StrategyStorage.instance().get_trading_id_of_desc("bt", "ws_day_hdg_vol_vwap")
        is_same = proceed_backtest_with_tid(sid)
        self.assertEqual(is_same, True)

    def test_ws_day_adaptive_param_hdg_volume_vol_bt4(self):
        sid = StrategyStorage.instance().get_trading_id_of_desc("bt", "ws_day_adaptive_param_hdg_volume_vol")
        is_same = proceed_backtest_with_tid(sid)
        self.assertEqual(is_same, True)

    def test_ws_day_hdg_volume_vol_bt4(self):
        sid = StrategyStorage.instance().get_trading_id_of_desc("bt", "ws_day_hdg_volume_vol")
        is_same = proceed_backtest_with_tid(sid)
        self.assertEqual(is_same, True)

    def test_ws_day_vol_bt4(self):
        sid = StrategyStorage.instance().get_trading_id_of_stgyname("bt", "ws_day_vol")
        is_same = proceed_backtest_with_tid(sid)
        self.assertEqual(is_same, True)


    def test_ws_day_hdg_fixed_bt4(self):
        sid = StrategyStorage.instance().get_trading_id_of_stgyname("bt", "ws_day_hdg_fixed")
        is_same = proceed_backtest_with_tid(sid)
        self.assertEqual(is_same, True)

    def test_ws_alt_vol_bt4(self):
        sid = StrategyStorage.instance().get_trading_id_of_desc("bt", "ws_alt_vol")
        is_same = proceed_backtest_with_tid(sid)
        self.assertEqual(is_same, True)


    def test_ws_day_hdg_vol_mma_bt4(self):
        sid = StrategyStorage.instance().get_trading_id_of_desc("bt", "ws_day_hdg_vol_mma")
        is_same = proceed_backtest_with_tid(sid)
        self.assertEqual(is_same, True)

    def test_ws_4h_vol_bt4(self):
        sid = StrategyStorage.instance().get_trading_id_of_desc("bt", "ws_4h_vol")
        is_same = proceed_backtest_with_tid(sid, False)
        self.assertEqual(is_same, True)



if __name__ == '__main__':
    unittest.main()
