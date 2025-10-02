import sys
import unittest

from bt4.model.storage_mgr import StrategyStorage
import bt4.exec.GAExecMain as ga

class MyTestCase(unittest.TestCase) :

    def test_ma_crossover_hdg_vol_mkt_specific_ga(self):
        tid = StrategyStorage.instance().get_trading_id_of_stgyname("ga", "ma_crossover_hdg_vol_mkt_specific_ga")
        sys.argv = ["GAExecMain", "ga", "-tid", f"{tid}"]
        ga.main(sys.argv)
    def test_sws_day_hdg_vol_tai_mkt_specific_ga(self):
        tid = StrategyStorage.instance().get_trading_id_of_stgyname("ga", "sws_day_hdg_vol_tai_mkt_specific_ga")
        sys.argv = ["GAExecMain", "ga", "-tid", f"{tid}"]
        ga.main(sys.argv)
    def test_swkim_1_hdg_vol_mkt_specific_ga(self):
        tid = StrategyStorage.instance().get_trading_id_of_stgyname("ga", "swkim_1_hdg_vol_mkt_specific_ga")
        sys.argv = ["GAExecMain", "ga", "-tid", f"{tid}"]
        ga.main(sys.argv)

    def test_sws_ma_crossover_hdg_vol_mkt_specific_ga(self) :
        tid = StrategyStorage.instance().get_trading_id_of_stgyname("ga", "sws_ma_crossover_hdg_vol_mkt_specific_ga")
        sys.argv = ["GAExecMain", "ga", "-tid", f"{tid}"]
        ga.main(sys.argv)


if __name__ == '__main__' :
    unittest.main()
