import datetime
import math
import time
import unittest
import pandas as pd
import numpy as np

from bt4.Constants import ExType, CandleType
from bt4.common.ResultAnalyzer import analyze_result
from bt4.core.ReportSupport import FileReportStorage
from bt4.quote.QuoteMgr import QuoteStorageMgr
from bt4.utils.python_utils import now_dt, dt2str, str2dt
from bt3_analysis.CaseAnalysis import CaseAnalyser

pd.set_option('display.max_columns', None)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('max_colwidth', None)
import matplotlib.pyplot as plt



class MyTestCase(unittest.TestCase):

    def test_analyze_result(self):
        # df = pd.read_csv('WinningSession_Day_BeforeRefactoring_33336.csv')
        # df = pd.read_csv('../bt3_test/SuperWinningSession_Hedge_BeforeRefactoring_37960.csv')
        # df = pd.read_csv('../report\SuperWinningSession_Hedge_BeforeRefactoring_21252.csv')
        df = pd.read_csv('../WinningSession_Volume_Hedge_BeforeRefactoring_22120.csv')

        frs = FileReportStorage()
        frs.set_params('test.txt', True)
        analyze_result(df, '', frs)
        frs.close()

    def test_shape_ratio(self):
        import numpy as np
        import pandas as pd

        # Assuming you have a DataFrame 'df' with daily returns for your portfolio and the risk-free rate
        df = pd.DataFrame({
            'portfolio' : [0.01, 0.02, -0.01, -0.02, 0.01, 0.02, -0.01, -0.02, 0.01, 0.02],
            'risk_free' : [0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001]
        })

        # Calculate excess returns
        df['excess_return'] = df['portfolio'] - df['risk_free']

        # Calculate the Sharpe Ratio
        sharpe_ratio = np.mean(df['excess_return']) / np.std(df['excess_return'])

        # Annualize the Sharpe Ratio
        annual_factor = np.sqrt(252)  # Use 252 for daily returns, 52 for weekly returns, 12 for monthly returns
        sharpe_ratio_annualized = sharpe_ratio * annual_factor

        print('Sharpe Ratio (Annualized):', sharpe_ratio_annualized)


    def test_compute_profit_of_markets(self):
        df = pd.read_csv('../bt3_test/SuperWinningSession_Hedge_BeforeRefactoring_41576.csv')
        df_group = df.groupby(by=['market'], as_index=False)
        stat_result_df = pd.DataFrame()
        for market in df_group.groups:
            if market != 'SETT':
                idx = df_group.groups[market]
                market_df = df.iloc[idx, :]

                sell_df = market_df[market_df.order == 'SELL'].copy(deep=True)
                num_of_trades = len(sell_df)
                sell_df['invest_total'] = sell_df['emarket_bal'] - sell_df['profit']
                sell_df['profit_ratio'] = sell_df['profit'] / sell_df['invest_total']

                profit_sum = round(sell_df['profit'].sum(), 2)
                profit_std = round(sell_df['profit'].std(), 2)
                invest_sum = round(sell_df['invest_total'].sum(), 2)
                num_1_pcnt = round(len(sell_df.loc[sell_df['profit_ratio'] > 0.01]) / num_of_trades, 3)
                num_2_pcnt = round(len(sell_df.loc[sell_df['profit_ratio'] > 0.02]) / num_of_trades, 3)
                num_3_pcnt = round(len(sell_df.loc[sell_df['profit_ratio'] > 0.03]) / num_of_trades, 3)
                num_5_pcnt = round(len(sell_df.loc[sell_df['profit_ratio'] > 0.05]) / num_of_trades, 3)
                avg_pft_ratio = profit_sum / invest_sum
                result_dict = {}
                result_dict['market'] = [market]
                result_dict['num_of_trades'] = [num_of_trades]
                result_dict['profit_sum'] = [profit_sum]
                result_dict['invest_sum'] = [invest_sum]
                result_dict['avg_pft_ratio'] = [avg_pft_ratio]
                result_dict['profit_std'] = [profit_std]
                result_dict['num_1_pcnt'] = [num_1_pcnt]
                result_dict['num_2_pcnt'] = [num_2_pcnt]
                result_dict['num_3_pcnt'] = [num_3_pcnt]
                result_dict['num_5_pcnt'] = [num_5_pcnt]
                col_result = pd.DataFrame(result_dict, index=[market])
                stat_result_df = pd.concat([stat_result_df, col_result], axis=0)
                # print(f'{market=}, {num_of_trades=},{profit_sum=},{invest_sum=}, {avg_pft_ratio=}, {profit_std=}, '
                #       f'{num_1_pcnt=}, {num_2_pcnt=},'
                #       f'{num_3_pcnt=}, {num_5_pcnt=}')

        print(stat_result_df.head(5))




if __name__ == '__main__':
    unittest.main()
