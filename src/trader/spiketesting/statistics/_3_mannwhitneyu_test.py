import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu
from scipy.stats import skew, kurtosis
import matplotlib.pyplot as plt
from scipy import stats

x = np.array([7, 5, 6, 4, 12, 9, 8])
y = np.array([3, 6, 4, 2, 1, 5, 1])

## 왜도, 첨도 구하기
print(f"skew x : {skew(x)}")
print(f"kurtosis: {kurtosis(x)}")  ## 모두 skew < 2, kurtosis < 7인데.. 그러면 정규분포를 따르지는 않음?
statistic, p_value = stats.shapiro(x)
print(f"shapiro: {p_value}")
kst_test, p_value = stats.kstest(x, 'norm')
print(f"kstest: {p_value}")

# skew x : 0.560332836838461
# kurtosis: -0.58972472299169
plt.hist(x)
plt.show()

print(f"skew y: {skew(y)}")
print(f"kurtosis: {kurtosis(y)}")
statistic, p_value = stats.shapiro(y)
print(f"shapiro: {p_value}")
kst_test, p_value = stats.kstest(y, 'norm')
print(f"kstest: {p_value}")

# skew: 0.22234764798058934
# kurtosis: -1.3526562500000001
plt.hist(y)
plt.show()

## pvalue=0.012326963542679745 -> H1이 채택됨. 즉 두 모집단의 평균이 다름
print(f"mean x: {np.mean(x)}")
print(f"mean y: {np.mean(y)}")
## 실제로 두개의 모집단의 평균이 많이 다름
# mean x: 7.285714285714286
# mean y: 3.142857142857143


# Mann-Whitney U test:
# H0 : mean1 == mean2, H1 : mean1 != mean2
print(mannwhitneyu(x, y))

