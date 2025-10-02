import unittest

from bt3_test._00_bt_test._01_BT_WinningSession_binance import WinningSession_binance
from bt3_test._00_bt_test._01_BT_WinningSession_upbit import WinningSession_upbit
from bt3_test._00_bt_test._02_BT_SuperWinningSession_binance import SuperWinningSession_binance
from bt3_test._00_bt_test._02_BT_SuperWinningSession_upbit import SuperWinningSession_upbit
from bt3_test._00_bt_test._03_BT_MACrossOver_binance import MACrossOver_binance
from bt3_test._00_bt_test._03_BT_MACrossOver_upbit import MACrossOver_upbit
from bt3_test._00_bt_test._04_BT_SWKim1_binance import SWKim1_binance
from bt3_test._00_bt_test._04_BT_SWKim1_upbit import SWKim1_upbit
from bt3_test._00_bt_test._05_BT_TTrading_binance import TTrading_binance
from bt3_test._00_bt_test._05_BT_TTrading_upbit import TTrading_upbit
from bt3_test._00_bt_test._07_BT_CompositeStrategy_binance import CompositeStrategy_binance
from bt3_test._00_bt_test._07_BT_CompositeStrategy_upbit import CompositeStrategy_upbit


def make_suite(testcase, tests):
    return unittest.TestSuite(map(testcase, tests))

def get_list_of_test_method(testcase):
    list_of_methods = dir(testcase)
    list_of_test_methods = []
    for method in list_of_methods:
        if method.startswith('test'):
            list_of_test_methods.append(method)

    return list_of_test_methods


class MyTestCase(unittest.TestCase):

    def test_list_of_methods(self):
        list_of_test_method = get_list_of_test_method(WinningSession_upbit)
        print(list_of_test_method)

    def test_make_testsuite_upbit(self):
        list_of_test_case_clss = [WinningSession_upbit, SuperWinningSession_upbit, MACrossOver_upbit,
                                  SWKim1_upbit, TTrading_upbit, CompositeStrategy_upbit]

        list_of_test_case = []
        for testcase in list_of_test_case_clss:
            suit1 = make_suite(testcase, get_list_of_test_method(testcase))
            list_of_test_case.append(suit1)

        allsuites = unittest.TestSuite(list_of_test_case)
        unittest.TextTestRunner(verbosity=2).run(allsuites)

    def test_make_testsuite_binance(self):
        list_of_test_case_clss = [WinningSession_binance, SuperWinningSession_binance, MACrossOver_binance,
                                  SWKim1_binance, TTrading_binance, CompositeStrategy_binance]

        list_of_test_case = []
        for testcase in list_of_test_case_clss:
            suit1 = make_suite(testcase, get_list_of_test_method(testcase))
            list_of_test_case.append(suit1)

        allsuites = unittest.TestSuite(list_of_test_case)
        unittest.TextTestRunner(verbosity=2).run(allsuites)


if __name__ == '__main__':
    unittest.main()
