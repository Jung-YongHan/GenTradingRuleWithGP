import importlib
import math

import ciso8601
import numpy
from datetime import datetime as dt
from datetime import timedelta
import re

import numpy as np
import pandas as pd
from dateutil.parser import parse
import pytz
import datetime
import time


def dict_to_key(dict):
    return tuple(sorted(dict.items()))

def convert_list_to_tuple_of_dict(dict):
    for key in dict:
        if isinstance(dict[key], list):
            dict[key] = tuple(dict[key])
    return dict

############################################################################
## Utils for Datetime
from bt4.Constants import ExType

TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

def to_kst_time(time_dt):
    return time_dt.astimezone(tz=pytz.timezone("Asia/Seoul"))

def to_utc_time(korea_time_dt):
    return korea_time_dt - timedelta(hours=9)

def to_utc_int_timestamp(time_dt):
    str_time = dt2str(time_dt)
    if not str_time.endswith('Z'):
        str_time = str_time + 'Z'
    UNIX = int(time.mktime(ciso8601.parse_datetime(str_time).timetuple()) * 1000)
    return UNIX

def from_utc_int_timestamp(utc_int_timestamp, to_kor_timezone = True):
    utc_pdt = pd.to_datetime(utc_int_timestamp, unit='ms')
    if to_kor_timezone :
        kst_dt = (utc_pdt + pd.Timedelta(hours=9)).to_pydatetime()
        return kst_dt
    else:
        ust_dt = utc_pdt.to_pydatetime()
        return ust_dt

def get_1min_after_dt(time_dt, reset_sec=False):
    _1min_after = time_dt + timedelta(minutes=1)
    if reset_sec:
        return create_dt_at(_1min_after.year, _1min_after.month, _1min_after.day, _1min_after.hour, _1min_after.minute, 0)
    else:
        return _1min_after

def get_1min_before_dt(time_dt, reset_sec=False):
    _1min_before = time_dt - timedelta(minutes=1)
    if reset_sec:
        return create_dt_at(_1min_before.year, _1min_before.month, _1min_before.day, _1min_before.hour, _1min_before.minute, 0)
    else:
        return _1min_before

def get_1day_before_dt(time_dt, reset_sec=False):
    _1day_before = time_dt - timedelta(days=1)
    if reset_sec:
        return create_dt_at(_1day_before.year, _1day_before.month, _1day_before.day, _1day_before.hour, _1day_before.minute, 0)
    else:
        return _1day_before

def get_start_dt_of(time_dt):
    return create_dt_at(time_dt.year, time_dt.month, time_dt.day, 0, 0, 0)

def get_1day_after_dt(time_dt, reset_sec=False):
    _1day_before = time_dt + timedelta(days=1)
    if reset_sec:
        return create_dt_at(_1day_before.year, _1day_before.month, _1day_before.day, _1day_before.hour,
                            _1day_before.minute, 0)
    else:
        return _1day_before

def create_dt_at(year, month, day, hour, min, sec):
    time = datetime.time(hour, min, sec)
    date = datetime.date(year, month, day)
    return dt.combine(date, time)

def svr2local_dt(svr_time_str):
    svr_utc_datetime = parse(svr_time_str)
    return to_kst_time(svr_utc_datetime)

def split_hour_min(time_str):
    '''
    08:59
    :param time_str:
    :return:
    '''
    time_list = time_str.split(':')
    return int(time_list[0]), int(time_list[1])

def is_the_time(time_dt, hour, minute):
    return True if time_dt.hour == hour and time_dt.minute == minute else False

def is_the_time2(time_dt, base_time):
    hour, minute = split_hour_min(base_time)
    return True if time_dt.hour == hour and time_dt.minute == minute else False

def count_minutes_btw(start_dt, end_dt):
    return (end_dt - start_dt).total_seconds() / 60.0 + 1

