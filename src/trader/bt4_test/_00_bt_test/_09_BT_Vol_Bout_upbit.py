import unittest

from bt4 import GlobalProperties
from bt4.model.storage_mgr import StrategyStorage

GlobalProperties.__VERSION__ = "bt4"

from bt4_test._00_bt_test._00_BTTestHelper import proceed_backtest_with_tid


class TTrading_upbit(unittest.TestCase):

    def test_vol_bout_sws_hdg_vol_bt4(self):
        sid = StrategyStorage.instance().get_trading_id_of_stgyname("bt", "vol_bout_sws_hdg_vol")
        is_same = proceed_backtest_with_tid(sid)
        self.assertEqual(is_same, True)

    def test_vol_bout_hdg_vol_bt4(self):
        sid = StrategyStorage.instance().get_trading_id_of_stgyname("bt", "vol_bout_hdg_vol")
        is_same = proceed_backtest_with_tid(sid)
        self.assertEqual(is_same, True)

    def test_vol_bout_vol_bt4(self):
        sid = StrategyStorage.instance().get_trading_id_of_stgyname("bt", "vol_bout_vol")
        is_same = proceed_backtest_with_tid(sid)
        self.assertEqual(is_same, True)





if __name__ == '__main__':
    unittest.main()
