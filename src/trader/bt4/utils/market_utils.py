from datetime import timedelta, datetime as dt

import pandas as pd

from bt4.Constants import CandleType, ExType, QItem
from bt4.utils.pandas_utils import create_df_with_series
from bt4.utils.python_utils import get_1min_before_dt, dt2str, split_hour_min, create_dt_at

def get_trade_start_time_of(time_dt, base_hour):
    '''
        return start of the start time based on the specific hour (e.g., 9)
        It returns an xx.xx.xxT9:00 matched with the current time.
        case1) base_hour: 9, call with 2022-03-30T15:00 --> returns 2022-03-30T09:00
        case2) base_hour: 9, call with 2022-03-31T06:00 --> returns 2022-03-30T09:00
        case3) base_hour: 9, call with 2022-03-31T09:20 --> returns 2022-03-31T09:00
    :param time_dt:
    :return:
    '''

    if time_dt.hour <= (base_hour -1) and time_dt.minute <= 59:  # for case 2 (00:00 ~ 8:59)
        adjusted_time_dt = time_dt - timedelta(days=1)
        return create_dt_at(adjusted_time_dt.year, adjusted_time_dt.month, adjusted_time_dt.day, 9, 0, 0)
    else:                                           # for case 1,3 (09:00 ~ 23:59)
        return create_dt_at(time_dt.year, time_dt.month, time_dt.day, 9, 0, 0)


def find_minutes_before_candles2(market, dataframe, desired_dt):
    need_to_discover = True
    desired_one_dt = desired_dt
    want_to_find_df = None
    total_len = len(dataframe)
    cur_idx = 0
    while need_to_discover and cur_idx < total_len:
    # while need_to_discover:
        one_min_before_dt = get_1min_before_dt(desired_one_dt)
        print(f'WARNING: Desired Quote at {dt2str(desired_one_dt)} of {market} market does not exist in '
              f'{dataframe.index.values}'
              f', so it is replaced with the previous quote at [{dt2str(one_min_before_dt)}].')
        want_to_find_df = dataframe.loc[dataframe.index == dt2str(one_min_before_dt)]
        if len(want_to_find_df) == 1:
            need_to_discover = False
        else:
            desired_one_dt = one_min_before_dt
            cur_idx = cur_idx + 1

    return want_to_find_df

## TODO: Deprecated! Need to remove after migration has been done. (stkim: 2023-01-10)
def find_minutes_before_candles(dataframe, desired_dt):
    need_to_discover = True
    desired_one_dt = desired_dt
    want_to_find_df = None
    total_len = len(dataframe)
    cur_idx = 0
    while need_to_discover and cur_idx < total_len:
    # while need_to_discover:
        one_min_before_dt = get_1min_before_dt(desired_one_dt)
        market = dataframe.head(1)['market'].values[0]
        print(f'WARNING: Desired Quote at {dt2str(desired_one_dt)} of {market} market does not exist in {dataframe.candle_date_time_kst.values}'
              f', so it is replaced with the previous quote at [{dt2str(one_min_before_dt)}].')
        want_to_find_series = dataframe[dataframe['candle_date_time_kst'] == dt2str(one_min_before_dt)]
        if len(want_to_find_series) == 1:
            want_to_find_series['candle_date_time_kst'] = dt2str(desired_dt)
            want_to_find_series.name = 'candle_date_time_kst'
            want_to_find_df = create_df_with_series(want_to_find_series)
            need_to_discover = False
        else:
            desired_one_dt = one_min_before_dt
            cur_idx = cur_idx + 1

    return want_to_find_df


def pick_market_unary_tais(ta_indicators, tai_name):
    market_tais = {}

    for market in ta_indicators:
        tais_for_each_market = ta_indicators[market]
        market_tais[market] = tais_for_each_market[tai_name][0]
    return market_tais

def pick_market_nary_tais(ta_indicators, tai_name):
    market_tais = {}

    for market in ta_indicators:
        tais_for_each_market = ta_indicators[market]
        market_tais[market] = tais_for_each_market[tai_name]
    return market_tais

'''
This method is used for LocalQuoteDispatcher in BT3
'''
def is_update_time_of_candle(cdl_type, dt_korea):
    current_hour = dt_korea.hour
    current_minute = dt_korea.minute

    if cdl_type == CandleType.DAYS:
        return True if current_hour == 8 and current_minute == 59 else False
    elif cdl_type == CandleType.HOUR4:
        return True if current_hour % 4 == 0 and current_minute == 59 else False
    elif cdl_type == CandleType.HOUR:
        return True if current_minute == 59 else False
    elif cdl_type == CandleType.MINUTES_3:
        return True if current_minute % 3 == 2 else False
    elif cdl_type == CandleType.MINUTES_5:
        return True if current_minute % 5 == 4 else False
    elif cdl_type == CandleType.MINUTES_10:
        return True if current_minute % 10 == 9 else False
    elif cdl_type == CandleType.MINUTES_15:
        return True if current_minute % 15 == 14 else False
    elif cdl_type == CandleType.MINUTES_30:
        return True if current_minute % 30 == 29 else False
    elif cdl_type == CandleType.MINUTES_1:
        return True



def is_update_time(dt_korea):
    current_hour = dt_korea.hour
    current_minute = dt_korea.minute

    is_day_update_time = True if current_hour == 8 and current_minute == 59 else False
    is_4h_update_time = True if current_hour % 4 == 0 and current_minute == 59 else False
    is_1h_update_time = True if current_minute == 59 else False
    # is_day_update_time = True if current_hour == 9 and current_minute == 0 else False
    # is_4h_update_time = True if current_hour % 4 == 1 and current_minute == 0 else False
    # is_1h_update_time = True if current_minute == 0 else False
    is_3m_update_time = True if current_minute % 3 == 2 else False
    is_5m_update_time = True if current_minute % 5 == 4 else False
    is_10m_update_time = True if current_minute % 10 == 9 else False
    is_15m_update_time = True if current_minute % 15 == 14 else False
    is_30m_update_time = True if current_minute % 30 == 29 else False
    return is_day_update_time, is_4h_update_time, is_1h_update_time, is_3m_update_time, is_5m_update_time, is_10m_update_time, is_15m_update_time, is_30m_update_time


