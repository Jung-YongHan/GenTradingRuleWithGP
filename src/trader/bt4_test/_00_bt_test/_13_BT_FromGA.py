import unittest

from bt4.model.storage_mgr import StrategyStorage
from bt4_test._00_bt_test._00_BTTestHelper import proceed_backtest_with_tid


class MyTestCase(unittest.TestCase) :

    def test_from_tid(self) :
        sid = 92
        is_same = proceed_backtest_with_tid(sid)
        self.assertEqual(is_same, True)

    def test_fromGA(self) :
        stgy = "ws_ga_result_test"
        sid = StrategyStorage.instance().get_trading_id_of_stgyname("bt", stgy)
        is_same = proceed_backtest_with_tid(sid)
        self.assertEqual(is_same, True)


if __name__ == '__main__' :
    unittest.main()
