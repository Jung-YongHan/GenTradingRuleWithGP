import unittest
from os.path import dirname, join

import matplotlib.pyplot as plt

from bt4.common.ResultAnalyzer import analyze_result
from bt4.core.ReportSupport import FileReportStorage
from bt4.utils.python_utils import str2dt, str2dt2
from bt4.utils.stat.RuleAnalyzer import RuleAnalyzer
import pandas as pd


def generate_result_file_from_new_bt_date(df, start_dt, end_dt):
    df = df.set_index(keys = ["date"])
    df.index = pd.to_datetime(df.index)

    new_df = df[start_dt:end_dt].copy(deep = True)

    sell_rows_df = new_df[new_df['order'] == 'SELL']
    sell_rows_to_remove_df = sell_rows_df[~sell_rows_df['origin_id'].isin(new_df['id'])]

    if not sell_rows_to_remove_df.empty :
        latest_date = sell_rows_to_remove_df.index.max()
        new_df = new_df[new_df.index > latest_date]

    new_df = new_df.reset_index()
    return new_df


class MyTestCase(unittest.TestCase) :


    def test_generate_result_file_from_update_bt_date(self):
        stgy_name = "aa"
        file_name = "2024-11-11T21_41_dummy(18304).csv"
        file_path = join(dirname(dirname(dirname(__file__))), f"./report/{file_name}")
        df = pd.read_csv(file_path)

        frs = FileReportStorage()
        frs.set_params('test.txt', True)
        analyze_result(df, stgy_name, None, frs)
        frs.close(df)

        key_results = frs.get_key_results()
        for rslt_key in key_results :
            print(f"{rslt_key} => {key_results[rslt_key]}")

        start_str = "2018-07-24 18:00:00"
        end_str = "2021-04-30 1:00:00"
        start_dt = str2dt2(start_str)
        end_dt = str2dt2(end_str)

        new_dt = generate_result_file_from_new_bt_date(df, start_dt, end_dt)

        file_name2 = "gened_df.csv"
        file_path2 = join(dirname(dirname(dirname(__file__))), f"./report/{file_name2}")
        new_dt.to_csv(file_path2)
        frs2 = FileReportStorage()
        frs2.set_params('test.txt', True)
        analyze_result(new_dt, stgy_name, None, frs2)
        frs2.close(new_dt)

        key_results2 = frs2.get_key_results()
        for rslt_key in key_results2:
            print(f"{rslt_key} => {key_results[rslt_key]}")



    def test_rule_analyzer(self):

        stgy_name = "aa"
        file_name = "2024-11-11T21_41_dummy(18304).csv"
        file_path = join(dirname(dirname(dirname(__file__))), f"./report/{file_name}")
        df = pd.read_csv(file_path)

        frs = FileReportStorage()
        frs.set_params('test.txt', True)
        analyze_result(df, stgy_name, None, frs)
        frs.close(df)

        key_results = frs.get_key_results()
        for rslt_key in key_results:
            print(f"{rslt_key} => {key_results[rslt_key]}")

        self.assertEquals(key_results["mdd"], '-50.46' )



    def test_rule_analyzer2(self) :
        import warnings

        warnings.filterwarnings("ignore", category = DeprecationWarning)

        ra = RuleAnalyzer()

        file_name = "2024-11-11T21_41_dummy(18304).csv"
        file_path = join(dirname(dirname(dirname(__file__))), f"./report/{file_name}")

        print(file_path)
        win_sell_tai_df, win_buy_tai_df, lose_sell_tai_df, lose_buy_tai_df = ra.analyze_rule_contribution2(file_path)
        ws_sum_ta_ser = self.__extract_ta_columns__(win_sell_tai_df).sum(axis=0)
        print(ws_sum_ta_ser.head())

        wb_sum_ta_ser = self.__extract_ta_columns__(win_buy_tai_df).sum(axis = 0)
        print(wb_sum_ta_ser.head())

        ls_sum_ta_ser = self.__extract_ta_columns__(lose_sell_tai_df).sum(axis = 0)
        print(ls_sum_ta_ser.head())

        lb_sum_ta_ser = self.__extract_ta_columns__(lose_buy_tai_df).sum(axis = 0)
        print(lb_sum_ta_ser.head())

        fig = plt.figure()
        fig.suptitle(f'Rule Analysis', fontsize = 12)
        ax1 = fig.add_subplot(2, 2, 1)

        bar_container = ax1.bar(ws_sum_ta_ser.index, ws_sum_ta_ser)
        ax1.set_title('Win SELL - TA')
        ax1.axhline(y = 0, color = 'black', linestyle = '-')
        ax1.bar_label(bar_container, label_type='center')
        ax1.set_xlabel('TA')
        ax1.set_ylabel("#")

        ax2 = fig.add_subplot(2, 2, 2)
        bar_container = ax2.bar(wb_sum_ta_ser.index, wb_sum_ta_ser)
        ax2.set_title('Win BUY - TA')
        ax2.axhline(y = 0, color = 'black', linestyle = '-')
        ax2.bar_label(bar_container, label_type='center')
        ax2.set_xlabel('TA')
        ax2.set_ylabel("#")

        ax3 = fig.add_subplot(2, 2, 3)
        bar_container = ax3.bar(ls_sum_ta_ser.index, ls_sum_ta_ser)
        ax3.set_title('LOSE SELL - TA')
        ax3.axhline(y = 0, color = 'black', linestyle = '-')
        ax3.bar_label(bar_container, label_type='center')
        ax3.set_xlabel('TA')
        ax3.set_ylabel("#")

        ax4 = fig.add_subplot(2, 2, 4)
        bar_container = ax4.bar(lb_sum_ta_ser.index, lb_sum_ta_ser)
        ax4.set_title('LOSE BUY - TA')
        ax4.axhline(y = 0, color = 'black', linestyle = '-')
        ax4.bar_label(bar_container, label_type='center')
        ax4.set_xlabel('TA')
        ax4.set_ylabel("#")

        fig.tight_layout(pad = 1.0)
        plt.show()

    def test_rule_support_confidence(self) :
        import warnings

        warnings.filterwarnings("ignore", category = DeprecationWarning)

        ra = RuleAnalyzer()
        # file_name = "2023-11-14T21_21_SuperWinningSession_TAI_Hedge(26224).csv" ## TAI
        # file_name = "2023-11-15T16_00_SuperWinningSession_Asym_Hedge(26576).csv"  ## Asymmetry SWS (1) - MA or MA
        # file_name = "2023-11-14T21_55_SuperWinningSession_Asym_Hedge(13672).csv"  ## Asymmetry SWS (3) - BBUpper
        # file_name = "2023-11-14T22_43_SuperWinningSession_Asym_Hedge(18320).csv"  ## Asymmetry SWS (6) - VWAP & MA3
        # file_name = "2023-11-14T22_55_SuperWinningSession_Asym_Hedge(9824).csv"    ## Asymmetry SWS (7) - VWAP
        # file_name = "2023-11-16T15_28_SuperWinningSession_Asym_Hedge(17720).csv"  # Asymmetry SWS (8)
        # file_name = "2023-11-16T15_45_SuperWinningSession_Asym_Hedge(19920).csv"  # Asymmetry SWS (9)
        # file_name = "2023-11-19T18_56_SuperWinningSession_Asym_Hedge(27416).csv"  # Asymmetry SWS (10)
        # file_name = "2023-11-19T19_06_SuperWinningSession_Asym_Hedge(13292).csv"  # Asymmetry SWS (11)
        file_name = "2023-11-19T19_19_SuperWinningSession_Asym_Hedge(20420).csv"  # Asymmetry SWS (12)

        file_path = join(dirname(dirname(dirname(__file__))), f"./report/{file_name}")

        print(file_path)
        win_sell_tai_df, win_buy_tai_df, lose_sell_tai_df, lose_buy_tai_df = ra.analyze_rule_contribution2(file_path)

        ra.analyze_ta_support_confidence(win_sell_tai_df, "WIN SELL", True)
        plt.show()

        ra.analyze_ta_support_confidence(win_buy_tai_df, "WIN BUY", True)
        plt.show()

        ra.analyze_ta_support_confidence(lose_sell_tai_df, "LOSE SELL", True)
        plt.show()

        ra.analyze_ta_support_confidence(lose_buy_tai_df, "LOSE BUY", True)
        plt.show()


    def __extract_ta_columns__(self, trade_df):
        tas = []
        tas_rename_dic = {}
        for ta in trade_df.columns :
            if ta.startswith("ta_"):
                tas.append(ta)
                tas_rename_dic[ta] = ta.replace("ta_", "")

        return trade_df[tas].rename(columns = tas_rename_dic)


if __name__ == '__main__' :
    unittest.main()
