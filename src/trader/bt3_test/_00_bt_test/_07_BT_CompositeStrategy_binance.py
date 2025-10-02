import unittest
import sys
from bt4.utils.mylog import init_log
import bt4.utils.mylog as log_module
from bt4.validator.RegressionTestor import RegressionTestor

log_module.log_mode = 'simulator'
log = init_log()

class CompositeStrategy_binance(unittest.TestCase):

    # @unittest.skip("Tested")
    def test_composite_bull_bear_market_hdg(self):
        sys.argv = ['BullTraderMain', 'backtestor', '-conf', 'bt3_config.binance.composite_bull_bear_market_hdg']
        import bt4.exec.BullTraderMain as bm
        ctx, result_file = bm.main(sys.argv)

        rtestor = RegressionTestor()
        is_same = rtestor.test_on_the_fly(ctx, result_file,
                                          only_for_the_same_cfg=False,
                                          show_trading_details=False,
                                          is_base=True)
        self.assertEqual(is_same, True)

    # @unittest.skip("Tested")
    def test_composite_bull_bear_strategy(self):
        sys.argv = ['BullTraderMain', 'backtestor', '-conf', 'bt3_config.binance.composite_bull_bear_market']
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
