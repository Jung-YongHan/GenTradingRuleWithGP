import unittest
import sys

from bt4.utils.visualize_utils import visualize_trades
from bt4.validator.RegressionTestor import RegressionTestor


class WinningSession_upbit(unittest.TestCase):

    # @unittest.skip("Tested")
    def test_tai_rule_fixed(self) :
        sys.argv = ['BullTraderMain', 'backtestor', '-conf', 'bt3_config.upbit.tai_rule_fixed']
        import bt4.exec.BullTraderMain as bm
        ctx, result_file = bm.main(sys.argv)

        # rtestor = RegressionTestor()
        # is_same = rtestor.test_on_the_fly(ctx, result_file,
        #                                   only_for_the_same_cfg=False,
        #                                   show_trading_details=False,
        #                                   is_base=True)
        # visualize_trades(result_file)
        # self.assertEqual(is_same, True)

    # @unittest.skip("Tested")
    def test_tai_comb_vol(self) :
        sys.argv = ['BullTraderMain', 'backtestor', '-conf', 'bt3_config.upbit.tai_comb_vol']
        import bt4.exec.BullTraderMain as bm
        ctx, result_file = bm.main(sys.argv)

        # rtestor = RegressionTestor()
        # is_same = rtestor.test_on_the_fly(ctx, result_file,
        #                                   only_for_the_same_cfg=False,
        #                                   show_trading_details=False,
        #                                   is_base=True)
        # visualize_trades(result_file)
        # self.assertEqual(is_same, True)

  # @unittest.skip("Tested")
    def test_tai_rule_vol(self) :
        sys.argv = ['BullTraderMain', 'backtestor', '-conf', 'bt3_config.upbit.tai_rule_vol']
        import bt4.exec.BullTraderMain as bm
        ctx, result_file = bm.main(sys.argv)

        # rtestor = RegressionTestor()
        # is_same = rtestor.test_on_the_fly(ctx, result_file,
        #                                   only_for_the_same_cfg=False,
        #                                   show_trading_details=False,
        #                                   is_base=True)
        # visualize_trades(result_file)
        # self.assertEqual(is_same, True)

if __name__ == '__main__':
    unittest.main()
