import unittest

from bt3_test._20_ga_test._migrated_35_GA_WinningSession_upbit import GA_WinningSession_upbit
from bt3_test._20_ga_test._migrated_36_GA_SuperWinningSession_upbit import GA_SuperWinningSession_upbit


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

    def test_make_testsuite_upbit(self):
        list_of_test_case_clss = [GA_SuperWinningSession_upbit, GA_WinningSession_upbit]

        list_of_test_case = []
        for testcase in list_of_test_case_clss:
            suit1 = make_suite(testcase, get_list_of_test_method(testcase))
            list_of_test_case.append(suit1)

        allsuites = unittest.TestSuite(list_of_test_case)
        unittest.TextTestRunner(verbosity=2).run(allsuites)


if __name__ == '__main__':
    unittest.main()