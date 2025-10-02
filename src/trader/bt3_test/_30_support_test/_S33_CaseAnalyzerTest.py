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

def shot_plot(df):
    # df["date2"] = pd.to_datetime(df.index).strftime("%Y-%m-%d")
    # plt.plot(df['date2'], df['profit_prop_bal'], marker = ".")
    plt.plot(df.index, df['profit_prop_bal'], marker = ".")
    plt.gcf().autofmt_xdate()
    plt.show()


class MyTestCase(unittest.TestCase):

    def test_analyze_cases_best_worst_profit_lost_prop(self) :
        ca = CaseAnalyser()

        # t_result_df = pd.read_csv('../bt3_test/SuperWinningSession_Hedge_BeforeRefactoring_37960.csv', index_col = 0)
        t_result_df = pd.read_csv('SuperWinningSession_TAI_Hedge_(~20231105).csv', index_col = 0)

        state_date_str = '2018-10-01 09:00:00'
        period_days = [30 * n for n in [1,2,3,4,5,6,12,24]]

        for period_day in period_days:
            print(f"##### Period : {period_day} ###########################################")
            last_date_str = t_result_df.tail(1)['date'].item()
            from datetime import datetime as dt
            last_date_dt = dt.strptime(last_date_str, "%Y-%m-%d %H:%M:%S")
            bt_dates = pd.date_range(state_date_str, last_date_dt-datetime.timedelta(days=period_day), freq = 'D')
            best_plp = 0
            best_result = {}
            worst_plp = 100
            worst_result = {}
            for bt_date in bt_dates:
                result_dic = ca.analyze_case(ExType.upbit, t_result_df, bt_date, period_day, False)
                plp = result_dic['profit_loss_prop']
                # print(f'back_testing : {bt_date} - plp : {plp}')
                if plp > best_plp:
                    # print(f'best plp recording ! (back_testing) : {bt_date} - plp {plp}')
                    best_plp = plp
                    best_result = result_dic

                if plp < worst_plp:
                    # print(f'worst plp recording ! (back_testing) : {bt_date} - plp {plp}')
                    worst_plp = plp
                    worst_result = result_dic

            print(f'##' * 50 )
            self.print_result('best_result', best_result)

            print(f'--'*50)
            self.print_result('worst_result', worst_result)
        time.sleep(1)

    def print_result(self, msg, result):
        print(f"{msg} : period ({result['start_date_pdt']}~{result['end_date_pdt']})")
        print(f"  # of wins : {result['#ofwins']}")
        print(f"  # of loses : {result['#ofloses']}")
        print(f"  winning_rate : {result['winning_rate']:.3f}")
        profit_ratio = (result['sum_win_amount'] + result['sum_lost_amount'])/ result['init_bal']
        print(f"  profit ratio : {profit_ratio:.3f}")
        win_profit = result['sum_win_amount'] / result['init_bal']
        lost_profit= result['sum_lost_amount'] / result['init_bal']
        print(f"  win_profit : {win_profit:.3f} (win_amount={int(result['sum_win_amount']):,}, start={int(result['init_bal']):,})")
        print(f"  avg win profit_prop  : {result['avg_win_profit_prop']:.3f}")
        print(f"  lost_profit: {lost_profit:.3f}(lost_amount={int(result['sum_lost_amount']):,}, start={int(result['init_bal']):,})")
        print(f"  avg lost profit_prop : {result['avg_lost_profit_prop']:.3f}")

        print(f"  avg_win_amount : {int(result['avg_win_amount']):,}")
        print(f"  avg_lost_amount : {int(result['avg_lost_amount']):,}")
        print(f" # average profit-loss amount: {result['avg_win_profit_prop']:.3f}")
        print(f" # profit-loss proportion: {result['profit_loss_prop']:.3f} (avg_win_profit_prop={result['avg_win_profit_prop']:.3f},avg_lose_profit_prop={result['avg_lost_profit_prop']:.3f})")


    def test_analyze_cases_worst_mdd(self) :
        ca = CaseAnalyser()

        # t_result_df = pd.read_csv('../bt3_test/SuperWinningSession_Hedge_BeforeRefactoring_37960.csv', index_col = 0)
        t_result_df = pd.read_csv('SuperWinningSession_TAI_Hedge_(~20231105).csv', index_col = 0)
        state_date_str = '2020-01-01 00:00:00'
        period_days = 30*6

        last_date_str = t_result_df.tail(1)['date'].item()
        from datetime import datetime as dt
        last_date_dt = dt.strptime(last_date_str, "%Y-%m-%d %H:%M:%S")
        bt_dates = pd.date_range('2018-10-01 09:00:00', last_date_dt-datetime.timedelta(days=period_days), freq = 'D')
        worst_mdd = 100
        worst_result = {}
        for bt_date in bt_dates:
            result_dic = ca.analyze_case(ExType.upbit, t_result_df, bt_date, period_days, False)
            cur_mdd = result_dic['s_mdd']
            print(f'back_testing : {bt_date} - mdd {cur_mdd}')
            if cur_mdd < worst_mdd:
                print(f'worst case recording ! (back_testing) : {bt_date} - mdd {cur_mdd}')
                worst_mdd = cur_mdd
                worst_result = result_dic

        print(f'worst_mdd : {worst_mdd}')
        print(f'worst_result : {worst_result}')


    def test_analyze_cases1(self) :
        ca = CaseAnalyser()

        # t_result_df = pd.read_csv('../bt3_test/SuperWinningSession_Hedge_BeforeRefactoring_37960.csv', index_col = 0)
        t_result_df = pd.read_csv('SuperWinningSession_TAI_Hedge_(~20231105).csv',
                                  index_col = 0)
        state_date_str = '2018-10-01 00:00:00'
        period_days = 30*12*5

        result_dic = ca.analyze_case(ExType.upbit, t_result_df, state_date_str, period_days, True)
        print(result_dic)
        time.sleep(1)


    def test_analyze_cases0(self):
        import warnings
        warnings.filterwarnings("ignore", category = DeprecationWarning)

        # df = pd.read_csv('../bt3_test/SuperWinningSession_Hedge_BeforeRefactoring_37960.csv', index_col = 0)
        df = pd.read_csv('SuperWinningSession_TAI_Hedge(~20231105).csv', index_col = 0)

        window_period_d = 30*12*6
        # window_period_d = 30*12
        df = df.drop(['desc'], axis = 1)
        df = df.set_index(['date'], drop=True)
        df.index = pd.to_datetime(df.index)

        # start_date = df.head(1).index.item()
        start_date = '2018-10-01 00:00:00'
        # start_date = '2020-01-01 00:00:00'
        start_date_pdt = pd.to_datetime(start_date)
        end_date_pdt = start_date_pdt + pd.Timedelta(days = window_period_d)
        df_end = df.tail(1).index
        if end_date_pdt > df_end.item():
            print(f'@@ Required End {end_date_pdt} is passed from the last date {df_end.item()}, so it is set to be {df_end.item()}.')
            end_date_pdt = pd.to_datetime(df_end.item())

        df = df[start_date_pdt : end_date_pdt]
        df = df.reset_index()

        ################################################################
        init_bal = df.head(1)['evaluated_balance'][0]
        sell_df = df.loc[df['order'] == 'SELL']
        # sell_df = sell_df.loc[sell_df['market'] == 'KRW-BTC']
        sell_df['inv'] = sell_df['evaluated_market_balance'] - sell_df['profit']
        sell_df['profit_prop'] = sell_df['profit'] / sell_df['inv']
        sell_df['profit_prop_bal'] = sell_df['evaluated_balance'] / init_bal

        ################################
        ## sorting KRW-BTC, KRW-ETH, KRW-XRP for exact evaluation
        priority_dict = {
            'KRW-BTC' : 1,
            'KRW-ETH' : 2,
            'KRW-XRP' : 3
        }
        sell_df['priority'] = sell_df['market'].map(priority_dict)
        sell_df = sell_df.sort_values(by=['date', 'priority'])
        # sell_df = sell_df.drop_duplicates(['date'], keep='last')
        sell_df = sell_df.set_index(['date'], drop=True)
        #######################
        print(f'#### Worst/Best Consecutive Trading Analysis ({start_date_pdt} ~ {end_date_pdt}, {window_period_d} days) ####')
        print(f'## Win/Lose Analysis')
        lose_df = sell_df.loc[sell_df['profit'] < 0]
        sum_lost_amount = lose_df['profit'].sum()
        print(f' # of loses : {len(lose_df)} tradings')
        print(f"   - lost amount : 1 times ({int(sum_lost_amount): ,}) ")
        win_df = sell_df.loc[sell_df['profit'] > 0]
        sum_win_amount = win_df['profit'].sum()
        print(f' # of wins : {len(win_df)} tradings (winning rate = {len(win_df) / (len(win_df) + len(lose_df)):.3f})')
        print(f"   - won amount : {sum_win_amount/abs(sum_lost_amount):.2f} times ({int(sum_win_amount):,})")

        print(f'----------------------------------------------------------------------')
        print(f'## Worst/Best Consecutive Tradings')
        max_lose, duration, l_profit, l_consec_start_bal = self.handle_consecutive_trading(sell_df, False)
        print(f' # max consecutive loses : {abs(max_lose)} tradings')
        print(f'  - duration : {duration}')
        print(f'  - profit   : {l_profit/l_consec_start_bal : .3f} (profit: {int(l_profit):,}, start: {int(l_consec_start_bal):,})')

        max_win, duration, w_profit, w_consec_start_bal = self.handle_consecutive_trading(sell_df, True)
        print(f' # max consecutive win : {abs(max_win)} tradings')
        print(f'  - duration : {duration}')
        print(f"  - profit   : {w_profit/w_consec_start_bal : .3f} (profit: {int(w_profit):,}, start: {int(w_consec_start_bal):,})")

        print(f'======================================================================')
        # s_init_bal, s_last_bal, s_mdd, s_period = self.analyze_sell(sell_df)

        sett_df = df.loc[df['market'] == 'SETT']
        s_init_bal, s_last_bal, s_mdd, s_period = self.analyze_sell(sett_df)

        print(f'#### Comparison between buy & hold ({s_period}) (settlement a day) ####')
        print(f' # strategy #')
        print(f'  - init_bal : 100 ({int(s_init_bal):,})')
        print(f'  - last_bal : {(s_last_bal / s_init_bal)*100:.2f} ({int(s_last_bal):,})')
        print(f'  - gap : {(s_last_bal / s_init_bal)*100 - 100:.3f} ({s_last_bal - s_init_bal:,.2f})')
        print(f'  - mdd : {s_mdd:.3f}%')

        init_bal, last_bal, mdd, period = self.analyze_with_bnh(sell_df, ['KRW-BTC', 'KRW-ETH', 'KRW-XRP'])
        print(f' # buy & hold  #')
        print(f'  - init_bal : {init_bal}')
        print(f'  - last_bal : {int(last_bal):,}')
        print(f'  - gap : {last_bal-init_bal:.2f} ({last_bal/init_bal:.3f} times)')
        print(f'  - mdd : {mdd:.3f}%')
        time.sleep(1)

    def analyze_sell(self, sell_df):
        start_pdt = sell_df.head(1).index.item()
        end_pdt = sell_df.tail(1).index.item()
        s_period = f'{start_pdt} ~ {end_pdt}'

        s_init_bal = sell_df.head(1)['evaluated_balance'].item() - sell_df.head(1)['profit'].item()
        s_last_bal = sell_df.tail(1)['evaluated_balance'].item()

        row_idx = 1
        def compute_prev_max(row) :
            nonlocal row_idx
            nonlocal s_init_bal
            prev_max = sell_df.iloc[0 : row_idx]['evaluated_balance'].max()
            if s_init_bal > prev_max :
                prev_max = s_init_bal
            row_idx = row_idx + 1
            return prev_max

        sell_df["prev_max_bal"] = sell_df.apply(compute_prev_max, axis = 1)
        sell_df["dd"] = (sell_df["evaluated_balance"] / sell_df["prev_max_bal"] - 1) * 100
        s_mdd = sell_df["dd"].min()
        return s_init_bal, s_last_bal, s_mdd, s_period

    def analyze_with_bnh(self, sell_df, markets):
        qsm = QuoteStorageMgr(markets, [CandleType.DAYS])

        quote_dfs = qsm.load_past_quote(ExType.upbit, CandleType.DAYS)
        start_pdt = sell_df.head(1).index.item()
        adjusted_start_pdt = start_pdt - pd.Timedelta(days=1)
        end_pdt = sell_df.tail(1).index.item()

        init_bal = 100
        bal_sum_df = pd.DataFrame()
        for market in quote_dfs:
            quote_df = quote_dfs[market]
            ranged_quote_df = quote_df[adjusted_start_pdt:end_pdt]

            ranged_quote_df['prev_close'] = ranged_quote_df['close'].shift(1)
            ranged_quote_df['gap_prop'] = (ranged_quote_df['close']-ranged_quote_df['prev_close']) / ranged_quote_df['prev_close']
            ranged_quote_df = ranged_quote_df[start_pdt:end_pdt]

            if bal_sum_df.empty:
                bal_sum_df.index = ranged_quote_df.index

            prev_bal = init_bal / len(quote_dfs)
            def compute_bal(row):
                nonlocal prev_bal
                prev_bal = prev_bal * (1+row['gap_prop'])
                return prev_bal
            ranged_quote_df['bal'] = ranged_quote_df.apply(compute_bal, axis=1)
            bal_sum_df[market] = ranged_quote_df['bal']
            # print(ranged_quote_df.head(10))

        bal_sum_df['bal_sum'] = 0
        for market in quote_dfs:
            bal_sum_df['bal_sum'] = bal_sum_df['bal_sum'] + bal_sum_df[market]

        row_idx = 1
        def compute_prev_max(row) :
            nonlocal row_idx
            prev_max = bal_sum_df.iloc[0 : row_idx]['bal_sum'].max()
            row_idx = row_idx + 1
            return prev_max
        bal_sum_df["prev_max_bal"] = bal_sum_df.apply(compute_prev_max, axis = 1)

        bal_sum_df["dd"] = (bal_sum_df["bal_sum"] / bal_sum_df["prev_max_bal"] - 1 ) * 100

        # print(f'mdd : {bal_sum_df["dd"].min()}')
        # print(bal_sum_df.head(10))
        last_bal = bal_sum_df.tail(1)["bal_sum"].item()
        mdd = bal_sum_df["dd"].min()
        period = f'{start_pdt} ~ {end_pdt}'

        return init_bal, last_bal, mdd, period


    def handle_consecutive_trading(self, sell_df, is_win):
        sell_df['prev_profit_prop'] = sell_df['profit_prop'].shift(1)

        is_win = is_win
        consecutive = 0

        def compute_consecutive_winlose(row) :
            nonlocal consecutive
            nonlocal is_win
            if is_win :
                if row['prev_profit_prop'] > 0 and row['profit_prop'] > 0 :
                    consecutive = consecutive + 1
                else :
                    consecutive = 0
            else :
                if row['prev_profit_prop'] < 0 and row['profit_prop'] < 0 :
                    consecutive = consecutive - 1
                else :
                    consecutive = 0
            return consecutive

        if is_win:
            sell_df["consecutive_win"] = sell_df.apply(compute_consecutive_winlose, axis = 1)
            idx = list(np.where(sell_df["consecutive_win"] == sell_df["consecutive_win"].max()))[0].tolist()[0]
            max_win_df = sell_df.loc[sell_df["consecutive_win"] == sell_df["consecutive_win"].max()]
            max_win = max_win_df["consecutive_win"][0].item()
            consecutive_win_df = sell_df.iloc[idx - max_win : idx]
            cwin_start_pdt = pd.to_datetime(consecutive_win_df.head(1).index.item())
            cwin_end_pdt = pd.to_datetime(consecutive_win_df.tail(1).index.item())
            time_gap = cwin_end_pdt - cwin_start_pdt

            start_df = consecutive_win_df.loc[consecutive_win_df.index == cwin_start_pdt]
            start_ser = start_df.iloc[-1]
            bal_at_start = start_ser['evaluated_balance'].item() - start_ser['profit'].item()
            return max_win, f'{time_gap.days} days ({cwin_start_pdt} ~ {cwin_end_pdt})',consecutive_win_df['profit'].sum(), bal_at_start

        else:
            sell_df["consecutive_lose"] = sell_df.apply(compute_consecutive_winlose, axis = 1)
            idx = list(np.where(sell_df["consecutive_lose"] == sell_df["consecutive_lose"].min()))[0].tolist()[0]
            max_lose_df = sell_df.loc[sell_df["consecutive_lose"] == sell_df["consecutive_lose"].min()]
            max_lose = max_lose_df["consecutive_lose"][0].item()
            consecutive_lose_df = sell_df.iloc[idx + max_lose : idx]
            close_start_pdt = pd.to_datetime(consecutive_lose_df.head(1).index.item())
            close_end_pdt = pd.to_datetime(consecutive_lose_df.tail(1).index.item())
            time_gap = close_end_pdt - close_start_pdt

            start_df = consecutive_lose_df.loc[consecutive_lose_df.index == close_start_pdt]
            start_ser = start_df.iloc[-1]
            bal_at_start = start_ser['evaluated_balance'].item() - start_ser['profit'].item()
            return max_lose, f'{time_gap.days} days ({close_start_pdt} ~ {close_end_pdt})', consecutive_lose_df['profit'].sum(), bal_at_start
        return -1



if __name__ == '__main__':
    unittest.main()
