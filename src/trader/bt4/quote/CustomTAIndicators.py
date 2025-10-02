import sys

from sklearn.linear_model import LinearRegression
import bt4.GlobalProperties as global_prop
from bt4.Constants import ExType
from bt4.utils.pandas_utils import shift
import numpy as np
import pandas as pd
from bt4.utils.mylog import init_log
log = init_log()

EXTRA_PARAM_SIZE = 2

def vwap(*args, **kwargs):
    if len(args) != 6:
        return [[np.nan]]

    open_price = args[0]
    high_price  = args[1]
    low_price   = args[2]
    close_price = args[3]
    volume      = args[4]
    period      = args[5]

    recent_open = open_price[-period:]
    recent_high = high_price[-period :]
    recent_low = low_price[-period :]
    recent_close = close_price[-period :]
    recent_vol = volume[-period :]

    mean_ohlc = np.stack([recent_open, recent_high, recent_low, recent_close]).sum(axis=0)/4
    vol_weighted_ohlc = mean_ohlc * recent_vol
    vwap = vol_weighted_ohlc.sum() / recent_vol.sum()
    return pd.Series([vwap])


'''
calculate Modified Ichimoku Cloud
'''
def ic1(*args, **kwargs):
    if len(args) != 4:
        return [[np.nan]]
    high_price   = args[0]
    low_price    = args[1]
    short_period = args[2]
    long_period  = args[3]

    short_high = np.max(high_price[-short_period:])
    short_low = np.min(low_price[-short_period :])
    long_high = np.max(high_price[-long_period :])
    long_low = np.min(low_price[-long_period :])

    return pd.Series([(short_high + short_low + long_high + long_low) / 4])

'''
calculate Ichimoku Cloud
'''
def ic(*args, **kwargs):
    if len(args) != 3:
        return [[np.nan]]
    high_price = args[0]
    low_price = args[1]
    period = args[2]

    high = np.max(high_price[-period:])
    low = np.min(low_price[-period :])

    return pd.Series([(high + low) / 2])

'''
calculate Chaikin Money Flow
'''
def cmf(*args, **kwargs):
    if len(args) != 5:
        return [[np.nan]]
    high_price  = args[0]
    low_price   = args[1]
    close_price = args[2]
    volume      = args[3]
    period      = args[4]

    f_hp  = high_price[-period:]
    f_lp  = low_price[-period :]
    f_cp  = close_price[-period :]
    f_vol = volume[-period :]

    p1 = (f_cp - f_lp) - (f_hp - f_cp)
    if (np.isnan(p1).any()):
        np.nan_to_num(p1, copy = False)

    p2 = (f_hp - f_lp)
    if (np.isnan(p2).any()):
        np.nan_to_num(p2, copy = False)

    p3 = p1 / p2
    if (np.isnan(p3).any()) :
        np.nan_to_num(p3, copy = False)

    price_sum = np.sum(p3 * f_vol)

    vol_sum = np.sum(volume)

    # result = price_sum / vol_sum
    # print(f"result - {result}")
    return pd.Series([price_sum / vol_sum])


'''
get recent data
'''
def recent(*args, **kwargs):
    if len(args) != 1:
        return [[np.nan]]
    data = args[0]
    return pd.Series(data)

'''
compute volatility
args[0] = opening_price
args[1] = high_price
args[0] = low_price
'''
def vol(*args, **kwargs):
    if len(args) != 3:
        return [[np.nan]]
    open_price = args[0]
    high_price = args[1]
    low_price = args[2]

    s_high_price = shift(high_price, 1)
    s_low_price  = shift(low_price, 1)
    range = s_high_price - s_low_price
    shifted_open_price = range / open_price
    return pd.Series(shifted_open_price)

'''
compute volatility
args[0] = opening_price
args[1] = high_price
args[0] = low_price
'''
def range(*args, **kwargs):
    if len(args) != 3:
        return [[np.nan]]

    high_price = args[0]
    low_price = args[1]
    filter_out_time_period = args[2]

    filtered_high_price = high_price[ : -filter_out_time_period]
    filtered_low_price = low_price[ : -filter_out_time_period]
    result = filtered_high_price - filtered_low_price
    return pd.Series([0, 0]) if len(result) == 0 else result

