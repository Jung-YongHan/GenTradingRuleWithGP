import unittest

import sys

from bt4.model.storage_mgr import StrategyStorage


class MyTestCase(unittest.TestCase):


    def test_lt_ws_day_vol(self):
        stkim_uuid = "844164d3-207f-4fdf-8464-01a7bf20e663"
        tid = StrategyStorage.instance().get_trading_id_of_stgyname("lt", "ws_day_vol")
        sys.argv = ["BullTraderMain", "lt",
                    "-usr_uuid", stkim_uuid,
                    "-usr_name", "stkim_bithumb",
                    "-exec_mode", "redis_kafka",
                    "-tid", f"{tid}"]
        import bt4.exec.BullTraderMain as bm
        bm.main(sys.argv)

    def test_lt_swkim_1_hdg_vol(self):
        stkim_uuid = "844164d3-207f-4fdf-8464-01a7bf20e663"
        tid = StrategyStorage.instance().get_trading_id_of_stgyname("lt", "swkim_1_hdg_vol")
        sys.argv = ["BullTraderMain", "lt",
                    "-usr_uuid", stkim_uuid,
                    "-usr_name", "stkim_bithumb",
                    "-exec_mode", "redis_kafka",
                    "-tid", f"{tid}"]
        import bt4.exec.BullTraderMain as bm
        bm.main(sys.argv)

    def test_lt_sws_ma_crossover_hdg_vol(self):
        stkim_uuid = "844164d3-207f-4fdf-8464-01a7bf20e663"
        tid = StrategyStorage.instance().get_trading_id_of_stgyname("lt", "sws_ma_crossover_hdg_vol")
        sys.argv = ["BullTraderMain", "lt",
                    "-usr_uuid", stkim_uuid,
                    "-usr_name", "stkim_bithumb",
                    "-exec_mode", "redis_kafka",
                    "-tid", f"{tid}"]
        import bt4.exec.BullTraderMain as bm
        bm.main(sys.argv)

    def test_lt_ma_crossover_vol(self) :
        stkim_uuid = "844164d3-207f-4fdf-8464-01a7bf20e663"
        tid = StrategyStorage.instance().get_trading_id_of_stgyname("lt", "ma_crossover_vol")
        sys.argv = ["BullTraderMain", "lt",
                    "-usr_uuid", stkim_uuid,
                    "-usr_name", "stkim_bithumb",
                    "-exec_mode", "redis_kafka",
                    "-reset_trades",
                    "-tid", f"{tid}"]
        import bt4.exec.BullTraderMain as bm
        bm.main(sys.argv)







if __name__ == '__main__':
    unittest.main()
