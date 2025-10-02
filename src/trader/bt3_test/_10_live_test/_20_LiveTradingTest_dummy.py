import unittest

import sys


class MyTestCase(unittest.TestCase):

    def test_bt3_live_trading_with_dummy_kafka(self):
        sys.argv = ['BullTraderMain', 'live_trading',
                    '-account', 'test_account',
                    '-dummy', 'True',
                    '-exec_mode', 'kafka',
                    '-conf',  'bt3_config.upbit.sws_day_hdg_vol']
        import bt4.exec.BullTraderMain as bm
        bm.main(sys.argv)



if __name__ == '__main__':
    unittest.main()
