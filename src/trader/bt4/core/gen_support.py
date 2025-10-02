from bt4.Constants import CandleType
import pandas as pd
import numpy as np
from bt4.quote.TAIMgr import TAIMgr
from bt4.utils.python_utils import flatten

NARY_THREE_FUNCS = ["BBANDS", "MACD", "MACDEXT"]
NARY_TWO_FUNCS = ["TRB", "AROON","HT_PHASOR","HT_SINE","MAMA","MINMAX","MINMAXINDEX","STOCH", "STOCHF","STOCHRSI","__AI__FORECASTING_DLINEAR"]
custom_tai_func_list = []
def is_custom_tai(tai_func):
    if len(custom_tai_func_list) == 0:
        import inspect
        import bt4.quote.CustomTAIndicators
        for name, func in inspect.getmembers(bt4.quote.CustomTAIndicators) :
            if inspect.isfunction(func) :
                custom_tai_func_list.append(name)
    return tai_func in custom_tai_func_list

def get_nary_vars(func_upper,var):
    if func_upper in NARY_THREE_FUNCS:
        return f"{var}[0]", f"{var}[1]", f"{var}[2]"
    elif func_upper in NARY_TWO_FUNCS :
        return f"{var}[0]", f"{var}[1]"
    return var

def is_nary_vars(func_upper):
    func_upper = func_upper.upper()
    if func_upper in NARY_THREE_FUNCS:
        return True
    elif func_upper in NARY_TWO_FUNCS:
        return True
    return False

def get_local_vars_of_func(func, var, ret_raws=False):
    func_upper = func.upper()

    if (func_upper in NARY_THREE_FUNCS) or (func_upper in NARY_TWO_FUNCS):
        if func_upper in NARY_THREE_FUNCS:
            size = 3
        else:
            size = 2
        vars =  [f"{var}_{i}" for i in range(0, size)]
        if ret_raws:
            var_raws = [f"{var}_{i}_raw" for i in range(0, size)]
            vars.extend(var_raws)
            return vars
        else:
            return vars
    else:
        if ret_raws:
            return [var, f"{var}_raw"]
        else:
            return [var]




def extract_time_vars(vars):
    time_vars = {}
    for var in vars:
        if ("time" in var) and ("ga_" not in var):
            time_vars[var] = vars[var]
    return time_vars

def parse_op(sys_op) :
    '''
    "system1 and system2" ==> ['system1', 'and', 'system2']
    "((system1 and system2) or (not system3 and system4))"
        ==> ['(', '(', 'system1', 'and', 'system2', ')', 'or', '(', 'not', 'system3', 'and', 'system4', ')', ')']
    :param sys_op:
    :return:
    '''
    ops = []
    cur_var = []
    for ch in sys_op :
        if ch == "(" :
            ops.append(ch)
        elif ch == ")" :
            token = ''.join(cur_var)
            if len(token) > 0 :
                ops.append(token)
                cur_var = []
            ops.append(ch)
        elif ch == " " :
            token = ''.join(cur_var)
            if len(token) > 0 :
                ops.append(token)
                cur_var = []
        else :
            cur_var.append(ch)

    if len(cur_var) > 0 :
        ops.append(''.join(cur_var))
        cur_var = []
    return ops

def is_col_name(token):
    is_digit = is_number(token)
    is_op = True if token in "()*/+-" else False
    is_bool = True if token in ["True", "False"] else False

    return (not is_digit) and (not is_op) and (not is_bool)

def is_ohlcv(token):
    return token in ["open", "high", "low", "close", "volume"]

