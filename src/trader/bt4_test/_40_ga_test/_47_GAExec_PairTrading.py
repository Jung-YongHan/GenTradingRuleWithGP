import sys
import unittest

from bt4.model.storage_mgr import StrategyStorage
import bt4.exec.GAExecMain as ga

class MyTestCase(unittest.TestCase) :

    def test_sws_ma_crossover_day_vol_pair_trading_ga2(self):
        tid = StrategyStorage.instance().get_trading_id_of_stgyname("ga", "sws_ma_crossover_day_vol_pair_trading_ga2")
        sys.argv = ["GAExecMain", "ga", "-tid", f"{tid}"]
        ga.main(sys.argv)

    def test_sws_day_hdg_vol_tai_pair_trading_ga(self): #516 -> 931
        tid = StrategyStorage.instance().get_trading_id_of_stgyname("ga", "sws_day_hdg_vol_tai_pair_trading_ga")
        sys.argv = ["GAExecMain", "ga", "-tid", f"{tid}"]
        ga.main(sys.argv)

    def test_sws_ma_crossover_day_vol_pair_trading_ga(self): #513 -> 930
        tid = StrategyStorage.instance().get_trading_id_of_stgyname("ga", "sws_ma_crossover_day_vol_pair_trading_ga")
        sys.argv = ["GAExecMain", "ga", "-tid", f"{tid}"]
        ga.main(sys.argv)
    def test_vol_bout_vol_pair_trading_ga(self): #512 -> #929
        tid = StrategyStorage.instance().get_trading_id_of_stgyname("ga", "vol_bout_vol_pair_trading_ga")
        sys.argv = ["GAExecMain", "ga", "-tid", f"{tid}"]
        ga.main(sys.argv)

    def test_ws_day_vol_pair_trading_ga(self) :
        tid = StrategyStorage.instance().get_trading_id_of_stgyname("ga", "ws_day_vol_pair_trading_ga")
        sys.argv = ["GAExecMain", "ga", "-tid", f"{tid}"]
        ga.main(sys.argv)


if __name__ == '__main__' :
    unittest.main()
