import unittest
import sys

from bt4 import GlobalProperties
from bt4.utils.visualize_utils import visualize_trades
from bt4.validator.RegressionTestor import RegressionTestor

GlobalProperties.__VERSION__ = "bt3"

class SuperWinningSession_upbit(unittest.TestCase):

    def test_sws_day_alt_weight(self) :

        sys.argv = ['BullTraderMain', 'backtestor', '-conf', 'bt3_config.upbit.sws_day_alt_weight']
        import bt4.exec.BullTraderMain as bm
        ctx, result_file = bm.main(sys.argv)

        rtestor = RegressionTestor()
        # rtestor.test_on_the_fly(ctx, result_file, only_for_the_same_cfg=False)
        is_same = rtestor.test_on_the_fly(ctx, result_file,
                                          only_for_the_same_cfg = False,
                                          show_trading_details=False,
                                          is_base = True)

        visualize_trades(result_file)
        self.assertEqual(is_same, True)

    # @unittest.skip("Tested")
    def test_sws_day_hdg_vol_tai_bt4(self):
        sys.argv = ['BullTraderMain', 'backtestor', '-conf', 'bt3_config.upbit.sws_day_hdg_vol_tai']
        import bt4.exec.BullTraderMain as bm
        ctx, result_file = bm.main(sys.argv)

        rtestor = RegressionTestor()
        # rtestor.test_on_the_fly(ctx, result_file, only_for_the_same_cfg=False)
        is_same = rtestor.test_on_the_fly(ctx, result_file,
                                          only_for_the_same_cfg = False,
                                          show_trading_details=False,
                                          is_base = True)
        visualize_trades(result_file)
        self.assertEqual(is_same, True)

    def test_bt_sws_day_hdg_vol(self):
        sys.argv = ['BullTraderMain', 'backtestor', '-conf', 'bt3_config.upbit.sws_day_hdg_vol']
        import bt4.exec.BullTraderMain as bm
        ctx, result_file = bm.main(sys.argv)

        rtestor = RegressionTestor()
        is_same = rtestor.test_on_the_fly(ctx, result_file,
                                          only_for_the_same_cfg = False,
                                          show_trading_details=False,
                                          is_base=True)
        self.assertEqual(is_same, True)

    def test_sws_day_hdg_vol_rule(self):
        sys.argv = ['BullTraderMain', 'backtestor', '-conf', 'bt3_config.upbit.sws_day_hdg_vol_rule']
        import bt4.exec.BullTraderMain as bm
        ctx, result_file = bm.main(sys.argv)

        rtestor = RegressionTestor()
        # rtestor.test_on_the_fly(ctx, result_file, only_for_the_same_cfg=False)
        is_same = rtestor.test_on_the_fly(ctx, result_file,
                                          only_for_the_same_cfg = False,
                                          show_trading_details=False,
                                          is_base = True)

        visualize_trades(result_file)
        self.assertEqual(is_same, True)


    def test_sws_day_hdg_asym_vol(self):
        sys.argv = ['BullTraderMain', 'backtestor', '-conf', 'bt3_config.upbit.sws_day_hdg_asym_vol']
        import bt4.exec.BullTraderMain as bm
        ctx, result_file = bm.main(sys.argv)

        rtestor = RegressionTestor()
        # rtestor.test_on_the_fly(ctx, result_file, only_for_the_same_cfg=False)
        is_same = rtestor.test_on_the_fly(ctx, result_file,
                                          only_for_the_same_cfg = False,
                                          show_trading_details=False,
                                          is_base = True)

        visualize_trades(result_file)
        self.assertEqual(is_same, True)


    def test_sws_day_hdg_vol_macd(self):
        sys.argv = ['BullTraderMain', 'backtestor', '-conf', 'bt3_config.upbit.sws_day_hdg_vol_macd']
        import bt4.exec.BullTraderMain as bm
        ctx, result_file = bm.main(sys.argv)

        rtestor = RegressionTestor()
        # rtestor.test_on_the_fly(ctx, result_file, only_for_the_same_cfg=False)
        is_same = rtestor.test_on_the_fly(ctx, result_file,
                                          only_for_the_same_cfg = False,
                                          show_trading_details=False,
                                          is_base = False)
        self.assertEqual(is_same, True)


    # @unittest.skip("Tested")
    def test_sws_ma_crossover_hdg_vol(self):
        sys.argv = ['BullTraderMain', 'backtestor', '-conf', 'bt3_config.upbit.sws_ma_crossover_hdg_vol']
        import bt4.exec.BullTraderMain as bm
        ctx, result_file = bm.main(sys.argv)

        rtestor = RegressionTestor()
        # rtestor.test_on_the_fly(ctx, result_file, only_for_the_same_cfg=False)
        is_same = rtestor.test_on_the_fly(ctx, result_file,
                                          only_for_the_same_cfg = False,
                                          show_trading_details=False,
                                          is_base = True)
        self.assertEqual(is_same, True)


    def test_sws_day_hdg_vol_bitholder_tai(self):
        sys.argv = ['BullTraderMain', 'backtestor', '-conf', 'bt3_config.upbit.sws_day_hdg_vol_bitholder_tai']
        import bt4.exec.BullTraderMain as bm
        ctx, result_file = bm.main(sys.argv)

        rtestor = RegressionTestor()
        # rtestor.test_on_the_fly(ctx, result_file, only_for_the_same_cfg=False)
        is_same = rtestor.test_on_the_fly(ctx, result_file,
                                          only_for_the_same_cfg = False,
                                          show_trading_details=False,
                                          is_base = True)
        self.assertEqual(is_same, True)


    def test_sws_day_hdg_vol_ema(self):
        sys.argv = ['BullTraderMain', 'backtestor', '-conf', 'bt3_config.upbit.sws_day_hdg_vol_ema']
        import bt4.exec.BullTraderMain as bm
        ctx, result_file = bm.main(sys.argv)

        rtestor = RegressionTestor()
        is_same = rtestor.test_on_the_fly(ctx, result_file,
                                          only_for_the_same_cfg = False,
                                          show_trading_details=False,
                                          is_base = True)
        self.assertEqual(is_same, True)



    def test_sws_4h_vol(self):
        sys.argv = ['BullTraderMain', 'backtestor', '-conf', 'bt3_config.upbit.sws_4h_vol']
        import bt4.exec.BullTraderMain as bm
        ctx, result_file = bm.main(sys.argv)

        rtestor = RegressionTestor()
        # rtestor.test_on_the_fly(ctx, result_file, only_for_the_same_cfg=False)
        is_same = rtestor.test_on_the_fly(ctx, result_file,
                                          only_for_the_same_cfg=False,
                                          show_trading_details=False,
                                          is_base=False)
        self.assertEqual(is_same, True)


    def test_sws_day_vol(self):
        sys.argv = ['BullTraderMain', 'backtestor', '-conf', 'bt3_config.upbit.sws_day_vol']
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
