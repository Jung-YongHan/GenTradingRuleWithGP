# domain/indicator.py

import random

from src.before.configs.indicator_configs import CDL_TYPES, INDICATOR_DEFINITIONS


class IndicatorGenerator:
    """지표 생성 및 관리를 담당하는 클래스"""

    def __init__(self):
        self.indicator_counters = {}  # 지표별 카운터 관리

    def get_unique_indicator_name(self, indicator_name):
        """지표별 고유 이름 생성 (SMA1, SMA2, MACD1, ...)"""
        if indicator_name not in self.indicator_counters:
            self.indicator_counters[indicator_name] = 0

        self.indicator_counters[indicator_name] += 1
        return f"{indicator_name}{self.indicator_counters[indicator_name]}"

    def generate_sources_for_indicator(self, indicator_name):
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

    def generate_all_params_for_indicator(self, indicator_name):
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

    def generate_cdl_type_for_indicator(self):
        """지표에 맞는 캔들 타입 생성"""
        return random.choice(CDL_TYPES)

    def generate_vars(self, n):
        """랜덤으로 vars 생성"""
        from src.before.utils.helpers import extract_base_indicator_name

        vars_dict = {}
        for _ in range(n):
            # 지표 선택
            indicator = random.choice(list(INDICATOR_DEFINITIONS.keys()))
            unique_indicator_name = self.get_unique_indicator_name(indicator)

            # 지표에 맞는 sources 생성
            sources = self.generate_sources_for_indicator(indicator)

            # 지표에 맞는 파라미터 생성
            params = self.generate_all_params_for_indicator(indicator)

            # 지표에 맞는 캔들 타입 생성
            cdl_type = self.generate_cdl_type_for_indicator()

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
