import json
import unittest
import numpy as np

from bt4.model.storage_mgr import StrategyStorage
from bt4.model.trade_request_support import rebuild_stgy_rules_from_ga_decoded


class MyTestCase(unittest.TestCase) :

    def test_sws_day_alt_weight_ga(self):
        stgy_name = "sws_day_alt_weight_ga"
        tid = StrategyStorage.instance().get_trading_id_of_desc("ga", stgy_name)
        stgy_model = StrategyStorage.instance().load_strategy_using_tid(tid)
        stgy_json = stgy_model.cfg_stgy_rules_json

        ga_decoded = {'markets'       : np.array([0, 1, 0, 1]),
                      'weighted_0' : 0.49282582369935146,
                      'weighted_1' : 0.24273126249125038,
                      'weighted_2' : 0.14602958477057829,
                      'ma1_params_0' : 15, 'ma1_cdl_types' : 1440,
                      'ma2_params_0' : 49, 'ma2_cdl_types' : 30,
                      'ma3_params_0' : 168, 'ma3_cdl_types' : 240,
                      'ma4_params_0' : 176, 'ma4_cdl_types' : 60}

        print(f"{ga_decoded=}")

        updated_stgy_json, updated_ga_decoded = rebuild_stgy_rules_from_ga_decoded(stgy_json, ga_decoded)
        json_string = json.dumps(updated_stgy_json, indent = 4)
        print(f"{updated_ga_decoded=}")
        print(json_string)

    def test_bb_breakout_ga(self):
        stgy_name = "bb_breakout_ga"
        tid = StrategyStorage.instance().get_trading_id_of_desc("bt", stgy_name)
        stgy_model = StrategyStorage.instance().load_strategy_using_tid(tid)
        stgy_json = stgy_model.cfg_stgy_rules_json

        ga_decoded = {'markets': np.array([1, 0, 0]), 'vol_tgt': 0.02,
                      'stop_loss_ratio': -0.03816871825067773,
                      'base_time': '06:59', 'sell_time': '19:59',
                      'bbands_params_0': 119, 'bbands_params_1': 3.812723421229203,
                      'bbands_params_2': 2.5368832472023315, 'bbands_params_3': 0, 'bbands_sources': 'open',
                      'up_breakout_params_0': 36, 'down_breakout_params_0': 23
                      }

        print(f"{ga_decoded=}")

        updated_stgy_json, updated_ga_decoded = rebuild_stgy_rules_from_ga_decoded(stgy_json, ga_decoded)
        json_string = json.dumps(updated_stgy_json, indent = 4)
        print(f"{updated_ga_decoded=}")
        print(json_string)

    def test_composite_bull_bear_market_ga(self):
        stgy_name = "composite_bull_bear_market_ga"
        tid = StrategyStorage.instance().get_trading_id_of_desc("bt", stgy_name)
        stgy_model = StrategyStorage.instance().load_strategy_using_tid(tid)
        stgy_json = stgy_model.cfg_stgy_rules_json

        ga_decoded = {'markets': np.array([0, 0, 0]), 'vol_tgt': 0.02,
                      'ma1_params_0': 3, 'ma1_sources': 'open',
                      'ma2_params_0': 15, 'ma2_sources': 'high',
                      'ma3_params_0': 37, 'ma3_sources': 'close',
                      'ma4_params_0': 58, 'ma4_sources': 'close',
                      'ma_decision_params_0': 99, 'ma_decision_sources': 'close'}

        print(f"{ga_decoded=}")

        updated_stgy_json, updated_ga_decoded = rebuild_stgy_rules_from_ga_decoded(stgy_json, ga_decoded)
        json_string = json.dumps(updated_stgy_json, indent = 4)
        print(f"{updated_ga_decoded=}")
        print(json_string)

    def test_sws_4h_vol_ga(self):
        stgy_name = "sws_4h_vol_ga"
        tid = StrategyStorage.instance().get_trading_id_of_desc("bt", stgy_name)
        stgy_model = StrategyStorage.instance().load_strategy_using_tid(tid)
        stgy_json = stgy_model.cfg_stgy_rules_json

        ga_decoded = {'ma1_params_0': 3, 'ma1_sources': 'low', 'ma2_params_0': 17, 'ma2_sources': 'high',
                      'ma3_params_0': 11, 'ma3_sources': 'high', 'ma4_params_0': 77, 'ma4_sources': 'high',
                      'markets': np.array([0, 1]), 'vol_tgt': 0.02}
        print(f"{ga_decoded=}")

        updated_stgy_json, updated_ga_decoded = rebuild_stgy_rules_from_ga_decoded(stgy_json, ga_decoded)
        json_string = json.dumps(updated_stgy_json, indent = 4)
        print(f"{updated_ga_decoded=}")
        print(json_string)

    def test_sws_day_hdg_vol_ga(self):
        stgy_name = "sws_4h_vol_ga"
        tid = StrategyStorage.instance().get_trading_id_of_desc("bt", stgy_name)
        stgy_model = StrategyStorage.instance().load_strategy_using_tid(tid)
        stgy_json = stgy_model.cfg_stgy_rules_json

        ga_decoded = {'ma1_params_0': 5, 'ma1_sources': 'open', 'ma2_params_0': 13, 'ma2_sources': 'high', 'ma3_params_0': 17,
             'ma3_sources': 'close', 'ma4_params_0': 42, 'ma4_sources': 'close', 'markets': np.array([0, 1]),
             'vol_tgt': 0.04}
        print(f"{ga_decoded=}")

        updated_stgy_json, updated_ga_decoded = rebuild_stgy_rules_from_ga_decoded(stgy_json, ga_decoded)
        json_string = json.dumps(updated_stgy_json, indent = 4)
        print(f"{updated_ga_decoded=}")
        print(json_string)

    def test_sws_30m_vol_ga(self):
        stgy_name = "sws_30m_vol_ga"
        tid = StrategyStorage.instance().get_trading_id_of_desc("bt", stgy_name)
        stgy_model = StrategyStorage.instance().load_strategy_using_tid(tid)
        stgy_json = stgy_model.cfg_stgy_rules_json

        ga_decoded = {'ma1_cdl_types' : 1440, 'ma1_params_0' : 40, 'ma2_cdl_types' : 60, 'ma2_params_0' : 30, 'ma3_cdl_types' : 1440,
         'ma3_params_0'  : 189, 'ma4_cdl_types' : 240, 'ma4_params_0' : 400, 'stop_loss_ratio' : -0.0895396651468838,
         'vol_tgt'       : 0.03}


        print(f"{ga_decoded=}")

        updated_stgy_json, updated_ga_decoded = rebuild_stgy_rules_from_ga_decoded(stgy_json, ga_decoded)
        json_string = json.dumps(updated_stgy_json, indent = 4)
        print(f"{updated_ga_decoded=}")
        print(json_string)

    def test_ga_ws_hdg_vol(self):
        stgy_name = "ws_day_hdg_vol_ga"
        tid = StrategyStorage.instance().get_trading_id_of_desc("bt", stgy_name)
        stgy_model = StrategyStorage.instance().load_strategy_using_tid(tid)
        stgy_json = stgy_model.cfg_stgy_rules_json

        ga_decoded = {'ma1_cdl_types': 240, 'ma1_params_0': 39, 'ma1_sources': 'close', 'markets': np.array([0, 0, 1, 0, 0, 0, 0]),
                      'timeframes': np.array([1, 0, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0]),
                      'timegap': 4, 'vol_tgt': 0.02}

        print(f"{ga_decoded=}")

        updated_stgy_json, updated_ga_decoded = rebuild_stgy_rules_from_ga_decoded(stgy_json, ga_decoded)
        json_string = json.dumps(updated_stgy_json, indent = 4)
        print(f"{updated_ga_decoded=}")
        print(json_string)

    def test_ga_ws_day_vol_ga(self) :

        stgy_name = "ws_day_vol_ga"
        tid = StrategyStorage.instance().get_trading_id_of_desc("bt", stgy_name)
        stgy_model = StrategyStorage.instance().load_strategy_using_tid(tid)
        stgy_json = stgy_model.cfg_stgy_rules_json

        ga_decoded = {'base_time' : '01:59', 'ma_cdl_types' : 60, 'ma_params_0' : 15, 'ma_sources' : 'low',
         'markets'   : np.array([1, 0, 0, 0, 0, 1, 0]), 'sell_time' : '04:59', 'vol_tgt' : 0.02}
        print(f"{ga_decoded=}")

        updated_stgy_json, updated_ga_decoded = rebuild_stgy_rules_from_ga_decoded(stgy_json, ga_decoded)
        json_string = json.dumps(updated_stgy_json, indent = 4)
        print(f"{updated_ga_decoded=}")
        print(json_string)



if __name__ == '__main__' :
    unittest.main()
