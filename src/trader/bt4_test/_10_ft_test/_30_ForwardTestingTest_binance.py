import unittest

import sys

from bt4.model.storage_mgr import StrategyStorage

stkim_usr_id = "844164d3-207f-4fdf-8464-01a7bf20e663"
class MyTestCase(unittest.TestCase):

    def test_ft_ws_day_vol_binance(self) :
        tid = StrategyStorage.instance().get_trading_id_of_stgyname("ft", "ws_day_vol_binance")
        sys.argv = ["BullTraderMain", "ft",
                    "-usr_uuid", stkim_usr_id,
                    "-usr_name", "stkim_ft_test",
                    "-exec_mode", "redis_kafka",  ## for version 4
                    "-tid", f"{tid}"]
        import bt4.exec.BullTraderMain as bm
        bm.main(sys.argv)




if __name__ == '__main__':
    unittest.main()
