import sys
import unittest

from bt4.validator.RegressionTestor import RegressionTestor


class TTrading_binance(unittest.TestCase):
    # @unittest.skip("Tested")
    def test_ttrading_vol(self):
        sys.argv = ['BullTraderMain', 'backtestor', '-conf', 'bt3_config.binance.ttrading_vol']
        import bt4.exec.BullTraderMain as bm
        ctx, result_file = bm.main(sys.argv)

        rtestor = RegressionTestor()
        is_same = rtestor.test_on_the_fly(ctx, result_file,
                                          only_for_the_same_cfg=False,
                                          show_trading_details=False,
                                          is_base=False)
        self.assertEqual(is_same, True)

    # @unittest.skip("Tested")
    def test_ttrading_origin_vol(self):
        sys.argv = ['BullTraderMain', 'backtestor', '-conf', 'bt3_config.binance.ttrading_origin_vol']
        import bt4.exec.BullTraderMain as bm
        ctx, result_file = bm.main(sys.argv)

        rtestor = RegressionTestor()
        is_same = rtestor.test_on_the_fly(ctx, result_file,
                                          only_for_the_same_cfg=False,
                                          show_trading_details=False,
                                          is_base=False)
        self.assertEqual(is_same, True)

    def test_ttrading_hdg_vol(self):
        sys.argv = ['BullTraderMain', 'backtestor', '-conf', 'bt3_config.binance.ttrading_hdg_vol']
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
