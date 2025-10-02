import unittest

from bt4.model.storage_mgr import StrategyStorage
from bt4_test._00_bt_test._00_BTTestHelper import proceed_backtest_with_tid


class MyTestCase(unittest.TestCase) :

    def test_ws_day_vol_pair_trading_using_spread(self):
        sid = StrategyStorage.instance().get_trading_id_of_stgyname("bt", "ws_day_vol_pair_trading_using_spread")
        is_same = proceed_backtest_with_tid(sid)
        self.assertEqual(is_same, True)

    def test_sws_ma_crossover_day_vol_pair_trading_ga2(self):
        sid = StrategyStorage.instance().get_trading_id_of_stgyname("bt", "sws_ma_crossover_day_vol_pair_trading_ga2")
        is_same = proceed_backtest_with_tid(sid)
        self.assertEqual(is_same, True)


    def test_vol_bout_vol_pair_trading(self):
        '''
            테스트 완료
        :return:
        '''
        sid = StrategyStorage.instance().get_trading_id_of_stgyname("bt", "vol_bout_vol_pair_trading")
        is_same = proceed_backtest_with_tid(sid)
        self.assertEqual(is_same, True)

    def test_sws_ma_crossover_day_vol_pair_trading(self):
        '''
            테스트 완료
        :return:
        '''
        sid = StrategyStorage.instance().get_trading_id_of_stgyname("bt", "sws_ma_crossover_day_vol_pair_trading")
        is_same = proceed_backtest_with_tid(sid)
        self.assertEqual(is_same, True)
    def test_sws_day_hdg_vol_tai_pair_trading(self):
        '''
            테스트 완료
        :return:
        '''
        sid = StrategyStorage.instance().get_trading_id_of_stgyname("bt", "sws_day_hdg_vol_tai_pair_trading")
        is_same = proceed_backtest_with_tid(sid)
        self.assertEqual(is_same, True)

    def test_sws_4h_vol_pair_trading(self):
        '''
            테스트 완료
        :return:
        '''
        sid = StrategyStorage.instance().get_trading_id_of_stgyname("bt", "sws_4h_vol_pair_trading")
        is_same = proceed_backtest_with_tid(sid)
        self.assertEqual(is_same, True)
    
    def test_swkim_1_hdg_vol_pair_trading(self):
        '''
            테스트 완료
        :return: 
        '''
        sid = StrategyStorage.instance().get_trading_id_of_stgyname("bt", "swkim_1_hdg_vol_pair_trading")
        is_same = proceed_backtest_with_tid(sid)
        self.assertEqual(is_same, True)

    def test_composite_bull_bear_market_pair_trading(self):
        '''
            테스트 완료
        :return:
        '''
        sid = StrategyStorage.instance().get_trading_id_of_stgyname("bt", "composite_bull_bear_market_pair_trading")
        is_same = proceed_backtest_with_tid(sid)
        self.assertEqual(is_same, True)

    def test_bb_bullish_bearish_reversal_hdg_vol_pair_trading(self):
        '''
            테스트 완료
        :return:
        '''
        sid = StrategyStorage.instance().get_trading_id_of_stgyname("bt", "bb_bullish_bearish_reversal_hdg_vol_pair_trading")
        is_same = proceed_backtest_with_tid(sid)
        self.assertEqual(is_same, True)
    def test_bb_breakout_pair_trading(self):
        '''
            테스트 완료
        :return:
        '''
        sid = StrategyStorage.instance().get_trading_id_of_stgyname("bt", "bb_breakout_pair_trading")
        is_same = proceed_backtest_with_tid(sid)
        self.assertEqual(is_same, True)

    def test_ma_crossover_hdg_vol_pair_trading(self):
        sid = StrategyStorage.instance().get_trading_id_of_stgyname("bt", "ma_crossover_hdg_vol_pair_trading")
        is_same = proceed_backtest_with_tid(sid)
        self.assertEqual(is_same, True)
    def test_ma_crossover_4h_vol_pair_trading(self):
        sid = StrategyStorage.instance().get_trading_id_of_stgyname("bt", "ma_crossover_4h_vol_pair_trading")
        is_same = proceed_backtest_with_tid(sid)
        self.assertEqual(is_same, True)

    def test_ws_day_hdg_vol_pair_trading(self):
        sid = StrategyStorage.instance().get_trading_id_of_stgyname("bt", "ws_day_hdg_vol_pair_trading")
        is_same = proceed_backtest_with_tid(sid)
        self.assertEqual(is_same, True)

    def test_ws_day_vol_pair_trading(self):
        sid = StrategyStorage.instance().get_trading_id_of_stgyname("bt", "ws_day_vol_pair_trading")
        is_same = proceed_backtest_with_tid(sid)
        self.assertEqual(is_same, True)


if __name__ == '__main__' :
    unittest.main()
