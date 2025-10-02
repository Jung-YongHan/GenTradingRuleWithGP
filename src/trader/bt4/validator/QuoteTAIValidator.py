import datetime

from bt4.quote.QuoteListener import QuoteListener
from bt4.quote.ExchangeQuoteDispatcher import QuoteReceiver, ExchangeQuoteDispatcher
from bt4.quote.LocalQuoteDispatcher import LocalQuoteDispatcher
from bt4.Constants import QUOTE_MODE, CandleType
from bt4.utils.pandas_utils import sort_df, get_excluded_indexes_from_list
from bt4.utils.python_utils import pattern_match, str2dt, dt2str, dt2str_for_filename, count_minutes_btw, count_hours_btw
from os.path import dirname, join
from collections import OrderedDict
from datetime import timedelta
from bt4.utils.mylog import init_log

import pandas as pd
from bt3_config.quote_conf import QUOTE_PARAMS

pd.set_option('display.max_columns', None)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('max_colwidth', None)

log = init_log()

DF_KEY = 'candle_date_time_kst'
class QuoteTAIValidator(QuoteListener):

    def __init__(self, markets, data_file_name, ignore_quote, ignore_tai):
        self.markets = markets

        self.quote_oracle_df, self.tai_oracle_df, self.tai_cols, self.quote_test_col_list = self.load_test_oracle(data_file_name)

        for market in markets:
            self.tai_cols[market] = [x for x in self.tai_cols[market] if (x not in ignore_tai[market])]
            self.quote_test_col_list[market] = [x for x in self.quote_test_col_list[market] if (x not in ignore_quote[market])]

        self.quote_test_market_dict = {}
        self.tai_test_market_dict = {}

        for market in self.markets:
            self.quote_test_market_dict[market] = OrderedDict()
            self.tai_test_market_dict[market] = OrderedDict()

    def load_test_oracle(self, data_file_name):
        root_dir = dirname(dirname(dirname(__file__)))
        file_name = join(root_dir, f'data_validation/{data_file_name}')

        quote_oracle_df = {}
        tai_oracle_df = {}
        tai_cols = {}
        quote_test_cols = {}

        with pd.ExcelFile(file_name, engine='openpyxl') as xlsx:
            for sheet_name in xlsx.sheet_names:
                if is_quote_text(sheet_name):
                    market_name = sheet_name.replace('_QUOTE', '')
                    quote_oracle_df[market_name] = xlsx.parse(sheet_name)
                    quote_test_cols[market_name] = quote_oracle_df[market_name].columns.tolist()[:7]
                    sort_df(quote_oracle_df[market_name], DF_KEY)
                    print(f'loading test oracle for quote : {len(quote_oracle_df[market_name])} test oracles in {sheet_name}')
                    # log.info(f'loading test oracle for quote : {len(quote_oracle_df[market_name])} test oracles in {sheet_name}')

                if is_tai_text(sheet_name):
                    market_name = sheet_name.replace('_TAI', '')
                    tai_oracle_df_raw = xlsx.parse(sheet_name)
                    sort_df(tai_oracle_df_raw, DF_KEY)
                    tai_oracle_df[market_name] = tai_oracle_df_raw
                    tai_cols[market_name] = tai_oracle_df_raw.columns.tolist()[7:]
                    print(f'loading test oracle for tai : {len(tai_oracle_df[market_name])} test oracles in {sheet_name}')
                    # log.info(f'loading test oracle for tai : {len(tai_oracle_df[market_name])} test oracles in {sheet_name}')
        return quote_oracle_df, tai_oracle_df, tai_cols, quote_test_cols

    def get_target_markets(self):
        return self.markets

    def quote_tai_received(self, time_dt, market_ticks, market_tais):
        self.collect_quote_and_tai(time_dt, market_ticks, market_tais)

    def collect_quote_and_tai(self, date_time, market_ticks, market_tais):
        for market in market_ticks:
            market_tick = market_ticks[market]
            market_tai = market_tais[market]
            q_market_dict = self.quote_test_market_dict[market]
            q_market_dict[date_time] = market_tick.to_dict()
            t_market_dict = self.tai_test_market_dict[market]
            t_market_dict[date_time] = market_tai

            log_str = f'{market} - {dt2str(date_time)} : c({market_tick.trade_price}), '
            for ta in market_tai:
                log_str = log_str + f'{ta}: {market_tai[ta]}, '
            log.info(log_str)

    def validate_quote_and_tai(self):
        quote_test_market_df = {}
        tai_test_market_df = {}
        result_dfs_files = []
        error_dfs_files = []

        for market in self.quote_test_market_dict:
            q_market_dict = self.quote_test_market_dict[market]
            all_quotes_dict = []
            for date_time in q_market_dict:
                all_quotes_dict.append(q_market_dict[date_time])

            quote_test_market_df[market] = pd.DataFrame.from_dict(all_quotes_dict)
            sort_df(quote_test_market_df[market], DF_KEY)
            print(f'validate_quote:{market} ==> {len(quote_test_market_df[market])}')

            t_market_dict = self.tai_test_market_dict[market]
            all_tai_dict = []
            for date_time in t_market_dict:
                dict = t_market_dict[date_time]
                list_offed_dict = {}
                for key in dict:
                    list_offed_dict[key] = dict[key][0]
                list_offed_dict[DF_KEY] = dt2str(date_time)
                all_tai_dict.append(list_offed_dict)
            tai_test_market_df[market] = pd.DataFrame.from_dict(all_tai_dict)
            sort_df(tai_test_market_df[market], DF_KEY)
            print(f'validate_tai:{market} ==> {len(tai_test_market_df[market])}')

        test_time = dt2str_for_filename(datetime.datetime.now())
        self.validate_num_of_candles(quote_test_market_df, self.start_dt, self.end_dt)

        root_dir = dirname(dirname(dirname(__file__)))  ## parent of parent of directory of simulator.py

        result_dfs, error_dfs = self.validate_quote(self.quote_oracle_df, quote_test_market_df, self.quote_test_col_list)
        '''
        아래의 코드는 추후 데이터 qu 유효성 검사값 저장이 필요하다면 활성화하여 사용할 수 있도록 남겨둠
        '''
        # for market in result_dfs:
        #     file_name = join(root_dir, f'report/{test_time}_{market}_quote_validation.csv')
        #     result_dfs[market].to_csv(file_name)
        #     result_dfs_files.append(file_name)
        #     file_name = join(root_dir, f'report/{test_time}_{market}_quote_error.csv')
        #     error_dfs[market].to_csv(file_name)
        #     error_dfs_files.append(file_name)
        #

        result_dfs, error_dfs = self.validate_tais(self.tai_oracle_df, tai_test_market_df, self.tai_cols)
        '''
        아래의 코드는 추후 데이터 ta 유효성 검사값 저장이 필요하다면 활성화하여 사용할 수 있도록 남겨둠
        '''
        # for market in result_dfs:
        #     file_name = join(root_dir, f'report/{test_time}_{market}_tai_validation.csv')
        #     result_dfs[market].to_csv(file_name)
        #     result_dfs_files.append(file_name)
        #     file_name = join(root_dir, f'report/{test_time}_{market}_quote_error.csv')
        #     error_dfs[market].to_csv(file_name)
        #     error_dfs_files.append(file_name)
        #
        # return result_dfs_files, error_dfs_files

    def start_rt_self_mode_quote_tai_validator(self):
        eqd = ExchangeQuoteDispatcher(QUOTE_MODE.SELF)
        eqd.addQuoteListener(self)
        eqd.process_quote()

    def start_rt_kafka_mode_quote_tai_validator(self):
        quote_receiver = QuoteReceiver()
        quote_receiver.add_quote_receiver(self)
        quote_receiver.start()

    def start_simulator_quote_tai_validator(self, markets, start_dt, end_dt, simul_hours, simul_data_type):
        self.markets = markets
        self.start_dt = start_dt
        self.end_dt = end_dt
        self.simul_hours = simul_hours
        self.data_type = simul_data_type

        quote_providers = QUOTE_PARAMS['exchanges']
        cdl_types_needed = [CandleType.DAYS, CandleType.DAYS_TF, CandleType.HOUR]
        lqd = LocalQuoteDispatcher(start_dt, end_dt, quote_providers, cdl_types_needed)
        lqd.addQuoteListener(self)
        lqd.process_quote([], simul_data_type)

    def validate_quote(self, quote_oracle_df, quote_test_market_df, quote_test_col_list):
        return self.__compare_dfs('==================== Validating QUOTE ', '==================== Error QUOTE ', quote_oracle_df,quote_test_market_df, quote_test_col_list)

    def validate_tais(self, tai_oracle_df, tai_test_market_df, tai_test_col_list):
        return self.__compare_dfs('==================== Validating TAIs', '==================== Error TAIs ', tai_oracle_df,tai_test_market_df, tai_test_col_list)

    def validate_num_of_candles(self, quote_test_market_df, start_dt, end_dt):

        if self.data_type == CandleType.MINUTES_1:
            oracle_num_of_candles = count_minutes_btw(start_dt, end_dt)
        elif self.data_type == CandleType.HOUR:
            oracle_num_of_candles = count_hours_btw(start_dt, end_dt)

        for market in quote_test_market_df:
            test_num_of_candles = len(quote_test_market_df[market])
            result_str = 'Passed' if oracle_num_of_candles == test_num_of_candles else 'Failed'
            print(f'### Checking Num of Candles of {market} market between {dt2str(start_dt)} ~ {dt2str(end_dt)} : {result_str}')
            print(f'### Oracle  : {oracle_num_of_candles}')
            print(f'### Test    : {test_num_of_candles}')

        oracle_caldle_list = []
        for delta in range(0, int(oracle_num_of_candles), 1):
            quote_t_market_df = quote_test_market_df[market]
            if self.data_type == CandleType.MINUTES_1:
                target_dt = start_dt + timedelta(minutes=delta)
            elif self.data_type == CandleType.HOUR:
                target_dt = start_dt + timedelta(hours=delta)
            oracle_caldle_list.append(dt2str(target_dt))
        # oradle_candle_idx = pd.Index(oracle_caldle_list)

        for market in quote_test_market_df:
            # result = oradle_candle_idx.isin(quote_t_market_df.index.tolist())
            # missing_caldle_list = oradle_candle_idx[result == False].tolist()
            missing_caldle_list = get_excluded_indexes_from_list(quote_t_market_df, oracle_caldle_list)
            missing_candle = len(missing_caldle_list)
            print(f'{market} - {missing_candle}: {missing_caldle_list}')


    def __compare_dfs(self, desc, desc_error, oracle_df, test_df, columns):
        merged_dfs = {}
        error_dfs = {}
        summary_list = [f'{desc} summary ====================']
        for market in test_df:
            total_validation_data_count = 0
            print(f'\n\n{desc} : {market} --- {columns[market]}')
            q_test_df = test_df[market]
            q_test_df.set_index([DF_KEY], drop=False, inplace=True)
            q_oracle_df = oracle_df[market]
            q_oracle_df.set_index([DF_KEY], drop=False, inplace=True)
            l_surfix= '_test'
            r_surfix = '_oracle'
            merged_df = q_test_df.join(q_oracle_df, how='inner', lsuffix=l_surfix, rsuffix=r_surfix)
            error_df = pd.DataFrame.from_dict({'Passed': [], 'type': [], 'test': [], 'oracle': []})

            list_of_col_names = []
            for col_name in columns[market]:
                col_left = col_name + l_surfix
                col_right= col_name + r_surfix
                merged_df['Passed ' + col_name] = merged_df[col_left] == merged_df[col_right]
                q_oracle_df_temp = q_oracle_df[(q_oracle_df[DF_KEY] >= dt2str(self.start_dt)) & (q_oracle_df[DF_KEY] <= dt2str(self.end_dt))]
                total_validation_data_count = total_validation_data_count + q_oracle_df_temp[col_name].notna().sum()
                str_temp = 'Passed ' + col_name
                temp_df = merged_df[[str_temp, col_left, col_right]]

                error_row = temp_df.loc[(temp_df['Passed ' + col_name] == False)
                                        & (temp_df[col_left].notna())
                                        & (temp_df[col_right].notna())]
                if not error_row.empty:
                    error_row_temp = error_row.copy()
                    error_row_temp.columns = ['Passed', 'test', 'oracle']
                    error_row_temp.loc[:, 'type'] = col_name
                    error_df = pd.concat([error_df, error_row_temp])
                    error_df = error_df[['type', 'test', 'oracle']]

                list_of_col_names.append('Passed '+ col_name)
                list_of_col_names.append(col_left)
                list_of_col_names.append(col_right)

            pd.options.display.max_columns = None
            pd.options.display.max_rows = None
            merged_dfs[market] = merged_df[[*list_of_col_names]]
            print(merged_df[[*list_of_col_names]])
            summary_list.append(f'######################## {market} - 검증 데이터 {total_validation_data_count}개')
            # print(f'\n######################## {market} - 검증 데이터 {total_validation_data_count}개')
            summary_list.append(f'######################## {market} - {len(error_df)}개 에러\n')
            # print(f'######################## {market} - {len(error_df)}개 에러\n')
            if not error_df.empty:
                print(f'\n{desc_error} : {market} --- {self.start_dt} ~ {self.end_dt} 검증 데이터 {total_validation_data_count}개 중 {len(error_df)}개 에러\n')
                print(error_df)
            else:
                print(f'\n{desc} : {market} --- {self.start_dt} ~ {self.end_dt} 검증 데이터 {total_validation_data_count}개 모두 통과\n')
                error_dfs[market] = error_df
        for summary in summary_list:
            print(summary)
        return merged_dfs, error_dfs


