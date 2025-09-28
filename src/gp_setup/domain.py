# gp_setup/domain.py

import random

from config import INDICATOR_PARAMS, INDICATORS, OPERATORS, SOURCES


# --- GP의 핵심 타입을 이곳에서 정의 ---
class BuyType:
    """매수 조건 또는 규칙 타입"""

    pass


class SellType:
    """매도 조건 또는 규칙 타입"""

    pass


def Strategy(buy_logic: BuyType, sell_logic: SellType):
    """전략 타입"""
    return (buy_logic, sell_logic)


# --- 핵심 도메인 클래스 ---
class ConditionManager:
    """매수/매도 조건을 미리 생성하고 관리하는 클래스"""

    def __init__(self, num_conditions):
        """초기화"""
        self.buy_pool = {}
        self.sell_pool = {}
        self.generate_conditions(num_conditions)

    def _create_random_condition(self):
        """랜덤 조건 생성"""
        indicator = random.choice(INDICATORS)
        source = random.choice(SOURCES)
        param = random.choice(INDICATOR_PARAMS)
        op_func = random.choice(OPERATORS)
        value = random.uniform(1, 100)

        condition = {
            "indicator": indicator,
            "source": source,
            "param": param,
            "op": op_func.__name__,
            "value": round(value, 2),
        }

        # 예시
        # {
        #    "indicator": "RSI",
        #    "source": "close",
        #    "param": 14,
        #    "op": "gt",
        #    "value": 70
        # }

        return condition

    def generate_conditions(self, n):
        """조건 생성"""
        for i in range(n):
            self.buy_pool[f"buy_system{i + 1}"] = self._create_random_condition()
            self.sell_pool[f"sell_system{i + 1}"] = self._create_random_condition()
