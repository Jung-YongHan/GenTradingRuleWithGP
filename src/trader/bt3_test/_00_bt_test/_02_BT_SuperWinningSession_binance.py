import unittest
import sys

from bt4.validator.RegressionTestor import RegressionTestor


class SuperWinningSession_binance(unittest.TestCase):
    def test_sws_day_hdg_vol_macd(self):
        sys.argv = ['BullTraderMain', 'backtestor', '-conf', 'bt3_config.binance.sws_day_hdg_vol_macd']
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
    def test_bt_sws_day_hdg_vol_binance(self):
        sys.argv = ['BullTraderMain', 'backtestor', '-conf', 'bt3_config.binance.sws_day_hdg_vol']
        import bt4.exec.BullTraderMain as bm
        ctx, result_file = bm.main(sys.argv)

        rtestor = RegressionTestor()
        is_same = rtestor.test_on_the_fly(ctx, result_file, only_for_the_same_cfg = False, show_trading_details=False)
        self.assertEqual(is_same, True)


    def test_sws_day_vol(self):
        sys.argv = ['BullTraderMain', 'backtestor', '-conf', 'bt3_config.binance.sws_day_vol']
        import bt4.exec.BullTraderMain as bm
        ctx, result_file = bm.main(sys.argv)

        rtestor = RegressionTestor()
        is_same = rtestor.test_on_the_fly(ctx, result_file, only_for_the_same_cfg=False, show_trading_details=False)
        self.assertEqual(is_same, True)

    def test_sws_4h_vol(self):
        sys.argv = ['BullTraderMain', 'backtestor', '-conf', 'bt3_config.binance.sws_4h_vol']
        import bt4.exec.BullTraderMain as bm
        ctx, result_file = bm.main(sys.argv)

        rtestor = RegressionTestor()
        is_same = rtestor.test_on_the_fly(ctx, result_file, only_for_the_same_cfg=False, show_trading_details=False)
        self.assertEqual(is_same, True)

    def test_sws_day_hdg_vol_ema(self):
        sys.argv = ['BullTraderMain', 'backtestor', '-conf', 'bt3_config.binance.sws_day_hdg_vol_ema']
        import bt4.exec.BullTraderMain as bm
        ctx, result_file = bm.main(sys.argv)

        rtestor = RegressionTestor()
        is_same = rtestor.test_on_the_fly(ctx, result_file, only_for_the_same_cfg=False, show_trading_details=False)
        self.assertEqual(is_same, True)

    def test_sws_ma_crossover_day_vol(self):
        sys.argv = ['BullTraderMain', 'backtestor', '-conf', 'bt3_config.binance.sws_ma_crossover_day_vol']
        import bt4.exec.BullTraderMain as bm
        ctx, result_file = bm.main(sys.argv)

        rtestor = RegressionTestor()
        is_same = rtestor.test_on_the_fly(ctx, result_file, only_for_the_same_cfg=False, show_trading_details=False)
        self.assertEqual(is_same, True)

    # @unittest.skip("Tested")
    def test_sws_ma_crossover_hdg_vol(self):
        sys.argv = ['BullTraderMain', 'backtestor', '-conf', 'bt3_config.binance.sws_ma_crossover_hdg_vol']
        import bt4.exec.BullTraderMain as bm
        ctx, result_file = bm.main(sys.argv)

        rtestor = RegressionTestor()
        is_same = rtestor.test_on_the_fly(ctx, result_file, only_for_the_same_cfg=False, show_trading_details=False)
        self.assertEqual(is_same, True)

    def __test_bull_trader_superwinning_session_scaled_sell_by_RSI_1H2(self): ### May be error?
        sys.argv = ['BullTraderMain', 'backtestor', '-conf', 'bt3_config.binance.sws_sell_1h_ta_comb_vol']
        import bt4.exec.BullTraderMain as bm
        ctx, result_file = bm.main(sys.argv)

        rtestor = RegressionTestor()
        is_same = rtestor.test_on_the_fly(ctx, result_file, only_for_the_same_cfg=False, show_trading_details=False)
        self.assertEqual(is_same, True)

if __name__ == '__main__':
    unittest.main()
