import sys
import unittest

from bt4.model.storage_mgr import StrategyStorage

import bt4.exec.GAExecMain as ga

class MyTestCase(unittest.TestCase) :
    def test_ma_crossover_4h_vol_ga(self):
        tid = StrategyStorage.instance().get_trading_id_of_stgyname("ga", "ma_crossover_4h_vol_ga")
        sys.argv = ["GAExecMain", "ga", "-tid", f"{tid}"]
        ga.main(sys.argv)


if __name__ == '__main__' :
    unittest.main()
