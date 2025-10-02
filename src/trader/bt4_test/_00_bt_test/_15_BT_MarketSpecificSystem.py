import unittest

from bt4.model.storage_mgr import StrategyStorage
from bt4_test._00_bt_test._00_BTTestHelper import proceed_backtest_with_tid


class MyTestCase(unittest.TestCase) :

    def test_ma_crossover_hdg_vol_mkt_specific(self):
        sid = StrategyStorage.instance().get_trading_id_of_stgyname("bt", "ma_crossover_hdg_vol_mkt_specific")
        is_same = proceed_backtest_with_tid(sid)
        self.assertEqual(is_same, True)
    def test_sws_day_hdg_vol_tai_mkt_specific(self):
        sid = StrategyStorage.instance().get_trading_id_of_stgyname("bt", "sws_day_hdg_vol_tai_mkt_specific")
        is_same = proceed_backtest_with_tid(sid)
        self.assertEqual(is_same, True)

    def test_swkim_1_hdg_vol_mkt_specific(self):
        sid = StrategyStorage.instance().get_trading_id_of_stgyname("bt", "swkim_1_hdg_vol_mkt_specific")
        is_same = proceed_backtest_with_tid(sid)
        self.assertEqual(is_same, True)

    def test_sws_ma_crossover_hdg_vol_mkt_specific(self):
        sid = StrategyStorage.instance().get_trading_id_of_stgyname("bt", "sws_ma_crossover_hdg_vol_mkt_specific")
        is_same = proceed_backtest_with_tid(sid)
        self.assertEqual(is_same, True)
    def test_sws_day_vol_mkt_specific(self):
        sid = StrategyStorage.instance().get_trading_id_of_stgyname("bt", "sws_day_vol_mkt_specific")
        is_same = proceed_backtest_with_tid(sid)
        self.assertEqual(is_same, True)
    def test_ws_day_hdg_vol_mkt_specific(self):
        sid = StrategyStorage.instance().get_trading_id_of_stgyname("bt", "ws_day_hdg_vol_mkt_specific")
        is_same = proceed_backtest_with_tid(sid)
        self.assertEqual(is_same, True)
    def test_ws_day_vol_mkt_specific(self):
        sid = StrategyStorage.instance().get_trading_id_of_stgyname("bt", "ws_day_vol_mkt_specific")
        is_same = proceed_backtest_with_tid(sid)
        self.assertEqual(is_same, True)


if __name__ == '__main__' :
    unittest.main()
