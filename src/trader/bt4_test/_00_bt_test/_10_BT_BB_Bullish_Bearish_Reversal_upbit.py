import unittest

from bt4 import GlobalProperties
from bt4.model.storage_mgr import StrategyStorage
import pandas as pd
import warnings

from bt4_test._00_bt_test._00_BTTestHelper import proceed_backtest_with_tid

warnings.filterwarnings("ignore", category=DeprecationWarning)

pd.set_option('display.max_columns', None)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('max_colwidth', None)

GlobalProperties.__VERSION__ = "bt4"
class BB_Bullish_Bearish_Reversal_upbit(unittest.TestCase):

    def test_bb_breakout_hdg_vol(self):
        sid = StrategyStorage.instance().get_trading_id_of_stgyname("bt", "bb_breakout_hdg_vol")
        is_same = proceed_backtest_with_tid(sid)
        self.assertEqual(is_same, True)


    def test_bb_bullish_bearish_reversal_hdg_vol(self):
        sid = StrategyStorage.instance().get_trading_id_of_stgyname("bt", "bb_bullish_bearish_reversal_hdg_vol")
        is_same = proceed_backtest_with_tid(sid)
        self.assertEqual(is_same, True)

    def test_bb_bullish_bearish_reversal(self):
        sid = StrategyStorage.instance().get_trading_id_of_stgyname("bt", "bb_bullish_bearish_reversal")
        is_same = proceed_backtest_with_tid(sid)
        self.assertEqual(is_same, True)

    def test_bb_breakout_with_id(self):
        sid = StrategyStorage.instance().get_trading_id_of_stgyname("bt", "bb_breakout")
        is_same = proceed_backtest_with_tid(sid)
        self.assertEqual(is_same, True)




if __name__ == '__main__':
    unittest.main()
