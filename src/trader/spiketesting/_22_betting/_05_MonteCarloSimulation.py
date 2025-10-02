import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Parameters
initial_price = 100000000  # BTC 초기 가격
mu = 0.001  # 일간 평균 수익률 (~0.1%)
sigma = 0.035  # 일간 변동성 (~3.5%)
days = 30  # 예측 기간 (30일)
simulations = 1000  # Monte Carlo 시뮬레이션 횟수

# Monte Carlo Simulation
np.random.seed(42)
results = np.zeros((days, simulations))

for sim in range(simulations):
    daily_returns = np.random.normal(mu, sigma, days)  # 일간 수익률
    price_path = [initial_price]
    for r in daily_returns:
        price_path.append(price_path[-1] * np.exp(r))
    results[:, sim] = price_path[1:]  # 첫 번째 값 제외

# Create DataFrame for analysis
df = pd.DataFrame(results)
df.index = range(1, days + 1)

# Visualization
plt.figure(figsize=(12, 6))
for i in range(100):  # 10개의 시뮬레이션만 시각화
    plt.plot(df.iloc[:, i], alpha=0.6)
plt.title("Monte Carlo Simulation: BTC Price Prediction (30 Days)")
plt.xlabel("Days")
plt.ylabel("Price (USD)")
plt.axhline(initial_price, color='red', linestyle='--', label="Initial Price")
plt.legend()
plt.show()

# Risk analysis
final_prices = df.iloc[-1, :]  # 마지막 날 가격
expected_price = np.mean(final_prices)
worst_5_percent = np.percentile(final_prices, 5)
best_95_percent = np.percentile(final_prices, 95)

print(f"Expected Price: {expected_price:.2f} KRW")
print(f"5% Worst Case Price: {worst_5_percent:.2f} KRW")
print(f"95% Best Case Price: {best_95_percent:.2f} KRW")