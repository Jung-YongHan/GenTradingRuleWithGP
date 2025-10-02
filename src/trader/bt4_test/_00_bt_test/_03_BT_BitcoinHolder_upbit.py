import unittest

from bt4 import GlobalProperties
from bt4.model.storage_mgr import StrategyStorage

GlobalProperties.__VERSION__ = "bt4"

from bt4_test._00_bt_test._00_BTTestHelper import proceed_backtest_with_tid


class BitcoinHolder_upbit(unittest.TestCase):

    def test_bitholder_hdg_vol_tai_bg4(self):
        sid = StrategyStorage.instance().get_trading_id_of_stgyname("bt", "bitholder_hdg_vol_tai")
        is_same = proceed_backtest_with_tid(sid)
        self.assertEqual(is_same, True)

    ###
    ## TODO : Need to improve the feature of the generating vals for the constants
    ## TODO: as a strategy parameters (2024.06.07 stkim)
    ## TODO: Do not execute this tai until the feature has been completed!
    def test_bitholder_hdg_vol_tai2(self) :
        sid = StrategyStorage.instance().get_trading_id_of_stgyname("bt", "bitholder_hdg_vol_tai2")
        is_same = proceed_backtest_with_tid(sid)
        self.assertEqual(is_same, True)



if __name__ == '__main__':
    unittest.main()