def is_reserved_vars(token):
    return token in ["open_d1", "high_d1", "low_d1"," close_d1", "vol_d1", "prev_open_d1", "prev_high_d1", "prev_low_d1", "prev_close_d1",
                     "prev_vol_d1", "open_4h", "high_4h", "low_4h", "close_4h", "vol_4h", "prev_open_4h", "prev_high_4h", "prev_low_4h",
                     "prev_close_4h", "prev_vol_4h", "open_1h", "high_1h", "low_1h", "close_1h", "vol_1h", "prev_open_1h", "prev_high_1h",
                     "prev_low_1h", "prev_close_1h", "prev_vol_1h", "open_30m", "high_30m", "low_30m", "close_30m", "vol_30m", "prev_open_30m",
                     "prev_high_30m", "prev_low_30m", "prev_close_30m", "prev_vol_30m", "open_15m", "high_15m", "low_15m", "close_15m",
                     "vol_15m", "prev_open_15m", "prev_high_15m", "prev_low_15m", "prev_close_15m", "prev_vol_15m",
                     "open_5m", "high_5m", "low_5m", "close_5m", "vol_5m", "prev_open_5m", "prev_high_5m", "prev_low_5m", "prev_close_5m",
                     "prev_vol_5m", "open_3m", "high_3m", "low_3m", "close_3m", "vol_3m", "prev_open_3m", "prev_high_3m", "prev_low_3m",
                     "prev_close_3m", "prev_vol_3m",  "prev_open_1m", "prev_high_1m", "prev_low_1m", "prev_close_1m", "prev_vol_1m"]

def is_number(value) :
    try :
        float(value)
        return True
    except ValueError :
        return False

def parse_exp(exp):

    # pattern = re.compile("\\w+[*/+-]?\\w*")
    # match = pattern.match(exp)
    # if match :
    #     print('Match found: ', match.groups())
    # else :
    #     print('No match')

    op_list = "*/+-"

    ops = []
    cur_var = []
    for ch in exp :
        if ch == "(" :
            ops.append(ch)
        elif ch == ")" :
            token = ''.join(cur_var)
            if len(token) > 0 :
                ops.append(token)
                cur_var = []
            ops.append(ch)
        elif ch == " " or ch in op_list:
            token = ''.join(cur_var)
            if len(token) > 0 :
                ops.append(token)
                cur_var = []
            if ch in op_list:
                if len(ops) > 0:
                    if ops[-1] not in op_list:
                        ops.append(f"{ch}")
                    else:
                        return f"Error: duplicated operations {ch} followed by {ops[-1]}."
                else:
                    ops.append(f"{ch}")
        else :
            cur_var.append(ch)

    if len(cur_var) > 0 :
        ops.append(''.join(cur_var))
        cur_var = []
    return ops

def build_params(ga_params):
    print(f"{ga_params=}")
    params_list = []

    # for ga_param in ga_params:
    #         for idx in range(len(params)) :
    #             params_list.append(var[f"ga_params_{idx}"])
    #         return params_list
    #
    # else:
    #     return []
    return ["ABC", "DEF"]


def extract_reserved_var_all_mkts(ex_type, tmgr, reserved_var_list, market_tai, tf_hour=None, signature=None):
    mkts = tmgr.get_quote().get_markets(ex_type)

    for mkt in mkts:
        rvar_vals = extract_reserved_vars(ex_type, mkt, tmgr, reserved_var_list, tf_hour)
        if isinstance(rvar_vals, tuple):
            rvar_vals = list(rvar_vals)
        else:
            rvar_vals = list([rvar_vals])

        if signature is None:
            key = mkt
        else:
            key = f"{mkt}_{signature}"

        for rvar_name, rvar_value in zip(reserved_var_list, rvar_vals):
            if key not in market_tai:
                market_tai[key] = {}
            market_tai[key][rvar_name] = rvar_value




