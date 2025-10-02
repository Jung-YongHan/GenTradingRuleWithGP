import unittest

import sys

from bt4.model.storage_mgr import StrategyStorage


class MyTestCase(unittest.TestCase):


    def test_lt_with_id2(self):
        joongi_uuid = "a848677a-9ccd-48dc-b438-923273418975"
        tid = 10
        sys.argv = ["BullTraderMain", "lt",
                    "-usr_uuid", joongi_uuid,
                    "-usr_name", "joongi",
                    # "-reset_trades",
                    "-exec_mode", "redis_kafka",
                    "-tid", f"{tid}"]
        import bt4.exec.BullTraderMain as bm
        bm.main(sys.argv)

    def test_lt_with_id(self):
        mingu_uuid = "02e432e9-4321-4b90-85e6-f39d1e17bc72"
        tid = 1287
        sys.argv = ["BullTraderMain", "lt",
                    "-usr_uuid", mingu_uuid,
                    "-usr_name", "mingu2",
                    # "-reset_trades",
                    "-exec_mode", "redis_kafka",
                    "-tid", f"{tid}"]
        import bt4.exec.BullTraderMain as bm
        bm.main(sys.argv)

    def test_lt_ws_day_vol(self):
        mingu_uuid = "02e432e9-4321-4b90-85e6-f39d1e17bc72"
        tid = StrategyStorage.instance().get_trading_id_of_stgyname("lt", "ws_day_vol")
        sys.argv = ["BullTraderMain", "lt",
                    "-usr_uuid", mingu_uuid,
                    "-usr_name", "mingu",
                    "-exec_mode", "redis_kafka",
                    "-tid", f"{tid}"]
        import bt4.exec.BullTraderMain as bm
        bm.main(sys.argv)

    def test_lt_ws_day_hdg_vol_bt4(self):
        mingu_uuid = "02e432e9-4321-4b90-85e6-f39d1e17bc72"
        tid = StrategyStorage.instance().get_trading_id_of_stgyname("lt", "sws_day_hdg_vol_tai")
        sys.argv = ["BullTraderMain", "lt",
                    "-usr_uuid", mingu_uuid,
                    "-usr_name", "mingu",
                    "-exec_mode", "redis_kafka",
                    "-tid", f"{tid}"]
        import bt4.exec.BullTraderMain as bm
        bm.main(sys.argv)





if __name__ == '__main__':
    unittest.main()
