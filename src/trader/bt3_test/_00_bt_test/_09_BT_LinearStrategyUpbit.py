import unittest
import sys

# from bt4.validator.RegressionTestor import RegressionTestor
from bt4.validator.RegressionTestor import RegressionTestor


class LinearStrategyUpbit(unittest.TestCase):
    # @unittest.skip("Tested")
    def test_super_linear_hour(self):
        sys.argv = ['BullTraderMain', 'backtestor', '-conf', 'bt3_config.upbit.super_linear_hour_vol']
        import bt4.exec.BullTraderMain as bm

        ctx, result_file = bm.main(sys.argv)

        rtestor = RegressionTestor()
        is_same = rtestor.test_on_the_fly(ctx, result_file,
                                          only_for_the_same_cfg=False,
                                          show_trading_details=False,
                                          is_base=False)
        self.assertEqual(is_same, True)

    @unittest.skip("Tested")
    def test_linear_hour(self):
        sys.argv = ['BullTraderMain', 'backtestor', '-conf', 'bt3_config.upbit.linear_hour_vol']
        import bt4.exec.BullTraderMain as bm

        ctx, result_file = bm.main(sys.argv)

        # rtestor = RegressionTestor()

        # is_same = rtestor.test_on_the_fly(ctx, result_file, only_for_the_same_cfg=False, show_trading_details=False, is_base=False)
        # self.assertEqual(is_same, True)


if __name__ == '__main__':
    unittest.main()