def extract_reserved_vars(ex_type, market, tmgr, reserved_var_list, tf_hour=None) :
    quote = tmgr.get_quote()
    '''
        open_d1, high_d1, low_d1, close_d1, vol_d1,     prev_open_d1, prev_high_d1, prev_low_d1, prev_close_d1, prev_vol_d1, \
        open_4h, high_4h, low_4h, close_4h, vol_4h,     prev_open_4h, prev_high_4h, prev_low_4h, prev_close_4h, prev_vol_4h, \
        open_1h, high_1h, low_1h, close_1h, vol_1h,     prev_open_1h, prev_high_1h, prev_low_1h, prev_close_1h, prev_vol_1h, \
        open_30m, high_30m, low_30m, close_30m, vol_30m, prev_open_30m, prev_high_30m, prev_low_30m, prev_close_30m, prev_vol_30m, \
        open_15m, high_15m, low_15m, close_15m, vol_15m, prev_open_15m, prev_high_15m, prev_low_15m, prev_close_15m, prev_vol_15m, \
        open_5m, high_5m, low_5m, close_5m, vol_5m,     prev_open_5m, prev_high_5m, prev_low_5m, prev_close_5m, prev_vol_5m, \
        open_3m, high_3m, low_3m, close_3m, vol_3m,     prev_open_3m, prev_high_3m, prev_low_3m, prev_close_3m, prev_vol_3m, \
                                                        prev_open_1m, prev_high_1m, prev_low_1m, prev_close_1m, prev_vol_1m
    '''

    result_list = []

    for reserved_var in reserved_var_list:
        target_df = None
        var_tokens = reserved_var.split("_")
        if var_tokens[-1] == "d1":
            if tf_hour is None :
                target_df = quote.get_candle_types(ex_type)[CandleType.DAYS][market]
            else :
                target_df = quote.get_candle_types(ex_type)[CandleType[f'DAYS_{tf_hour}']][market]
        elif var_tokens[-1] == "4h":
            target_df = quote.get_candle_types(ex_type)[CandleType.HOUR4][market]
        elif var_tokens[-1] == "1h":
            target_df = quote.get_candle_types(ex_type)[CandleType.HOUR][market]
        elif var_tokens[-1] == "30m":
            target_df = quote.get_candle_types(ex_type)[CandleType.MINUTES_30][market]
        elif var_tokens[-1] == "15m":
            target_df = quote.get_candle_types(ex_type)[CandleType.MINUTES_15][market]
        elif var_tokens[-1] == "5m":
            target_df = quote.get_candle_types(ex_type)[CandleType.MINUTES_5][market]
        elif var_tokens[-1] == "3m":
            target_df = quote.get_candle_types(ex_type)[CandleType.MINUTES_3][market]
        elif var_tokens[-1] == "1m":
            target_df = quote.get_candle_types(ex_type)[CandleType.MINUTES_1][market]

        ### prev_open_d1, prev_high_d1, prev_low_d1, prev_close_d1, prev_vol_d1,
        if len(var_tokens) >= 3 and var_tokens[0] == "prev":
            tgt_prev_df = target_df.iloc[-2]
            prev_value = tgt_prev_df[var_tokens[1]].item()
            result_list.append(prev_value)
        ### open_d1, high_d1, low_d1, close_d1, vol_d1, open_4h, high_4h, low_4h, close_4h, vol_4h,
        elif len(var_tokens) == 2:
            tgt_df = target_df.tail(1)
            value = tgt_df[var_tokens[0]].item()
            result_list.append(value)

    return result_list[0] if len(result_list) == 1 else tuple(result_list)

