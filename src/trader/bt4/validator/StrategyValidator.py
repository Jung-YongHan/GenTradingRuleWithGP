
import pandas as pd
from os.path import dirname, join
import sys
from bt4.utils.pandas_utils import sort_df_with_multi_index, get_date_range
from bt4.validator.ValidationConfig import STGY_VAL_ORACLE_FILE, STGY_VAL_CONFIG_HOME
from bt4.utils.pandas_utils import get_first_row, get_last_row

def _log_(log_list, log):
    print(log)
    log_list.append(log)


class StrategyValidator:

    def __init__(self, config_name):
        self.config_name = config_name
        self.oracle_cols = ['candle_date_time_kst', 'order', 'market','price']
        self.test_cols = ['date', 'order', 'market','price']

        self.load_validation_sheet()
        self.log_list = []

    def load_validation_sheet(self):
        root_dir = dirname(dirname(dirname(__file__)))
        file_name = join(root_dir, STGY_VAL_ORACLE_FILE)

        with pd.ExcelFile(file_name) as xlsx:
            self.stgy_oracle_df = xlsx.parse(self.config_name)
            self.stgy_oracle_df = self.stgy_oracle_df[self.oracle_cols].dropna()


    def start_validation(self):
        config_path = f'{STGY_VAL_CONFIG_HOME}.{self.config_name}'
        sys.argv = ['BullTraderMain', 'simulator', '-conf', config_path]
        import bt4.exec.BullTraderMain as bm
        simul_result = bm.main_depreciated(sys.argv)
        print(f'simul_result : {simul_result}')

        # simul_result = 'D:\\40.Projects\\2021_Crypto\\auto_trader_python\\report/WinningSession_Day_BeforeRefactoring.csv'
        return simul_result

    def validate_result(self, simul_result_loc):
        print('#################### Simulation Result')
        test_df = pd.read_csv(simul_result_loc)
        test_df = test_df[self.test_cols]
        test_df = test_df.drop(test_df[test_df['order'] == 'SETT'].index)
        sort_df_with_multi_index(test_df, ['date', 'market', 'order'])
        print(test_df.head(20))
        print(test_df.columns)

        print('#################### Strategy Oracle')
        sort_df_with_multi_index(self.stgy_oracle_df, ['candle_date_time_kst', 'market', 'order'])
        print(self.stgy_oracle_df.head(20))
        print(self.stgy_oracle_df.columns)

        self.validate_market_timing_precision(self.stgy_oracle_df, test_df)
        self.validate_price_precision(self.stgy_oracle_df, test_df)
        return self.log_list

    def validate_market_timing_precision(self, stgy_oracle_df, test_df):
        _log_(self.log_list, '######################### validate_market_timing_precision')
        selected_oracle_df_for_test, test_end_date_str, test_start_date_str = self.extract_stgy_oracle_in_test(stgy_oracle_df, test_df)

        result = selected_oracle_df_for_test.index.isin(test_df.index)
        excluded_market_timing = selected_oracle_df_for_test.index[result == False].tolist()
        num_ex_mkt_timing = len(excluded_market_timing)
        num_sel_oracle_mkt_timing = len(selected_oracle_df_for_test)
        _log_(self.log_list, f'Market Timing Precision : {((1 - num_ex_mkt_timing/num_sel_oracle_mkt_timing)*100)} %')
        _log_(self.log_list, f'in Oracle : {num_sel_oracle_mkt_timing} market orders from {test_start_date_str} to {test_end_date_str}')
        _log_(self.log_list, f'in Test   : {num_ex_mkt_timing} market orders from {test_start_date_str} to {test_end_date_str}')
        _log_(self.log_list, str(excluded_market_timing))

    def validate_price_precision(self, stgy_oracle_df, test_df):
        _log_(self.log_list, '######################### validate_price_precision')
        selected_oracle_df_for_test, test_end_date_str, test_start_date_str = self.extract_stgy_oracle_in_test(stgy_oracle_df, test_df)

        permitted_price_boundaries = [0., 0.01, 0.02 ]
        result = selected_oracle_df_for_test.index.isin(test_df.index)
        matched_market_timing = selected_oracle_df_for_test.index[result == True].tolist()
        num_of_matched_market_timing = len(matched_market_timing)
        _log_(self.log_list, f'selected oracle: {num_of_matched_market_timing}')
        if num_of_matched_market_timing > 0:
            price_oracle = selected_oracle_df_for_test[matched_market_timing].settled_price
            _log_(self.log_list, price_oracle)
            _log_(self.log_list, 'test oracle')
            if len(test_df[matched_market_timing]) > 0:
                price_test = test_df[matched_market_timing].settled_price
                _log_(self.log_list, price_test)

                for p_boundary in permitted_price_boundaries:
                    result = (price_oracle >= price_test * (1 - p_boundary)) and (price_oracle <= price_test * (1 + p_boundary))
                    precision = len(result == True) / len(result)
                    _log_(self.log_list, f'Price Precision: {precision} % for {p_boundary} price range')

            else:
                _log_(self.log_list, f'No Matched Market Timing!!')
                _log_(self.log_list, f'in Test : {test_df.index}')
                _log_(self.log_list, f'in Oracle : {test_df.index}')
        else:
            _log_(self.log_list, f'No Matched Market Timing!!')
            _log_(self.log_list, f'in Test : {test_df.index}')
            _log_(self.log_list, f'in Oracle : {test_df.index}')

    def extract_stgy_oracle_in_test(self, stgy_oracle_df, test_df):
        test_start_date_str = get_first_row(test_df).date[0]
        test_end_date_str = get_last_row(test_df).date[0]
        _log_(self.log_list, f'test : {test_start_date_str} ~ {test_end_date_str}')
        oracle_start_date_str = get_first_row(stgy_oracle_df).candle_date_time_kst[0]
        oracle_end_date_str = get_last_row(stgy_oracle_df).candle_date_time_kst[0]
        _log_(self.log_list, f'oracle : {oracle_start_date_str} ~ {oracle_end_date_str}')
        selected_oracle_df_for_test = get_date_range(stgy_oracle_df, 'candle_date_time_kst', test_start_date_str,
                                                     test_end_date_str)
        # _log_(self.log_list, "selected_oracle_df_for_test ----------------------------------------------------")
        # _log_(self.log_list, selected_oracle_df_for_test.head(10))
        return selected_oracle_df_for_test, test_end_date_str, test_start_date_str



