import unittest

from bt4.model.storage_mgr import StrategyStorage
from bt4.utils.mylog import init_log
import bt4.utils.mylog as log_module
from bt4_test._00_bt_test._00_BTTestHelper import proceed_backtest_with_tid

log_module.log_mode = 'simulator'
log = init_log()

class CompositeStrategy_upbit(unittest.TestCase):

    def test_composite_bull_bear_market_bt4(self):
        sid = StrategyStorage.instance().get_trading_id_of_stgyname("bt", "composite_bull_bear_market")
        is_same = proceed_backtest_with_tid(sid)
        self.assertEqual(is_same, True)

    def test_composite_bull_bear_market_hdg_bt4(self):
        sid = StrategyStorage.instance().get_trading_id_of_stgyname("bt", "composite_bull_bear_market_hdg")
        is_same = proceed_backtest_with_tid(sid)
        self.assertEqual(is_same, True)


if __name__ == '__main__':
    unittest.main()