def extract_reserved_vars_from_dfs(var_mkt_cdl_dfs, reserved_vars, tf_adj_cdl=None):
    target_df = None
    result_list = []

    for rvar in reserved_vars:
        var_tokens = rvar.split("_")
        if var_tokens[-1] == "d1":
            if tf_adj_cdl is None :
                target_df = var_mkt_cdl_dfs[CandleType.DAYS]
            else :
                target_df = var_mkt_cdl_dfs[tf_adj_cdl]
        elif var_tokens[-1] == "4h":
            target_df = var_mkt_cdl_dfs[CandleType.HOUR4]
        elif var_tokens[-1] == "1h":
            target_df = var_mkt_cdl_dfs[CandleType.HOUR]
        elif var_tokens[-1] == "30m":
            target_df = var_mkt_cdl_dfs[CandleType.MINUTES_30]
        elif var_tokens[-1] == "15m":
            target_df = var_mkt_cdl_dfs[CandleType.MINUTES_15]
        elif var_tokens[-1] == "5m":
            target_df = var_mkt_cdl_dfs[CandleType.MINUTES_5]
        elif var_tokens[-1] == "3m":
            target_df = var_mkt_cdl_dfs[CandleType.MINUTES_3]
        elif var_tokens[-1] == "1m":
            target_df = var_mkt_cdl_dfs[CandleType.MINUTES_1]

        ### prev_open_d1, prev_high_d1, prev_low_d1, prev_close_d1, prev_vol_d1,
        if len(var_tokens) >= 3 and var_tokens[0] == "prev" :
            if len(target_df) > 3:
                tgt_prev_df = target_df.iloc[-2]
                prev_value = tgt_prev_df[var_tokens[1]].item()
            else:
                prev_value = -1
            result_list.append(prev_value)
        ### open_d1, high_d1, low_d1, close_d1, vol_d1, open_4h, high_4h, low_4h, close_4h, vol_4h,
        elif len(var_tokens) == 2 :
            tgt_df = target_df.tail(1)
            if len(tgt_df) > 0:
                value = tgt_df[var_tokens[0]].item()
            else:
                value = -1
            result_list.append(value)
    return result_list

