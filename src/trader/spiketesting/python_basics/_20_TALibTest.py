import unittest
import talib
from talib import abstract
import pandas as pd

from bulltrader.quote.TAIndicatorMgr import TAIndicatorMgr
from bulltrader.utils.python_utils import convert_nd_array
import numpy
from talib import MA_Type

real_data = [54812000, 54636000, 53863000, 52660000, 52812000,54812000, 54636000, 53863000, 52660000, 52812000,54812000, 54636000, 53863000, 52660000, 52812000,54812000, 54636000, 53863000, 52660000, 52812000,54812000, 54636000, 53863000, 52660000, 52812000,54812000, 54636000, 53863000, 52660000, 52812000,54812000, 54636000, 53863000, 52660000, 52812000]

# df = pd.read_csv('./../../../data/KRW-XRP_MINUTES_1.csv', index_col='date')
df = pd.read_csv('daily_market_cache_DAYS_for_test.csv')
df.set_index(keys=['date'], drop=True, inplace=True)
print(f'columns : {df.columns}')
col1= df['open']
print(f'columns to_numpy: {col1.to_numpy()}')

close = convert_nd_array(real_data)

class MyTestCase(unittest.TestCase):

    @unittest.skip("Tested")
    def test_sma(self):
        output = talib.SMA(close, timeperiod=5)
        print(output)


    def test_ema(self):
        import bulltrader_conf.quote.quote_config as QC
        qd_params = QC.QUOTE_DISPATCHER_PARAMS
        tai = TAIndicatorMgr(qd_params)

        test_df = pd.read_csv('KRW-BTC_HOUR_short.csv')
        inputs = {'TEST': {'KRW-BTC': test_df}}
        alias = 'ema30'
        params = {'function': 'ema', 'dataframe': 'TEST', 'input': ['trade_price'], 'params': [30]}

        output = tai.call_function('KRW-BTC', inputs, alias, params)
        print(output)

    @unittest.skip("Tested")
    def test_trb(self):
        import bulltrader_conf.quote.quote_config as QC
        qd_params = QC.QUOTE_DISPATCHER_PARAMS
        tai = TAIndicatorMgr(qd_params)

        test_df = pd.read_csv('KRW-BTC_HOUR_short.csv')
        inputs = {'TEST': {'KRW-BTC': test_df}}
        alias = 'trb3'
        params = {'function': 'trb', 'dataframe': 'TEST', 'input': ['high_price', 'low_price'], 'params': [20]}

        output = tai.call_function('KRW-BTC', inputs, alias, params)
        print(output)

    @unittest.skip("Tested")
    def test_meta(self):
        print('')
        inputs = {'open': df['open'].to_numpy(), 'high': df['high'].to_numpy(), 'low': df['low'].to_numpy(), 'close': df['close'].to_numpy() }
        alias = 'ma3'
        params = {'function': 'sma', 'input': ['close'], 'params': [3]}
        self.call_function(alias, params, inputs)

        alias = 'rsi14'
        params = {'function': 'rsi', 'input': ['close'], 'params': [14]}
        self.call_function(alias, params, inputs)

        alias = 'bbands2'
        params = {'function': 'bbands', 'input': ['close'], 'params': [5, 2., 2.,0]}
        self.call_function(alias, params, inputs)

        alias = 'bbands_rsi14'
        params = {'function': 'bbands', 'input': ['rsi14'], 'params': [5, 2., 2., 0]}
        self.call_function(alias, params, inputs)

        alias = 'atr'
        params = {'function': 'atr', 'input': ['high', 'low', 'close'], 'params': [14]}
        self.call_function(alias, params, inputs)


    def call_function(self, alias, params, inputs):
        func_name = params['function']
        print(f'###############################################################')
        print(f'CALL: {alias} - function : {func_name}')
        print(f'inputs ==> {inputs}')
        result = self.call_ta_functions(alias, params, inputs)
        for result_elem_key in result:
            print(f'{result_elem_key} ==> {result[result_elem_key]}')
            if result_elem_key.endswith('_raw'):
                origin_alias = result_elem_key.replace('_raw','')
                inputs[origin_alias] = result[result_elem_key]


    def call_ta_functions(self, alias, params, inputs):
        func = abstract.Function(params['function'])
        input_name_list = params['input']
        param_list = params['params']

        input_list = []
        for input_name in input_name_list:
            input_list.append(inputs[input_name])

        result_set = {}
        result = func(*input_list, *param_list) ### CALL Function

        recent_result_set = []
        if isinstance(result, list):
            for result_elem in result:
                recent_result_set.append(result_elem[-1])
        else:
            recent_result_set.append(result[-1])

        result_set[alias] = recent_result_set
        result_set[alias+'_raw'] = result
        return result_set



if __name__ == '__main__':
    unittest.main()
