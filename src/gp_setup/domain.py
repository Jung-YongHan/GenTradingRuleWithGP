# gp_setup/domain.py

import random

from config import INDICATORS, NUM_INDICATOR_PARAMS, OPS, SOURCES


# --- GP의 핵심 타입을 이곳에서 정의 ---
class BuyType:
    pass


class SellType:
    pass


def Strategy(buy_logic, sell_logic):
    return (buy_logic, sell_logic)


# --- 핵심 도메인 클래스 ---
class ConditionManager:
    """매수/매도 조건을 미리 생성하고 관리하는 클래스"""

    def __init__(self, num_conditions):
        self.buy_pool = {}
        self.sell_pool = {}
        self.generate_conditions(num_conditions)

    def _create_random_condition(self):
        indicator = random.choice(INDICATORS)
        source = random.choice(SOURCES)
        param = random.choice(NUM_INDICATOR_PARAMS)
        op_func = random.choice(OPS)
        value = random.uniform(1, 100)
        return {
            "indicator": indicator,
            "source": source,
            "param": param,
            "op": op_func.__name__,
            "value": round(value, 2),
        }

    def generate_conditions(self, n):
        for i in range(n):
            self.buy_pool[f"buy_system{i + 1}"] = self._create_random_condition()
            self.sell_pool[f"sell_system{i + 1}"] = self._create_random_condition()
