import unittest

from bt4.Constants import ExType
from bt4.model.storage_mgr import StrategyStorage
from bt4_cfg_stgy_rules.CfgStgyRuleLoader import CfgStgyRuleLoader


class MyTestCase(unittest.TestCase):

    # @unittest.skip("Tested")
    def test_store_bt_request(self):

        stgy_json_name = [
            # "vol_bout_sws_hdg_vol",
            # "vol_bout_hdg_vol",
            # "vol_bout_vol",
            # "ttrading_vol",
            # "ttrading_hdg_vol",
            # "ttrading_origin_vol",
            # "tai_comb_vol",
            # "ma_crossover_hdg_vol",
            # "composite_bull_bear_market_hdg",
            # "composite_bull_bear_market",
            # "swkim_1_vol",
            # "swkim_1_hdg_vol",
            # "swkim_1_4h_vol",
            # "ma_crossover_4h_vol",
            # "ma_crossover_4h_vol2",
            "sws_day_vol",
            # "sws_4h_vol",
            # "sws_day_hdg_vol_ema",
            # "sws_ma_crossover_day_vol",
            # "bitholder_hdg_vol_tai",
            # "sws_ma_crossover_hdg_vol",
            # "sws_day_hdg_vol_macd",
            # "sws_day_hdg_asym_vol",
            # "ws_4h_vol",
            # "ws_day_hdg_vol_mma",
            # "ws_alt_vol",
            # "ws_day_hdg_fixed",
            # "ws_day_vol",
            # "ws_day_hdg_volume_vol",
            # "ws_day_adaptive_param_hdg_volume_vol",
            # "sws_day_alt_weight",
            "sws_day_hdg_vol_tai",
            # "ws_day_fixed",
            # "ws_day_hdg_vol_vwap",
            # "ws_day_hdg_vol",
            "sws_day_hdg_vol",
            # "ws_day_vol_cascade_tais",
            # "ws_day_hdg_vol_cascade_tais",
            # "bb_bullish_bearish_reversal",
            # "bb_bullish_bearish_reversal_hdg_vol",
            # "bb_bullish_bearish_reversal_15m",
            # "bb_breakout",
            # "bb_breakout_hdg_vol",
            # "ma_crossover_vol",
            # "sws_1m_vol",
            # "ws_ga_result_test",
            # "ws_day_vol_wo_sell_only_stoploss",
            # "ws_day_hdg_vol_wo_sell_only_stoploss",
            # "ws_day_vol_pair_trading",
            # "ws_day_hdg_vol_pair_trading",
            # "ma_crossover_4h_vol_pair_trading",
            # "ma_crossover_hdg_vol_pair_trading",
            # "bb_breakout_pair_trading",
            # "bb_bullish_bearish_reversal_hdg_vol_pair_trading",
            # "composite_bull_bear_market_pair_trading",
            # "swkim_1_hdg_vol_pair_trading",
            # "sws_4h_vol_pair_trading",
            # "sws_day_hdg_vol_tai_pair_trading",
            # "sws_ma_crossover_day_vol_pair_trading",
            # "vol_bout_vol_pair_trading",
            # "ws_day_vol_pair_trading_ga_optim",
            # "ws_day_vol_pair_trading_using_spread",
            # "ws_day_vol_mkt_specific",
            # "ws_day_hdg_vol_mkt_specific",
            # "sws_day_vol_mkt_specific",
            # "sws_ma_crossover_hdg_vol_mkt_specific",
            # "swkim_1_hdg_vol_mkt_specific"
            # "sws_day_hdg_vol_tai_mkt_specific",
            # "ma_crossover_hdg_vol_mkt_specific"
        ]

        ex_type = ExType.upbit
        for stgy_json_name in stgy_json_name:
            cfg_stgy_rules = CfgStgyRuleLoader().load(f"{stgy_json_name}.json")
            sid = StrategyStorage.instance().store_trading_request(stgy_json_name, ex_type, "bt", cfg_stgy_rules)
            print(f"{stgy_json_name} stored with '{sid}'.")

    def test_store_ft_request(self):

        stgy_json_name = [
            # "vol_bout_sws_hdg_vol",
            # "vol_bout_hdg_vol",
            # "vol_bout_vol",
            # "ttrading_vol",
            # "ttrading_hdg_vol",
            # "ttrading_origin_vol",
            # "tai_comb_vol",
            # "ma_crossover_hdg_vol",
            # "composite_bull_bear_market_hdg",
            # "composite_bull_bear_market",
            # "swkim_1_vol",
            # "swkim_1_hdg_vol",
            # "swkim_1_4h_vol",
            # "ma_crossover_4h_vol",
            # "sws_day_vol",
            "sws_4h_vol",
            # "sws_day_hdg_vol_ema",
            # "sws_ma_crossover_day_vol",
            # "bitholder_hdg_vol_tai",
            # "sws_ma_crossover_hdg_vol",
            # "sws_day_hdg_vol_macd",
            # "sws_day_hdg_asym_vol",
            # "ws_4h_vol",
            # "ws_day_hdg_vol_mma",
            # "ws_alt_vol",
            # "ws_day_hdg_fixed",
            # "ws_day_vol",
            # "ws_day_hdg_volume_vol",
            # "ws_day_adaptive_param_hdg_volume_vol",
            # "sws_day_alt_weight",
            # "sws_day_hdg_vol_tai",
            # "ws_day_fixed",
            # "ws_day_hdg_vol_vwap",
            # "ws_day_hdg_vol",
            # "sws_day_hdg_vol",
            # "ws_day_vol_cascade_tais"
        ]
        ex_type = ExType.upbit
        for stgy_json_name in stgy_json_name:
            cfg_stgy_rules = CfgStgyRuleLoader().load(f"{stgy_json_name}.json")
            sid = StrategyStorage.instance().store_trading_request(stgy_json_name, ex_type, "ft", cfg_stgy_rules)
            print(f"{stgy_json_name} stored with '{sid}'.")

    def test_store_lt_request(self):
        stgy_json_name = [
            "ws_day_vol",
            # "sws_day_hdg_vol",
            # "sws_day_hdg_vol_tai"
        ]
        ex_type = ExType.upbit
        for stgy_json_name in stgy_json_name:
            cfg_stgy_rules = CfgStgyRuleLoader().load(f"{stgy_json_name}.json")
            sid = StrategyStorage.instance().store_trading_request(stgy_json_name, ex_type, "lt", cfg_stgy_rules)
            print(f"{stgy_json_name} stored with '{sid}'.")

    def test_store_ga_request(self):
        stgy_json_name = [
            # "ws_day_vol_ga",                  # ga_cdl_types, ga_vol_tgt Test Test완료
            # "ws_day_vol_ga2",
            # "ws_day_vol_ga3",
            # "ws_day_vol_ga4",
            # "ws_day_hdg_vol_ga",
            # "ws_day_hdg_vol_ga2",
            # "ws_day_hdg_vol_ga3",
            # "ws_day_hdg_vol_ga",              # ga_cdl_types, ga_vol_tgt Test Test완료
            # "sws_day_hdg_vol_ga",
            # "sws_day_hdg_vol_tai_ga",
            # "composite_bull_bear_market_ga",
            # "bb_breakout_ga",
            # "bitholder_hdg_vol_tai_ga",
            # "ma_crossover_4h_vol_ga",           # ga_cdl_types, ga_vol_tgt Test 완료 => 수행중
            # "swkim_1_4h_vol_ga",
            # "sws_4h_vol_ga",
            # "sws_30m_vol_ga",                 # ga_cdl_types, ga_vol_tgt Test 완료 => 수행중
            # "swkim1_macrossover_4h_vol_ga",    # ga_cdl_types, ga_vol_tgt Test 완료 => 수행중
            # "sws_day_alt_weight_ga",
            # "ws_ga_result_test",
            # "ws_day_hdg_vol_ga2"
            # "ws_day_vol_ga4",
            # "ws_day_vol_pair_trading_ga",
            # "vol_bout_vol_pair_trading_ga",
            # "sws_ma_crossover_day_vol_pair_trading_ga"
            # "sws_day_hdg_vol_tai_pair_trading_ga",
            # "sws_ma_crossover_day_vol_pair_trading_ga2"
            # "sws_ma_crossover_hdg_vol_mkt_specific_ga",
            # "swkim_1_hdg_vol_mkt_specific_ga"
            # "sws_day_hdg_vol_tai_mkt_specific_ga"
            "ma_crossover_hdg_vol_mkt_specific_ga"
        ]


        ex_type = ExType.upbit
        for stgy_json_name in stgy_json_name:
            cfg_stgy_rules = CfgStgyRuleLoader().load(f"{stgy_json_name}.json")
            sid = StrategyStorage.instance().store_trading_request(stgy_json_name, ex_type, "ga", cfg_stgy_rules)
            print(f"{stgy_json_name} stored with '{sid}'.")


if __name__ == "__main__":
    # unittest.main()
    MyTestCase().test_store_bt_request()
