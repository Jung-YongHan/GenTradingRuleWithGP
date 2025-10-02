import unittest

from bt4.model.storage_mgr import StrategyStorage
from bt4.utils.mylog import init_log
import bt4.utils.mylog as log_module
from bt4_test._00_bt_test._00_BTTestHelper import proceed_backtest_with_tid

log_module.log_mode = 'simulator'
log = init_log()

class SWKim1_upbit(unittest.TestCase):


    def test_swkim_1_4h_vol_bt4(self):
        sid = StrategyStorage.instance().get_trading_id_of_stgyname("bt", "swkim_1_4h_vol")
        is_same = proceed_backtest_with_tid(sid)
        self.assertEqual(is_same, True)

    def test_swkim_1_hdg_vol_bt4(self):
        sid = StrategyStorage.instance().get_trading_id_of_stgyname("bt", "swkim_1_hdg_vol")
        is_same = proceed_backtest_with_tid(sid)
        self.assertEqual(is_same, True)


    def test_swkim_1_vol_bt4(self):
        sid = StrategyStorage.instance().get_trading_id_of_stgyname("bt", "swkim_1_vol")
        is_same = proceed_backtest_with_tid(sid)
        self.assertEqual(is_same, True)

    def test_ma_crossover_vol2(self):
        sid = StrategyStorage.instance().get_trading_id_of_stgyname("bt", "ma_crossover_vol2")
        is_same = proceed_backtest_with_tid(sid)
        self.assertEqual(is_same, True)



if __name__ == '__main__':
    unittest.main()
