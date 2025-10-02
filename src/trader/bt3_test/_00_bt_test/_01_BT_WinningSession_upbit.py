import unittest
import sys

from bt4 import GlobalProperties
from bt4.utils.visualize_utils import visualize_trades
from bt4.validator.RegressionTestor import RegressionTestor
import pandas as pd

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

pd.set_option('display.max_columns', None)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('max_colwidth', None)

GlobalProperties.__VERSION__ = "bt3"
class WinningSession_upbit(unittest.TestCase):


    def test_ws_day_hdg_vol_vwap(self):
        sys.argv = ['BullTraderMain', 'backtestor', '-conf', 'bt3_config.upbit.ws_day_hdg_vol_vwap']
        import bt4.exec.BullTraderMain as bm
        ctx, result_file = bm.main(sys.argv)

        rtestor = RegressionTestor()
        is_same = rtestor.test_on_the_fly(ctx, result_file,
                                          only_for_the_same_cfg=False,
                                          show_trading_details=False,
                                          is_base=True)
        visualize_trades(result_file)
        self.assertEqual(is_same, True)

    def test_ws_day_adaptive_param_optim_hdg_volume_vol(self):
        sys.argv = ['BullTraderMain', 'backtestor', '-conf', 'bt3_config.upbit.ws_day_adaptive_param_optim_hdg_volume_vol']
        import bt4.exec.BullTraderMain as bm
        ctx, result_file = bm.main(sys.argv)

        rtestor = RegressionTestor()
        is_same = rtestor.test_on_the_fly(ctx, result_file,
                                          only_for_the_same_cfg=False,
                                          show_trading_details=False,
                                          is_base=False)
        self.assertEqual(is_same, True)

    # @unittest.skip("Tested")
    def test_ws_day_hdg_volume_vol(self):
        sys.argv = ['BullTraderMain', 'backtestor', '-conf', 'bt3_config.upbit.ws_day_hdg_volume_vol']
        import bt4.exec.BullTraderMain as bm
        ctx, result_file = bm.main(sys.argv)

        rtestor = RegressionTestor()
        is_same = rtestor.test_on_the_fly(ctx, result_file,
                                          only_for_the_same_cfg=False,
                                          show_trading_details=False,
                                          is_base=True)
        self.assertEqual(is_same, True)

    # @unittest.skip("Tested")
    def test_ws_alt_pr_resid_weight(self):
        import warnings
        warnings.filterwarnings("ignore", category = FutureWarning)
        sys.argv = ['BullTraderMain', 'backtestor', '-conf', 'bt3_config.upbit.ws_alt_pr_resid_weight']
        import bt4.exec.BullTraderMain as bm
        ctx, result_file = bm.main(sys.argv)

        rtestor = RegressionTestor()
        is_same = rtestor.test_on_the_fly(ctx, result_file,
                                          only_for_the_same_cfg=False,
                                          show_trading_details=False,
                                          is_base=True)

        # result_file = "../report/WSAlt_Price_Residual_Strategy_BeforeRefactoring_34712.csv"
        visualize_trades(result_file)

        # self.assertEqual(is_same, True)

    # @unittest.skip("Tested")
    def test_ws_alt_pr_resid_vol(self):
        sys.argv = ['BullTraderMain', 'backtestor', '-conf', 'bt3_config.upbit.ws_alt_pr_resid_vol']
        import bt4.exec.BullTraderMain as bm
        ctx, result_file = bm.main(sys.argv)

        rtestor = RegressionTestor()
        is_same = rtestor.test_on_the_fly(ctx, result_file,
                                          only_for_the_same_cfg=False,
                                          show_trading_details=False,
                                          is_base=True)
        self.assertEqual(is_same, True)

    # @unittest.skip("Tested")
    def test_ws_alt_vol(self):
        sys.argv = ['BullTraderMain', 'backtestor', '-conf', 'bt3_config.upbit.ws_alt_vol']
        import bt4.exec.BullTraderMain as bm
        ctx, result_file = bm.main(sys.argv)

        rtestor = RegressionTestor()
        is_same = rtestor.test_on_the_fly(ctx, result_file,
                                          only_for_the_same_cfg=False,
                                          show_trading_details=False,
                                          is_base=True)
        self.assertEqual(is_same, True)

    # @unittest.skip("Tested")
    def test_ws_day_hdg_vol_mma(self):
        sys.argv = ['BullTraderMain', 'backtestor', '-conf', 'bt3_config.upbit.ws_day_hdg_vol_mma']
        import bt4.exec.BullTraderMain as bm
        ctx, result_file = bm.main(sys.argv)

        rtestor = RegressionTestor()
        is_same = rtestor.test_on_the_fly(ctx, result_file,
                                          only_for_the_same_cfg=False,
                                          show_trading_details=False,
                                          is_base=False)
        self.assertEqual(is_same, True)

    # @unittest.skip("Tested")
    def test_ws_day_hdg_vol(self):
        sys.argv = ['BullTraderMain', 'backtestor', '-conf', 'bt3_config.upbit.ws_day_hdg_vol']
        import bt4.exec.BullTraderMain as bm
        ctx, result_file = bm.main(sys.argv)

        rtestor = RegressionTestor()
        is_same = rtestor.test_on_the_fly(ctx, result_file,
                                          only_for_the_same_cfg=False,
                                          show_trading_details=False,
                                          is_base=False)
        self.assertEqual(is_same, True)

    # @unittest.skip("Tested")
    def test_ws_day_hdg_fixed(self):
        sys.argv = ['BullTraderMain', 'backtestor', '-conf', 'bt3_config.upbit.ws_day_hdg_fixed']
        import bt4.exec.BullTraderMain as bm
        ctx, result_file = bm.main(sys.argv)

        rtestor = RegressionTestor()
        is_same = rtestor.test_on_the_fly(ctx, result_file,
                                          only_for_the_same_cfg=False,
                                          show_trading_details=False,
                                          is_base = False)
        self.assertEqual(is_same, True)


    # @unittest.skip("Tested")
    def test_ws_4h_vol(self):
        sys.argv = ['BullTraderMain', 'backtestor', '-conf', 'bt3_config.upbit.ws_4h_vol']
        import bt4.exec.BullTraderMain as bm
        ctx, result_file = bm.main(sys.argv)

        rtestor = RegressionTestor()
        is_same = rtestor.test_on_the_fly(ctx, result_file,
                                          only_for_the_same_cfg=False,
                                          show_trading_details=False,
                                          is_base = False)
        self.assertEqual(is_same, True)


    # @unittest.skip("Tested")
    def test_ws_day_vol(self):

        sys.argv = ['BullTraderMain', 'backtestor', '-conf', 'bt3_config.upbit.ws_day_vol']
        import bt4.exec.BullTraderMain as bm
        ctx, result_file = bm.main(sys.argv)

        rtestor = RegressionTestor()
        # rtestor.test_on_the_fly(ctx, result_file, only_for_the_same_cfg=False)
        is_same = rtestor.test_on_the_fly(ctx, result_file,
                                          only_for_the_same_cfg=False,
                                          show_trading_details=False,
                                          is_base=True)
        self.assertEqual(is_same, True)


    # @unittest.skip("Tested")
    def test_ws_day_fixed(self):
        import warnings
        warnings.filterwarnings("ignore", category = DeprecationWarning)

        sys.argv = ['BullTraderMain', 'backtestor', '-conf', 'bt3_config.upbit.ws_day_fixed']
        import bt4.exec.BullTraderMain as bm
        ctx, result_file = bm.main(sys.argv)

        rtestor = RegressionTestor()
        is_same = rtestor.test_on_the_fly(ctx, result_file,
                                          only_for_the_same_cfg=False,
                                          show_trading_details=False,
                                          is_base = True)
        visualize_trades(result_file)
        self.assertEqual(is_same, True)


if __name__ == '__main__':
    unittest.main()
