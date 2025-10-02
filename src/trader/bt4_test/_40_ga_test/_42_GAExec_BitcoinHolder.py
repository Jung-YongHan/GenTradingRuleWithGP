import sys
import unittest

from bt4.model.storage_mgr import StrategyStorage

import bt4.exec.GAExecMain as ga

class MyTestCase(unittest.TestCase) :
    def test_bitholder_hdg_vol_tai_ga(self):
        tid = StrategyStorage.instance().get_trading_id_of_stgyname("ga", "bitholder_hdg_vol_tai_ga")
        sys.argv = ["GAExecMain", "ga", "-tid", f"{tid}"]
        ga.main(sys.argv)


if __name__ == '__main__' :
    unittest.main()
