import sys
import unittest

from bt4.model.storage_mgr import StrategyStorage

import bt4.exec.GAExecMain as ga


class MyTestCase(unittest.TestCase) :

    def test_ws_test_id(self) :
        tid = 1258
        sys.argv = ["GAExecMain", "ga", "-tid", f"{tid}"]
        ga.main(sys.argv)

    def test_ws_day_hdg_vol_ga3(self):
        stgy_name = "ws_day_hdg_vol_ga3"
        tid = StrategyStorage.instance().get_trading_id_of_stgyname("ga", stgy_name)

        sys.argv = ["GAExecMain", "ga", "-tid", f"{tid}"]
        ga.main(sys.argv)

    def test_ws_day_hdg_vol_ga2(self):
        stgy_name = "ws_day_hdg_vol_ga2"
        tid = StrategyStorage.instance().get_trading_id_of_stgyname("ga", stgy_name)

        sys.argv = ["GAExecMain", "ga", "-tid", f"{tid}"]
        ga.main(sys.argv)

    def test_ws_day_hdg_vol_ga(self) :
        stgy_name = "ws_day_hdg_vol_ga"
        tid = StrategyStorage.instance().get_trading_id_of_stgyname("ga", stgy_name)

        sys.argv = ["GAExecMain", "ga", "-tid", f"{tid}"]
        ga.main(sys.argv)

    def test_ws_ga_result_test(self) :
        stgy_name = "ws_ga_result_test"
        tid = StrategyStorage.instance().get_trading_id_of_stgyname("ga", stgy_name)

        sys.argv = ["GAExecMain", "ga", "-tid", f"{tid}"]
        ga.main(sys.argv)

    def test_ws_day_vol_ga4(self) :
        stgy_name = "ws_day_vol_ga4"
        tid = StrategyStorage.instance().get_trading_id_of_stgyname("ga", stgy_name)

        sys.argv = ["GAExecMain", "ga", "-tid", f"{tid}"]
        ga.main(sys.argv)


    def test_ws_day_vol_ga3(self) :
        stgy_name = "ws_day_vol_ga3"
        tid = StrategyStorage.instance().get_trading_id_of_stgyname("ga", stgy_name)

        sys.argv = ["GAExecMain", "ga", "-tid", f"{tid}"]
        ga.main(sys.argv)


    def test_ws_day_vol_ga2(self) :
        stgy_name = "ws_day_vol_ga2"
        tid = StrategyStorage.instance().get_trading_id_of_stgyname("ga", stgy_name)

        sys.argv = ["GAExecMain", "ga", "-tid", f"{tid}"]
        ga.main(sys.argv)

    def test_ws_day_vol_ga(self) :
        stgy_name = "ws_day_vol_ga"
        tid = StrategyStorage.instance().get_trading_id_of_stgyname("ga", stgy_name)

        sys.argv = ["GAExecMain", "ga", "-tid", f"{tid}"]
        ga.main(sys.argv)






if __name__ == '__main__' :
    unittest.main()
