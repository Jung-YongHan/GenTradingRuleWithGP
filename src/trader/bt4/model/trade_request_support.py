import copy
import numpy as np

from bt4.core.gen_support import convert_primitive


def rebuild_stgy_rules_from_ga_decoded(stgy_json, origin_ga_decoded) :
    ga_decoded_for_processing = copy.deepcopy(origin_ga_decoded)
    ga_decoded_for_human = copy.deepcopy(origin_ga_decoded)
    updated_stgy_json = copy.deepcopy(stgy_json)

    updated_stgy_json["ga_exec"] = False  # Disable ga

    ga_markets = updated_stgy_json["markets"]
    if "markets" in ga_decoded_for_processing :
        mkt_comb = ga_decoded_for_processing["markets"]
        mkt_indices = np.where(mkt_comb == 1)[0]
        updated_stgy_json["markets"] = [ga_markets[i] for i in mkt_indices]
        ga_decoded_for_human["markets"] = updated_stgy_json["markets"]
        del ga_decoded_for_processing["markets"]

    if "timeframes" in ga_decoded_for_processing :
        tf_comb = ga_decoded_for_processing["timeframes"]
        tf_indices = np.where(tf_comb == 1)[0]
        updated_stgy_json["timeframe"]["timeframes"] = [updated_stgy_json["timeframe"]["timeframes"][i] for i in
                                                        tf_indices]
        ga_decoded_for_human["timeframes"] = updated_stgy_json["timeframe"]["timeframes"]
        del ga_decoded_for_processing["timeframes"]

    if "timegap" in ga_decoded_for_processing :
        updated_stgy_json["timeframe"]["time_gap"] = convert_primitive(ga_decoded_for_processing["timegap"])
        ga_decoded_for_human["timegap"] = convert_primitive(ga_decoded_for_processing["timegap"])
        del ga_decoded_for_processing["timegap"]

    if "vol_tgt" in ga_decoded_for_processing :
        updated_stgy_json["vola"]["vol_tgt"] = ga_decoded_for_processing["vol_tgt"]
        del ga_decoded_for_processing["vol_tgt"]

    if "fixed_t_ratio" in ga_decoded_for_processing :
        updated_stgy_json["fixed"]["trade_ratio"] = ga_decoded_for_processing["fixed_t_ratio"]
        del ga_decoded_for_processing["fixed_t_ratio"]

    if "weighted_0" in ga_decoded_for_processing:
        updated_stgy_json["weighted"]["top_n"] = __search_weighted__(ga_decoded_for_processing)

    if "stop_loss_ratio" in ga_decoded_for_processing :
        updated_stgy_json["stop_loss"]["ratio"] = ga_decoded_for_processing["stop_loss_ratio"]
        del ga_decoded_for_processing["stop_loss_ratio"]

    if "trailing_stop_ratio" in ga_decoded_for_processing :
        updated_stgy_json["trailing_stop"]["ratio"] = ga_decoded_for_processing["trailing_stop_ratio"]
        del ga_decoded_for_processing["trailing_stop_ratio"]

    if "take_profit_ratio" in ga_decoded_for_processing :
        updated_stgy_json["take_profit"]["ratio"] = ga_decoded_for_processing["take_profit_ratio"]
        del ga_decoded_for_processing["take_profit_ratio"]

    if "buy_sell_left_market" in ga_decoded_for_processing:
        left_market = ga_decoded_for_processing["buy_sell_left_market"]
        for bsys, ssys in zip(updated_stgy_json["buy_systems"], updated_stgy_json["sell_systems"]):
            updated_stgy_json["buy_systems"][bsys]["left_market"] = left_market
            updated_stgy_json["sell_systems"][ssys]["left_market"] = left_market
        del ga_decoded_for_processing["buy_sell_left_market"]

    if "buy_sell_right_market" in ga_decoded_for_processing:
        right_market = ga_decoded_for_processing["buy_sell_right_market"]
        for bsys, ssys in zip(updated_stgy_json["buy_systems"], updated_stgy_json["sell_systems"]):
            updated_stgy_json["buy_systems"][bsys]["right_market"] = right_market
            updated_stgy_json["sell_systems"][ssys]["right_market"] = right_market
        del ga_decoded_for_processing["buy_sell_right_market"]

    if "buy_sell_tgt_market" in ga_decoded_for_processing:
        tgt_market = ga_decoded_for_processing["buy_sell_tgt_market"]
        for bsys, ssys in zip(updated_stgy_json["buy_systems"], updated_stgy_json["sell_systems"]):
            updated_stgy_json["buy_systems"][bsys]["tgt_market"] = tgt_market
            updated_stgy_json["sell_systems"][ssys]["tgt_market"] = tgt_market
        del ga_decoded_for_processing["buy_sell_tgt_market"]

    buy_systems = __search_systems__(ga_decoded_for_processing, "buy_system")
    for bsys in buy_systems:
        tokens = bsys.split("_")
        updated_stgy_json["buy_systems"][tokens[1]][f"{tokens[2]}_{tokens[3]}"] = ga_decoded_for_processing[bsys]
        del ga_decoded_for_processing[bsys]

    sell_systems = __search_systems__(ga_decoded_for_processing, "sell_system")
    for ssys in sell_systems :
        tokens = ssys.split("_")
        updated_stgy_json["sell_systems"][tokens[1]][f"{tokens[2]}_{tokens[3]}"] = ga_decoded_for_processing[ssys]
        del ga_decoded_for_processing[ssys]

    time_vals = __search_time_vals__(ga_decoded_for_processing)
    for time_val in time_vals :
        updated_stgy_json["vars"][time_val] = ga_decoded_for_processing[time_val]
        del ga_decoded_for_processing[time_val]

    tai_vars = __search_tai_vars__(ga_decoded_for_processing, ga_decoded_for_human)
    for tai_var in tai_vars :
        for tai_elem in tai_vars[tai_var] :
            if tai_elem == "sources" :
                updated_stgy_json["vars"][tai_var][tai_elem] = [tai_vars[tai_var][tai_elem]]
                del ga_decoded_for_processing[f"{tai_var}_sources"]
            elif tai_elem == "cdl_types" :
                updated_stgy_json["vars"][tai_var]["cdl_type"] = tai_vars[tai_var][tai_elem]
                del ga_decoded_for_processing[f"{tai_var}_cdl_types"]
            else :
                updated_stgy_json["vars"][tai_var]["params"] = tai_vars[tai_var][tai_elem]
                del ga_decoded_for_processing[f"{tai_var}_{tai_elem}"]

    return updated_stgy_json, ga_decoded_for_human

