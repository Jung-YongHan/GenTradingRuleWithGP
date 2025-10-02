import unittest

import sys

from bt4.model.storage_mgr import StrategyStorage


class MyTestCase(unittest.TestCase):


    def test_lt_ws_day_vol_binance(self):
        stkim_uuid = "844164d3-207f-4fdf-8464-01a7bf20e663"
        tid = StrategyStorage.instance().get_trading_id_of_stgyname("lt", "ws_day_vol_binance")
        sys.argv = ["BullTraderMain", "lt",
                    "-usr_uuid", stkim_uuid,
                    "-usr_name", "stkim_binance",
                    "-exec_mode", "redis_kafka",
                    "-tid", f"{tid}"]
        import bt4.exec.BullTraderMain as bm
        bm.main(sys.argv)


if __name__ == '__main__':
    unittest.main()
