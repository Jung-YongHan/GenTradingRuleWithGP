import unittest
import sys
from bt4.utils.mylog import init_log
import bt4.utils.mylog as log_module
from bt4.validator.RegressionTestor import RegressionTestor

log_module.log_mode = 'simulator'
log = init_log()

class MACrossOver_upbit(unittest.TestCase):

    # @unittest.skip("Tested")
    def test_ma_cross_over_vol(self):
        sys.argv = ['BullTraderMain', 'backtestor', '-conf', 'bt3_config.upbit.ma_cross_over_vol']
        import bt4.exec.BullTraderMain as bm
        ctx, result_file = bm.main(sys.argv)

        rtestor = RegressionTestor()
        is_same = rtestor.test_on_the_fly(ctx, result_file,
                                          only_for_the_same_cfg = False,
                                          show_trading_details=False,
                                          is_base=True)
        self.assertEqual(is_same, True)


    # @unittest.skip("Tested")
    def test_ma_cross_over_hdg_vol(self):
        sys.argv = ['BullTraderMain', 'backtestor', '-conf', 'bt3_config.upbit.ma_cross_over_hdg_vol']
        import bt4.exec.BullTraderMain as bm
        ctx, result_file = bm.main(sys.argv)

        rtestor = RegressionTestor()
        is_same = rtestor.test_on_the_fly(ctx, result_file,
                                          only_for_the_same_cfg = False,
                                          show_trading_details=False,
                                          is_base=False)
        self.assertEqual(is_same, True)

if __name__ == '__main__':
    unittest.main()
