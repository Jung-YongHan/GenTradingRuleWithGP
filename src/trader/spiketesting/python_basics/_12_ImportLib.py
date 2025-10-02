

# class Cal():
#     def say(self, name):
#         print(f'Hello World!, {name}')
#
#     def add(self, one, two):
#         print(f'{one} + {two}')
#         return one +two
#
# myCal = Cal()
# myCal.say('akami')
# myCal.add(3,4)

print('######################################')

# mod = importlib.import_module("bulltrader.strategy.MontlyRedistributionWithDays")
# # #방법1 : getattr 를 통해서 갖어오기
# cls = getattr(mod, 'MontlyRedistributionWithDays')()

# mod = importlib.import_module("conf.winning_session_best")
# # #방법1 : getattr 를 통해서 갖어오기
# cls = getattr(mod, 'Config')()


print('######################################')
import talib
import numpy
real_data = [54812000, 54636000, 53863000, 52660000, 52812000]

def convert_nd_array(p_list):
    c = [float(x) for x in p_list]
    return numpy.array(c)
nd_array = convert_nd_array(real_data)

output = talib.SMA(nd_array, timeperiod=5)
print(output)

method_to_call = getattr(talib, 'SMA')
result = method_to_call(nd_array, 5)
print(output)

from talib import abstract
sma = abstract.SMA
sma = abstract.Function('sma')
result = sma(nd_array, 5)
print(output)

import bt4.quote.CustomTAIndicators as cta
vol = getattr(cta, 'vol')
vol(*['abc', 'def'])

#################################################################
import bt4.quote.CustomTAIndicators as cta
import numpy as np
vwap = getattr(cta, 'vwap')
o = np.array([4201000	,	4317000	,	4322000	,	4657000	,	4586000	,	4657000	,	4889000	,	4962000	,	5021000	,	4987000	,	4894000	,	4927000	,	4983000	,	5044000	,	5222000	,	5469000	,	5533000	,	5569000	,	6346000	,	6427000	,	6610000	,	6403000])
h = np.array([4333000	,	4418000	,	4677000	,	4772000	,	4709000	,	4896000	,	4978000	,	5095000	,	5079000	,	5002000	,	4993000	,	5034000	,	5070000	,	5263000	,	5761000	,	5665000	,	5605000	,	6377000	,	6950000	,	6664000	,	6700000	,	6527000])
l = np.array([4175000	,	4311000	,	4318000	,	4519000	,	4476000	,	4651000	,	4682000	,	4956000	,	4811000	,	4837000	,	4811000	,	4885000	,	4935000	,	4993000	,	5188000	,	5459000	,	5451000	,	5515000	,	6149000	,	6322000	,	6142000	,	6282000])
c = np.array([4322000	,	4321000	,	4657000	,	4586000	,	4657000	,	4895000	,	4962000	,	5025000	,	4964000	,	4895000	,	4926000	,	5027000	,	5047000	,	5217000	,	5477000	,	5486000	,	5557000	,	6332000	,	6438000	,	6664000	,	6381000	,	6491000])
v = np.array([132.484755	,	22.78833969	,	32.2696617	,	80.5882434	,	59.35237346	,	19.99848332	,	27.32333246	,	31.72800385	,	11.89930699	,	7.03874388	,	5.36365175	,	25.16382027	,	4.343932	,	145.9178596	,	8.07043419	,	11.69369387	,	4.21265003	,	20.91828711	,	26.82608423	,	3.35282452	,	7.63078273	,	22.92663476])

before=-3
print( vwap(*[o[:before], h[:before], l[:before], c[:before], v[:before], 10]) )