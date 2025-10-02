import unittest

from bt4 import GlobalProperties
from bt4.model.storage_mgr import StrategyStorage

GlobalProperties.__VERSION__ = "bt4"

from bt4_test._00_bt_test._00_BTTestHelper import proceed_backtest_with_tid


class SuperWinningSession_upbit(unittest.TestCase):

    def test_sws_1m_vol(self):
        sid = StrategyStorage.instance().get_trading_id_of_stgyname("bt", "sws_1m_vol")
        is_same = proceed_backtest_with_tid(sid)
        self.assertEqual(is_same, True)

    def test_sws_day_alt_weight_bt4(self):
        sid = StrategyStorage.instance().get_trading_id_of_stgyname("bt", "sws_day_alt_weight")
        is_same = proceed_backtest_with_tid(sid)
        self.assertEqual(is_same, True)


    def test_sws_day_hdg_vol_tai_bt4(self):
        sid = StrategyStorage.instance().get_trading_id_of_stgyname("bt", "sws_day_hdg_vol_tai")
        is_same = proceed_backtest_with_tid(sid)
        self.assertEqual(is_same, True)


    def test_sws_day_hdg_vol_bt4(self):
        sid = StrategyStorage.instance().get_trading_id_of_stgyname("bt", "sws_day_hdg_vol")
        is_same = proceed_backtest_with_tid(sid)
        self.assertEqual(is_same, True)


    def test_sws_day_hdg_asym_vol_bt4(self):
        sid = StrategyStorage.instance().get_trading_id_of_stgyname("bt", "sws_day_hdg_asym_vol")
        is_same = proceed_backtest_with_tid(sid)
        self.assertEqual(is_same, True)

    def test_sws_day_hdg_vol_macd_bt4(self):
        sid = StrategyStorage.instance().get_trading_id_of_stgyname("bt", "sws_day_hdg_vol_macd")
        is_same = proceed_backtest_with_tid(sid)
        self.assertEqual(is_same, True)


    def test_sws_ma_crossover_hdg_vol_bt4(self):
        sid = StrategyStorage.instance().get_trading_id_of_stgyname("bt", "sws_ma_crossover_hdg_vol")
        is_same = proceed_backtest_with_tid(sid)
        self.assertEqual(is_same, True)


    def test_sws_ma_crossover_day_vol_bt4(self):
        sid = StrategyStorage.instance().get_trading_id_of_stgyname("bt", "sws_ma_crossover_day_vol")
        is_same = proceed_backtest_with_tid(sid)
        self.assertEqual(is_same, True)


    def test_sws_day_hdg_vol_ema_bt4(self):
        sid = StrategyStorage.instance().get_trading_id_of_stgyname("bt", "sws_day_hdg_vol_ema")
        is_same = proceed_backtest_with_tid(sid)
        self.assertEqual(is_same, True)


    def test_sws_4h_vol_bt4(self):
        sid = StrategyStorage.instance().get_trading_id_of_stgyname("bt", "sws_4h_vol")
        is_same = proceed_backtest_with_tid(sid)
        self.assertEqual(is_same, True)


    def test_sws_day_vol_bt4(self):
        sid = StrategyStorage.instance().get_trading_id_of_stgyname("bt", "sws_day_vol")
        is_same = proceed_backtest_with_tid(sid, False)
        self.assertEqual(is_same, True)



if __name__ == '__main__':
    unittest.main()