def count_hours_btw(start_dt, end_dt):
    return (end_dt - start_dt).total_seconds() / 60.0 / 60.0 + 1

def now_dt():
    return dt.now()

def now_str_date():
    return dt.now().strftime("%Y-%m-%d")

def now_str():
    return dt.now().strftime("%Y-%m-%dT%H:%M:%S")

def str2dt(time_str):
    return dt.strptime(time_str, "%Y-%m-%dT%H:%M:%S")

def str2dt2(time_str):
    return dt.strptime(time_str, "%Y-%m-%d %H:%M:%S")

def dt2str(time_dt):
    return dt.strftime(time_dt, "%Y-%m-%dT%H:%M:%S")

def dt2str2(time_dt):
    return dt.strftime(time_dt, "%Y-%m-%d %H:%M:%S")

def dt2str_for_filename(time_dt):
    return dt.strftime(time_dt, "%Y-%m-%dT%H_%M")

def start_timing():
    return time.time()

def end_n_elapsed_time(start_time, task_name):
    end_time = time.time()
    elapsed_time = end_time - start_time
    return f'[[{task_name}]] ==> elapsed time:{elapsed_time}'

############################################################################
## Class/Function Loading
def load_class_from_module(module_name, class_name, **kwargs):
    mod = importlib.import_module(module_name)
    return getattr(mod, class_name)(**kwargs)

def load_func_from_module(module_name, func_name):
    mod = importlib.import_module(module_name)
    return getattr(mod, func_name)
############################################################################
## misc
def pattern_match(pattern_text, source):
    pattern = re.compile(pattern_text)
    m = pattern.match(source)
    return bool(m)

def convert_nd_array(p_list):
    c = [float(x) for x in p_list]
    return numpy.array(c)


def to_curr_unit_str2(krw_value, ex_type = ExType.upbit):
    if not ( krw_value is None or krw_value is math.isnan(krw_value)):
        if (isinstance(krw_value, int) or isinstance(krw_value, float)):
            krw_value_as_int = int(krw_value)
            if ex_type == None:
                return f'{krw_value_as_int:,}'
            elif ex_type == ExType.upbit:
                return f'{krw_value_as_int:,}₩'
            elif ex_type == ExType.binance or ex_type == ExType.binanceusdm:
                return f'${krw_value_as_int:,}'
        return '0'
    else:
        return '0'

def to_int_str(fiat_currency, krw_mark_flag=False):
    if fiat_currency is not None and (isinstance(fiat_currency, int) or isinstance(fiat_currency, float)):
        try:
            fiat_as_int = int(fiat_currency)
        except ValueError:
            fiat_as_int = 0
        if krw_mark_flag:
            return f'{fiat_as_int:,}₩'
        else:
            return f'{fiat_as_int:,}'
    else:
        return '0'

def str_startswith_list(str_list, match_str):
    result_list = []
    for col in str_list:
        if col.startswith(match_str):
            result_list.append(col)
    return result_list

############################################################################
## Singleton Implementation:
## Refer to https://wikidocs.net/3693
class SingletonInstance:
  __instance = None

  @classmethod
  def __getInstance(cls):
    return cls.__instance

  @classmethod
  def instance(cls, *args, **kargs):
    cls.__instance = cls(*args, **kargs)
    cls.instance = cls.__getInstance
    return cls.__instance

'''
convert string ['08:59', '09:59'] ==> int [[8, 59], [9, 59]]
'''
def conv_hr_min_str_time_to_int(hr_min_str_lst):
    hr_min_int_lst = []
    for s_time in hr_min_str_lst:
        h, m = split_hour_min(s_time)
        hr_min_int_lst.append([h, m])
    return hr_min_int_lst

def flatten(lst, return_tuple=True):
    result = []

    for item in lst:
        if isinstance(item, list) or isinstance(item, tuple):
            result.extend(flatten(item))
        else:
            result.append(item)

    ret = result
    if return_tuple:
        ret = tuple(result)
    return ret