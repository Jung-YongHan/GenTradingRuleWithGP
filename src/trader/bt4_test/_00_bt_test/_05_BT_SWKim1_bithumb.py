import unittest

from bt4.model.storage_mgr import StrategyStorage
from bt4.utils.mylog import init_log
import bt4.utils.mylog as log_module
from bt4_test._00_bt_test._00_BTTestHelper import proceed_backtest_with_tid

log_module.log_mode = 'simulator'
log = init_log()

class SWKim1_upbit(unittest.TestCase):

    def test_swkim_1_hdg_vol(self):
        sid = StrategyStorage.instance().get_trading_id_of_stgyname("bt", "swkim_1_hdg_vol")
        is_same = proceed_backtest_with_tid(sid)
        self.assertEqual(is_same, True)


if __name__ == '__main__':
    unittest.main()
