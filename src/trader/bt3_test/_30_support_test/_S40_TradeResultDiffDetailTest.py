import unittest

from bt3_test._30_support_test.TradeResultDiffDetail import TradeResultDiffDetail


class MyTestCase(unittest.TestCase):
    def test_trade_result_diff_detail_test(self):
        src = '''d:\\40.Projects\\2022_Bulltrader3\\bulltrader3\\report\\WinningSession_Hedge_BeforeRefactoring_23884.csv'''
        tgt = '''d:\\40.Projects\\2022_Bulltrader3\\bulltrader3\\report\\WinningSession_Hedge_BeforeRefactoring_23924.csv'''

        trdd = TradeResultDiffDetail()
        trdd.compare_detail(src, tgt)




if __name__ == '__main__':
    unittest.main()
