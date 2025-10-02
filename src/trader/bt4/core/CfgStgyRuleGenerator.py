import os

from jinja2 import Environment, FileSystemLoader

from bt4.core.gen_support import parse_op, extract_time_vars, get_nary_vars, parse_exp, is_col_name, is_custom_tai, \
    get_local_vars_of_func, build_params, is_ohlcv, is_reserved_vars
from bt4.utils.market_utils import handle_dummy_ex
from bt4.utils.mylog import init_log
from bt4.Constants import ExType
from bt4.resource_path_mgr import RPath
from bt4_cfg_stgy_rules.CfgStgyRuleLoader import CfgStgyRuleLoader

log = init_log()
class CfgStgyRuleGenerator:
    def __init__(self):
        pass

    def generate_cfg_stgy_rule(self, stgy_name: str, ex_type: ExType, cfg_stgy_rules_json = None):
        if cfg_stgy_rules_json == None:
            context = CfgStgyRuleLoader().load(f"{stgy_name}.json")
        else:
            context =cfg_stgy_rules_json
        ex_type2 = handle_dummy_ex(ex_type)

        ## generating config files
        t_root = RPath.instance().template_root()
        environment = Environment(loader = FileSystemLoader(t_root))
        tgt_cfg_file = f"{RPath.instance().stgy_root()}{os.sep}{ex_type2.name}{os.sep}{stgy_name}.py"
        results_template = environment.get_template("config_template.jinja2")

        with open(tgt_cfg_file, mode = "w", encoding = "utf-8") as results :
            results.write(results_template.render(context))
            log.debug(f"... wrote {tgt_cfg_file}")

        ## compose the config module name
        cfg_module = f"{RPath.instance().stgy_root_module()}.{ex_type2.name}.{stgy_name}"

        ## generating strategy file
        results_template = None
        t_root = RPath.instance().template_root()
        environment = Environment(loader = FileSystemLoader(t_root))

        if context["timeframe"]["support"] == True :
            results_template = environment.get_template("hdge_stgy_template.jinja2")
        else :
            results_template = environment.get_template("netting_stgy_template.jinja2")

        ## Custom Function of Jinja
        func_dict = {
            "parse_op" : parse_op,
            "extract_time_vars" : extract_time_vars,
            "len" : len,
            "get_nary_vars" : get_nary_vars,
            "parse_exp" : parse_exp,
            "is_col_name" : is_col_name,
            "is_custom_tai" : is_custom_tai,
            "isinstance" : isinstance,
            "get_local_vars_of_func" : get_local_vars_of_func,
            "build_params" : build_params,
            "str" : str,
            "is_ohlcv" : is_ohlcv,
            "is_reserved_vars" : is_reserved_vars
        }
        results_template.globals.update(func_dict)

        tgt_stgy_file = f"{RPath.instance().stgy_root()}{os.sep}{ex_type2.name}{os.sep}{context['module_name']}.py"
        with open(tgt_stgy_file, mode = "w", encoding = "utf-8") as results :
            results.write(results_template.render(context))
            log.debug(f"... wrote {tgt_stgy_file}")

        if "ga_exec" in context and context["ga_exec"] == True:
            results_template = environment.get_template("ga_stgy_template.jinja2")
            results_template.globals.update(func_dict)

            ga_tgt_stgy_file = f"{RPath.instance().stgy_root()}{os.sep}{ex_type2.name}{os.sep}{context['module_name']}_ga.py"
            with open(ga_tgt_stgy_file, mode = "w", encoding = "utf-8") as results :
                results.write(results_template.render(context))
                log.debug(f"... wrote {ga_tgt_stgy_file}")

        return  tgt_cfg_file, tgt_stgy_file, cfg_module


