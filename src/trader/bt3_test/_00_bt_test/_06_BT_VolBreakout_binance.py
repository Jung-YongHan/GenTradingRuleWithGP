import unittest
import sys
from bt4.utils.mylog import init_log
import bt4.utils.mylog as log_module
from bt4.validator.RegressionTestor import RegressionTestor

log_module.log_mode = 'simulator'
log = init_log()

class VolBreakout_binance(unittest.TestCase):

    # @unittest.skip("Tested")
    def test_vol_bout_sws_hdg_vol(self):
        sys.argv = ['BullTraderMain', 'backtestor', '-conf', 'bt3_config.binance.vol_bout_sws_hdg_vol']
        import bt4.exec.BullTraderMain as bm
        ctx, result_file = bm.main(sys.argv)

        rtestor = RegressionTestor()
        is_same = rtestor.test_on_the_fly(ctx, result_file,
                                          only_for_the_same_cfg=False,
                                          show_trading_details=False,
                                          is_base=False)
        self.assertEqual(is_same, True)

    # @unittest.skip("Tested")
    def test_vol_bout_ws_hdg_vol(self):
        sys.argv = ['BullTraderMain', 'backtestor', '-conf', 'bt3_config.binance.vol_bout_ws_hdg_vol']
        import bt4.exec.BullTraderMain as bm
        ctx, result_file = bm.main(sys.argv)

        rtestor = RegressionTestor()
        is_same = rtestor.test_on_the_fly(ctx, result_file,
                                          only_for_the_same_cfg=False,
                                          show_trading_details=False,
                                          is_base=False)
        self.assertEqual(is_same, True)

    # @unittest.skip("Tested")
    def test_vol_bout_hdg_vol(self):
        sys.argv = ['BullTraderMain', 'backtestor', '-conf', 'bt3_config.binance.vol_bout_hdg_vol']
        import bt4.exec.BullTraderMain as bm
        ctx, result_file = bm.main(sys.argv)

        rtestor = RegressionTestor()
        is_same = rtestor.test_on_the_fly(ctx, result_file,
                                          only_for_the_same_cfg=False,
                                          show_trading_details=False,
                                          is_base=False)
        self.assertEqual(is_same, True)

    # @unittest.skip("Tested")
    def test_vol_bout_sws_vol(self):
        sys.argv = ['BullTraderMain', 'backtestor', '-conf', 'bt3_config.binance.vol_bout_sws_vol']
        import bt4.exec.BullTraderMain as bm
        ctx, result_file = bm.main(sys.argv)

        rtestor = RegressionTestor()
        is_same = rtestor.test_on_the_fly(ctx, result_file,
                                          only_for_the_same_cfg=False,
                                          show_trading_details=False,
                                          is_base=False)
        self.assertEqual(is_same, True)

    # @unittest.skip("Tested")
    def test_vol_bout_ws_vol(self):
        sys.argv = ['BullTraderMain', 'backtestor', '-conf', 'bt3_config.binance.vol_bout_ws_vol']
        import bt4.exec.BullTraderMain as bm
        ctx, result_file = bm.main(sys.argv)

        rtestor = RegressionTestor()
        is_same = rtestor.test_on_the_fly(ctx, result_file,
                                          only_for_the_same_cfg=False,
                                          show_trading_details=False,
                                          is_base=False)
        self.assertEqual(is_same, True)

    # @unittest.skip("Tested")
    def test_vol_bout_vol(self):
        sys.argv = ['BullTraderMain', 'backtestor', '-conf', 'bt3_config.binance.vol_bout_vol']
        import bt4.exec.BullTraderMain as bm
        ctx, result_file = bm.main(sys.argv)

        rtestor = RegressionTestor()
        is_same = rtestor.test_on_the_fly(ctx, result_file,
                                          only_for_the_same_cfg=False,
                                          show_trading_details=False,
                                          is_base=False)
        self.assertEqual(is_same, True)

if __name__ == '__main__':
    unittest.main()
