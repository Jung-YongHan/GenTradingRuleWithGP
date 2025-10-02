

import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

##############################################################################
## Shaprio_wilks test (n < 2000)
from scipy import stats
x = [6, 1, -4, 8, -2, 5, 0]
statistic, p_value = stats.shapiro(x)
## H0: 정규성을 갖는다. H1: 정규성을 갖지 않는다.
print(f"{statistic=}, {p_value=}")
## p_value=0.7611944079399109 -> 정규성을 갖는다.


##############################################################################
## Kolmogoroe-Smirnov test (n > 2000)
rand1 = np.random.randn(1000) + 3.0
plt.hist(rand1)
plt.show()

print(f"length: {len(rand1)}")
kst_test, p_value = stats.kstest(rand1, 'norm')
print(f"{kst_test=}, {p_value=}")
## Kolmogoroe-Smirnov test : p_value=0.0 -> 정규성을 갖지 않다고 판단함 (n =1000이라서 그런듯)

statistic, p_value = stats.shapiro(rand1)
print(f"{statistic=}, {p_value=}")
## Shaprio_wilks test: p_value=0.9305603504180908 -> 여기에서는 정규성을 갖는다고 판단함 (n = 1000이라서 그런듯)

################### 그러면 N=3000으로 올려보기
rand2 = np.random.randn(10000) + 3.0
plt.hist(rand2)
plt.show()


print(f"length: {len(rand2)}")
kst_test, p_value = stats.kstest(rand2, 'norm')
print(f"{kst_test=}, {p_value=}")
## Kolmogoroe-Smirnov test : p_value=0.0 -> 여기에서도 정규성을 갖지 않는다 판단함
## 내가 보기에는 정규성이 있다고 판단됨

statistic, p_value = stats.shapiro(rand2)
print(f"{statistic=}, {p_value=}")
## Shaprio_wilks test: p_value=0.711929440498352 -> 여기에는 정규성을 갖는다고 판단함
## 내가 보기에는 정규성이 있다고 판단됨 => Shapiro 테스트가 좋아보임

##############################################################################
### https://velog.io/@changhtun1/%EC%A0%95%EA%B7%9C%EC%84%B1%EA%B2%80%EC%A0%95-%EA%BC%AD-%ED%95%84%EC%9A%94%ED%95%9C-%EA%B1%B8%EA%B9%8C
### 1995년에 발표한 skewness and kurtosis를 활용한 정규성 평가 - West 연구논문에 의하면
## "skewness(=왜도)는 2, kurtosis(=첨도)는 7보다 작으면 정규분포에서 크게 벗어나지 않고
# 정규성을 보인다" 라고 말해도 된다고 합니다.

from scipy.stats import skew, kurtosis

r1_skew = skew(rand2)  # 왜도
r1_kurto = kurtosis(rand2, fisher=True)  # 첨도
print(f"skwe: {r1_skew=} , kurtosis: {r1_kurto=}")
## r1_skew=0.04700672310102022 , kurtosis: r1_kurto=0.03736422887073099 => 왜도가 2보다 작고, kurtosis가 7보다 작으므로 정규성을 따른다고 볼수 있음.

