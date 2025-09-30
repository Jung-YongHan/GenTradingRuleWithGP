# gp_setup/domain.py

import random

from config import (
    CDL_TYPES,
    INDICATOR_DEFINITIONS,
    INDICATORS_COUNT,
    OHLCV_SOURCES,
    OPERATORS,
)
from utils.parsing import extract_base_from_access_name, extract_base_indicator_name


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
        self.indicator_counters = {}  # 지표별 카운터 관리
        self.condition_counters = {}  # 조건별 카운터 관리

        # 1. 먼저 vars 생성 (config에서 설정된 개수)
        self.vars_dict = self.generate_vars(INDICATORS_COUNT)

        # 2. 생성된 vars에서 지표 이름들 추출
        available_indicators = list(self.vars_dict.keys())

        # 3. 사용 가능한 지표들로 조건들 생성
        for i in range(num_conditions):
            self.buy_pool[f"buy_system{i + 1}"] = (
                self._create_condition_from_indicators(available_indicators, i + 1)
            )
            self.sell_pool[f"sell_system{i + 1}"] = (
                self._create_condition_from_indicators(available_indicators, i + 1)
            )

    def _get_unique_indicator_name(self, indicator_name):
        """지표별 고유 이름 생성 (SMA1, SMA2, MACD1, ...)"""
        if indicator_name not in self.indicator_counters:
            self.indicator_counters[indicator_name] = 1

        self.indicator_counters[indicator_name] += 1
        return f"{indicator_name}{self.indicator_counters[indicator_name]}"

    def _generate_sources_for_indicator(self, indicator_name):
        """지표에 맞는 sources 생성"""
        indicator_def = INDICATOR_DEFINITIONS.get(indicator_name)
        if not indicator_def:
            return ["close"]  # 기본값

        sources_config = indicator_def["sources"]
        if sources_config["fixed"] is not None:
            # 고정된 sources 사용
            return sources_config["fixed"]
        else:
            # allowed에서 랜덤 선택
            allowed_sources = sources_config["allowed"]
            count = sources_config["count"]
            return random.sample(allowed_sources, min(count, len(allowed_sources)))

    def _generate_all_params_for_indicator(self, indicator_name):
        """지표에 맞는 모든 파라미터 생성"""
        indicator_def = INDICATOR_DEFINITIONS.get(indicator_name)
        if not indicator_def:
            return [14]  # 기본값

        param_types = indicator_def.get("param_types", [])
        if param_types:
            params = []
            for param_type_def in param_types:
                if param_type_def["type"] == "int":
                    params.append(
                        random.randint(param_type_def["min"], param_type_def["max"])
                    )
                elif param_type_def["type"] == "float":
                    params.append(
                        round(
                            random.uniform(
                                param_type_def["min"], param_type_def["max"]
                            ),
                            2,
                        )
                    )
                elif param_type_def["type"] == "category":
                    params.append(random.choice(param_type_def["values"]))
                else:
                    params.append(14)
            return params
        else:
            return [14]

    def _create_random_condition(self):
        """랜덤 조건 생성"""
        # 지표 선택
        indicator = random.choice(list(INDICATOR_DEFINITIONS.keys()))

        # 지표별 고유 이름 생성
        unique_indicator_name = self._get_unique_indicator_name(indicator)

        # 지표에 맞는 sources 생성
        sources = self._generate_sources_for_indicator(indicator)

        # 지표에 맞는 파라미터 생성
        params = self._generate_all_params_for_indicator(indicator)

        # 연산자와 피연산자 생성
        op_func = random.choice(OPERATORS)

        # left와 right 피연산자로 다른 지표들 선택
        all_indicators = list(INDICATOR_DEFINITIONS.keys())
        left_indicator = random.choice(all_indicators)
        right_indicator = random.choice(all_indicators)

        # 피연산자용 고유 이름 생성
        left_name = self._get_unique_indicator_name(left_indicator)
        right_name = self._get_unique_indicator_name(right_indicator)

        condition = {
            "indicator": unique_indicator_name,  # 고유 이름 사용
            "sources": sources,  # 배열로 저장
            "params": params,  # 배열로 저장
            "op": op_func.__name__,
            "left": left_name,
            "right": right_name,
        }

        # 예시
        # {
        #    "indicator": "RSI1",
        #    "sources": ["close"],
        #    "params": [14],
        #    "op": "gt",
        #    "left": "SMA2",
        #    "right": "MACD3"
        # }

        return condition

    def generate_vars(self, n):
        """랜덤으로 vars 생성"""
        vars_dict = {}
        for _ in range(n):
            # 지표 선택
            indicator = random.choice(list(INDICATOR_DEFINITIONS.keys()))
            unique_indicator_name = self._get_unique_indicator_name(indicator)

            # 지표에 맞는 sources 생성
            sources = self._generate_sources_for_indicator(indicator)

            # 지표에 맞는 파라미터 생성
            params = self._generate_all_params_for_indicator(indicator)

            # 지표에 맞는 캔들 타입 생성
            cdl_type = self._generate_cdl_type_for_indicator()

            # vars에 추가
            base_indicator_name = extract_base_indicator_name(unique_indicator_name)
            indicator_def = INDICATOR_DEFINITIONS.get(base_indicator_name)

            vars_dict[unique_indicator_name] = {
                "func": indicator_def["func"],
                "params": params,
                "cdl_type": cdl_type,
                "sources": sources,
                "unary": indicator_def["unary"],
            }

        return vars_dict

    def _generate_cdl_type_for_indicator(self):
        """지표에 맞는 캔들 타입 생성"""
        return random.choice(CDL_TYPES)

    def _create_condition_from_indicators(self, available_indicators, index):
        """사용 가능한 지표들로 조건 생성"""
        if len(available_indicators) < 2:
            # 지표가 2개 미만이면 기본 조건 생성
            return self._create_random_condition()

        # 연산자 선택
        op_func = random.choice(OPERATORS)

        # left와 right 피연산자 선택 (지표 또는 OHLCV 데이터)
        left_operand = self._get_random_operand(available_indicators)
        right_operand = self._get_random_operand(available_indicators)

        # 고유한 조건 이름 생성
        condition_name = f"system{index}"
        self.condition_counters[condition_name] = 1

        # op는 문자열로 저장
        op_name = op_func

        condition = {
            "alias": condition_name,
            "op": op_name,
            "left": left_operand,
            "right": right_operand,
        }

        return condition

    def _get_random_operand(self, available_indicators):
        """랜덤으로 지표 또는 OHLCV 데이터를 선택하여 반환"""
        # 50% 확률로 지표 또는 OHLCV 데이터 선택
        if random.choice([True, False]):
            # 지표 선택
            indicator = random.choice(available_indicators)
            return self._get_indicator_access_name(indicator)
        else:
            # OHLCV 데이터 선택
            return random.choice(OHLCV_SOURCES)

    def _get_indicator_access_name(self, indicator_name):
        """지표의 unary 속성에 따라 접근 이름을 반환"""
        # 고유 이름에서 원본 지표 이름 추출
        base_indicator_name = extract_base_indicator_name(indicator_name)
        indicator_def = INDICATOR_DEFINITIONS.get(base_indicator_name)

        if not indicator_def:
            return indicator_name  # 기본값

        if indicator_def["unary"]:
            # unary=True: 그냥 지표 이름 사용 (예: "RSI1")
            return indicator_name
        else:
            # unary=False: return_count에 따라 랜덤 인덱스로 접근
            return_count = indicator_def.get("return_count", 1)
            random_index = random.randint(0, return_count - 1)
            return f"{indicator_name}[{random_index}]"

    def remove_unused_indicators(self, used_indicators):
        """사용되지 않은 지표들을 vars_dict에서 제거"""
        # 사용된 지표들만 남기기
        self.vars_dict = {
            indicator_name: indicator_data
            for indicator_name, indicator_data in self.vars_dict.items()
            if indicator_name in used_indicators
        }

        # 사용된 지표들로 buy_pool과 sell_pool도 업데이트
        self._update_conditions_with_used_indicators(used_indicators)

    def _update_conditions_with_used_indicators(self, used_indicators):
        """사용된 지표들로 조건들을 업데이트"""
        # buy_pool 업데이트
        for condition_name, condition_data in self.buy_pool.items():
            # left 업데이트
            left_base = extract_base_from_access_name(condition_data["left"])
            if left_base not in used_indicators and left_base not in OHLCV_SOURCES:
                if random.choice([True, False]):
                    new_left = random.choice(used_indicators)
                    condition_data["left"] = self._get_indicator_access_name(new_left)
                else:
                    condition_data["left"] = random.choice(OHLCV_SOURCES)

            # right 업데이트
            right_base = extract_base_from_access_name(condition_data["right"])
            if right_base not in used_indicators and right_base not in OHLCV_SOURCES:
                if random.choice([True, False]):
                    new_right = random.choice(used_indicators)
                    condition_data["right"] = self._get_indicator_access_name(new_right)
                else:
                    condition_data["right"] = random.choice(OHLCV_SOURCES)

        # sell_pool 업데이트
        for condition_name, condition_data in self.sell_pool.items():
            # left 업데이트
            left_base = extract_base_from_access_name(condition_data["left"])
            if left_base not in used_indicators and left_base not in OHLCV_SOURCES:
                if random.choice([True, False]):
                    new_left = random.choice(used_indicators)
                    condition_data["left"] = self._get_indicator_access_name(new_left)
                else:
                    condition_data["left"] = random.choice(OHLCV_SOURCES)

            # right 업데이트
            right_base = extract_base_from_access_name(condition_data["right"])
            if right_base not in used_indicators and right_base not in OHLCV_SOURCES:
                if random.choice([True, False]):
                    new_right = random.choice(used_indicators)
                    condition_data["right"] = self._get_indicator_access_name(new_right)
                else:
                    condition_data["right"] = random.choice(OHLCV_SOURCES)