def extract_local_variables(ex_type, market, tmgr, tf_hour=None) :
    quote = tmgr.get_quote()
    if tf_hour is None :
        market_d1_df = quote.get_candle_types(ex_type)[CandleType.DAYS][market]
    else :
        market_d1_df = quote.get_candle_types(ex_type)[CandleType[f'DAYS_{tf_hour}']][market]
    market_d1_tail_df = market_d1_df.tail(1)
    volume_d1 = market_d1_tail_df["vol"].item()
    open_d1 = market_d1_tail_df["open"].item()
    high_d1 = market_d1_tail_df["high"].item()
    low_d1 = market_d1_tail_df["low"].item()
    close_d1 = market_d1_tail_df["close"].item()

    market_d1_prev_df = market_d1_df.iloc[-2]
    prev_open_d1 = market_d1_prev_df["open"].item()
    prev_high_d1 = market_d1_prev_df["high"].item()
    prev_low_d1 = market_d1_prev_df["low"].item()
    prev_close_d1 = market_d1_prev_df["close"].item()
    prev_vol_d1 = market_d1_prev_df["vol"].item()

    market_4h_df = quote.get_candle_types(ex_type)[CandleType.HOUR4][market]
    market_4h_tail_df = market_4h_df.tail(1)
    open_4h = market_4h_tail_df["open"].item()
    high_4h = market_4h_tail_df["high"].item()
    low_4h = market_4h_tail_df["low"].item()
    close_4h = market_4h_tail_df["close"].item()
    volume_4h = market_4h_tail_df["vol"].item()

    market_4h_prev_df = market_4h_df.iloc[-2]
    prev_open_4h = market_4h_prev_df["open"].item()
    prev_high_4h = market_4h_prev_df["high"].item()
    prev_low_4h = market_4h_prev_df["low"].item()
    prev_close_4h = market_4h_prev_df["close"].item()
    prev_vol_4h = market_4h_prev_df["vol"].item()

    market_1h_df = quote.get_candle_types(ex_type)[CandleType.HOUR][market]
    market_1h_tail_df = market_1h_df.tail(1)
    open_1h = market_1h_tail_df["open"].item()
    high_1h = market_1h_tail_df["high"].item()
    low_1h = market_1h_tail_df["low"].item()
    close_1h = market_1h_tail_df["close"].item()
    volume_1h = market_1h_tail_df["vol"].item()

    market_1h_prev_df = market_1h_df.iloc[-2]
    prev_open_1h = market_1h_prev_df["open"].item()
    prev_high_1h = market_1h_prev_df["high"].item()
    prev_low_1h = market_1h_prev_df["low"].item()
    prev_close_1h = market_1h_prev_df["close"].item()
    prev_vol_1h = market_1h_prev_df["vol"].item()

    market_30m_df = quote.get_candle_types(ex_type)[CandleType.MINUTES_30][market]
    market_30m_tail_df = market_30m_df.tail(1)
    open_30m = market_30m_tail_df["open"].item()
    high_30m = market_30m_tail_df["high"].item()
    low_30m = market_30m_tail_df["low"].item()
    close_30m = market_30m_tail_df["close"].item()
    volume_30m = market_30m_tail_df["vol"].item()

    market_30m_prev_df = market_30m_df.iloc[-2]
    prev_open_30m = market_30m_prev_df["open"].item()
    prev_high_30m = market_30m_prev_df["high"].item()
    prev_low_30m = market_30m_prev_df["low"].item()
    prev_close_30m = market_30m_prev_df["close"].item()
    prev_vol_30m = market_30m_prev_df["vol"].item()

    market_15m_df = quote.get_candle_types(ex_type)[CandleType.MINUTES_15][market]
    market_15m_tail_df = market_15m_df.tail(1)
    open_15m = market_15m_tail_df["open"].item()
    high_15m = market_15m_tail_df["high"].item()
    low_15m = market_15m_tail_df["low"].item()
    close_15m = market_15m_tail_df["close"].item()
    volume_15m = market_15m_tail_df["vol"].item()

    market_15m_prev_df = market_15m_df.iloc[-2]
    prev_open_15m = market_15m_prev_df["open"].item()
    prev_high_15m = market_15m_prev_df["high"].item()
    prev_low_15m = market_15m_prev_df["low"].item()
    prev_close_15m = market_15m_prev_df["close"].item()
    prev_vol_15m = market_15m_prev_df["vol"].item()

    market_5m_df = quote.get_candle_types(ex_type)[CandleType.MINUTES_5][market]
    market_5m_tail_df = market_5m_df.tail(1)
    open_5m = market_5m_tail_df["open"].item()
    high_5m = market_5m_tail_df["high"].item()
    low_5m = market_5m_tail_df["low"].item()
    close_5m = market_5m_tail_df["close"].item()
    volume_5m = market_5m_tail_df["vol"].item()

    market_5m_prev_df = market_5m_df.iloc[-2]
    prev_open_5m = market_5m_prev_df["open"].item()
    prev_high_5m = market_5m_prev_df["high"].item()
    prev_low_5m = market_5m_prev_df["low"].item()
    prev_close_5m = market_5m_prev_df["close"].item()
    prev_vol_5m = market_5m_prev_df["vol"].item()

    market_3m_df = quote.get_candle_types(ex_type)[CandleType.MINUTES_3][market]
    market_3m_tail_df = market_3m_df.tail(1)
    open_3m = market_3m_tail_df["open"].item()
    high_3m = market_3m_tail_df["high"].item()
    low_3m = market_3m_tail_df["low"].item()
    close_3m = market_3m_tail_df["close"].item()
    volume_3m = market_3m_tail_df["vol"].item()

    market_3m_prev_df = market_3m_df.iloc[-2]
    prev_open_3m = market_3m_prev_df["open"].item()
    prev_high_3m = market_3m_prev_df["high"].item()
    prev_low_3m = market_3m_prev_df["low"].item()
    prev_close_3m = market_3m_prev_df["close"].item()
    prev_vol_3m = market_3m_prev_df["vol"].item()

    market_1m_df = quote.get_candle_types(ex_type)[CandleType.MINUTES_1][market]
    market_1m_prev_df = market_1m_df.iloc[-2]
    prev_open_1m = market_1m_prev_df["open"].item()
    prev_high_1m = market_1m_prev_df["high"].item()
    prev_low_1m = market_1m_prev_df["low"].item()
    prev_close_1m = market_1m_prev_df["close"].item()
    prev_vol_1m = market_1m_prev_df["vol"].item()
    return volume_d1, open_d1, high_d1, low_d1, close_d1, prev_open_d1, prev_high_d1, prev_low_d1, prev_close_d1, prev_vol_d1, \
        open_4h, high_4h, low_4h, close_4h, volume_4h, prev_open_4h, prev_high_4h, prev_low_4h, prev_close_4h, prev_vol_4h, \
        open_1h, high_1h, low_1h, close_1h, volume_1h, prev_open_1h, prev_high_1h, prev_low_1h, prev_close_1h, prev_vol_1h, \
        open_30m, high_30m, low_30m, close_30m, volume_30m, prev_open_30m, prev_high_30m, prev_low_30m, prev_close_30m, prev_vol_30m, \
        open_15m, high_15m, low_15m, close_15m, volume_15m, prev_open_15m, prev_high_15m, prev_low_15m, prev_close_15m, prev_vol_15m, \
        open_5m, high_5m, low_5m, close_5m, volume_5m, prev_open_5m, prev_high_5m, prev_low_5m, prev_close_5m, prev_vol_5m, \
        open_3m, high_3m, low_3m, close_3m, volume_3m, prev_open_3m, prev_high_3m, prev_low_3m, prev_close_3m, prev_vol_3m, \
        prev_open_1m, prev_high_1m, prev_low_1m, prev_close_1m, prev_vol_1m

