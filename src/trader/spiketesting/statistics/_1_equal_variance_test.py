
### https://signature95.tistory.com/15
# 라이브러리 호출
import numpy as np
import scipy as sp
import seaborn as sns
import matplotlib.pyplot as plt

# Mac OS에서 한글 폰트 출력을 위한 코드
from matplotlib import rc
rc('font', family='AppleGothic')
plt.rcParams['axes.unicode_minus'] = False

# 이분산을 가지는 두 데이터 조건 형성
# 데이터 개수 100개, 분산 1, 2으로 분리함
N1 = 100
N2 = 100
sigma_1 = 1
sigma_2 = 2
mu = 0

# 데이터 형성
np.random.seed(0)
x1 = sp.stats.norm(mu, sigma_1).rvs(N1)
x2 = sp.stats.norm(mu, sigma_2).rvs(N2)

# 시각화
ax = sns.distplot(x1, kde=False, fit=sp.stats.norm, label=f"1번 데이터 집합 (분산 :{np.round(x1.std(),2)})")
ax = sns.distplot(x2, kde=False, fit=sp.stats.norm, label=f"2번 데이터 집합 (분산 :{np.round(x2.std(),2)})")
ax.lines[0].set_linestyle(":")
plt.legend(bbox_to_anchor=(1.0, .2))
plt.show()

####################################################################
## 등분산성 검정: 두 개의 데이터 집합으로부터 두 정규분포의 모분산이 같은지 확인하기 위한 검정이다.
# 바틀렛(bartlett), 플리그너(fligner), 레빈(levene) 검정을 주로 사용한다.

## Bartlett
# - 귀무가설
# 데이터의 모분산이 일치한다고 통계적으로 유의하게 말 할 수 있다. (등분산 충족한다)

from scipy.stats import bartlett
var1 = np.var(x1)
var2 = np.var(x2)
print(f"{var1=}, {var2=}")
### H0 : var(x1) = var(x2), H1: var(x1) != var(x2)
b_test, p_value = bartlett(x1, x2)
print(f"bartlett test: {b_test=}, {p_value=}")
## p_value=6.733268261181105e-12 -> H1 채택! 즉 두 분산은 서로 다름

#######################################################################################
## 다른 데이터 셋에 적용
rand1 = np.random.randn(1000) + 3.0
rand2 = 4.0 * np.random.randn(800) - 2.0
rand3 = np.random.randn(1000)

plt.figure(figsize = (20,5))
sns.kdeplot(data=rand1, color="red", fill = True)
sns.kdeplot(data=rand2, color="blue", fill = True)
sns.kdeplot(data=rand3, color="green", fill = True)

plt.show()

var1 = np.var(rand1)
var2 = np.var(rand2)
var3 = np.var(rand3)
print(f"{var1=}, {var2=}, {var3=}")

b_test, p_value = bartlett(rand1, rand2)
print(f"(rand1, rand2) - diff variance: bartlett test: {b_test=}, {p_value=}")
## p_value=0.0 -> 대립가설 채택: 두개의 분산은 서로 다름 (실제로 var1=0.9372251824713643, var2=15.30505947276798으로 서로 다름)

b_test, p_value = bartlett(rand1, rand3)
print(f"(rand1, rand3) - same variance: bartlett test: {b_test=}, {p_value=}")
## p_value=0.6456155103739873 -> 귀무가설 채택: 두개의 분산은 서로 같음(실제로 var1=0.9372251824713643, var3=0.9103389678864449로 서로 같음)

