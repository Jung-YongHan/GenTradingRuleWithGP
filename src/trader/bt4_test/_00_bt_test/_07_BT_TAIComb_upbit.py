import unittest

from bt4.model.storage_mgr import StrategyStorage
from bt4_test._00_bt_test._00_BTTestHelper import proceed_backtest_with_tid


class WinningSession_upbit(unittest.TestCase):

    def test_tai_comb_vol_bt4(self):
        sid = StrategyStorage.instance().get_trading_id_of_stgyname("bt", "tai_comb_vol")
        is_same = proceed_backtest_with_tid(sid)
        self.assertEqual(is_same, True)



if __name__ == '__main__':
    unittest.main()
