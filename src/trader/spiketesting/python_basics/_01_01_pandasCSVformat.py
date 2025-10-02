import pandas as pd

################################

# tobg = TicOrderBookDispatcher()
# tob = tobg.fetchOrderBook()
#
# print(type(tob.ask_sizes))
# print(tob.ask_sizes.values.tolist())
# ask_sizes_aslist = tob.ask_sizes.values.tolist()
#
# csv_format = ''.join(str(e[0])+',' for e in ask_sizes_aslist)
# print(csv_format)


# columns = ['date','market','open','high','low','close']
# file_name = 'cache_daily_market.csv'
#
# cache_df = pd.read_csv(file_name, index_col ='date')
#
# values = ['KRW-BTC222',  7385000.0, 7499000.0,7362000.0,7481000.0]
# new_df = pd.DataFrame({'market': 'KRW-BTC',
#                                     'open': 7385000.0,
#                                     'high': 7499000.0,
#                                     'low': 7362000.0,
#                                     'close': 7481000.0}, index=['2018-10-04T09:00:00'])
# cache_df = pd.concat([cache_df,new_df])
#
# row = cache_df.loc[(cache_df.market == 'KRW-BTC') & (cache_df.index == '2018-10-04T09:00:00')]
#
# if not row.empty:
#     open = row['open'].values[0]
#     high = row['high'].values[0]
#     low = row['low'].values[0]
#     close = row['close'].values[0]
#
#     print(open, high, low, close)
#
# cache_df.to_csv(file_name, index_label = 'date')

###############################################
# df1 = pd.DataFrame(data = {'col1' : [1, 2, 3, 4, 5, 3],
#                            'col2' : [10, 11, 12, 13, 14, 10]})
# df2 = pd.DataFrame(data = {'col1' : [1, 2, 3],
#                            'col2' : [10, 11, 12]})

df1 = pd.read_csv('../../data/KRW-ETH_MINUTES_1.csv')
df1.columns = ['idx', 'market', 'ust', 'kst', 'open', 'high', 'low', 'close', 'vol',
       'col1', 'col2', 'unit']

df2 = pd.read_csv('../../data/KRW-BTC_MINUTES_1.csv')
df2.columns = ['idx', 'market', 'ust', 'kst', 'open', 'high', 'low', 'close', 'vol',
       'col1', 'col2', 'unit']

df3 = df2[df2['kst'].isin(df1.kst)] # New BTC
df4 = df1[df1['kst'].isin(df3.kst)] # New ETH
df3.to_csv('new_BTC.csv', index = None)
df4.to_csv('new_ETH.csv', index = None)
print(df3)