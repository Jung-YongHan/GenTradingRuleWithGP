import json
import unittest
from collections import OrderedDict
from os.path import dirname

from bt4.Constants import CandleType
from bt4.core.gen_support import parse_exp, parse_op

class Stgy_CommentGenerator:
    def __init__(self):
        pass

    def generate_comment_from_stgy_file(self, comment_filepath, print_support = True):
        stgy_rule_json = {}
        with open(comment_filepath, mode = 'r') as stgy_rule :
            stgy_rule_json = json.load(stgy_rule)

        comment, comp_dict = self.__generate_comment0__(stgy_rule_json, print_support)
        return comment, comp_dict

    def generate_two_stgy_files(self, stgy_file1, stgy_file2, print_support = True):
        comment1, comp_dict1 = self.generate_comment_from_stgy_file(stgy_file1, False)
        comment2, comp_dict2 = self.generate_comment_from_stgy_file(stgy_file2, False)

        diff_dict = OrderedDict()
        key_list = []
        for key in comp_dict1:
            if comp_dict1[key] != comp_dict2[key]:
                key_list.append(key)
                update = self.shrink_update(comp_dict1[key], comp_dict2[key])

                if print_support:
                    if comp_dict2[key] == "":
                        print(f"{key}: {comp_dict1[key]} => n/a")
                    else:
                        print(f"{key}: {comp_dict1[key]}\n => {update}")

    def shrink_update(self, v1, v2):
        if len(str(v2)) < 20:
            return v2
        else:
            ## Shrink if it is possible.
            return v2

    def __generate_comment0__(self, comment_json, print_support):
        comp_dict = OrderedDict()
        self.gen_enabled_components(comment_json, comp_dict)

        vars = comment_json["vars"]
        buy_system_op = comment_json["buy_system_op"]
        buy_systems = comment_json["buy_systems"]
        buy_system_comment = self.gen_system_comment(buy_system_op, buy_systems, vars)
        comp_dict["buy"] = buy_system_comment

        sell_system_op = comment_json["sell_system_op"]
        sell_systems = comment_json["sell_systems"]
        sell_system_comment = self.gen_system_comment(sell_system_op, sell_systems, vars)
        comp_dict["sell"] = sell_system_comment

        return self.print_components(comp_dict, print_support), comp_dict

    def print_components(self, comp_dict, print_support) :
        comment = ""
        for comp in comp_dict :
            if comp_dict[comp] != "" :
                if comp == "buy" or comp == "sell" :
                    msg = f"{comp} => {comp_dict[comp]}"
                    comment += msg + "\n"
                    if print_support:
                        print(msg)
                else :
                    msg = f"{comp} : {comp_dict[comp]}"
                    comment += msg + "\n"
                    if print_support :
                        print(msg)
        return comment[:-1]

    def gen_system_comment(self, system_op, systems, vars) :
        tokens = parse_op(system_op)
        statements = []
        for token in tokens :
            if token in systems :
                system_json = systems[token]  ## TODO: This may be an expression

                sys_left = system_json['left']
                sys_right = system_json['right']

                sys_left_exp = self.gen_expression(sys_left, vars)
                sys_right_exp = self.gen_expression(sys_right, vars)
                system = f"{sys_left_exp} {system_json['op']} {sys_right_exp}"
                statements.append(system)

            else :
                statements.append(token)

        return self.gen_exp_comment_detail(statements)

    def gen_expression(self, exp, vars) :
        exps = parse_exp(exp)
        expression = ""
        for exp in exps :
            if exp in vars :
                sys_detail = vars[exp]
                if "params" in sys_detail :
                    params = ",".join(str(e) for e in sys_detail['params'])
                    expression = expression + f"{exp}({params}/{CandleType(sys_detail['cdl_type']).name})"
                else :
                    expression = expression + f"{sys_detail}"
            else :
                expression = expression + f"{exp}"
        return expression

    def gen_exp_comment_detail(self, expressions) :
        rev_token = ["and", "or", "not", "(", ")", "+", "-", "*"]
        comment = ""
        for exp in expressions :
            if exp not in rev_token :
                comment = f"{comment} ({exp})"
            else :
                comment = f"{comment} {exp}"
        return comment

    def gen_enabled_components(self, stgy_rule_json, comp_dict) :
        bt_period = f"{stgy_rule_json['bt_start']}~{stgy_rule_json['bt_end']}"
        comp_dict["backtesting"] = bt_period

        markets = ",".join(stgy_rule_json['markets'])
        comp_dict["markets"] = markets

        cdl_type = CandleType(stgy_rule_json['cdl_type']).name
        comp_dict["candle"] = cdl_type

        init_balance = f"{stgy_rule_json['init_balance']}"
        comp_dict["init_balance"] = init_balance

        slippage = f"{stgy_rule_json['slippage']}"
        comp_dict["slippage"] = slippage

        vola = f"{stgy_rule_json['vola']['vol_tgt']}" if stgy_rule_json["vola"]["support"] == True else ""
        comp_dict["vol_tgt"] = vola

        timeframe = f"{stgy_rule_json['timeframe']['timeframes']}" if stgy_rule_json["timeframe"][
                                                                          "support"] == True else ""
        comp_dict["timeframe"] = timeframe

        timegap = f"{stgy_rule_json['timeframe']['timegap']}" if stgy_rule_json["timeframe"]["support"] == True else ""
        comp_dict["timegap"] = timegap

        fixed_trade_ratio = f"{stgy_rule_json['fixed']['trade_ratio']}" if stgy_rule_json["fixed"][
                                                                               "support"] == True else ""
        comp_dict["fixed_trade_ratio"] = fixed_trade_ratio

        weighted_top_n = stgy_rule_json["weighted"]["top_n"] if stgy_rule_json["weighted"]["support"] == True else ""
        comp_dict["weighted_top_n"] = weighted_top_n

        stop_loss_ratio = f"{stgy_rule_json['stop_loss']['ratio']}" if stgy_rule_json["stop_loss"][
                                                                           "support"] == True else ""
        comp_dict["stop_loss_ratio"] = stop_loss_ratio

        trailing_stop_ratio = stgy_rule_json["trailing_stop"]["ratio"] if stgy_rule_json["trailing_stop"][
                                                                              "support"] == True else ""
        comp_dict["trailing_stop_ratio"] = trailing_stop_ratio

        take_profit_ratio = "take_profit_ratio: " + stgy_rule_json["take_profit"]["ratio"] + "\n" if \
        stgy_rule_json["take_profit"]["support"] == True else ""
        comp_dict["take_profit_ratio"] = take_profit_ratio

