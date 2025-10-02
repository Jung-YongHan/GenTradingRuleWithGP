import time

import numpy as np
import pandas as pd
from bt4.utils.python_utils import convert_nd_array

# x1 = np.arange(9.0).reshape((3, 3))
# x2 = np.arange(3.0)
# print(x1)
# print(x2)
# print(x1 - x2)
#
# values = [3.3333333, 4.444444, 5.55555, 6.3433452]
# x3 = convert_nd_array(values)
# x3_ = np.round(x3, decimals=4)
# print(x3_)

df = pd.read_csv("../../data/upbit/KRW-BTC_MINUTES_1.csv", index_col =["datetime"], parse_dates = True)
data = df["2018-03-10 00:00:00":"2018-03-13 23:59:00"]["close"].tolist()
def compute_ts_with_np(data):
    ts_param = -0.02
    source = np.array(data)
    max = np.maximum.accumulate(source)
    ts_price = max * (1+ts_param)

    print(source)
    print(ts_price)
    print(np.where(source < ts_price, 1, -1))
    ts_start_price = data[0] * (1 - ts_param)
    enter_condition = np.where(source > ts_start_price, True, False)
    ts_condition = np.where(source < ts_price, True, False)
    condition = ts_condition & enter_condition
    first_idx = np.argmax(condition)
    if first_idx == 0:
        return -1, None
    else:
        print(first_idx)
        print(source[first_idx])
        return first_idx, source[first_idx]


def compute_ts_with_list(data):
    min_range_list = data
    ts_param = -0.02
    prev_max = -1

    ts_start_price = data[0] * (1 - ts_param)
    min_max = max(data)
    if min_max > ts_start_price:
        for idx, min_close in enumerate(min_range_list):
            if prev_max < min_close :
                prev_max = min_close
            ts_price = prev_max * (1 + ts_param)
            if prev_max > ts_start_price and min_close < ts_price :
                return idx, min_close
    return -1, None

iteration = 1
answer = -1
idx = -1
start = time.time()
for i in range(iteration):
    idx, answer = compute_ts_with_np(data)
    # print(compute_ts_with_np(data))
end = time.time()

print(f'compute_ts_with_np - elapsed time: {end-start} / answer = {answer}, {idx=}')

start = time.time()
for i in range(iteration):
    idx, answer = compute_ts_with_list(data)
    # print(compute_ts_with_list(data))
end = time.time()
print(f'compute_ts_with_list - elapsed time: {end-start} / answer = {answer}, {idx=}')

