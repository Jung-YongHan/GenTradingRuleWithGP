
## https://blog.naver.com/breezehome50/222324249905
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

rand1 = np.random.randn(1000) + 3.0
rand2 = 4.0 * np.random.randn(800) - 2.0
rand3 = np.random.randn(1000)

plt.figure(figsize = (20,5))
sns.kdeplot(data=rand1, color="red", fill = True)
sns.kdeplot(data=rand2, color="blue", fill = True)
sns.kdeplot(data=rand3, color="green", fill = True)

plt.show()

####################################################################
## One-Sample T-Test : 특정 집단의 평균이 N임을 테스트
from scipy import stats
## H0: mean = 3(귀무가설), H1: Mean != 3(대립가설)
print(f"mean:{np.mean(rand1)}") ## mean:2.993582369815334
t_stat, p_val = stats.ttest_1samp(rand1, 3)                 ## 귀무가설을 기술
print(f"t-statistics: {t_stat}, p-value: {p_val}")
# p-value: 0.5743600327426581 이므로 P<0.05이면 H1을 채택,
# 하지만 아니므로 H0을 채택하게됨
# 즉 평균이 3이라고 할수 있음. 실제로도 평균은 3임

####################################################################
## One-Sample T-Test : 특정 집단의 평균이 N보다 크다(작다)를 테스트
## H0: mean > 3(귀무가설), H1: Mean !> 3(대립가설)
t_stat, p_val = stats.ttest_1samp(rand1, 3, alternative = "greater") ## 여기에 대립가설을 기술!?
print(f"t-statistics: {t_stat}, p-value: {p_val}")
## p-value: 0.6217175036955089 이므로 H0를 기각하지 못함
## 평균이 3보다 크다고 할수도 있음

## 아래는 5보다 크다! 라고 한다면?
## H0: mean !> 5(귀무가설), H1: Mean > 5(대립가설)
t_stat, p_val = stats.ttest_1samp(rand1, 5, alternative = "greater") ## 여기에 대립가설을 기술!
print(f"t-statistics: {t_stat}, p-value: {p_val}")
## p-value: 1.0이라면 평균이 5보다 크지 않다(귀무가설) 채택

## H0: mean !> 2(귀무가설), H1: Mean > 2(대립가설)
t_stat, p_val = stats.ttest_1samp(rand1, 2, alternative = "greater") ## 여기에 대립가설을 기술!
print(f"t-statistics: {t_stat}, p-value: {p_val}")
## p-value: 5.051172886648245e-156이라면 평균이 2보다 크다(대립가설 채택)


####################################################################
## One-Sample T-Test : 두 표본 집단의 평균이 같은지 평가

print(f"rand1 - mean:{np.mean(rand1)}") ## mean:2.9674869361216873
print(f"rand2 - mean:{np.mean(rand2)}") ## mean:-1.927478424341723

## H0: mean1 = mean2(귀무가설), H1: Mean1 != Mean2(대립가설)
## 두 Group의 분산이 같다라고 전제하고 있음 "equal_var=True"
## 양측 검정 수행
t_stat, p_val = stats.ttest_ind(rand1, rand2, equal_var = True, alternative = "two-sided") ## 여기에 대립가설을 기술!
print(f"t-statistics: {t_stat}, p-value: {p_val}")
# p-value: 4.39615035016493e-229가 0.05보다 작기 때문에 두 집단간의 평균이 다르다고 판단

#####################################
## 두 집단간의 평균이 N만큼 차이가 나는지 검정
mean1 = np.mean(rand1)
mean2 = np.mean(rand2)
print(f"rand1 - mean:{mean1}") ## mean:2.9674869361216873
print(f"rand2 - mean:{mean2}") ## mean:-1.927478424341723

t_stat, p_val = stats.ttest_ind(rand1, rand2+(mean1-mean2), equal_var = True, alternative = "two-sided") ## 여기에 대립가설을 기술!
print(f"t-statistics: {t_stat}, p-value: {p_val}")
## 분산이 서로 다름에도 p-value: 0.9999999999999973 이렇게 나와서 두 집단은 동일하다고 판단함 -> 이래도 되나?

print(f"rand1 - stdev:{np.std(rand1)}") ## mean:2.9674869361216873
print(f"rand2 - stdev:{np.std(rand2)}") ## mean:-1.927478424341723
## Equal_var = False로 설정
t_stat, p_val = stats.ttest_ind(rand1, rand2+(mean1-mean2), equal_var = False, alternative = "two-sided") ## 여기에 대립가설을 기술!
print(f"t-statistics: {t_stat}, p-value: {p_val}")
## 그럼에도 p-value: 0.9999999999999977 두개의 평균은 동일하다고 나옴
