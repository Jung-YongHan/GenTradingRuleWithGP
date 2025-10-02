# strategy/formatter.py

import re

from src.configs.indicator_configs import OHLCV_SOURCES
from src.utils.helpers import extract_base_from_access_name, extract_base_indicator_name


def filter_used_systems(systems_dict, system_op):
    """system_op에서 실제로 사용되는 시스템들만 필터링하고 번호를 1부터 재정렬"""
    if not system_op or system_op.strip() == "":
        return {}, {}

    # system_op에서 사용되는 시스템 번호들 추출
    used_systems = set()
    pattern = r"system(\d+)"
    matches = re.findall(pattern, system_op)
    for match in matches:
        used_systems.add(f"system{match}")

    # 사용되는 시스템들만 필터링하고 번호를 1부터 재정렬
    filtered_systems = {}
    system_mapping = {}  # 원래 번호 -> 새 번호 매핑
    new_index = 1

    for system_name, system_data in systems_dict.items():
        if system_name in used_systems:
            new_system_name = f"system{new_index}"
            system_mapping[system_name] = new_system_name

            # 새로운 시스템 데이터 생성 (alias도 업데이트)
            new_system_data = system_data.copy()
            new_system_data["alias"] = new_system_name
            filtered_systems[new_system_name] = new_system_data
            new_index += 1

    return filtered_systems, system_mapping


def update_system_numbers(system_op, system_mapping):
    """system_op에서 시스템 번호를 새로운 번호로 업데이트"""
    if not system_op or not system_mapping:
        return system_op

    # system_op에서 시스템 번호를 새로운 번호로 교체
    updated_op = system_op
    for old_system, new_system in system_mapping.items():
        # system25 -> system1 같은 패턴으로 교체
        pattern = re.escape(old_system)
        updated_op = re.sub(pattern, new_system, updated_op)

    return updated_op


def filter_used_indicators(vars_dict, buy_systems, sell_systems):
    """buy_systems와 sell_systems에서 실제로 사용되는 지표들만 필터링하고 번호를 1부터 재정렬"""
    used_indicators = set()

    # buy_systems에서 사용되는 지표들 추출
    for system_data in buy_systems.values():
        left_base = extract_base_from_access_name(system_data["left"])
        right_base = extract_base_from_access_name(system_data["right"])

        if left_base not in OHLCV_SOURCES and not left_base.isdigit():
            used_indicators.add(left_base)
        if right_base not in OHLCV_SOURCES and not right_base.isdigit():
            used_indicators.add(right_base)

    # sell_systems에서 사용되는 지표들 추출
    for system_data in sell_systems.values():
        left_base = extract_base_from_access_name(system_data["left"])
        right_base = extract_base_from_access_name(system_data["right"])

        if left_base not in OHLCV_SOURCES and not left_base.isdigit():
            used_indicators.add(left_base)
        if right_base not in OHLCV_SOURCES and not right_base.isdigit():
            used_indicators.add(right_base)

    # 사용되는 지표들을 기본 지표명별로 그룹화
    indicator_groups = {}
    for indicator_name in used_indicators:
        base_name = extract_base_indicator_name(indicator_name)
        if base_name not in indicator_groups:
            indicator_groups[base_name] = []
        indicator_groups[base_name].append(indicator_name)

    # 각 그룹별로 번호를 1부터 재정렬
    filtered_vars = {}
    indicator_mapping = {}  # 원래 이름 -> 새 이름 매핑

    for base_name, indicator_list in indicator_groups.items():
        # 같은 기본 지표명의 지표들을 정렬
        indicator_list.sort()

        for i, old_name in enumerate(indicator_list, 1):
            new_name = f"{base_name}{i}"
            indicator_mapping[old_name] = new_name
            filtered_vars[new_name] = vars_dict[old_name]

    return filtered_vars, indicator_mapping


def update_indicator_names(systems_dict, indicator_mapping):
    """시스템의 지표 이름을 새로운 이름으로 업데이트"""
    updated_systems = {}

    for system_name, system_data in systems_dict.items():
        updated_system = system_data.copy()

        # left와 right의 지표 이름 업데이트
        left_operand = system_data["left"]
        right_operand = system_data["right"]

        # left 업데이트
        if "[" in left_operand:
            # MACD1[0] 형태인 경우
            base_name = left_operand.split("[")[0]
            index_part = left_operand.split("[")[1]
            if base_name in indicator_mapping:
                updated_system["left"] = f"{indicator_mapping[base_name]}[{index_part}"
        else:
            # RSI1 형태인 경우
            if left_operand in indicator_mapping:
                updated_system["left"] = indicator_mapping[left_operand]

        # right 업데이트
        if "[" in right_operand:
            # MACD1[0] 형태인 경우
            base_name = right_operand.split("[")[0]
            index_part = right_operand.split("[")[1]
            if base_name in indicator_mapping:
                updated_system["right"] = f"{indicator_mapping[base_name]}[{index_part}"
        else:
            # RSI1 형태인 경우
            if right_operand in indicator_mapping:
                updated_system["right"] = indicator_mapping[right_operand]

        updated_systems[system_name] = updated_system

    return updated_systems