class MyTestCase(unittest.TestCase) :
    def test_generate_comment(self) :
        root_dir = dirname(__file__)
        # rule_sample1 = f"{root_dir}/rule_samples/ws_day_vol.json"
        # rule_sample1 = f"{root_dir}/rule_samples/composite_bull_bear_market.json"
        # rule_sample1 = f"{root_dir}/rule_samples/ws_day_vol_stoploss.json"
        # rule_sample1 = f"{root_dir}/rule_samples/vol_bout_sws_hdg_vol.json"
        # rule_sample1 = f"{root_dir}/rule_samples/ttrading_origin_vol.json"
        rule_sample1 = f"{root_dir}/rule_samples/bb_breakout_hdg_vol.json"

        scg = Stgy_CommentGenerator()
        scg.generate_comment_from_stgy_file(rule_sample1, True)


    def test_compare_two_stgy_files(self) :
        root_dir = dirname(__file__)
        # rule_sample1 = f"{root_dir}/rule_samples/bb_breakout_hdg_vol.json"
        # rule_sample2 = f"{root_dir}/rule_samples/bb_breakout_hdg_vol2.json"

        rule_sample1 = f"{root_dir}/rule_samples/composite_bull_bear_market.json"
        rule_sample2 = f"{root_dir}/rule_samples/composite_bull_bear_market2.json"

        scg = Stgy_CommentGenerator()
        scg.generate_two_stgy_files(rule_sample1, rule_sample2, True)






if __name__ == '__main__' :
    unittest.main()
