# after/strategy/formatter.py
"""사용된 시스템/지표 필터링 및 번호 재정렬.

최적화
------
* ``system(\\d+)`` 패턴을 모듈 로드 시 1회 컴파일.
* 지표 그룹화에 ``collections.defaultdict(list)`` 사용(원본의
  ``if k not in d: d[k] = []`` 관용구 제거). 그룹 내 정렬·번호 재부여 로직은 동일하므로
  결과 매핑은 원본과 같다.
"""

from __future__ import annotations

import re
from collections import defaultdict

from src.after.configs.indicator_configs import OHLCV_SOURCES_SET
from src.after.utils.helpers import (
    extract_base_from_access_name,
    extract_base_indicator_name,
)

_RE_SYSTEM = re.compile(r"system(\d+)")


def filter_used_systems(systems_dict, system_op):
    """system_op 에서 실제 사용되는 시스템만 남기고 1번부터 재정렬."""
    if not system_op or not system_op.strip():
        return {}, {}

    used_systems = {f"system{m}" for m in _RE_SYSTEM.findall(system_op)}

    filtered_systems = {}
    system_mapping = {}
    new_index = 1
    for system_name, system_data in systems_dict.items():
        if system_name in used_systems:
            new_system_name = f"system{new_index}"
            system_mapping[system_name] = new_system_name
            new_system_data = system_data.copy()
            new_system_data["alias"] = new_system_name
            filtered_systems[new_system_name] = new_system_data
            new_index += 1
    return filtered_systems, system_mapping


def update_system_numbers(system_op, system_mapping):
    """system_op 의 시스템 번호를 새 번호로 치환."""
    if not system_op or not system_mapping:
        return system_op
    updated_op = system_op
    for old_system, new_system in system_mapping.items():
        updated_op = re.sub(re.escape(old_system), new_system, updated_op)
    return updated_op


def filter_used_indicators(vars_dict, buy_systems, sell_systems):
    """buy/sell 시스템에서 실제 사용된 지표만 남기고 기본지표명별 1번부터 재정렬."""
    used_indicators = set()
    for systems in (buy_systems, sell_systems):
        for system_data in systems.values():
            for side in ("left", "right"):
                base = extract_base_from_access_name(system_data[side])
                if base not in OHLCV_SOURCES_SET and not base.isdigit():
                    used_indicators.add(base)

    # 기본 지표명별 그룹화 (defaultdict 로 단순화)
    indicator_groups = defaultdict(list)
    for indicator_name in used_indicators:
        base_name = extract_base_indicator_name(indicator_name)
        indicator_groups[base_name].append(indicator_name)

    filtered_vars = {}
    indicator_mapping = {}
    for base_name, indicator_list in indicator_groups.items():
        indicator_list.sort()
        for i, old_name in enumerate(indicator_list, 1):
            new_name = f"{base_name}{i}"
            indicator_mapping[old_name] = new_name
            filtered_vars[new_name] = vars_dict[old_name]
    return filtered_vars, indicator_mapping


def update_indicator_names(systems_dict, indicator_mapping):
    """시스템의 지표 이름을 새 이름으로 갱신."""
    updated_systems = {}
    for system_name, system_data in systems_dict.items():
        updated_system = system_data.copy()
        for side in ("left", "right"):
            operand = system_data[side]
            if "[" in operand:
                base_name, _, index_part = operand.partition("[")
                if base_name in indicator_mapping:
                    updated_system[side] = f"{indicator_mapping[base_name]}[{index_part}"
            else:
                if operand in indicator_mapping:
                    updated_system[side] = indicator_mapping[operand]
        updated_systems[system_name] = updated_system
    return updated_systems