def call_func(func_name, dfs, cdl_type_val, sources, params, local_vars):
    market_df = dfs[cdl_type_val]
    if len(market_df) == 0:
        if func_name.upper() in NARY_THREE_FUNCS:
            return -1, -1, -1, -1, -1, -1
        elif func_name.upper() in NARY_TWO_FUNCS:
            return -1, -1, -1, -1
        else:
            return -1, -1

    input_list = []
    for src_col in sources:
        if src_col in market_df.columns:
            temp_float = market_df[src_col].astype(float)
            input_list.append(temp_float.to_numpy())
        else:
            if src_col.endswith("]"):
                src_alias = src_col[:src_col.index("[")]
                idx = int(src_col[src_col.index("[") + 1 : src_col.index("]")])
                src_with_idx = f"{src_alias}_{idx}"
                raw_vals = local_vars[f"{src_with_idx}_raw"]

                if isinstance(raw_vals, (list, np.ndarray)):
                    input_list.append(raw_vals)
                else:
                    input_list.append(raw_vals.to_numpy())
            else:
                if src_col in local_vars:
                    input_list.append(local_vars[f"{src_col}_raw"])
                else:
                    print(f"{src_col} does not exist in the data set. ")

    context = {}
    context["candle_type"] = cdl_type_val
    context["dfs"] = dfs
    context["sources"] = sources

    tmgr = TAIMgr()
    if is_nary_vars(func_name):
        result = tmgr.call_talib_nary(func_name, params, input_list, context, True)
    else:
        result = tmgr.call_talib_unary(func_name, params, input_list, context, True)
    return flatten(result)

def convert_primitive(numpy_val):
    if isinstance(numpy_val, list):
        primitive_list = []
        for val in numpy_val:
            if isinstance(val, np.int32) or isinstance(val, np.float32) or isinstance(val, np.int64) or isinstance(val, np.float64):
                primitive_list.append(val.item())
            else:
                primitive_list.append(val)
        return primitive_list
    else:
        if isinstance(numpy_val, np.int32) or isinstance(numpy_val, np.float32) or isinstance(numpy_val, np.int64) or isinstance(numpy_val, np.float64):
            return numpy_val.item()
        else:
            return numpy_val