'''
compute volatility
args[0] = high_price
args[1] = low_price
args[2] = trade_price
'''
def range_c(*args, **kwargs):
    if len(args) != 3:
        return [[np.nan]]

    high_price  = args[0]
    low_price   = args[1]
    trade_price = args[2]

    return pd.Series([high_price - low_price, trade_price])

'''
trading range breakout
args[0] = high_price
args[1] = low_price
args[2] = periods
'''
def trb(*args, **kwargs):
    if len(args) != 3:
        return [[np.nan]]

    high_price  = args[0]
    low_price   = args[1]
    period      = args[2]

    filtered_high_price = high_price[-period : ]
    filtered_low_price = low_price[-period: ]

    df = pd.DataFrame({"high":filtered_high_price, "low" : filtered_low_price })
    cummax = df["high"].cummax()
    cummin = df["low"].cummin()
    return [cummax, cummin]
'''
average noise ratio
args[0] = opening_price
args[1] = high_price
args[2] = low_price
args[3] = trade_price
args[4] = period
anr = sum(1-abs(o-c)/(h-l))/period
anr < 0.4 ==> 안정적인 시장 ==> 투자대상
anr > 0.4 ==> 높은 변동성 ==> 제외 
'''
def anr(*args, **kwargs):
    if len(args) != 5:
        return [[np.nan]]

    opening_price   = args[0]
    high_price      = args[1]
    low_price       = args[2]
    trade_price     = args[3]
    period          = args[4]

    filtered_op = opening_price[-period:]
    filtered_hp = high_price[-period:]
    filtered_lp = low_price[-period:]
    filtered_tp = trade_price[-period:]
    range_open_close = abs(filtered_op-filtered_tp)
    range_high_low = filtered_hp - filtered_lp
    anr = sum(1-range_open_close/range_high_low) / period
    return pd.Series([anr])


def bullish_reversal(*args, **kwargs):
    '''
    상승반전 체크: 값들이 특정 길이 안에서 하락하다가 상승반전하는 구간이 존재하는지 체크
    :param values: 값
    :param length: 특정 길이
    :return: True/False
    '''
    if len(args) != 2:
        return pd.Series([False])

    values   = args[0]
    length   = args[1]

    if len(values) < length:
        return pd.Series([False])

    if length < 4:
        log.warning(f"Too short period({length}) to check the down trend in 'bullish_reversal' function. The period should be longer than 4 at least.")
        return pd.Series([False])

    filtered_val = values[-length :]

    num_of_zeros = np.count_nonzero(np.isnan(filtered_val))
    if num_of_zeros > 0:
        log.warning(f"{num_of_zeros} values are NaN.")
        return pd.Series([False])

    time = np.arange(0, length).reshape(length, 1)

    # 하락 추제인지 확인: 상승추세이면 상승반전은 일단 아님
    lreg = LinearRegression().fit(time, filtered_val)
    coef = lreg.coef_[0]
    if coef >= 0:
        return pd.Series([False])

    # 하락 후 최근 상승 패턴 확인
    recent = None
    if len(values) >= 10:
        recent = filtered_val[-int(length*0.3):]
    elif (len(values) > 4) and (len(values) < 10):
        recent = filtered_val[-4 :]
    else:
        log.warning(f"Too Short Period({length}) to check the down trend in 'bullish_reversal' function.")
        return pd.Series([False])

    changes = np.diff(recent)  ## Calc the gap
    signs = np.sign(changes)   ## make signs
    rev_signs = signs[::-1]    ## reverse the sign to catch the recent reversion first.
    for i, sign in enumerate(rev_signs):
        if i < len(signs) - 1 :
            if sign == 1 and rev_signs[i + 1] == -1 :
                return pd.Series([True])

    return pd.Series([False])

