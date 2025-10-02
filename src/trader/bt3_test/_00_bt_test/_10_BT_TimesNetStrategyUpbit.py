import unittest
import sys

# from bt4.validator.RegressionTestor import RegressionTestor
from bt4.validator.RegressionTestor import RegressionTestor


class TimesNetStrategyUpbit(unittest.TestCase):
    # @unittest.skip("Tested")
    def test_super_timesnet_hour(self):
        sys.argv = ['BullTraderMain', 'backtestor', '-conf', 'bt3_config.upbit.super_timesnet_hour_vol']
        import bt4.exec.BullTraderMain as bm

        ctx, result_file = bm.main(sys.argv)

        rtestor = RegressionTestor()
        is_same = rtestor.test_on_the_fly(ctx, result_file,
                                          only_for_the_same_cfg=False,
                                          show_trading_details=False,
                                          is_base=False)
        self.assertEqual(is_same, True)

    @unittest.skip("Tested")
    def test_timesnet_hour(self):
        sys.argv = ['BullTraderMain', 'backtestor', '-conf', 'bt3_config.upbit.timesnet_hour_vol']
        import bt4.exec.BullTraderMain as bm

        ctx, result_file = bm.main(sys.argv)

        # rtestor = RegressionTestor()

        # is_same = rtestor.test_on_the_fly(ctx, result_file, only_for_the_same_cfg=False, show_trading_details=False, is_base=False)
        # self.assertEqual(is_same, True)

    @unittest.skip("Tested")
    def test_anomaly_timesnet_15m(self):
        sys.argv = ['BullTraderMain', 'backtestor', '-conf', 'bt3_config.upbit.anomaly_timesnet_15m_vol']
        import bt4.exec.BullTraderMain as bm

        ctx, result_file = bm.main(sys.argv)


if __name__ == '__main__':
    unittest.main()
