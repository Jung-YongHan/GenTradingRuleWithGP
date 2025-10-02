import talib
import numpy
from talib import MA_Type

# c = numpy.random.randn(100)
# c = numpy.array([54812000, 54636000, 53863000, 52660000, 52812000, 55017000,55361000])

real_data = [54812000, 54636000, 53863000, 52660000, 52812000]

def convert_nd_array(p_list):
    c = [float(x) for x in p_list]
    return numpy.array(c)

def compute_sma(nd_array, is_sma=True):
    if is_sma:
        output = talib.SMA(nd_array, timeperiod=5)
    else:
        output = talib.EMA(nd_array, timeperiod=5)

    print(output)

    # print(f'ma:{output}')
    # upper, middle, lower = talib.BBANDS(c, timeperiod=5, matype=MA_Type.T3)
    # print(f'bband: upper={upper}, middle={middle}, lower={lower}')
    return output[-1]

c = convert_nd_array(real_data)
ma = compute_sma(c, False)
print(f'data={c}, ma={ma}')

real_data.append(55017000)
c = convert_nd_array(real_data)
ma = compute_sma(c)
print(f'data={c}, ma={ma}')

real_data.append(55361000)
c = convert_nd_array(real_data)
ma = compute_sma(c)
print(f'data={c}, ma={ma}')

real_data[-1] = 55363000
c = convert_nd_array(real_data)
ma = compute_sma(c)
print(f'data={c}, ma={ma}')

rsi = talib.RSI(c, timeperiod=5)
print(f'rsi={rsi}')

# # this is the library function
# k, d = talib.STOCHRSI(c)
# print(f'STOCHRSI k={k}, d={d}')
#
# k, d = talib.STOCHF(rsi, rsi, rsi)
# print(f'STOCHF of rsi({rsi}) k={k}, d={d}')
#
# # you might want this instead, calling STOCH
# rsi = talib.RSI(c)
# k, d = talib.STOCH(rsi, rsi, rsi)
# print(f'STOCHF of rsi({rsi}) k={k}, d={d}')

print('-----------------------------------------------------------')
# close = numpy.random.random(100)

