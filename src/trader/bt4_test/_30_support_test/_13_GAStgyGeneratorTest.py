import unittest

from bt4.Constants import ExType
from bt4.core.CfgStgyRuleGenerator import CfgStgyRuleGenerator
from bt4.model.storage_mgr import StrategyStorage


class MyTestCase(unittest.TestCase) :
    def test_ga_generation(self) :
        stgy_name = "ws_day_vol_ga"
        tid = StrategyStorage.instance().get_trading_id_of_desc("bt", stgy_name)
        btrt = StrategyStorage.instance().load_backtesting_request(tid)

        if btrt is not None :
            print(btrt.cfg_stgy_rules_json)
            ex_type = ExType(btrt.ex_type)
            cfg_stgy_rules_json = btrt.cfg_stgy_rules_json
            cfg_stgy_rules_json["stgy_name"] = "GAStrategyOptimizer"
            cfg_stgy_rules_json["module_name"] = f"{tid}_ga_module"

            ga_csr = CfgStgyRuleGenerator()
            if cfg_stgy_rules_json is not None :
                print("###### Load Cfg_Stgy_Rules_JSON.json from database")
                cfg_py, stgy_py, cfg_module = ga_csr.generate_cfg_stgy_rule(tid, ex_type, cfg_stgy_rules_json)
            return cfg_module, btrt.desc


if __name__ == '__main__' :
    unittest.main()
