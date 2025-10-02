import os
import re
import unittest

from jinja2 import Environment, FileSystemLoader

from bt4 import GlobalProperties
from bt4.Constants import CandleType, QItem, ExType
from bt4.core.CfgStgyRuleGenerator import CfgStgyRuleGenerator
from bt4.core.gen_support import parse_exp
from bt4.resource_path_mgr import RPath
from bt4_cfg_stgy_rules.CfgStgyRuleLoader import CfgStgyRuleLoader

GlobalProperties.__VERSION__ = "bt4"
class MyTestCase(unittest.TestCase) :


    def test_list_custom_tai(self):
        import inspect
        import bt4.quote.CustomTAIndicators

        custom_tai_func_list = []
        for name, func in inspect.getmembers(bt4.quote.CustomTAIndicators) :
            if inspect.isfunction(func) :
                custom_tai_func_list.append(name)




    def test_generate_ws_day_vol(self) :
        stgy_name = "ws_day_vol"
        ex_type = ExType.upbit

        csr = CfgStgyRuleGenerator()
        cfg_py, stgy_py, cfg_module = csr.generate_cfg_stgy_rule(stgy_name, ex_type)

    def test_generate_ws_day_fixed(self) :
        stgy_name = "ws_day_fixed"
        ex_type = ExType.upbit

        csr = CfgStgyRuleGenerator()
        cfg_py, stgy_py, cfg_module = csr.generate_cfg_stgy_rule(stgy_name, ex_type)

    def test_generate_config_stgy_rules3(self) :
        stgy_name = "sws_day_alt_weight"
        ex_type = ExType.upbit

        csr = CfgStgyRuleGenerator()
        cfg_py, stgy_py, cfg_module = csr.generate_cfg_stgy_rule(stgy_name, ex_type)

    def test_generate_config_stgy_rules2(self) :
        stgy_name = "sws_day_hdg_vol"
        ex_type = ExType.upbit

        csr = CfgStgyRuleGenerator()
        cfg_py, stgy_py, cfg_module = csr.generate_cfg_stgy_rule(stgy_name, ex_type)

    def test_generate_config_stgy_rules2(self) :
        stgy_name = "ws_day_hdg_vol"
        ex_type = ExType.upbit

        csr = CfgStgyRuleGenerator()
        cfg_py, stgy_py, cfg_module = csr.generate_cfg_stgy_rule(stgy_name, ex_type)

    def test_parsing_system_op(self):
        system_op1 = "system1 and system2"
        from bt4.core.gen_support import parse_op
        print(parse_op(system_op1)) ##['system1', 'and', 'system2']

        system_op2 = "(system1 and system2)"
        print(parse_op(system_op2)) ## ['(', 'system1', 'and', 'system2', ')']

        system_op3 = "((system1 and system2) or (not system3 and system4))"
        print(parse_op(system_op3)) ## ['(', '(', 'system1', 'and', 'system2', ')', 'or', '(', 'not', 'system3', 'and', 'system4', ')', ')']

        system_op4 = "(system1 and system2 and system3) or (not system1 and system4 and system5)"
        print(parse_op(system_op4))

    def test_parsing_expression(self):
        exp1 = "ma2 * (1+0.01)"
        tokens1 = parse_exp(exp1)
        print(f"exp: {exp1} => list : {tokens1}")

        exp2 = "prev_close_d1 - 2 * atr"
        tokens2 = parse_exp(exp2)
        print(f"exp: {exp2} => list : {tokens2}")

        exp3 = "prev_close_d1 -- 2 * atr"
        tokens3 = parse_exp(exp3)
        print(f"exp: {exp3} => list : {tokens3}")

        exp4 = "ma2"
        tokens4 = parse_exp(exp4)
        print(f"exp: {exp4} => list : {tokens4}")

        exp5 = "-50"
        tokens5 = parse_exp(exp5)
        print(f"exp: {exp5} => list : {tokens5}")


    @unittest.skip("Tested")
    def test_generate_config_stgy_rules(self) :
        # id = "db76bfa0-5554-4f1b-8927-6003cd92c41c"
        # strategy_name = "sws_day_hdg_vol_rule"

        # id = "13aab3a9-1950-4219-bd3b-4d8054f4ee6f" ## WinningSession_Hedge
        # strategy_name = "ws_day_hdg_vol"

        id = "112de9fc-506c-4ff9-9c3a-073348b16801" ## SuperWinningSession_Hdge
        strategy_name = "sws_day_hdg_vol"

        cfg_stgy_obj = MongoDBService.instance().get_cfg_stgy_rules(id)
        if cfg_stgy_obj is None:
            print(f"cfg_stgy_obj is None")
            return

        context = cfg_stgy_obj.cfg_rules
        ex_type = cfg_stgy_obj.extype

        self.assertTrue(context["cdl_type"] == CandleType.HOUR)
        self.assertTrue(context["vars"]["ma1"]["cdl_type"] == CandleType.DAYS_TF)


        t_root = RPath.instance().template_root()
        environment = Environment(loader = FileSystemLoader(t_root))

        cfg_file = f"{RPath.instance().stgy_root()}{os.sep}{ex_type}{os.sep}{strategy_name}.py"
        results_template = environment.get_template("config_template.jinja2")

        with open(cfg_file, mode = "w", encoding = "utf-8") as results :
            results.write(results_template.render(context))
            print(f"... wrote {cfg_file}")

        results_template = None
        if context["timeframe"]["support"] == True :
            t_root = RPath.instance().template_root()
            environment = Environment(loader = FileSystemLoader(t_root))
            results_template = environment.get_template("hdge_stgy_template.jinja2")

        stgy_file = f"{RPath.instance().stgy_root()}{os.sep}{ex_type}{os.sep}{context['module_name']}.py"
        with open(stgy_file, mode = "w", encoding = "utf-8") as results :
            results.write(results_template.render(context))
            print(f"... wrote {stgy_file}")


if __name__ == '__main__' :
    unittest.main()