def bearish_reversal(*args, **kwargs):
    '''
    하락반전 체크: 값들이 특정 길이 안에서 상승하다가 하락반전하는 구간이 존재하는지 체크
    :param values: 값
    :param length: 특정 길이
    :return: True/False
    '''
    if len(args) != 2:
        return pd.Series([False])

    values   = args[0]
    length   = args[1]

    if len(values) < length :
        return pd.Series([False])

    if length < 4:
        log.warning(f"Too short period({length}) to check the up trend in 'bearish_reversal' function. The period should be longer than 4 at least.")
        return pd.Series([False])

    filtered_val = values[-length :]

    num_of_zeros = np.count_nonzero(np.isnan(filtered_val))
    if num_of_zeros > 0:
        log.warning(f"{num_of_zeros} values are NaN.")
        return pd.Series([False])

    time = np.arange(0, length).reshape(length, 1)

    # 상승 추제인지 확인: 하락추세이면 하락 반전은 일단 아님
    lreg = LinearRegression().fit(time, filtered_val)
    coef = lreg.coef_[0]
    if coef <= 0:
        return pd.Series([False])

    # 상승후 최근 하락 패턴이 발생하는지 확인
    recent = None
    if len(values) >= 10 :
        recent = filtered_val[-int(length * 0.3) :]
    elif (len(values) > 4) and (len(values) < 10) :
        recent = filtered_val[-4 :]
    else :
        log.warning(f"Too Short Period({length}) to check the down trend in 'bearish_reversal' function.")
        return pd.Series([False])

    changes = np.diff(recent)  ## Calc the gap
    signs = np.sign(changes)  ## make signs
    rev_signs = signs[: :-1]  ## reverse the sign to catch the recent reversion first.
    for i, sign in enumerate(rev_signs) :
        if i < len(signs) - 1 :
            if sign == -1 and rev_signs[i + 1] == 1 :
                return pd.Series([True])

    return pd.Series([False])

def up_breakout_val(*args, **kwargs):
    '''
    상승 돌파 체크: 값들이 특정 길이 안에서 특정 값을 상승 돌파하는가 체크
    :param values: 값
    :param length: 특정 길이
    :param threshold: 특정 값
    :return: True/False
    '''
    if len(args) != 3:
        return pd.Series([False])

    values   = args[0]
    threshold = args[1]
    length   = args[2]

    if ((type(values) != list) and (type(values) != np.ndarray)) or (len(values) < length) :
        return pd.Series([False])

    filtered_val = values[-length :]

    num_of_zeros = np.count_nonzero(np.isnan(filtered_val))
    if num_of_zeros > 0:
        log.warning(f"up_breakout_val => {num_of_zeros} values are NaN.")
        return pd.Series([False])

    thresholds = np.full(length, threshold)

    t_gaps = np.subtract(filtered_val, thresholds)
    signs = np.sign(t_gaps)

    rev_signs = signs[: :-1]  ## reverse the sign to catch the recent reversion first.
    for i, sign in enumerate(rev_signs) :
        if i < len(signs) - 1 :
            if sign == 1 and rev_signs[i + 1] == -1 :
                return pd.Series([True])

    return pd.Series([False])

def up_breakout_vals(*args, **kwargs):
    '''
    상승 돌파 체크: 값들이 특정 길이 안에서 특정 값을 상승 돌파하는가 체크
    :param values: 값
    :param threshold: 값들의 배열일수도 있음 (예, Price > BBand_Up)
    :param length: 특정 길이
    :return: True/False
    '''
    if len(args) != 3 :
        return pd.Series([False])

    values = args[0]
    thresholds = args[1]
    length = args[2]

    if len(values) < length :
        return pd.Series([False])

    filtered_val = values[-length :]
    filtered_thresholds = thresholds[-length :]

    num_of_zeros_of_val = np.count_nonzero(np.isnan(filtered_val))
    if num_of_zeros_of_val > 0 :
        log.warning(f"up_breakout_vals => {num_of_zeros_of_val} values are NaN.")
        return pd.Series([False])

    num_of_zeros_of_thrs = np.count_nonzero(np.isnan(filtered_thresholds))
    if num_of_zeros_of_thrs > 0 :
        log.warning(f"up_breakout_vals => {num_of_zeros_of_thrs} values are NaN.")
        return pd.Series([False])

    # thresholds = np.full(length, threshold)
    t_gaps = np.subtract(filtered_val, filtered_thresholds)
    signs = np.sign(t_gaps)

    rev_signs = signs[: :-1]  ## reverse the sign to catch the recent reversion first.
    for i, sign in enumerate(rev_signs) :
        if i < len(signs) - 1 :
            if sign == 1 and rev_signs[i + 1] == -1 :
                return pd.Series([True])

    return pd.Series([False])