def match_time_frame(time_dt, timeframes, zero_padding = True):
    h_prefix = '0' if (time_dt.hour < 10) and (zero_padding == True) else ''
    m_prefix = '0' if (time_dt.minute < 10) and (zero_padding == True) else ''
    hour_min_str = f'{h_prefix}{time_dt.hour}:{m_prefix}{time_dt.minute}'
    if pd.Series(timeframes).isin([hour_min_str]).any():
        timeframe_hour = time_dt.hour + 1
        if timeframe_hour == 24:
            timeframe_hour = 0
        return True, hour_min_str, timeframe_hour
    else:
        close_tf = ''
        close_tf_hour = -1
        close_tf_gap_in_min = 48 * 60
        #print(f'tf : {timeframes} at {dt2str(time_dt)}')
        for timeframe in timeframes:
            t_hour, t_min = split_hour_min(timeframe)
            t_hour = t_hour + 24 if t_hour < time_dt.hour else t_hour
            gap_in_min = (t_hour - time_dt.hour)*60 + (t_min - time_dt.minute)
            if 0 < gap_in_min < close_tf_gap_in_min:
                close_tf_gap_in_min = gap_in_min
                close_tf_hour= t_hour + 1
                close_tf = timeframe
        if close_tf_hour >= 24:
            close_tf_hour = close_tf_hour - 24
        #print(f'close_tf : {close_tf} close_tf_hour: {close_tf_hour}')
        return False, close_tf, close_tf_hour


def compute_sell_timeframes(buy_tf_list, h_gap, _0_front_padding = True):
    buy_sell_tf_dic = {}
    sell_buy_tf_dic = {}
    sell_timeframes = []
    for buy_tf in buy_tf_list:
        buy_hour, buy_min = split_hour_min(buy_tf)
        sell_h = buy_hour-h_gap if buy_hour-h_gap > 0 else 24 - abs(buy_hour-h_gap)
        sell_h = 0 if sell_h == 24 else sell_h
        sell_h_prefix = '0' if (sell_h < 10) and (_0_front_padding == True) else ''
        sell_m_prefix = '0' if (buy_min < 10) and (_0_front_padding == True) else ''
        sell_tf = f'{sell_h_prefix}{sell_h}:{sell_m_prefix}{buy_min}'
        buy_sell_tf_dic[buy_tf] = sell_tf
        sell_buy_tf_dic[sell_tf] = buy_tf
        sell_timeframes.append(sell_tf)
    return buy_sell_tf_dic, sell_buy_tf_dic, sell_timeframes


def get_hour(date):
    date_time = dt.strptime(date.strip(), "%Y-%m-%dT%H:%M:%S")
    hour = date_time.hour
    is_zero_minute = True if date_time.minute == 0 else False
    return hour, is_zero_minute


def get_xh_before_string(x, cur_date_time):
    yesterday_dt = cur_date_time - timedelta(hours=x)
    yesterday_string = dt.strftime(yesterday_dt, "%Y-%m-%dT%H:%M:%S")
    return yesterday_string


def get_yesterday_string2(base_hour, current_date_time):
    curr_day = current_date_time
    yesterday_dt = curr_day - timedelta(1)
    yesterday_dt = yesterday_dt.replace(hour=base_hour, minute=1)
    yesterday_string = dt.strftime(yesterday_dt, "%Y-%m-%dT%H:%M:%S")
    return yesterday_string


def get_yesterday_string(base_hour, current_date):
    curr_day = dt.strptime(current_date, "%Y-%m-%dT%H:%M:%S")
    yesterday_dt = curr_day - timedelta(1)
    yesterday_dt = yesterday_dt.replace(hour=base_hour, minute=1)
    yesterday_string = dt.strftime(yesterday_dt, "%Y-%m-%dT%H:%M:%S")
    return yesterday_string


def compute_vol5(quote, tmgr, exchange):
    vol = tmgr.get_unary('vol', [], CandleType.DAYS, [QItem.open, QItem.high, QItem.low], True)
    markets = quote.get_markets(exchange)
    vol5 = {}
    for market in markets:
        raw_input = vol[market + '_raw']
        market_vol5 = tmgr.call_talib_unary('sma', [5], [raw_input])
        vol5[market] = market_vol5
    return vol5

def compute_bb_rsi14(quote, tmgr, ex_type=ExType.upbit):
    market_rsis = tmgr.get_unary('rsi', [14], CandleType.DAYS, [QItem.close], return_raw=True)
    markets = quote.get_markets(ex_type)
    bb_rsi14 = {}
    for market in markets:
        raw_input = market_rsis[market + '_raw']
        market_bb_rsi14 = tmgr.call_talib_nary('bbands', [5, 2.0, 2.0, 0], [raw_input])
        bb_rsi14[market] = market_bb_rsi14
    return bb_rsi14


def handle_dummy_ex(ex_type):
    if ex_type == ExType.dummy_upbit:
        return ExType.upbit
    elif ex_type == ExType.dummy_bithumb:
        return ExType.bithumb
    elif ex_type == ExType.dummy_binance:
        return ExType.binance
    elif ex_type == ExType.dummy_binanceusdm:
        return ExType.binanceusdm
    return ex_type