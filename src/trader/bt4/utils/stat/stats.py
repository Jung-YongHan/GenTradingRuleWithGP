from scipy import stats
from scipy.stats import mannwhitneyu, bartlett, skew, kurtosis


class TTest:
    def __init__(self):
        pass

    def perform(self, sample1, sample2):
        ## 1, normality test
        norm_test_result = self.__normality_test__(sample1, sample2)
        if not norm_test_result :
            ## 1.1 Mann-Whitney U-test
            _, p_mwtest = mannwhitneyu(sample1, sample2)
            if p_mwtest > 0.05:
                return True, "Two samples's means seem to be the SAME (by Mann-Whitney U-test, without normality)"
            else:
                return False, "Two samples's means seem to be DIFFERENT (by Mann-Whitney U-test, without normality)"

        ## 2. equal-variance test
        _, p_barlett  = bartlett(sample1, sample2)
        is_equal_variance = True
        if p_barlett < 0.05: ## Different Variance
            is_equal_variance = False
            # return False, f"Two samples's variance seem to be DIFFERENT, (by Bartlett's Equal Variance Test)"

        ev_log = "PASSED" if is_equal_variance is True else "NOT passed"
        _, p_ttest = stats.ttest_ind(sample1, sample2, equal_var = is_equal_variance,
                                        alternative = "two-sided")  ## 여기에 대립가설을 기술!

        if p_ttest > 0.05:
            return True, f"Two samples's means seem to be the SAME, (by T-Test with {ev_log} equal-variance test(welch's t-test))"
        else:
            return False, f"Two samples's means seem to be DIFFERENT, (by T-Test with {ev_log} equal-variance test)"

    def __normality_test__(self, sample1, sample2):
        ## 1. Shaprio_wilks test
        _, p_stest1 = stats.shapiro(sample1)
        _, p_stest2 = stats.shapiro(sample2)
        if p_stest1 > 0.05 and p_stest2 > 0.05:
            return True

        ## 2. Kolmogoroe-Smirnov test
        _, p_kstest1 = stats.kstest(sample1, 'norm')
        _, p_kstest2 = stats.kstest(sample2, 'norm')
        if p_kstest1 > 0.05 and p_kstest2 > 0.05:
            return True

        s1_skew = skew(sample1)  # 왜도
        s1_kurto = kurtosis(sample1, fisher = True)  # 첨도
        s2_skew = skew(sample2)  # 왜도
        s2_kurto = kurtosis(sample2, fisher = True)  # 첨도

        if (s1_skew < 2 and s1_kurto < 7) and (s2_skew < 2 and s2_kurto < 7):
            return True
        else:
            return False
