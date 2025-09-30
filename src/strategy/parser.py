# strategy/parser.py

import re

from deap import gp

from config import OHLCV_SOURCES
from utils.helpers import extract_base_from_access_name

from .formatter import (
    filter_used_indicators,
    filter_used_systems,
    update_indicator_names,
    update_system_numbers,
)


def parse_gp_tree_to_json(individual: gp.PrimitiveTree, condition_manager):
    """최종 트리를 분석하여 JSON 객체로 변환"""
    if not isinstance(individual, gp.PrimitiveTree) or individual[0].name != "Strategy":
        return None

    buy_systems_new = {}
    sell_systems_new = {}
    used_indicators = set()

    # buy_pool에서 시스템 생성
    for i, (_, details) in enumerate(condition_manager.buy_pool.items(), 1):
        new_name = f"system{i}"

        buy_systems_new[new_name] = {
            "alias": new_name,
            "left": details["left"],
            "op": details["op"],
            "right": details["right"],
        }

        left_base = extract_base_from_access_name(details["left"])
        right_base = extract_base_from_access_name(details["right"])
        if left_base not in OHLCV_SOURCES:
            used_indicators.add(left_base)
        if right_base not in OHLCV_SOURCES:
            used_indicators.add(right_base)

    # sell_pool에서 시스템 생성
    for i, (_, details) in enumerate(condition_manager.sell_pool.items(), 1):
        new_name = f"system{i}"

        sell_systems_new[new_name] = {
            "alias": new_name,
            "left": details["left"],
            "op": details["op"],
            "right": details["right"],
        }

        # 사용된 지표들 추적 (기본 지표 이름만, OHLCV는 제외)
        left_base = extract_base_from_access_name(details["left"])
        right_base = extract_base_from_access_name(details["right"])
        if left_base not in OHLCV_SOURCES:
            used_indicators.add(left_base)
        if right_base not in OHLCV_SOURCES:
            used_indicators.add(right_base)

    vars_dict = condition_manager.vars_dict

    buy_system_op = _analyze_tree_structure(individual, "buy")
    sell_system_op = _analyze_tree_structure(individual, "sell")

    # 사용되지 않는 시스템들 제거하고 번호 재정렬
    buy_systems_filtered, buy_mapping = filter_used_systems(
        buy_systems_new, buy_system_op
    )
    sell_systems_filtered, sell_mapping = filter_used_systems(
        sell_systems_new, sell_system_op
    )

    # system_op의 번호를 새로운 번호로 업데이트
    buy_system_op_updated = update_system_numbers(buy_system_op, buy_mapping)
    sell_system_op_updated = update_system_numbers(sell_system_op, sell_mapping)

    # 사용되지 않는 지표들 제거하고 번호 재정렬
    vars_filtered, indicator_mapping = filter_used_indicators(
        vars_dict, buy_systems_filtered, sell_systems_filtered
    )

    # 시스템의 지표 이름을 새로운 이름으로 업데이트
    buy_systems_updated = update_indicator_names(
        buy_systems_filtered, indicator_mapping
    )
    sell_systems_updated = update_indicator_names(
        sell_systems_filtered, indicator_mapping
    )

    result = {
        "vars": vars_filtered,
        "buy_systems": buy_systems_updated,
        "buy_system_op": buy_system_op_updated,
        "sell_systems": sell_systems_updated,
        "sell_system_op": sell_system_op_updated,
    }

    return result


def _analyze_tree_structure(individual, system_type):
    """GP 개체의 트리 구조를 분석하여 연산 문자열을 생성"""
    if not individual or len(individual) < 2:
        return ""

    strategy_node = individual[0]
    if strategy_node.name != "Strategy":
        return ""

    if len(individual) < 3:
        return ""

    tree_str = str(individual)

    if system_type == "buy":
        operation_str = _extract_buy_condition_from_tree(tree_str)
    else:
        operation_str = _extract_sell_condition_from_tree(tree_str)

    operation_str = _convert_system_names_in_string(operation_str, system_type)

    return operation_str


def _extract_buy_condition_from_tree(tree_str):
    """트리 문자열에서 buy_condition 부분을 추출"""
    start_marker = "Strategy("
    start_idx = tree_str.find(start_marker) + len(start_marker)

    paren_count = 0
    comma_idx = -1

    for i in range(start_idx, len(tree_str)):
        char = tree_str[i]
        if char == "(":
            paren_count += 1
        elif char == ")":
            paren_count -= 1
        elif char == "," and paren_count == 0:
            comma_idx = i
            break

    if comma_idx != -1:
        buy_part = tree_str[start_idx:comma_idx].strip()
        return buy_part
    else:
        return ""


def _extract_sell_condition_from_tree(tree_str):
    """트리 문자열에서 sell_condition 부분을 추출"""
    start_marker = "Strategy("
    start_idx = tree_str.find(start_marker) + len(start_marker)

    paren_count = 0
    comma_idx = -1

    for i in range(start_idx, len(tree_str)):
        char = tree_str[i]
        if char == "(":
            paren_count += 1
        elif char == ")":
            paren_count -= 1
        elif char == "," and paren_count == 0:
            comma_idx = i
            break

    if comma_idx != -1:
        sell_part = tree_str[comma_idx + 1 :].strip()
        if sell_part.endswith(")"):
            sell_part = sell_part[:-1].strip()
        return sell_part
    else:
        return ""


def _convert_system_names_in_string(operation_str, system_type):
    """문자열에서 시스템 이름을 변환하고 올바른 논리 구조를 생성"""
    pattern = rf"{system_type}_system(\d+)"
    replacement = r"system\1"
    result = re.sub(pattern, replacement, operation_str)

    result = re.sub(r"'[^']*\{[^}]*\}[^']*'", "", result)
    result = re.sub(r"''", "", result)
    result = re.sub(r'"([^"]+)"', r"\1", result)

    for _ in range(10):
        old_result = result

        result = re.sub(r"not_\(([^)]+)\)", r"!(\1)", result)
        result = re.sub(r"and_\(([^,]+),\s*([^)]+)\)", r"(\1 and \2)", result)
        result = re.sub(r"or_\(([^,]+),\s*([^)]+)\)", r"(\1 or \2)", result)
        result = re.sub(r"and_\(\(([^)]+)\),\s*([^,()]+)\)", r"((\1) and \2)", result)
        result = re.sub(r"or_\(\(([^)]+)\),\s*([^,()]+)\)", r"((\1) or \2)", result)

        if result == old_result:
            break

    result = re.sub(r"and_\(", " and ", result)
    result = re.sub(r"or_\(", " or ", result)
    result = re.sub(r"not_\(", "!(", result)
    result = re.sub(r"'", "", result)

    result = re.sub(r"\s*\(\s*", "(", result)
    result = re.sub(r"\s*\)\s*", ")", result)
    result = re.sub(r"\s*(and|or)\s*", r" \1 ", result)
    result = re.sub(r"!\s*\(", "!(", result)
    result = re.sub(r",\s*", ", ", result)
    result = re.sub(r"\s+", " ", result)
    result = result.strip()

    if not result or result.strip() == "":
        return ""

    return result
