import matplotlib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pykrx import stock

code = '069500'
name = 'KODEX200'
start = '2019-07-01'
end = '2022-04-30'

# 주식 데이터 받기
df = stock.get_market_ohlcv(start, end, code)
# 컬럼명 변경
df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']

# 이동편균선 데이터 만든기
df['ma5'] = df['Close'].rolling(window = 5).mean()
df['ma20'] = df['Close'].rolling(window = 20).mean()
df['ma60'] = df['Close'].rolling(window = 60).mean()
df['ma120'] = df['Close'].rolling(window = 120).mean()

# Null 데이터 삭제
df = df.dropna()

# 골든크로스(Golden cross) 및 데드크로스(Death cross) 확인(20일, 60일 이동편균선)
# 매수, 매도 지점 등록
buy = []
sell = []


def chkCross(df) :
    chk = 0
    for i in range(len(df)) :
        buy.append(False)
        sell.append(False)
        if df['ma60'][i] < df['ma20'][i] and chk == 0 :
            print('Golden cross ', str(df.index[i])[:10])
            chk = 1
            buy[i] = True
        elif df['ma60'][i] > df['ma20'][i] and chk == 1 :
            print('Death cross ', str(df.index[i])[:10])
            chk = 0
            sell[i] = True


# 골든코로스/데드코로스 함수 실행
chkCross(df)

df['buy'] = buy
df['sell'] = sell

# %matplotlib Qt5
fig = plt.figure(figsize = (15, 8))
plt.plot(df['Close'], label = 'Close')
plt.plot(df['ma20'], label = 'ma20')
plt.plot(df['ma60'], label = 'ma60')
plt.plot(df.ma20[df.buy == True], '^')  # 매수지점 Marking
plt.plot(df.ma20[df.sell == True], 'v')  # 메도지점 Marking

# 매도, 매수 시점에 종가 Text 보여 주기. +500은 Text가 조금 높게 보이도록 함
for i in range(len(df)) :
    if df.buy[i] == True :
        # (X, Y, Text), X는 index, Y는 ma20 값에 + 500
        plt.text(df.index[i], int(df['ma20'][i]) + 500, str(df['Close'][i]))

    if df.sell[i] == True :
        plt.text(df.index[i], int(df['ma20'][i]) + 500, str(df['Close'][i]))

plt.legend()
plt.grid()
plt.tight_layout()
plt.show()