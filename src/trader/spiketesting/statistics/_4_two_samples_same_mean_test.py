import unittest
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from bt4.utils.stat.stats import TTest


class MyTestCase(unittest.TestCase) :

    def test_ttest0(self) :
        '''
        [[실패 사례]]
        유사평균(0.5만큼 차이), 유사 분산
        결과: 평균이 다름 -> 정규성과, 등분산성 조건이 모두 성립되는  T-Test
              0.5 (분산 1의 절반 수준)만큼 차이 인데, 평균이 다르다고 판단함
        :return:
        '''

        ttest = TTest()

        rand1 = np.random.randn(1000) + 0.5
        # rand2 = 4.0 * np.random.randn(800) - 2.0
        rand3 = np.random.randn(1000)

        plt.figure(figsize = (20, 5))
        sns.kdeplot(data = rand1, color = "red", fill = True)
        # sns.kdeplot(data = rand2, color = "blue", fill = True)
        sns.kdeplot(data = rand3, color = "green", fill = True)

        plt.show()

        print(f"rand1 - mean:{np.mean(rand1)}")  ## mean:0.5377471028078171
        print(f"rand3 - mean:{np.mean(rand3)}")  ## mean:-0.011349386123920256
        var1 = np.var(rand1)
        var3 = np.var(rand3)
        print(f"{var1=}, {var3=}")      ## var1=0.9568422676479403, var3=1.001040984871747

        is_same, reason = ttest.perform(rand1, rand3)
        print(f"{is_same=}, {reason=}")
        ### 평균이 0.5 정도 차이나고 분산이 1정도 차이나는 상황에서 두개의 분산이 서로 다르다고 판단함
        ## Two samples's means seem to be DIFFERENT, (by T-Test with PASSED equal-variance test)
        ## 한 분산의 반절정도가 달라도 평균이 다르다고 판단함 -> 약간 너무 민감한 느낌이 있음

    def test_ttest01(self) :
        '''
        [[실패 사례]]
        유사평균(0.1만큼 차이), 유사 분산
        결과: 평균이 다름 -> 정규성과, 등분산성 조건이 모두 성립되는  T-Test
              평균이 0.1만큼 차이가 나도 다르다고 판단함 -> 너무나 작은 차이도 서로 다르다고 판단하는 듯한 느낌
              "Two samples's means seem to be DIFFERENT, (by T-Test with PASSED equal-variance test)"
        :return:
        '''

        ttest = TTest()

        rand1 = np.random.randn(1000) + 0.1
        # rand2 = 4.0 * np.random.randn(800) - 2.0
        rand3 = np.random.randn(1000)

        plt.figure(figsize = (20, 5))
        sns.kdeplot(data = rand1, color = "red", fill = True)
        # sns.kdeplot(data = rand2, color = "blue", fill = True)
        sns.kdeplot(data = rand3, color = "green", fill = True)

        plt.show()

        print(f"rand1 - mean:{np.mean(rand1)}")  ## mean:0.06932551282653293
        print(f"rand3 - mean:{np.mean(rand3)}")  ## mean:-0.04829674038581496
        var1 = np.var(rand1)
        var3 = np.var(rand3)
        print(f"{var1=}, {var3=}")      ## var1=1.0096835730927807, var3=0.9451423082061504

        is_same, reason = ttest.perform(rand1, rand3)
        print(f"{is_same=}, {reason=}")
        ## is_same=False, reason="Two samples's means seem to be DIFFERENT, (by T-Test with PASSED equal-variance test)"

    def test_ttest02(self) :
        '''
        [[성공 사례]]
        유사평균(0.05만큼 차이), 유사 분산
        결과: 평균이 같음 -> 정규성과, 등분산성 조건이 모두 성립되는  T-Test
                평균이 상당히 조금 차이 나고 분산이 거의 비슷해야 유사한 평균이라고 판단함
                너무 민감함
                "Two samples's means seem to be the SAME, (by T-Test with PASSED equal-variance test)"
        :return:
        '''

        ttest = TTest()

        rand1 = np.random.randn(1000) + 0.05
        print(f"rand1:{rand1[:20]}")
        # rand2 = 4.0 * np.random.randn(800) - 2.0
        rand3 = np.random.randn(1000)
        print(f"rand3: {rand3[:20]}")

        plt.figure(figsize = (20, 5))
        sns.kdeplot(data = rand1, color = "red", fill = True)
        # sns.kdeplot(data = rand2, color = "blue", fill = True)
        sns.kdeplot(data = rand3, color = "green", fill = True)

        plt.show()

        print(f"rand1 - mean:{np.mean(rand1)}")  ## mean:0.002275152584270845
        print(f"rand3 - mean:{np.mean(rand3)}")  ## mean:0.046221070776030056
        var1 = np.var(rand1)
        var3 = np.var(rand3)
        print(f"{var1=}, {var3=}")      ## var1=0.9261057213934277, var3=1.0126640782935699

        is_same, reason = ttest.perform(rand1, rand3)
        print(f"{is_same=}, {reason=}")
        ## is_same=True, reason="Two samples's means seem to be the SAME, (by T-Test with PASSED equal-variance test)"

    def test_ttest03(self) :
        '''
        [[실패 사례]]
        개수를 30개 정도로 줄여봄, 
        결과: 평균이 같음 -> 정규성과, 등분산성 조건이 모두 성립되는  T-Test
                개수: 30 -> 평균의 차이를 늘려보니 0.5정도 차이에서 때로는 동일하게, 떄로는 다른 평균을 갖고 있다고 판단함
                개수: 60 -> 평균의 차이가 0.3 정도면 두 집단이 동일하다고 판단하며, 0.3이상이면 두 집단이 다른 평균을 갖고 있다고 판단함
        :return:
        '''

        ttest = TTest()
        nums = 60
        rand1 = np.random.randn(nums) + 0.3
        print(f"rand1:{rand1[:20]}")
        # rand2 = 4.0 * np.random.randn(800) - 2.0
        rand3 = np.random.randn(nums)
        print(f"rand3: {rand3[:20]}")

        plt.figure(figsize = (20, 5))
        sns.kdeplot(data = rand1, color = "red", fill = True)
        # sns.kdeplot(data = rand2, color = "blue", fill = True)
        sns.kdeplot(data = rand3, color = "green", fill = True)

        plt.show()

        print(f"rand1 - mean:{np.mean(rand1)}")  ## mean:0.21564704780241417
        print(f"rand3 - mean:{np.mean(rand3)}")  ## mean:-0.1865104357681397
        var1 = np.var(rand1)
        var3 = np.var(rand3)
        print(f"{var1=}, {var3=}")      ## var1=1.0383286552181568, var3=1.0292737818346853

        is_same, reason = ttest.perform(rand1, rand3)
        print(f"{is_same=}, {reason=}")
        ## is_same=True, reason="Two samples's means seem to be the SAME, (by T-Test with PASSED equal-variance test)"

    '''
    분산 검정
    '''
    def test_ttest1(self) :
        '''
        [[실패 사례]]
        유사 평균 다른 분산
        결과: 평균은 거의 유사하나 분산이 서로 다름 -> (Bartlett's Equal Variance Test )
             is_same=False, reason="Two samples's variance seem to be DIFFERENT, (by Bartlett's Equal Variance Test)"
        :return:
        '''

        ttest = TTest()

        rand1 = np.random.randn(1000)
        rand2 = 4.0 * np.random.randn(800)
        # rand3 = np.random.randn(1000)

        plt.figure(figsize = (20, 5))
        sns.kdeplot(data = rand1, color = "red", fill = True)
        sns.kdeplot(data = rand2, color = "blue", fill = True)
        # sns.kdeplot(data = rand3, color = "green", fill = True)

        plt.show()

        print(f"rand1 - mean:{np.mean(rand1)}")  ## mean:-0.03698776015457822
        print(f"rand2 - mean:{np.mean(rand2)}")  ## mean:0.20773837107774257
        var1 = np.var(rand1)
        var2 = np.var(rand2)
        print(f"{var1=}, {var2=}")

        is_same, reason = ttest.perform(rand1, rand2)
        print(f"{is_same=}, {reason=}")


    def test_ttest10(self) :
        '''
        [[성공 사례]]
        유사 평균, 유사분산 (개수 1000개)

        결과: 평균은 거의 유사하나 분산이 서로 다름 -> (Bartlett's Equal Variance Test )
            분산이 0.05정도의 차이정도를 유사한 분산이라고 판단함 -> 너무 민감함
        :return:
        '''

        ttest = TTest()

        rand1 = np.random.randn(1000)
        rand2 = 1.05 * np.random.randn(1000)
        # rand3 = np.random.randn(1000)

        plt.figure(figsize = (20, 5))
        sns.kdeplot(data = rand1, color = "red", fill = True)
        sns.kdeplot(data = rand2, color = "blue", fill = True)
        # sns.kdeplot(data = rand3, color = "green", fill = True)

        plt.show()

        print(f"rand1 - mean:{np.mean(rand1)}")  ## mean:-0.03698776015457822
        print(f"rand2 - mean:{np.mean(rand2)}")  ## mean:0.20773837107774257
        var1 = np.var(rand1)
        var2 = np.var(rand2)
        print(f"{var1=}, {var2=}")

        is_same, reason = ttest.perform(rand1, rand2)
        print(f"{is_same=}, {reason=}")

    def test_ttest11(self) :
        '''
        [[성공 사례]]
        유사 평균, 유사분산 (개수 30개)

        결과: 평균은 거의 유사하나 분산이 서로 다름 -> (Bartlett's Equal Variance Test )
            분산이 0.4정도의 차이정도를 유사한 분산이라고 판단함
        :return:
        '''

        ttest = TTest()
        nums = 30
        rand1 = np.random.randn(nums)
        rand2 = 1.4 * np.random.randn(nums)
        # rand3 = np.random.randn(1000)

        plt.figure(figsize = (20, 5))
        sns.kdeplot(data = rand1, color = "red", fill = True)
        sns.kdeplot(data = rand2, color = "blue", fill = True)
        # sns.kdeplot(data = rand3, color = "green", fill = True)

        plt.show()

        print(f"rand1 - mean:{np.mean(rand1)}")  ## mean:-0.03698776015457822
        print(f"rand2 - mean:{np.mean(rand2)}")  ## mean:0.20773837107774257
        var1 = np.var(rand1)
        var2 = np.var(rand2)
        print(f"{var1=}, {var2=}")

        is_same, reason = ttest.perform(rand1, rand2)
        print(f"{is_same=}, {reason=}")
    def test_ttest2(self) :
        '''
        [[성공 사례]]
        유사 평균 (0.3), 유사분산 (1.3) (개수 30개)
        기대: 두집단은 비슷하다고 판단할것이라 예상
        결과: 평균은 거의 유사하나 분산이 서로 다름 -> (Bartlett's Equal Variance Test )
             경우에 따라서, 동일 평균을 가졌다, 안가졌다함.
        :return:
        '''

        ttest = TTest()
        nums = 30
        rand1 = np.random.randn(nums) + 0.3
        rand3 = 1.3 * np.random.randn(1000)

        plt.figure(figsize = (20, 5))
        sns.kdeplot(data = rand1, color = "red", fill = True)
        sns.kdeplot(data = rand3, color = "green", fill = True)

        plt.show()

        print(f"rand1 - mean:{np.mean(rand1)}")  ## mean:2.9674869361216873
        print(f"rand3 - mean:{np.mean(rand3)}")  ## mean:-1.927478424341723
        var1 = np.var(rand1)
        var3 = np.var(rand3)
        print(f"{var1=}, {var3=}")

        is_same, reason = ttest.perform(rand1, rand3)
        print(f"{is_same=}, {reason=}")


if __name__ == '__main__' :
    unittest.main()
