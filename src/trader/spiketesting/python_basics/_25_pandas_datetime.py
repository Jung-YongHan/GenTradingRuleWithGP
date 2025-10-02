import unittest
import pandas as pd
import datetime
from bt4.Constants import QItem


class CustomTestCase(unittest.TestCase):
    def setUp(self):
        """테스트 시작되기 전 파일 작성"""
        pass

    def tearDown(self):
        """테스트 종료 후 파일 삭제 """
        pass

    def test_df_datetime(self):
        file_data = pd.read_csv('C:/Users/jg_hong/PycharmProjects/bulltrader3/data/upbit/KRW-XRP_DAYS.csv',
                                parse_dates=True, index_col=QItem.time.value)
        print(file_data)
        simul_start_dt = datetime.datetime(2020, 1, 1, 8, 59, 0)
        simul_range_end_dt = datetime.datetime(2021, 1, 1, 8, 59, 0)
        print(file_data.loc[simul_start_dt:simul_range_end_dt])

    def test_df_datetime_resample(self):
        file_data = pd.read_csv('C:/Users/jg_hong/PycharmProjects/bulltrader3/data/upbit/KRW-XRP_DAYS.csv',
                                parse_dates=True, index_col=QItem.time.value)
        print(file_data)
        idx = pd.date_range('2017-12-30', periods=60 * 24 * 365 * 5, freq='min')
        print(idx.max())

        df = pd.DataFrame(index=idx)
        print(df)

        concat_df = pd.concat([df, file_data], axis=1)
        concat_df.ffill(inplace=True)
        print(concat_df.tail(2000))
        print(concat_df)

        simul_start_dt = datetime.datetime(2020, 1, 1, 8, 59, 0)
        simul_range_end_dt = datetime.datetime(2021, 1, 1, 8, 59, 0)
        print(concat_df.loc[simul_start_dt:simul_range_end_dt])

    def test_df_datetime_range(self):
        file_data = pd.read_csv('C:/Users/jg_hong/PycharmProjects/bulltrader3/data/upbit/KRW-BTC_MINUTES_1.csv',
                                parse_dates=True, index_col=QItem.time.value)
        print(file_data)

        print('가장 오래된 날짜:', file_data.index.min())
        print('가장 최근 날짜:', file_data.index.max())
        idx = pd.date_range(file_data.index.min(), file_data.index.max(), freq='min')
        df = pd.DataFrame(index=idx)  # 빈 데이터 프레임 생성
        print(df)
        concat_df = pd.concat([df, file_data], axis=1)
        print(concat_df)
        print('nan 수:', concat_df['market'].isna().sum(), '개')

    def test_df_concat(self):
        btc_data = pd.read_csv('C:/Users/jg_hong/PycharmProjects/bulltrader3/data/upbit/KRW-BTC_HOUR.csv',
                               parse_dates=True, index_col=QItem.time.value)
        print(btc_data)
        eth_data = pd.read_csv('C:/Users/jg_hong/PycharmProjects/bulltrader3/data/upbit/KRW-ETH_HOUR.csv',
                               parse_dates=True, index_col=QItem.time.value)
        print(eth_data)
        concat_df = pd.concat([btc_data, eth_data])
        print(concat_df)

    def test_df_dataframe_optimization(self):
        btc_data = pd.read_csv('C:/Users/jg_hong/PycharmProjects/bulltrader3/data/upbit/KRW-BTC_HOUR.csv',
                               parse_dates=True, index_col=QItem.time.value)
        print(btc_data)
        print(btc_data.dtypes)
        # btc_data.astype()


if __name__ == '__main__':
    unittest.main()