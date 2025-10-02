import unittest

import pandas as pd

from bt4.Constants import ExType, CandleType
from bt4.core.BulkQuoteLoader import BulkQuoteLoader




class MyTestCase(unittest.TestCase) :


    def test_something2(self) :
        print(self.test2())
        a, b, c, d, e = self.test2()
        print(f"{a=},{b=},{c=},{d=},{e=},")


    def test2(self) :
        my_list = list((1, 2, 3, 4))
        my_list.append(10)
        returns = tuple(my_list)
        print("xxxx: ", returns)
        return returns


    # def test2(self, row):
    #     returns = (1,2,3,4)
    #
    #     return returns, 10



if __name__ == '__main__' :
    unittest.main()