def down_breakout_val(*args, **kwargs):
    '''
    하향 돌파 체크: 값들이 특정 길이 안에서 특정 값을 하향 돌파하는가 체크
    :param values: 값
    :param length: 특정 길이
    :param threshold: 특정 값일수도 있고, 값들의 배열일수도 있음 (예, RSI < 70, Price < BBand_Down)
    :return: True/False
    '''
    if len(args) != 3 :
        return pd.Series([False])

    values = args[0]
    threshold = args[1]
    length = args[2]

    if ((type(values) != list) and (type(values) != np.ndarray)) or (len(values) < length) :
        return pd.Series([False])

    filtered_val = values[-length :]

    num_of_zeros = np.count_nonzero(np.isnan(filtered_val))
    if num_of_zeros > 0 :
        log.warning(f"down_breakout_val => {num_of_zeros} values are NaN.")
        return pd.Series([False])

    thresholds = np.full(length, threshold)

    t_gaps = np.subtract(filtered_val, thresholds)
    signs = np.sign(t_gaps)

    rev_signs = signs[: :-1]  ## reverse the sign to catch the recent reversion first.
    for i, sign in enumerate(rev_signs) :
        if i < len(signs) - 1 :
            if sign == -1 and rev_signs[i + 1] == +1 :
                return pd.Series([True])

    return pd.Series([False])

def down_breakout_vals(*args, **kwargs):
    '''
    하향 돌파 체크: 값들이 특정 길이 안에서 특정 값을 하향 돌파하는가 체크
    :param values: 값
    :param length: 특정 길이
    :param threshold: 특정 값일수도 있고, 값들의 배열일수도 있음 (예, RSI < 70, Price < BBand_Down)
    :return: True/False
    '''
    if len(args) != 3 :
        return pd.Series([False])

    values = args[0]
    thresholds = args[1]
    length = args[2]

    if len(values) < length :
        return pd.Series([False])

    filtered_val = values[-length :]
    filtered_thresholds = thresholds[-length :]

    num_of_zeros_of_val = np.count_nonzero(np.isnan(filtered_val))
    if num_of_zeros_of_val > 0 :
        log.warning(f"down_breakout_vals => {num_of_zeros_of_val} values are NaN.")
        return pd.Series([False])

    num_of_zeros_of_thrs = np.count_nonzero(np.isnan(filtered_thresholds))
    if num_of_zeros_of_thrs > 0 :
        log.warning(f"down_breakout_vals => {num_of_zeros_of_thrs} values are NaN.")
        return pd.Series([False])

    # thresholds = np.full(length, threshold)
    t_gaps = np.subtract(filtered_val, filtered_thresholds)
    signs = np.sign(t_gaps)

    rev_signs = signs[: :-1]  ## reverse the sign to catch the recent reversion first.
    for i, sign in enumerate(rev_signs) :
        if i < len(signs) - 1 :
            if sign == -1 and rev_signs[i + 1] == 1 :
                return pd.Series([True])

    return pd.Series([False])

"""
standardized spread
https://blog.naver.com/chunjein/100149631087
"""
def spread(*args, **kwargs):
    if len(args) != 4+1:
        return pd.Series([[np.nan]])

    close_vals = args[0] ## useless
    ex_type = ExType(args[1])
    src_mkt = args[2]
    tgt_mkt = args[3]
    period  = args[4]

    cdl_type = kwargs["candle_type"]
    dfs = kwargs["dfs"]
    srcs = kwargs["sources"]

    quote = global_prop.cur_quote  # Fetch Quote

    cur_mkt = dfs[cdl_type].head(1)["market"].item()

    src_mkt_cdl_ser = quote.get_candle_types(ex_type)[cdl_type][src_mkt][srcs[0]][-period:]
    tgt_mkt_cdl_ser = quote.get_candle_types(ex_type)[cdl_type][tgt_mkt][srcs[0]][-period:]

    normalized_src_ser = (src_mkt_cdl_ser - src_mkt_cdl_ser.mean())/src_mkt_cdl_ser.std()
    normalized_tgt_ser = (tgt_mkt_cdl_ser - tgt_mkt_cdl_ser.mean())/tgt_mkt_cdl_ser.std()

    spread = normalized_src_ser - normalized_tgt_ser

    return spread

def ai_predict(*args, **kwargs):
    if len(args) != 3:
        return pd.Series([[np.nan]])

    close = args[0]
    algorithm = args[1]
    period = args[2]

    # print(f"predict {algorithm=}, {period=}: {close=}")
    predict = close * 1.1

    return pd.Series([predict[-1]])
