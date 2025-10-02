from os.path import dirname, join

from bt4.Constants import ExType
from bt4.core.CfgStgyRuleGenerator import CfgStgyRuleGenerator
from bt4.model.storage_mgr import StrategyStorage
from bt4.utils.python_utils import load_class_from_module, dt2str_for_filename, now_dt
from bt4.utils.bt4_cli_args import get_ga_argument
import bt4.GlobalProperties as global_prop
from bt4.validator.json_schema_validator import JSonSchemaValidator
import sys

def main(args):
    arg_map = get_ga_argument()
    tid = arg_map["tid"]
    global_prop.tid = tid

    from bt4.Constants import R
    r = R()
    parameters = {}

    bt_request = None
    if tid is not None :
        bt_request = StrategyStorage.instance().load_backtesting_request(tid)
    if bt_request is None :
        print(f"[ERROR] Backtesting Request \"{tid}\" does not exist in {global_prop.postgre_sql_db} database of {global_prop.postgre_sql_svr}.")
        sys.exit(0)

    if global_prop.json_schema_validation_support:
        jsv = JSonSchemaValidator()
        if not jsv.validate(bt_request.cfg_stgy_rules_json):
            print(f"JSon Schema Validation Error!")
            sys.exit(0)

    cfg_module, ga_stgy_module = generate_ga_config_strategy(bt_request)
    stgy_name = tid

    root_dir = dirname(__file__)
    ga_hist_output = join(root_dir, f'ga/ga_{stgy_name}_{dt2str_for_filename(now_dt())}.csv')
    stgy_module = f"{cfg_module}_module_ga"

    print(f"{ga_hist_output=}")
    print(f"{cfg_module=}")
    print(f"{stgy_module=}")

    stgy_name = "GAStrategyOptimizer"
    kwarg = {"tid" : tid, "stgy_name":stgy_name, "cfg_module":cfg_module, "ga_hist_output":ga_hist_output}
    ga_stgy_optim = load_class_from_module(stgy_module, stgy_name, **kwarg)
    # ga_stgy_optim.set_params(tid, stgy_cfg_alias, config_module, ga_hist_output)

    tuner = ga_stgy_optim.start_ga_optim()
    # print(tuner.best_score)
    # print(tuner.best_params)
    # print(tuner.best_algorithm)
    # print(tuner.best_algorithm.get_name())


def generate_ga_config_strategy(bt_request) :

    if bt_request is not None:
        print(bt_request.cfg_stgy_rules_json)
        ex_type = ExType(bt_request.ex_type)
        cfg_stgy_rules_json = bt_request.cfg_stgy_rules_json
        cfg_stgy_rules_json["stgy_name"] = "ga_dummy"
        cfg_stgy_rules_json["module_name"] = f"{bt_request.tid}_module"

        ga_csr = CfgStgyRuleGenerator()
        if cfg_stgy_rules_json is not None :
            print("###### Load Cfg_Stgy_Rules_JSON.json from database")
            cfg_py, stgy_py, cfg_module = ga_csr.generate_cfg_stgy_rule(bt_request.tid, ex_type, cfg_stgy_rules_json)
        return cfg_module, f"{stgy_py}_ga"

    return None

if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
