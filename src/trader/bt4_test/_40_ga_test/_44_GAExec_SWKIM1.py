import sys
import unittest

from bt4.model.storage_mgr import StrategyStorage

import bt4.exec.GAExecMain as ga

class MyTestCase(unittest.TestCase) :
    def test_swkim_1_4h_vol_ga(self):
        tid = StrategyStorage.instance().get_trading_id_of_stgyname("ga", "swkim_1_4h_vol_ga")
        sys.argv = ["GAExecMain", "ga", "-tid", f"{tid}"]
        ga.main(sys.argv)

    def test_swkim1_macrossover_4h_vol_ga(self):
        tid = StrategyStorage.instance().get_trading_id_of_stgyname("ga", "swkim1_macrossover_4h_vol_ga")
        sys.argv = ["GAExecMain", "ga", "-tid", f"{tid}"]
        ga.main(sys.argv)

    def test_swkim_1_4h_vol_ga2(self):
        tid = StrategyStorage.instance().get_trading_id_of_desc("bt", "swkim_1_4h_vol_ga2")
        sys.argv = ["GAExecMain", "ga", "-tid", f"{tid}"]
        ga.main(sys.argv)



if __name__ == '__main__' :
    unittest.main()
