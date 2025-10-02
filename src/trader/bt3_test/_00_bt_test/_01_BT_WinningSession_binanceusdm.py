import unittest
import sys

from bt4.validator.RegressionTestor import RegressionTestor


class WinningSession_binanceusdm(unittest.TestCase):

    # # @unittest.skip("Tested")
    # def test_ws_day_hdg_vol(self):
    #     sys.argv = ['BullTraderMain', 'backtestor', '-conf', 'bt3_config.binance.ws_day_hdg_vol']
    #     import bt4.exec.BullTraderMain as bm
    #     ctx, result_file = bm.main(sys.argv)
    #
    #     rtestor = RegressionTestor()
    #     is_same = rtestor.test_on_the_fly(ctx, result_file, only_for_the_same_cfg=False, show_trading_details=False)
    #     self.assertEqual(is_same, True)
    #
    # # @unittest.skip("Tested")
    # def test_ws_day_hdg_fixed(self):
    #     sys.argv = ['BullTraderMain', 'backtestor', '-conf', 'bt3_config.binance.ws_day_hdg_fixed']
    #     import bt4.exec.BullTraderMain as bm
    #     ctx, result_file = bm.main(sys.argv)
    #
    #     rtestor = RegressionTestor()
    #     is_same = rtestor.test_on_the_fly(ctx, result_file, only_for_the_same_cfg=False, show_trading_details=False)
    #     self.assertEqual(is_same, True)
    #
    #
    # # @unittest.skip("Tested")
    # def test_ws_4h_vol(self):
    #     sys.argv = ['BullTraderMain', 'backtestor', '-conf', 'bt3_config.binance.ws_4h_vol']
    #     import bt4.exec.BullTraderMain as bm
    #     ctx, result_file = bm.main(sys.argv)
    #
    #     rtestor = RegressionTestor()
    #     is_same = rtestor.test_on_the_fly(ctx, result_file, only_for_the_same_cfg=False, show_trading_details=False)
    #     self.assertEqual(is_same, True)
    #
    #
    # # @unittest.skip("Tested")
    # def test_ws_day_vol(self):
    #     sys.argv = ['BullTraderMain', 'backtestor', '-conf', 'bt3_config.binance.ws_day_vol']
    #     import bt4.exec.BullTraderMain as bm
    #     ctx, result_file = bm.main(sys.argv)
    #
    #     rtestor = RegressionTestor()
    #     # rtestor.test_on_the_fly(ctx, result_file, only_for_the_same_cfg=False)
    #     is_same = rtestor.test_on_the_fly(ctx, result_file, only_for_the_same_cfg=False, show_trading_details=False)
    #     self.assertEqual(is_same, True)


    # @unittest.skip("Tested")
    def test_ws_day_fixed(self):
        sys.argv = ['BullTraderMain', 'backtestor', '-conf', 'bt3_config.binanceusdm.ws_day_fixed']
        import bt4.exec.BullTraderMain as bm
        ctx, result_file = bm.main(sys.argv)

        rtestor = RegressionTestor()
        is_same = rtestor.test_on_the_fly(ctx, result_file, only_for_the_same_cfg=False, show_trading_details=False)
        self.assertEqual(is_same, True)


if __name__ == '__main__':
    unittest.main()