def __search_systems__(ga_decoded_for_processing, prefix_of_key):
    system_list = []
    for key in ga_decoded_for_processing:
        if key.startswith(prefix_of_key):
            system_list.append(key)
    return system_list


def __search_weighted__(ga_decoded):
    weight_list = []
    for idx in range(100):
        if f"weighted_{idx}" in ga_decoded:
            weight_list.append(ga_decoded[f"weighted_{idx}"])
            del ga_decoded[f"weighted_{idx}"]
        else:
            break
    return weight_list
def __search_time_vals__(ga_decoded) :
    time_vals = []
    for ga_param in ga_decoded :
        if ga_param.endswith("time") :
            time_vals.append(ga_param)
    return time_vals


def __search_tai_vars__(ga_decoded, ga_decoded_for_human) :
    tai_vals = {}

    for tai_var in ga_decoded :
        if tai_var.endswith(("params_0", "params_1", "params_2", "params_3", "params_4", "params_5")):
            tai_name = tai_var[0: -9]
        elif tai_var.endswith("sources"):
            tai_name = tai_var[0: -8]
        elif tai_var.endswith("cdl_types"):
            tai_name = tai_var[0: -10]
        else:
            tai_name = tai_var.split("_")[0]

        if tai_name not in tai_vals :
            tai_vals[tai_name] = {}
        tai_elem = tai_var.replace(f"{tai_name}_", "")
        if tai_elem.endswith("cdl_types") or tai_elem.endswith("sources") :
            tai_vals[tai_name][tai_elem] = ga_decoded[tai_var]
        else :  ## param_0, param_1, param_2
            params = []
            for i in range(100) :
                if f"{tai_name}_params_{i}" in ga_decoded :
                    params.append(convert_primitive(ga_decoded[f"{tai_name}_params_{i}"]))
                    ga_decoded_for_human[f"{tai_name}_params_{i}"] = convert_primitive(ga_decoded[f"{tai_name}_params_{i}"])
                else :
                    break
            tai_vals[tai_name][tai_elem] = params
    return tai_vals