import unittest
from bt4.utils.mylog import init_log
import bt4.utils.mylog as log_module

from bt3_test._00_bt_test._30_BT_MultiProcessor_MultiStgy import MultiProcessor_MultiStgy
from bt3_test._00_bt_test._31_BT_MultiProcessor_CompositeStgy import MultiProcessor_CompositeStgy
from bt3_test._00_bt_test._32_BT_MultiProcessor_MultiStgy_Hdg import MultiProcessor_MultiStgy_Hdg
from bt3_test._00_bt_test._33_BT_MultiProcessor_CompositeStgy_Hdg import MultiProcessor_CompositeStgy_Hdg

log_module.log_mode = 'simulator'
log = init_log()


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
        list_of_test_case_clss = [MultiProcessor_MultiStgy, MultiProcessor_CompositeStgy, MultiProcessor_MultiStgy_Hdg,
                                  MultiProcessor_CompositeStgy_Hdg]

        list_of_test_case = []
        for testcase in list_of_test_case_clss:
            suit1 = make_suite(testcase, get_list_of_test_method(testcase))
            list_of_test_case.append(suit1)

        allsuites = unittest.TestSuite(list_of_test_case)
        unittest.TextTestRunner(verbosity=2).run(allsuites)


if __name__ == '__main__':
    unittest.main()