def is_quote_text(source):
    pattern_text = '[A-Z]+[A-Z]+[A-Z]+-[A-Z]*_QUOTE'
    return pattern_match(pattern_text, source)

def is_tai_text(source):
    pattern_text = '[A-Z]+[A-Z]+[A-Z]+-[A-Z]*_TAI'
    return pattern_match(pattern_text, source)

if __name__ == '__main__':
    '''
    1. data_file_name:          검증 엑셀 파일 이름 설정
    2. 검증 엑셀 ta로 지정되도록
        - ta 위치 고정 -> 엑셀의 7번째 칸부터 ta 입력
        - 또한 ta는 현재 다루고 있는 quote_config.py 에 명시되어 있는 값만 가능
        - 마켓별로 ta를 지정 -> 모든 마켓이 동일하게 테스팅을 안할 수 있기 때문에
        - 예를 들어 비트코인만 우선적으로 해보고 적용하고 싶을 때 모든 ta를 만들지 않아도 됨 

    3. 검증 엑셀의 컬럼들을 읽어오도록 하며, 
       ignore_col: 불필요한 컬럼은 입력하여 제거 가능하게 수정
        - 간단하고 빠르게 테스팅을 하고 싶을 때
        - 새롭게 ta를 추가해보거나 기존 ta를 변경하여 테스팅해보고 싶을 때

    4. data_type:               시간 데이터 타입 설정
    5. simul_hours:             실행 시간 입력 
    6. start_dt/end_dt:         시작/끝 시간 지정
    7. markets:                 검증 마켓 설정
    '''

    data_file_name = 'quote_tai_validation_data_v2.xlsx'

    # 'market', 'candle_date_time_utc' 두 컬럼은 현재 완전히 사용하지 않음
    ignore_quote = {'KRW-BTC': ['market', 'candle_date_time_utc', 'candle_date_time_kst', 'opening_price', 'high_price', 'low_price'],
                    'KRW-ETH': ['market', 'candle_date_time_utc', 'candle_date_time_kst', 'opening_price', 'high_price', 'low_price'],
                    'KRW-XRP': ['market', 'candle_date_time_utc', 'candle_date_time_kst', 'opening_price', 'high_price', 'low_price']}

    ignore_tai = {'KRW-BTC': [],
                  'KRW-ETH': [],
                  'KRW-XRP': []}
    # ignore_tai = {'KRW-BTC': ['ma3_1', 'ma5_1', 'ma10_1', 'ma20_1', 'ma3_5'], # 예시
    #               'KRW-ETH': [],
    #               'KRW-XRP': []}

    data_type = CandleType.HOUR
    simul_hours = []

    # start_dt = str2dt('2018-10-01T09:00:00')
    # start_dt = str2dt('2021-5-02T08:59:00')
    start_dt = str2dt('2021-08-10T08:59:00') # 검증 데이터로 되어 있는 제일 처음
    # start_dt = str2dt('2021-12-02T08:59:00')
    end_dt = str2dt('2021-12-26T08:59:00')

    markets = ('KRW-BTC', 'KRW-ETH', 'KRW-XRP')
    # markets = ('KRW-BTC', )

    qtv = QuoteTAIValidator(markets, data_file_name, ignore_quote, ignore_tai)
    qtv.start_simulator_quote_tai_validator(markets, start_dt, end_dt, simul_hours, data_type)
    qtv.validate_quote_and_tai()