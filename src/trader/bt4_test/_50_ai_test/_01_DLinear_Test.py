import unittest

from bt4.model.storage_mgr import StrategyStorage
from bt4_test._00_bt_test._00_BTTestHelper import proceed_backtest_with_tid


class MyTestCase(unittest.TestCase) :
    def test_ai_ws_day_vol_dlinear(self) :
        # sid = StrategyStorage.instance().get_trading_id_of_desc("bt", "ai_ws_day_vol_dlinear")
        is_same = proceed_backtest_with_tid(257)
        self.assertEqual(is_same, True)


if __name__ == '__main__' :
    unittest.main()
