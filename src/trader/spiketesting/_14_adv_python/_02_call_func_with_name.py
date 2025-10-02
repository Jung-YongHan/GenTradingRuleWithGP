import unittest

import talib
import numpy as np

class MyTestCase(unittest.TestCase) :
    def test_something(self) :
        xx = {"xxxxx": "1"}
        sampl = np.random.uniform(low=0.5, high=13.3, size=(50,))
        result = self.call_function(talib.SMA, sampl, [3],  locals())
        # print(f"{result=}")

    def call_function(self, func, data, params, local_variables):
        xx_val = local_variables['xx']
        print(f"{xx_val}")
        return func(data, *params)
        # talib.SMA(var_mkt_cdl_dfs[1440]["close"], 3)


if __name__ == '__main__' :
    unittest.main()
