
import pandas as pd

from bulltrader.utils.python_utils import create_dt_at, dt2str

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

from bulltrader.utils.pandas_utils import rename_columns, rename_columns2

column_names = ['market', 'candle_date_time_utc', 'candle_date_time_kst', 'opening_price', 'high_price',
                            'low_price', 'trade_price', 'timestamp', 'candle_acc_trade_price',
                            'candle_acc_trade_volume', 'unit']

# year, month, day, hour, min, sec
simul_start_dt = create_dt_at(2018,10,1,8,59,00)
simul_end_dt = create_dt_at(2022,2,28,11,59,00)

markets = ['KRW-BTC', 'KRW-ETH', 'KRW-XRP']
time_intervals = ['DAYS', 'HOUR4', 'HOUR']
df_all = pd.DataFrame()
for market in markets:
    for time_interval in time_intervals:
        market_time = f'{market}_{time_interval}'
        print(f'########################### : {market_time}')
        filename = f'../../data/{market_time}.csv'
        df = pd.read_csv(filename, header=None)

        ############################################################
        simul_start_str = dt2str(simul_start_dt)
        simul_end_str = dt2str(simul_end_dt)
        df.set_index(df.columns[2], inplace=True, drop=False)
        df.sort_index(inplace=True, ascending=True)
        ranged_df = df.loc[simul_start_str:simul_end_str]
        ############################################################
        c_name_dic = {}
        for i, cname in enumerate(column_names):
            c_name_dic[f'{i}'] = cname
            c_name_dic[i] = cname
        ranged_df = rename_columns2(ranged_df, c_name_dic)

        ##############################################################
        trade_price_col = ranged_df['trade_price']

        ser_basic_stat = trade_price_col.describe().apply(lambda s: f'{s:.5f}')
        ser_skew = pd.Series({'skew':trade_price_col.astype(float).skew()})
        ser_basic_stat = ser_basic_stat.append(ser_skew)

        ser_kurt = pd.Series({'kurt': trade_price_col.astype(float).kurt()})
        ser_basic_stat = ser_basic_stat.append(ser_kurt)

        first_close_raw = trade_price_col[0]
        first_close = pd.Series({'Initial_P': first_close_raw})
        ser_basic_stat = ser_basic_stat.append(first_close)

        last_close_raw = trade_price_col[-1]
        last_close = pd.Series({'Last_P': last_close_raw})
        ser_basic_stat = ser_basic_stat.append(last_close)

        # bnh = first_close_raw.div(last_close_raw)
        ser_hnh = pd.Series({'Buy_n_Hold': last_close_raw/first_close_raw})
        ser_basic_stat = ser_basic_stat.append(ser_hnh)

        ser_basic_stat = ser_basic_stat.rename(market_time)
        df_all = pd.concat([df_all,ser_basic_stat], axis=1)

print(df_all.head(20))
