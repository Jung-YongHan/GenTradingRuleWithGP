import unittest

import sys

from bt4.model.storage_mgr import StrategyStorage

stkim_usr_id = "844164d3-207f-4fdf-8464-01a7bf20e663"
class MyTestCase(unittest.TestCase):

    def test_ft_id(self) :
        tid = 15
        sys.argv = ["BullTraderMain", "ft",
                    "-usr_uuid", stkim_usr_id,
                    "-usr_name", "stkim_ft_test",
                    "-exec_mode", "redis_kafka",  ## for version 4
                    "-tid", f"{tid}"]
        import bt4.exec.BullTraderMain as bm
        bm.main(sys.argv)

    def test_ft_ws_4h_vol_bt4_with_redis_kafka(self) :
        tid = StrategyStorage.instance().get_trading_id_of_stgyname("ft", "ws_4h_vol")
        sys.argv = ["BullTraderMain", "ft",
                    "-usr_uuid", stkim_usr_id,
                    "-usr_name", "stkim_ft_test",
                    "-exec_mode", "redis_kafka",  ## for version 4
                    "-tid", f"{tid}"]
        import bt4.exec.BullTraderMain as bm
        bm.main(sys.argv)

    def test_ft_ws_day_vol_bt4(self):
        tid = StrategyStorage.instance().get_trading_id_of_stgyname("ft", "ws_day_vol")
        sys.argv = ["BullTraderMain", "ft",
                    "-usr_uuid", stkim_usr_id,
                    "-usr_name", "stkim_ft_test",
                    "-exec_mode", "kafka",
                    "-tid", f"{tid}"]
        import bt4.exec.BullTraderMain as bm
        bm.main(sys.argv)

    def test_ft_ws_4h_vol_bt4(self) :
        tid = StrategyStorage.instance().get_trading_id_of_stgyname("ft", "ws_4h_vol")
        sys.argv = ["BullTraderMain", "ft",
                    "-usr_uuid", stkim_usr_id,
                    "-usr_name", "stkim_ft_test",
                    "-exec_mode", "kafka",
                    "-tid", f"{tid}"]
        import bt4.exec.BullTraderMain as bm
        bm.main(sys.argv)

    def test_ft_ws_alt_vol_bt4(self) :
        tid = StrategyStorage.instance().get_trading_id_of_stgyname("ft", "ws_alt_vol")
        sys.argv = ["BullTraderMain", "ft",
                    "-usr_uuid", stkim_usr_id,
                    "-usr_name", "stkim_ft_test",
                    "-exec_mode", "kafka",
                    "-tid", f"{tid}"]
        import bt4.exec.BullTraderMain as bm
        bm.main(sys.argv)

    def test_ft_tai_comb_vol_bt4(self) :
        tid = StrategyStorage.instance().get_trading_id_of_stgyname("ft", "tai_comb_vol")
        sys.argv = ["BullTraderMain", "ft",
                    "-usr_uuid", stkim_usr_id,
                    "-usr_name", "stkim_ft_test",
                    "-exec_mode", "kafka",
                    "-tid", f"{tid}"]
        import bt4.exec.BullTraderMain as bm
        bm.main(sys.argv)

    def test_ft_sws_day_hdg_vol_tai_bt4(self) :
        tid = StrategyStorage.instance().get_trading_id_of_stgyname("ft", "sws_day_hdg_vol_tai")
        sys.argv = ["BullTraderMain", "ft",
                    "-usr_uuid", stkim_usr_id,
                    "-usr_name", "stkim_ft_test",
                    "-exec_mode", "kafka",
                    "-tid", f"{tid}"]
        import bt4.exec.BullTraderMain as bm
        bm.main(sys.argv)

if __name__ == '__main__':
    unittest.main()
