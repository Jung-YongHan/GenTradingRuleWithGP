# after/domain/indicator.py
"""지표 생성/관리.

최적화: ``random.choice(list(INDICATOR_DEFINITIONS.keys()))`` 처럼 호출마다 리스트를
새로 만들던 부분을 모듈 로드 시 1회 계산한 ``INDICATOR_NAMES`` 재사용으로 대체한다.
(리스트 순서·길이가 동일하므로 ``random.choice`` 결과는 원본과 동일 → 재현성 유지.)
"""

from __future__ import annotations

import random

from src.after.configs.indicator_configs import (
    CDL_TYPES,
    INDICATOR_DEFINITIONS,
    INDICATOR_NAMES,
)
from src.after.utils.helpers import extract_base_indicator_name


class IndicatorGenerator:
    """지표 생성 및 관리를 담당하는 클래스"""

    def __init__(self):
        self.indicator_counters = {}

    def get_unique_indicator_name(self, indicator_name):
        """지표별 고유 이름 생성 (SMA1, SMA2, MACD1, ...)"""
        count = self.indicator_counters.get(indicator_name, 0) + 1
        self.indicator_counters[indicator_name] = count
        return f"{indicator_name}{count}"

    def generate_sources_for_indicator(self, indicator_name):
        """지표에 맞는 sources 생성"""
        indicator_def = INDICATOR_DEFINITIONS.get(indicator_name)
        if not indicator_def:
            return ["close"]

        sources_config = indicator_def["sources"]
        if sources_config["fixed"] is not None:
            return sources_config["fixed"]
        allowed_sources = sources_config["allowed"]
        count = sources_config["count"]
        return random.sample(allowed_sources, min(count, len(allowed_sources)))

    def generate_all_params_for_indicator(self, indicator_name):
        """지표에 맞는 모든 파라미터 생성"""
        indicator_def = INDICATOR_DEFINITIONS.get(indicator_name)
        if not indicator_def:
            return [14]

        param_types = indicator_def.get("param_types", [])
        if not param_types:
            return [14]

        params = []
        for param_type_def in param_types:
            ptype = param_type_def["type"]
            if ptype == "int":
                params.append(random.randint(param_type_def["min"], param_type_def["max"]))
            elif ptype == "float":
                params.append(
                    round(random.uniform(param_type_def["min"], param_type_def["max"]), 2)
                )
            elif ptype == "category":
                params.append(random.choice(param_type_def["values"]))
            else:
                params.append(14)
        return params

    def generate_cdl_type_for_indicator(self):
        """지표에 맞는 캔들 타입 생성"""
        return random.choice(CDL_TYPES)

    def generate_vars(self, n):
        """랜덤으로 vars 생성"""
        vars_dict = {}
        for _ in range(n):
            indicator = random.choice(INDICATOR_NAMES)
            unique_indicator_name = self.get_unique_indicator_name(indicator)
            sources = self.generate_sources_for_indicator(indicator)
            params = self.generate_all_params_for_indicator(indicator)
            cdl_type = self.generate_cdl_type_for_indicator()

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
