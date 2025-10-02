import unittest

import sys


class MyTestCase(unittest.TestCase):

    def test_bt3_live_trading_sws_day_hdg_vol_with_dummy_kafka(self) :
        sys.argv = ['BullTraderMain', 'live_trading',
                    '-account', 'test_account',
                    '-dummy', 'True',
                    '-exec_mode', 'kafka',
                    '-conf', 'bt3_config.binance.sws_day_hdg_vol']
        import bt4.exec.BullTraderMain as bm
        bm.main(sys.argv)

    def test_bt3_live_trading_ws_day_vol_with_dummy_kafka(self) :
        sys.argv = ['BullTraderMain', 'live_trading',
                    '-account', 'test_account',
                    '-dummy', 'True',
                    '-exec_mode', 'kafka',
                    '-conf', 'bt3_config.binance.ws_day_vol']
        import bt4.exec.BullTraderMain as bm
        bm.main(sys.argv)

    #################################################################################
    ### For Real Trading
    def test_bt3_binance_live_trading_with_sws_day_hdg_vol(self):
        '''

                bt3_config/lt_common_conf.py
                # parameters[r.EX.EX_TYPE] = ExchangeType.UPBIT   --> Kafka Connection
                # parameters[r.EX.EX_TYPE] = ExchangeType.DUMMY    --> Self Data Collection

               :return:
        '''

        sys.argv = ['BullTraderMain', 'live_trading',
                    '-account', 'mingu',
                    '-dummy', 'False',
                    '-exec_mode', 'kafka',
                    '-conf', 'bt3_config.binance.sws_day_hdg_vol']
        import bt4.exec.BullTraderMain as bm
        bm.main(sys.argv)







if __name__ == '__main__':
    unittest.main()
