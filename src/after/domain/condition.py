# after/domain/condition.py
"""매수/매도 조건 풀 생성·관리.

최적화: membership test 에 ``OHLCV_SOURCES_SET`` (frozenset) 사용. ``random.choice`` 가
필요한 곳은 순서 리스트(``OHLCV_SOURCES``/``OPERATORS``/``INDICATOR_NAMES``)를 그대로 써서
원본과 동일한 난수열을 보장(재현성).
"""

from __future__ import annotations

import random

from src.after.configs.indicator_configs import (
    INDICATOR_DEFINITIONS,
    INDICATOR_NAMES,
    OHLCV_SOURCES,
    OHLCV_SOURCES_SET,
    OPERATORS,
)
from src.after.utils.helpers import (
    extract_base_from_access_name,
    extract_base_indicator_name,
)

from .indicator import IndicatorGenerator


class ConditionManager:
    """매수/매도 조건을 미리 생성하고 관리하는 클래스"""

    def __init__(self, num_conditions, num_indicators):
        self.buy_pool = {}
        self.sell_pool = {}
        self.condition_counters = {}
        self.indicator_generator = IndicatorGenerator()

        self.vars_dict = self.indicator_generator.generate_vars(num_indicators)
        available_indicators = list(self.vars_dict.keys())

        for i in range(num_conditions):
            self.buy_pool[f"buy_system{i + 1}"] = (
                self._create_condition_from_indicators(available_indicators, i + 1)
            )
            self.sell_pool[f"sell_system{i + 1}"] = (
                self._create_condition_from_indicators(available_indicators, i + 1)
            )

    def _create_condition_from_indicators(self, available_indicators, index):
        if len(available_indicators) < 2:
            return self._create_random_condition()

        op_func = random.choice(OPERATORS)
        left_operand = self._get_random_operand(available_indicators)
        right_operand = self._get_random_operand(available_indicators)

        condition_name = f"system{index}"
        self.condition_counters[condition_name] = 1
        return {
            "alias": condition_name,
            "op": op_func,
            "left": left_operand,
            "right": right_operand,
        }

    def _get_random_operand(self, available_indicators):
        if random.choice([True, False]):
            indicator = random.choice(available_indicators)
            return self._get_indicator_access_name(indicator)
        return random.choice(OHLCV_SOURCES)

    def _get_indicator_access_name(self, indicator_name):
        base_indicator_name = extract_base_indicator_name(indicator_name)
        indicator_def = INDICATOR_DEFINITIONS.get(base_indicator_name)
        if not indicator_def:
            return indicator_name

        if indicator_def["unary"]:
            return indicator_name
        return_count = indicator_def.get("return_count", 1)
        random_index = random.randint(0, return_count - 1)
        return f"{indicator_name}[{random_index}]"

    def _create_random_condition(self):
        indicator = random.choice(INDICATOR_NAMES)
        unique_indicator_name = self.indicator_generator.get_unique_indicator_name(
            indicator
        )
        sources = self.indicator_generator.generate_sources_for_indicator(indicator)
        params = self.indicator_generator.generate_all_params_for_indicator(indicator)
        op_func = random.choice(OPERATORS)

        left_indicator = random.choice(INDICATOR_NAMES)
        right_indicator = random.choice(INDICATOR_NAMES)
        left_name = self.indicator_generator.get_unique_indicator_name(left_indicator)
        right_name = self.indicator_generator.get_unique_indicator_name(right_indicator)
        return {
            "indicator": unique_indicator_name,
            "sources": sources,
            "params": params,
            "op": op_func,
            "left": left_name,
            "right": right_name,
        }

    def remove_unused_indicators(self, used_indicators):
        """사용되지 않은 지표들을 vars_dict에서 제거"""
        self.vars_dict = {
            name: data
            for name, data in self.vars_dict.items()
            if name in used_indicators
        }
        self._update_conditions_with_used_indicators(used_indicators)

    def _update_conditions_with_used_indicators(self, used_indicators):
        used_set = set(used_indicators)
        used_list = list(used_set)
        for pool in (self.buy_pool, self.sell_pool):
            for condition_data in pool.values():
                for side in ("left", "right"):
                    base = extract_base_from_access_name(condition_data[side])
                    if base not in used_set and base not in OHLCV_SOURCES_SET:
                        if random.choice([True, False]):
                            new_ind = random.choice(used_list)
                            condition_data[side] = self._get_indicator_access_name(new_ind)
                        else:
                            condition_data[side] = random.choice(OHLCV_SOURCES)
