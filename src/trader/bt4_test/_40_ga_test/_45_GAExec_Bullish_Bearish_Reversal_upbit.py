import unittest
import sys

from bt4 import GlobalProperties
from bt4.model.storage_mgr import StrategyStorage
import pandas as pd
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

pd.set_option('display.max_columns', None)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('max_colwidth', None)

GlobalProperties.__VERSION__ = "bt4"

import bt4.exec.GAExecMain as ga

class BB_Bullish_Bearish_Reversal_upbit(unittest.TestCase):

    def test_bb_breakout_ga(self):
        tid = StrategyStorage.instance().get_trading_id_of_stgyname("ga", "bb_breakout_ga")
        sys.argv = ["GAExecMain", "ga", "-tid", f"{tid}"]
        ga.main(sys.argv)



if __name__ == '__main__':
    unittest.main()
