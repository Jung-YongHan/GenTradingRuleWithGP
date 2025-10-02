import unittest

from bt4.Constants import ExType
from bt4.model.storage_mgr import StrategyStorage
from bt4_cfg_stgy_rules.CfgStgyRuleLoader import CfgStgyRuleLoader


class MyTestCase(unittest.TestCase):

    # @unittest.skip("Tested")
    def test_store_bt_request(self):

        stgy_json_name = [
            # "ws_day_vol",
            # "swkim_1_hdg_vol"
            "sws_ma_crossover_hdg_vol",
            "ma_crossover_vol"
        ]

        ex_type = ExType.bithumb
        for stgy_json_name in stgy_json_name:
            cfg_stgy_rules = CfgStgyRuleLoader().load(f"{stgy_json_name}.json")
            sid = StrategyStorage.instance().store_trading_request(stgy_json_name, ex_type, "bt", cfg_stgy_rules)
            print(f"{stgy_json_name} stored with '{sid}'.")

    def test_store_ft_request(self):

        stgy_json_name = [
            # "ws_day_vol",
            # "swkim_1_hdg_vol"
            # "sws_ma_crossover_hdg_vol",
            "ma_crossover_vol"
        ]
        ex_type = ExType.bithumb
        for stgy_json_name in stgy_json_name:
            cfg_stgy_rules = CfgStgyRuleLoader().load(f"{stgy_json_name}.json")
            sid = StrategyStorage.instance().store_trading_request(stgy_json_name, ex_type, "ft", cfg_stgy_rules)
            print(f"{stgy_json_name} stored with '{sid}'.")

    def test_store_lt_request(self):
        stgy_json_name = [
            # "ws_day_vol",
            # "swkim_1_hdg_vol"
            # "sws_ma_crossover_hdg_vol",
            "ma_crossover_vol"
        ]
        ex_type = ExType.bithumb
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
