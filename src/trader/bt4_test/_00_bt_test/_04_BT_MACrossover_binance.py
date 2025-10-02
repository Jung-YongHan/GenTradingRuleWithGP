import unittest

from bt4 import GlobalProperties
from bt4.model.storage_mgr import StrategyStorage
GlobalProperties.__VERSION__ = "bt4"

from bt4_test._00_bt_test._00_BTTestHelper import proceed_backtest_with_tid


class SuperWinningSession_upbit(unittest.TestCase):

    def test_ma_crossover_vol_binance(self):
        sid = StrategyStorage.instance().get_trading_id_of_stgyname("bt", "ma_crossover_vol_binance")
        is_same = proceed_backtest_with_tid(sid)
        self.assertEqual(is_same, True)



if __name__ == '__main__':
    unittest.main()
