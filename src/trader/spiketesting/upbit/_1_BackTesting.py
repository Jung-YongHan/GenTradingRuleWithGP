
import pyupbit

import numpy as np

df = pyupbit.get_ohlcv("KRW-BTC", count=10)

k = 0.5
##############################################
### 전략.
## 변동성 돌파 전략 구현 1.범위구하기  (high-low)*k
df['range'] = (df['high'] - df['low']) * k
## df.shift(1) 한칸 밑으로 내리기
df['s_range'] = df['range'].shift(1)
df['target'] = df['open'] + df['s_range']

# fee = 0.0032
fee = 0.0
##############################################
### 백테스팅. 
## ROR(Return on ?) 수익율
df['ror'] = np.where(df['high'] > df['target'],
                     df['close'] / df['target'] - fee,
                     1)

df['hpr'] = df['ror'].cumprod()
df['dd'] = (df['hpr'].cummax() - df['hpr']) / df['hpr'].cummax() * 100
print("MDD(%): ", df['dd'].max())
df.to_excel("dd.xlsx")