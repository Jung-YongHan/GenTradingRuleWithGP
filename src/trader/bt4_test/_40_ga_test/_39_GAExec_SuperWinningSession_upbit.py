import sys
import unittest

from bt4.model.storage_mgr import StrategyStorage

import bt4.exec.GAExecMain as ga


class MyTestCase(unittest.TestCase) :

    def test_sws_day_alt_weight(self):
        stgy_name = "sws_day_alt_weight_ga"
        tid = StrategyStorage.instance().get_trading_id_of_stgyname("ga", stgy_name)
        sys.argv = ["GAExecMain", "ga", "-tid", f"{tid}"]
        ga.main(sys.argv)

    def test_sws_30m_vol_ga(self) :
        stgy_name = "sws_30m_vol_ga"
        tid = StrategyStorage.instance().get_trading_id_of_stgyname("ga", stgy_name)
        sys.argv = ["GAExecMain", "ga", "-tid", f"{tid}"]
        ga.main(sys.argv)


    def test_sws_day_hdg_vol_ga(self) :
        stgy_name = "sws_4h_vol_ga"
        tid = StrategyStorage.instance().get_trading_id_of_stgyname("ga", stgy_name)
        sys.argv = ["GAExecMain", "ga", "-tid", f"{tid}"]
        ga.main(sys.argv)


    def test_sws_4h_vol_ga(self) :
        stgy_name = "sws_4h_vol_ga"
        tid = StrategyStorage.instance().get_trading_id_of_stgyname("ga", stgy_name)
        sys.argv = ["GAExecMain", "ga", "-tid", f"{tid}"]
        ga.main(sys.argv)



if __name__ == '__main__' :
    unittest.main()
