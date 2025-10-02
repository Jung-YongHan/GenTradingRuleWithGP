import unittest
import sys

from bt4.validator.RegressionTestor import RegressionTestor


class WinningSession_upbit(unittest.TestCase):

    # @unittest.skip("Tested")
    def test_verzit_sws_vol(self) :
        sys.argv = ['BullTraderMain', 'backtestor', '-conf', 'bt3_config.upbit.verzit_sws_vol']
        import bt4.exec.BullTraderMain as bm
        ctx, result_file = bm.main(sys.argv)

        # rtestor = RegressionTestor()
        # is_same = rtestor.test_on_the_fly(ctx, result_file,
        #                                   only_for_the_same_cfg=False,
        #                                   show_trading_details=False,
        #                                   is_base=False)
        # self.assertEqual(is_same, True)

    # @unittest.skip("Tested")
    def test_verzit2_sws_vol(self) :
        sys.argv = ['BullTraderMain', 'backtestor', '-conf', 'bt3_config.upbit.verzit2_sws_vol']
        import bt4.exec.BullTraderMain as bm
        ctx, result_file = bm.main(sys.argv)

        # rtestor = RegressionTestor()
        # is_same = rtestor.test_on_the_fly(ctx, result_file,
        #                                   only_for_the_same_cfg=False,
        #                                   show_trading_details=False,
        #                                   is_base=False)
        # self.assertEqual(is_same, True)

    # @unittest.skip("Tested")
    def test_verzit2_vol(self) :
        sys.argv = ['BullTraderMain', 'backtestor', '-conf', 'bt3_config.upbit.verzit2_vol']
        import bt4.exec.BullTraderMain as bm
        ctx, result_file = bm.main(sys.argv)

        # rtestor = RegressionTestor()
        # is_same = rtestor.test_on_the_fly(ctx, result_file,
        #                                   only_for_the_same_cfg=False,
        #                                   show_trading_details=False,
        #                                   is_base=False)
        # self.assertEqual(is_same, True)

    # @unittest.skip("Tested")
    def test_verzit_vol(self):
        sys.argv = ['BullTraderMain', 'backtestor', '-conf', 'bt3_config.upbit.verzit_vol']
        import bt4.exec.BullTraderMain as bm
        ctx, result_file = bm.main(sys.argv)

        # rtestor = RegressionTestor()
        # is_same = rtestor.test_on_the_fly(ctx, result_file,
        #                                   only_for_the_same_cfg=False,
        #                                   show_trading_details=False,
        #                                   is_base=False)
        # self.assertEqual(is_same, True)



if __name__ == '__main__':
    unittest.main()
