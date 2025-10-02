import unittest
from os.path import dirname, join
import numpy as np
import pandas as pd

from bt4.utils.stat.stats import TTest


class MyTestCase(unittest.TestCase) :
    def test_check_same_mean_in_BTC_0(self) :
        import warnings
        warnings.filterwarnings("ignore", category = DeprecationWarning)

        root_dir = dirname(dirname(dirname(__file__)))  ## parent of parent of directory of simulator.py
        file_name = join(root_dir, f'data/upbit/KRW-BTC_DAYS.csv')

        # test_df = pd.read_csv(file_name, index_col=['candle_date_time_kst'], parse_dates=True)
        btc_df = pd.read_csv(file_name, index_col = ["datetime"], parse_dates = True)
        print(btc_df.head())

        windows_size = 30
        move_count = 0
        print(btc_df.iloc[windows_size * move_count :windows_size * (move_count + 1)].head(100))

        first_sample_df = btc_df.iloc[windows_size * move_count :windows_size * (move_count + 1)]
        first_period = f"{first_sample_df.head(1).index.item()} ~ {first_sample_df.tail(1).index.item()}"
        print(first_period)
        first_sample_ser = first_sample_df["vol"]
        mean1 = np.mean(first_sample_ser.to_numpy())
        var1 = np.var(first_sample_ser.to_numpy())
        print(f"{first_period=}, {mean1=}, {var1=}")

        second_sample_df = btc_df.iloc[windows_size * (move_count + 1) : windows_size * (move_count + 2)]
        second_period = f"{second_sample_df.head(1).index.item()} ~ {second_sample_df.tail(1).index.item()}"
        second_sample_ser = second_sample_df["vol"]
        mean2 = np.mean(second_sample_ser.to_numpy())
        var2 = np.var(second_sample_ser.to_numpy())
        print(f"{second_period=}, {mean2=}, {var2=}")

        # mean1 = 30.287699099000005, var1 = 1327.3832056448218
        # mean2 = 4703.502677455333, var2 = 20308111.16773005
        ## 전후의 상황이 확실히 다름 => 그러면 T-Test는 서로 다르다고 판단해야
        ttest = TTest()
        is_same, reason = ttest.perform(first_sample_ser.to_numpy(), second_sample_ser.to_numpy())
        print(f"{is_same}, {reason}")
        ## False, Two samples's means seem to be DIFFERENT (by Mann-Whitney U-test, without normality)
        ## 둘 사이가 평균과 분산도 엄청 달라보임,
        ## TTest의 결과도 상이함

    def test_check_same_mean_in_BTC_1(self) :
        import warnings
        warnings.filterwarnings("ignore", category = DeprecationWarning)

        root_dir = dirname(dirname(dirname(__file__)))  ## parent of parent of directory of simulator.py
        file_name = join(root_dir, f'data/upbit/KRW-BTC_DAYS.csv')

        # test_df = pd.read_csv(file_name, index_col=['candle_date_time_kst'], parse_dates=True)
        btc_df = pd.read_csv(file_name, index_col = ["datetime"], parse_dates=True)
        print(btc_df.head())

        windows_size = 30
        move_count = 1
        print(btc_df.iloc[windows_size*move_count:windows_size*(move_count+1)].head(100))

        first_sample_df = btc_df.iloc[windows_size*move_count:windows_size*(move_count+1)]
        first_period = f"{first_sample_df.head(1).index.item()} ~ {first_sample_df.tail(1).index.item()}"
        print(first_period)
        first_sample_ser = first_sample_df["vol"]
        mean1 = np.mean(first_sample_ser.to_numpy())
        var1 = np.var(first_sample_ser.to_numpy())
        print(f"{first_period=}, {mean1=}, {var1=}")

        second_sample_df = btc_df.iloc[windows_size*(move_count+1) : windows_size*(move_count+2)]
        second_period = f"{second_sample_df.head(1).index.item()} ~ {second_sample_df.tail(1).index.item()}"
        second_sample_ser = second_sample_df["vol"]
        mean2 = np.mean(second_sample_ser.to_numpy())
        var2 = np.var(second_sample_ser.to_numpy())
        print(f"{second_period=}, {mean2=}, {var2=}")

        # first_period = '2017-10-25 09:00:00 ~ 2017-11-23 09:00:00', mean1 = 4703.502677455333, var1 = 20308111.16773005
        # second_period = '2017-11-24 09:00:00 ~ 2017-12-23 09:00:00', mean2 = 42883.32944805033, var2 = 381588122.3066095
        ## 거래량 평균이 매우 다름
        ttest = TTest()
        is_same, reason = ttest.perform(first_sample_ser.to_numpy(),second_sample_ser.to_numpy() )
        print(f"{is_same}, {reason}")
        ## False, Two samples's variance seem to be DIFFERENT, (by Bartlett's Equal Variance Test)
        ## 둘 사이가 평균과 분산도 엄청 달라보임,
        ## 등분산 분석에서 서로 다르다고 판단함

    def test_check_same_mean_in_BTC_2(self) :
        import warnings
        warnings.filterwarnings("ignore", category = DeprecationWarning)

        root_dir = dirname(dirname(dirname(__file__)))  ## parent of parent of directory of simulator.py
        file_name = join(root_dir, f'data/upbit/KRW-BTC_DAYS.csv')

        # test_df = pd.read_csv(file_name, index_col=['candle_date_time_kst'], parse_dates=True)
        btc_df = pd.read_csv(file_name, index_col = ["datetime"], parse_dates=True)
        print(btc_df.head())

        windows_size = 30
        move_count = 2
        print(btc_df.iloc[windows_size*move_count:windows_size*(move_count+1)].head(100))

        first_sample_df = btc_df.iloc[windows_size*move_count:windows_size*(move_count+1)]
        first_period = f"{first_sample_df.head(1).index.item()} ~ {first_sample_df.tail(1).index.item()}"
        print(first_period)
        first_sample_ser = first_sample_df["vol"]
        mean1 = np.mean(first_sample_ser.to_numpy())
        var1 = np.var(first_sample_ser.to_numpy())
        print(f"{first_period=}, {mean1=}, {var1=}")

        second_sample_df = btc_df.iloc[windows_size*(move_count+1) : windows_size*(move_count+2)]
        second_period = f"{second_sample_df.head(1).index.item()} ~ {second_sample_df.tail(1).index.item()}"
        second_sample_ser = second_sample_df["vol"]
        mean2 = np.mean(second_sample_ser.to_numpy())
        var2 = np.var(second_sample_ser.to_numpy())
        print(f"{second_period=}, {mean2=}, {var2=}")

        # first_period = '2017-11-24 09:00:00 ~ 2017-12-23 09:00:00', mean1 = 42883.32944805033, var1 = 381588122.3066095
        # second_period = '2017-12-24 09:00:00 ~ 2018-01-22 09:00:00', mean2 = 42278.732056577006, var2 = 97883194.3779859
        ## 거래량 평균은 비슷하지만, 분산이 많이 다름 3배정도 차이남
        ttest = TTest()
        is_same, reason = ttest.perform(first_sample_ser.to_numpy(),second_sample_ser.to_numpy() )
        print(f"{is_same}, {reason}")
        ## True, Two samples's means seem to be the SAME, (by T-Test with NOT passed equal-variance test(welch's t-test))
        ## 분산은 다르지만, 두 집단의 평균이 동일하다고 판단함

    def test_check_same_mean_in_BTC_3(self) :
        import warnings
        warnings.filterwarnings("ignore", category = DeprecationWarning)

        root_dir = dirname(dirname(dirname(__file__)))  ## parent of parent of directory of simulator.py
        file_name = join(root_dir, f'data/upbit/KRW-BTC_DAYS.csv')

        # test_df = pd.read_csv(file_name, index_col=['candle_date_time_kst'], parse_dates=True)
        btc_df = pd.read_csv(file_name, index_col = ["datetime"], parse_dates=True)
        print(btc_df.head())

        windows_size = 30
        move_count = 3
        print(btc_df.iloc[windows_size*move_count:windows_size*(move_count+1)].head(100))

        first_sample_df = btc_df.iloc[windows_size*move_count:windows_size*(move_count+1)]
        first_period = f"{first_sample_df.head(1).index.item()} ~ {first_sample_df.tail(1).index.item()}"
        print(first_period)
        first_sample_ser = first_sample_df["vol"]
        mean1 = np.mean(first_sample_ser.to_numpy())
        var1 = np.var(first_sample_ser.to_numpy())
        print(f"{first_period=}, {mean1=}, {var1=}")

        second_sample_df = btc_df.iloc[windows_size*(move_count+1) : windows_size*(move_count+2)]
        second_period = f"{second_sample_df.head(1).index.item()} ~ {second_sample_df.tail(1).index.item()}"
        second_sample_ser = second_sample_df["vol"]
        mean2 = np.mean(second_sample_ser.to_numpy())
        var2 = np.var(second_sample_ser.to_numpy())
        print(f"{second_period=}, {mean2=}, {var2=}")

        # first_period = '2017-12-24 09:00:00 ~ 2018-01-22 09:00:00', mean1 = 42278.732056577006, var1 = 97883194.3779859
        # second_period = '2018-01-23 09:00:00 ~ 2018-02-21 09:00:00', mean2 = 26962.418049922, var2 = 95775113.36893383
        ## 분산은 비슷하지만, 평균이 반절이 되었음
        ttest = TTest()
        is_same, reason = ttest.perform(first_sample_ser.to_numpy(),second_sample_ser.to_numpy() )
        print(f"{is_same}, {reason}")
        ## False, Two samples's means seem to be DIFFERENT, (by T-Test with PASSED equal-variance test)
        ## 등분산 분석은 통과되었지만, T-Test에서 다르다고 판단함

    def test_check_same_mean_in_BTC_4(self) :
        import warnings
        warnings.filterwarnings("ignore", category = DeprecationWarning)

        root_dir = dirname(dirname(dirname(__file__)))  ## parent of parent of directory of simulator.py
        file_name = join(root_dir, f'data/upbit/KRW-BTC_DAYS.csv')

        # test_df = pd.read_csv(file_name, index_col=['candle_date_time_kst'], parse_dates=True)
        btc_df = pd.read_csv(file_name, index_col = ["datetime"], parse_dates = True)
        print(btc_df.head())

        windows_size = 30
        move_count = 4
        print(btc_df.iloc[windows_size * move_count :windows_size * (move_count + 1)].head(100))

        first_sample_df = btc_df.iloc[windows_size * move_count :windows_size * (move_count + 1)]
        first_period = f"{first_sample_df.head(1).index.item()} ~ {first_sample_df.tail(1).index.item()}"
        print(first_period)
        first_sample_ser = first_sample_df["vol"]
        mean1 = np.mean(first_sample_ser.to_numpy())
        var1 = np.var(first_sample_ser.to_numpy())
        print(f"{first_period=}, {mean1=}, {var1=}")

        second_sample_df = btc_df.iloc[windows_size * (move_count + 1) : windows_size * (move_count + 2)]
        second_period = f"{second_sample_df.head(1).index.item()} ~ {second_sample_df.tail(1).index.item()}"
        second_sample_ser = second_sample_df["vol"]
        mean2 = np.mean(second_sample_ser.to_numpy())
        var2 = np.var(second_sample_ser.to_numpy())
        print(f"{second_period=}, {mean2=}, {var2=}")

        # first_period = '2018-01-23 09:00:00 ~ 2018-02-21 09:00:00', mean1 = 26962.418049922, var1 = 95775113.36893383
        # second_period = '2018-02-22 09:00:00 ~ 2018-03-23 09:00:00', mean2 = 20999.26323124833, var2 = 41197587.87117806
        ## 분산은 비슷하지만, 평균이 반절이 되었음
        ttest = TTest()
        is_same, reason = ttest.perform(first_sample_ser.to_numpy(), second_sample_ser.to_numpy())
        print(f"{is_same}, {reason}")
        ## False, Two samples's means seem to be DIFFERENT, (by T-Test with NOT passed equal-variance test)
        ## 이정도 평균이 다른것을 다른것으로 판단함

    def test_check_same_mean_in_BTC_5(self) :
        import warnings
        warnings.filterwarnings("ignore", category = DeprecationWarning)

        root_dir = dirname(dirname(dirname(__file__)))  ## parent of parent of directory of simulator.py
        file_name = join(root_dir, f'data/upbit/KRW-BTC_DAYS.csv')

        # test_df = pd.read_csv(file_name, index_col=['candle_date_time_kst'], parse_dates=True)
        btc_df = pd.read_csv(file_name, index_col = ["datetime"], parse_dates = True)
        print(btc_df.head())

        windows_size = 30
        move_count = 5
        print(btc_df.iloc[windows_size * move_count :windows_size * (move_count + 1)].head(100))

        first_sample_df = btc_df.iloc[windows_size * move_count :windows_size * (move_count + 1)]
        first_period = f"{first_sample_df.head(1).index.item()} ~ {first_sample_df.tail(1).index.item()}"
        print(first_period)
        first_sample_ser = first_sample_df["vol"]
        mean1 = np.mean(first_sample_ser.to_numpy())
        var1 = np.var(first_sample_ser.to_numpy())
        print(f"{first_period=}, {mean1=}, {var1=}")

        second_sample_df = btc_df.iloc[windows_size * (move_count + 1) : windows_size * (move_count + 2)]
        second_period = f"{second_sample_df.head(1).index.item()} ~ {second_sample_df.tail(1).index.item()}"
        second_sample_ser = second_sample_df["vol"]
        mean2 = np.mean(second_sample_ser.to_numpy())
        var2 = np.var(second_sample_ser.to_numpy())
        print(f"{second_period=}, {mean2=}, {var2=}")

        # first_period = '2018-02-22 09:00:00 ~ 2018-03-23 09:00:00', mean1 = 20999.26323124833, var1 = 41197587.87117806
        # second_period = '2018-03-24 09:00:00 ~ 2018-04-22 09:00:00', mean2 = 18286.034033206, var2 = 50332947.49190926
        ## 분산은 비슷하지만, 평균이 반절이 되었음
        ttest = TTest()
        is_same, reason = ttest.perform(first_sample_ser.to_numpy(), second_sample_ser.to_numpy())
        print(f"{is_same}, {reason}")
        ## True, Two samples's means seem to be the SAME, (by T-Test with PASSED equal-variance test(welch's t-test))
        ## 평균이 같은 것으로 판단함

    def test_check_same_mean_in_BTC_6(self) :
        import warnings
        warnings.filterwarnings("ignore", category = DeprecationWarning)

        root_dir = dirname(dirname(dirname(__file__)))  ## parent of parent of directory of simulator.py
        file_name = join(root_dir, f'data/upbit/KRW-BTC_DAYS.csv')

        # test_df = pd.read_csv(file_name, index_col=['candle_date_time_kst'], parse_dates=True)
        btc_df = pd.read_csv(file_name, index_col = ["datetime"], parse_dates = True)
        print(btc_df.head())

        windows_size = 30
        move_count = 13
        print(btc_df.iloc[windows_size * move_count :windows_size * (move_count + 1)].head(100))

        first_sample_df = btc_df.iloc[windows_size * move_count :windows_size * (move_count + 1)]
        first_period = f"{first_sample_df.head(1).index.item()} ~ {first_sample_df.tail(1).index.item()}"
        print(first_period)
        first_sample_ser = first_sample_df["vol"]
        mean1 = np.mean(first_sample_ser.to_numpy())
        var1 = np.var(first_sample_ser.to_numpy())
        print(f"{first_period=}, {mean1=}, {var1=}")

        second_sample_df = btc_df.iloc[windows_size * (move_count + 1) : windows_size * (move_count + 2)]
        second_period = f"{second_sample_df.head(1).index.item()} ~ {second_sample_df.tail(1).index.item()}"
        second_sample_ser = second_sample_df["vol"]
        mean2 = np.mean(second_sample_ser.to_numpy())
        var2 = np.var(second_sample_ser.to_numpy())
        print(f"{second_period=}, {mean2=}, {var2=}")

        # first_period = '2018-02-22 09:00:00 ~ 2018-03-23 09:00:00', mean1 = 20999.26323124833, var1 = 41197587.87117806
        # second_period = '2018-03-24 09:00:00 ~ 2018-04-22 09:00:00', mean2 = 18286.034033206, var2 = 50332947.49190926
        ## 분산은 비슷하지만, 평균이 반절이 되었음
        ttest = TTest()
        is_same, reason = ttest.perform(first_sample_ser.to_numpy(), second_sample_ser.to_numpy())
        print(f"{is_same}, {reason}")
        ## True, Two samples's means seem to be the SAME, (by T-Test with PASSED equal-variance test(welch's t-test))
        ## 평균이 같은 것으로 판단함

    def test_check_same_mean_in_ETH_0(self) :
        import warnings
        warnings.filterwarnings("ignore", category = DeprecationWarning)

        root_dir = dirname(dirname(dirname(__file__)))  ## parent of parent of directory of simulator.py
        file_name = join(root_dir, f'data/upbit/KRW-ETH_DAYS.csv')

        # test_df = pd.read_csv(file_name, index_col=['candle_date_time_kst'], parse_dates=True)
        btc_df = pd.read_csv(file_name, index_col = ["datetime"], parse_dates = True)
        print(btc_df.head())

        windows_size = 30
        move_count = 0
        print(btc_df.iloc[windows_size * move_count :windows_size * (move_count + 1)].head(100))

        first_sample_df = btc_df.iloc[windows_size * move_count :windows_size * (move_count + 1)]
        first_period = f"{first_sample_df.head(1).index.item()} ~ {first_sample_df.tail(1).index.item()}"
        print(first_period)
        first_sample_ser = first_sample_df["vol"]
        mean1 = np.mean(first_sample_ser.to_numpy())
        var1 = np.var(first_sample_ser.to_numpy())
        print(f"{first_period=}, {mean1=}, {var1=}")

        second_sample_df = btc_df.iloc[windows_size * (move_count + 1) : windows_size * (move_count + 2)]
        second_period = f"{second_sample_df.head(1).index.item()} ~ {second_sample_df.tail(1).index.item()}"
        second_sample_ser = second_sample_df["vol"]
        mean2 = np.mean(second_sample_ser.to_numpy())
        var2 = np.var(second_sample_ser.to_numpy())
        print(f"{second_period=}, {mean2=}, {var2=}")

        # first_period = '2017-09-25 09:00:00 ~ 2017-10-24 09:00:00', mean1 = 66.69846756733334, var1 = 65562.50494703162
        # second_period = '2017-10-25 09:00:00 ~ 2017-11-23 09:00:00', mean2 = 27016.796549007668, var2 = 1180928578.1374884
        ttest = TTest()
        is_same, reason = ttest.perform(first_sample_ser.to_numpy(), second_sample_ser.to_numpy())
        print(f"{is_same}, {reason}")
        ## False, Two samples's means seem to be DIFFERENT (by Mann-Whitney U-test, without normality)

    def test_check_same_mean_in_ETH_1(self) :
        import warnings
        warnings.filterwarnings("ignore", category = DeprecationWarning)

        root_dir = dirname(dirname(dirname(__file__)))  ## parent of parent of directory of simulator.py
        file_name = join(root_dir, f'data/upbit/KRW-ETH_DAYS.csv')

        # test_df = pd.read_csv(file_name, index_col=['candle_date_time_kst'], parse_dates=True)
        btc_df = pd.read_csv(file_name, index_col = ["datetime"], parse_dates = True)
        print(btc_df.head())

        windows_size = 30
        move_count = 1
        print(btc_df.iloc[windows_size * move_count :windows_size * (move_count + 1)].head(100))

        first_sample_df = btc_df.iloc[windows_size * move_count :windows_size * (move_count + 1)]
        first_period = f"{first_sample_df.head(1).index.item()} ~ {first_sample_df.tail(1).index.item()}"
        print(first_period)
        first_sample_ser = first_sample_df["vol"]
        mean1 = np.mean(first_sample_ser.to_numpy())
        var1 = np.var(first_sample_ser.to_numpy())
        print(f"{first_period=}, {mean1=}, {var1=}")

        second_sample_df = btc_df.iloc[windows_size * (move_count + 1) : windows_size * (move_count + 2)]
        second_period = f"{second_sample_df.head(1).index.item()} ~ {second_sample_df.tail(1).index.item()}"
        second_sample_ser = second_sample_df["vol"]
        mean2 = np.mean(second_sample_ser.to_numpy())
        var2 = np.var(second_sample_ser.to_numpy())
        print(f"{second_period=}, {mean2=}, {var2=}")

        # first_period = '2017-09-25 09:00:00 ~ 2017-10-24 09:00:00', mean1 = 66.69846756733334, var1 = 65562.50494703162
        # second_period = '2017-10-25 09:00:00 ~ 2017-11-23 09:00:00', mean2 = 27016.796549007668, var2 = 1180928578.1374884
        ttest = TTest()
        is_same, reason = ttest.perform(first_sample_ser.to_numpy(), second_sample_ser.to_numpy())
        print(f"{is_same}, {reason}")
        ## False, Two samples's means seem to be DIFFERENT (by Mann-Whitney U-test, without normality)

    def test_check_same_mean_in_ETH_2(self) :
        import warnings
        warnings.filterwarnings("ignore", category = DeprecationWarning)

        root_dir = dirname(dirname(dirname(__file__)))  ## parent of parent of directory of simulator.py
        file_name = join(root_dir, f'data/upbit/KRW-ETH_DAYS.csv')

        # test_df = pd.read_csv(file_name, index_col=['candle_date_time_kst'], parse_dates=True)
        btc_df = pd.read_csv(file_name, index_col = ["datetime"], parse_dates = True)
        print(btc_df.head())

        windows_size = 30
        move_count = 2
        print(btc_df.iloc[windows_size * move_count :windows_size * (move_count + 1)].head(100))

        first_sample_df = btc_df.iloc[windows_size * move_count :windows_size * (move_count + 1)]
        first_period = f"{first_sample_df.head(1).index.item()} ~ {first_sample_df.tail(1).index.item()}"
        print(first_period)
        first_sample_ser = first_sample_df["vol"]
        mean1 = np.mean(first_sample_ser.to_numpy())
        var1 = np.var(first_sample_ser.to_numpy())
        print(f"{first_period=}, {mean1=}, {var1=}")

        second_sample_df = btc_df.iloc[windows_size * (move_count + 1) : windows_size * (move_count + 2)]
        second_period = f"{second_sample_df.head(1).index.item()} ~ {second_sample_df.tail(1).index.item()}"
        second_sample_ser = second_sample_df["vol"]
        mean2 = np.mean(second_sample_ser.to_numpy())
        var2 = np.var(second_sample_ser.to_numpy())
        print(f"{second_period=}, {mean2=}, {var2=}")

        # first_period = '2017-11-24 09:00:00 ~ 2017-12-23 09:00:00', mean1 = 100709.14421390832, var1 = 2481114785.439825
        # second_period = '2017-12-24 09:00:00 ~ 2018-01-22 09:00:00', mean2 = 149176.50152396303, var2 = 10182408502.257387
        ttest = TTest()
        is_same, reason = ttest.perform(first_sample_ser.to_numpy(), second_sample_ser.to_numpy())
        print(f"{is_same}, {reason}")
        ## False, Two samples's means seem to be DIFFERENT, (by T-Test with NOT passed equal-variance test)

    def test_check_same_mean_in_ETH_3(self) :
        import warnings
        warnings.filterwarnings("ignore", category = DeprecationWarning)

        root_dir = dirname(dirname(dirname(__file__)))  ## parent of parent of directory of simulator.py
        file_name = join(root_dir, f'data/upbit/KRW-ETH_DAYS.csv')

        # test_df = pd.read_csv(file_name, index_col=['candle_date_time_kst'], parse_dates=True)
        btc_df = pd.read_csv(file_name, index_col = ["datetime"], parse_dates = True)
        print(btc_df.head())

        windows_size = 30
        move_count = 3
        print(btc_df.iloc[windows_size * move_count :windows_size * (move_count + 1)].head(100))

        first_sample_df = btc_df.iloc[windows_size * move_count :windows_size * (move_count + 1)]
        first_period = f"{first_sample_df.head(1).index.item()} ~ {first_sample_df.tail(1).index.item()}"
        print(first_period)
        first_sample_ser = first_sample_df["vol"]
        mean1 = np.mean(first_sample_ser.to_numpy())
        var1 = np.var(first_sample_ser.to_numpy())
        print(f"{first_period=}, {mean1=}, {var1=}")

        second_sample_df = btc_df.iloc[windows_size * (move_count + 1) : windows_size * (move_count + 2)]
        second_period = f"{second_sample_df.head(1).index.item()} ~ {second_sample_df.tail(1).index.item()}"
        second_sample_ser = second_sample_df["vol"]
        mean2 = np.mean(second_sample_ser.to_numpy())
        var2 = np.var(second_sample_ser.to_numpy())
        print(f"{second_period=}, {mean2=}, {var2=}")

        # first_period = '2017-12-24 09:00:00 ~ 2018-01-22 09:00:00', mean1 = 149176.50152396303, var1 = 10182408502.257387
        # second_period = '2018-01-23 09:00:00 ~ 2018-02-21 09:00:00', mean2 = 142695.13393827368, var2 = 11266451124.631422
        ttest = TTest()
        is_same, reason = ttest.perform(first_sample_ser.to_numpy(), second_sample_ser.to_numpy())
        print(f"{is_same}, {reason}")
        ## True, Two samples's means seem to be the SAME (by Mann-Whitney U-test, without normality)

    def test_check_same_mean_in_ETH_4(self) :
        import warnings
        warnings.filterwarnings("ignore", category = DeprecationWarning)

        root_dir = dirname(dirname(dirname(__file__)))  ## parent of parent of directory of simulator.py
        file_name = join(root_dir, f'data/upbit/KRW-ETH_DAYS.csv')

        # test_df = pd.read_csv(file_name, index_col=['candle_date_time_kst'], parse_dates=True)
        btc_df = pd.read_csv(file_name, index_col = ["datetime"], parse_dates = True)
        print(btc_df.head())

        windows_size = 30
        move_count = 4
        print(btc_df.iloc[windows_size * move_count :windows_size * (move_count + 1)].head(100))

        first_sample_df = btc_df.iloc[windows_size * move_count :windows_size * (move_count + 1)]
        first_period = f"{first_sample_df.head(1).index.item()} ~ {first_sample_df.tail(1).index.item()}"
        print(first_period)
        first_sample_ser = first_sample_df["vol"]
        mean1 = np.mean(first_sample_ser.to_numpy())
        var1 = np.var(first_sample_ser.to_numpy())
        print(f"{first_period=}, {mean1=}, {var1=}")

        second_sample_df = btc_df.iloc[windows_size * (move_count + 1) : windows_size * (move_count + 2)]
        second_period = f"{second_sample_df.head(1).index.item()} ~ {second_sample_df.tail(1).index.item()}"
        second_sample_ser = second_sample_df["vol"]
        mean2 = np.mean(second_sample_ser.to_numpy())
        var2 = np.var(second_sample_ser.to_numpy())
        print(f"{second_period=}, {mean2=}, {var2=}")

        # first_period = '2018-01-23 09:00:00 ~ 2018-02-21 09:00:00', mean1 = 142695.13393827368, var1 = 11266451124.631422
        # second_period = '2018-02-22 09:00:00 ~ 2018-03-23 09:00:00', mean2 = 33027.557775657995, var2 = 443221583.7579297
        ttest = TTest()
        is_same, reason = ttest.perform(first_sample_ser.to_numpy(), second_sample_ser.to_numpy())
        print(f"{is_same}, {reason}")
        ## False, Two samples's means seem to be DIFFERENT (by Mann-Whitney U-test, without normality)

    def test_check_same_mean_in_XRP_1(self) :
        import warnings
        warnings.filterwarnings("ignore", category = DeprecationWarning)

        root_dir = dirname(dirname(dirname(__file__)))  ## parent of parent of directory of simulator.py
        file_name = join(root_dir, f'data/upbit/KRW-XRP_DAYS.csv')

        # test_df = pd.read_csv(file_name, index_col=['candle_date_time_kst'], parse_dates=True)
        btc_df = pd.read_csv(file_name, index_col = ["datetime"], parse_dates = True)
        print(btc_df.head())

        windows_size = 30
        move_count = 0
        print(btc_df.iloc[windows_size * move_count :windows_size * (move_count + 1)].head(100))

        first_sample_df = btc_df.iloc[windows_size * move_count :windows_size * (move_count + 1)]
        first_period = f"{first_sample_df.head(1).index.item()} ~ {first_sample_df.tail(1).index.item()}"
        print(first_period)
        first_sample_ser = first_sample_df["vol"]
        mean1 = np.mean(first_sample_ser.to_numpy())
        var1 = np.var(first_sample_ser.to_numpy())
        print(f"{first_period=}, {mean1=}, {var1=}")

        second_sample_df = btc_df.iloc[windows_size * (move_count + 1) : windows_size * (move_count + 2)]
        second_period = f"{second_sample_df.head(1).index.item()} ~ {second_sample_df.tail(1).index.item()}"
        second_sample_ser = second_sample_df["vol"]
        mean2 = np.mean(second_sample_ser.to_numpy())
        var2 = np.var(second_sample_ser.to_numpy())
        print(f"{second_period=}, {mean2=}, {var2=}")

        # first_period = '2017-09-25 09:00:00 ~ 2017-10-24 09:00:00', mean1 = 19.301956666666666, var1 = 2249.353757876456
        # second_period = '2017-10-25 09:00:00 ~ 2017-11-23 09:00:00', mean2 = 8862352.73891775, var2 = 265164620032564.38
        ttest = TTest()
        is_same, reason = ttest.perform(first_sample_ser.to_numpy(), second_sample_ser.to_numpy())
        print(f"{is_same}, {reason}")
        ## False, Two samples's means seem to be DIFFERENT (by Mann-Whitney U-test, without normality)

    def test_check_same_mean_in_XRP_2(self) :
        import warnings
        warnings.filterwarnings("ignore", category = DeprecationWarning)

        root_dir = dirname(dirname(dirname(__file__)))  ## parent of parent of directory of simulator.py
        file_name = join(root_dir, f'data/upbit/KRW-XRP_DAYS.csv')

        # test_df = pd.read_csv(file_name, index_col=['candle_date_time_kst'], parse_dates=True)
        btc_df = pd.read_csv(file_name, index_col = ["datetime"], parse_dates = True)
        print(btc_df.head())

        windows_size = 30
        move_count = 2
        print(btc_df.iloc[windows_size * move_count :windows_size * (move_count + 1)].head(100))

        first_sample_df = btc_df.iloc[windows_size * move_count :windows_size * (move_count + 1)]
        first_period = f"{first_sample_df.head(1).index.item()} ~ {first_sample_df.tail(1).index.item()}"
        print(first_period)
        first_sample_ser = first_sample_df["vol"]
        mean1 = np.mean(first_sample_ser.to_numpy())
        var1 = np.var(first_sample_ser.to_numpy())
        print(f"{first_period=}, {mean1=}, {var1=}")

        second_sample_df = btc_df.iloc[windows_size * (move_count + 1) : windows_size * (move_count + 2)]
        second_period = f"{second_sample_df.head(1).index.item()} ~ {second_sample_df.tail(1).index.item()}"
        second_sample_ser = second_sample_df["vol"]
        mean2 = np.mean(second_sample_ser.to_numpy())
        var2 = np.var(second_sample_ser.to_numpy())
        print(f"{second_period=}, {mean2=}, {var2=}")

        # first_period = '2017-11-24 09:00:00 ~ 2017-12-23 09:00:00', mean1 = 261758115.82399642, var1 = 1.4873895965005782e+17
        # second_period = '2017-12-24 09:00:00 ~ 2018-01-22 09:00:00', mean2 = 322815262.692447, var2 = 6.590651128406309e+16
        ttest = TTest()
        is_same, reason = ttest.perform(first_sample_ser.to_numpy(), second_sample_ser.to_numpy())
        print(f"{is_same}, {reason}")
        ## False, Two samples's means seem to be DIFFERENT (by Mann-Whitney U-test, without normality)

    def test_check_same_mean_in_XRP_3(self) :
        import warnings
        warnings.filterwarnings("ignore", category = DeprecationWarning)

        root_dir = dirname(dirname(dirname(__file__)))  ## parent of parent of directory of simulator.py
        file_name = join(root_dir, f'data/upbit/KRW-XRP_DAYS.csv')

        # test_df = pd.read_csv(file_name, index_col=['candle_date_time_kst'], parse_dates=True)
        btc_df = pd.read_csv(file_name, index_col = ["datetime"], parse_dates = True)
        print(btc_df.head())

        windows_size = 30
        move_count = 3
        print(btc_df.iloc[windows_size * move_count :windows_size * (move_count + 1)].head(100))

        first_sample_df = btc_df.iloc[windows_size * move_count :windows_size * (move_count + 1)]
        first_period = f"{first_sample_df.head(1).index.item()} ~ {first_sample_df.tail(1).index.item()}"
        print(first_period)
        first_sample_ser = first_sample_df["vol"]
        mean1 = np.mean(first_sample_ser.to_numpy())
        var1 = np.var(first_sample_ser.to_numpy())
        print(f"{first_period=}, {mean1=}, {var1=}")

        second_sample_df = btc_df.iloc[windows_size * (move_count + 1) : windows_size * (move_count + 2)]
        second_period = f"{second_sample_df.head(1).index.item()} ~ {second_sample_df.tail(1).index.item()}"
        second_sample_ser = second_sample_df["vol"]
        mean2 = np.mean(second_sample_ser.to_numpy())
        var2 = np.var(second_sample_ser.to_numpy())
        print(f"{second_period=}, {mean2=}, {var2=}")

        # first_period = '2017-12-24 09:00:00 ~ 2018-01-22 09:00:00', mean1 = 322815262.692447, var1 = 6.590651128406309e+16
        # second_period = '2018-01-23 09:00:00 ~ 2018-02-21 09:00:00', mean2 = 196066969.01969132, var2 = 3.01288267301231e+16
        ttest = TTest()
        is_same, reason = ttest.perform(first_sample_ser.to_numpy(), second_sample_ser.to_numpy())
        print(f"{is_same}, {reason}")
        ## False, Two samples's means seem to be DIFFERENT (by Mann-Whitney U-test, without normality)

    def test_check_same_mean_in_XRP_4(self) :
        import warnings
        warnings.filterwarnings("ignore", category = DeprecationWarning)

        root_dir = dirname(dirname(dirname(__file__)))  ## parent of parent of directory of simulator.py
        file_name = join(root_dir, f'data/upbit/KRW-XRP_DAYS.csv')

        # test_df = pd.read_csv(file_name, index_col=['candle_date_time_kst'], parse_dates=True)
        btc_df = pd.read_csv(file_name, index_col = ["datetime"], parse_dates = True)
        print(btc_df.head())

        windows_size = 30
        move_count = 4
        print(btc_df.iloc[windows_size * move_count :windows_size * (move_count + 1)].head(100))

        first_sample_df = btc_df.iloc[windows_size * move_count :windows_size * (move_count + 1)]
        first_period = f"{first_sample_df.head(1).index.item()} ~ {first_sample_df.tail(1).index.item()}"
        print(first_period)
        first_sample_ser = first_sample_df["vol"]
        mean1 = np.mean(first_sample_ser.to_numpy())
        var1 = np.var(first_sample_ser.to_numpy())
        print(f"{first_period=}, {mean1=}, {var1=}")

        second_sample_df = btc_df.iloc[windows_size * (move_count + 1) : windows_size * (move_count + 2)]
        second_period = f"{second_sample_df.head(1).index.item()} ~ {second_sample_df.tail(1).index.item()}"
        second_sample_ser = second_sample_df["vol"]
        mean2 = np.mean(second_sample_ser.to_numpy())
        var2 = np.var(second_sample_ser.to_numpy())
        print(f"{second_period=}, {mean2=}, {var2=}")

        # first_period = '2017-12-24 09:00:00 ~ 2018-01-22 09:00:00', mean1 = 322815262.692447, var1 = 6.590651128406309e+16
        # second_period = '2018-01-23 09:00:00 ~ 2018-02-21 09:00:00', mean2 = 196066969.01969132, var2 = 3.01288267301231e+16
        ttest = TTest()
        is_same, reason = ttest.perform(first_sample_ser.to_numpy(), second_sample_ser.to_numpy())
        print(f"{is_same}, {reason}")
        ## False, Two samples's means seem to be DIFFERENT (by Mann-Whitney U-test, without normality)

if __name__ == '__main__' :
    unittest.main()
