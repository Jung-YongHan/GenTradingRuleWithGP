import pandas as pd
import numpy as np

# 1. 데이터 로드
# 예: 'date', 'BTC_price', 'ETH_price' 컬럼이 있는 CSV 파일
data = pd.read_csv('crypto_prices.csv')
data['date'] = pd.to_datetime(data['date'])
data.set_index('date', inplace = True)

# 2. 이동 평균 계산
short_window = 10  # 단기 이동 평균 (10일)
long_window = 50  # 장기 이동 평균 (50일)

data['BTC_short_ma'] = data['BTC_price'].rolling(window = short_window).mean()
data['BTC_long_ma'] = data['BTC_price'].rolling(window = long_window).mean()
data['ETH_short_ma'] = data['ETH_price'].rolling(window = short_window).mean()
data['ETH_long_ma'] = data['ETH_price'].rolling(window = long_window).mean()

# 3. 초기 투자 비중 설정
initial_investment = 1_000_000  # 1000만 원
weights = {'BTC' : 0.5, 'ETH' : 0.5}  # 초기 비중
portfolio_value = initial_investment


# 4. 동적 비율 조정 함수
def adjust_weights(row, weights) :
    new_weights = weights.copy()
    # BTC 추세 분석
    if row['BTC_short_ma'] > row['BTC_long_ma'] :  # 상승 추세
        new_weights['BTC'] += 0.1  # 비중 증가
    else :  # 하락 추세
        new_weights['BTC'] -= 0.1  # 비중 감소

    # ETH 추세 분석
    if row['ETH_short_ma'] > row['ETH_long_ma'] :  # 상승 추세
        new_weights['ETH'] += 0.1  # 비중 증가
    else :  # 하락 추세
        new_weights['ETH'] -= 0.1  # 비중 감소

    # 비중 정규화 (합이 1이 되도록)
    total_weight = sum(new_weights.values())
    for key in new_weights :
        new_weights[key] = max(new_weights[key] / total_weight, 0)  # 음수 방지

    return new_weights


# 5. 시뮬레이션 실행
results = []
for i, row in data.iterrows() :
    # 비중 조정
    weights = adjust_weights(row, weights)

    # 포트폴리오 가치 계산
    btc_value = portfolio_value * weights['BTC'] * (row['BTC_price'] / data.iloc[0]['BTC_price'])
    eth_value = portfolio_value * weights['ETH'] * (row['ETH_price'] / data.iloc[0]['ETH_price'])
    portfolio_value = btc_value + eth_value

    # 결과 저장
    results.append({
        'date'            : i,
        'portfolio_value' : portfolio_value,
        'BTC_weight'      : weights['BTC'],
        'ETH_weight'      : weights['ETH']
    })

# 6. 결과 저장 및 시각화
results_df = pd.DataFrame(results)
results_df.set_index('date', inplace = True)
results_df.to_csv('dynamic_allocation_results.csv')

# 시각화
import matplotlib.pyplot as plt

plt.figure(figsize = (10, 6))
plt.plot(results_df['portfolio_value'], label = 'Portfolio Value')
plt.title('Portfolio Value Over Time')
plt.xlabel('Date')
plt.ylabel('Portfolio Value (KRW)')
plt.legend()
plt.show()