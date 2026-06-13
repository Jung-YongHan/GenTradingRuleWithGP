# after/strategy/parser.py
"""GP 트리 → 전략 JSON 변환 (핫패스 최적화).

최적화 요약 (보고서 §4 핵심)
---------------------------
1. **``str(individual)`` 1회 계산**: 원본은 buy/sell 조건식을 각각 만들 때 트리를
   두 번 직렬화(``_analyze_tree_structure`` × 2)했다. 트리 직렬화는 O(트리 크기)이고
   개체마다 일어나므로 비용이 컸다. 여기서는 한 번만 문자열화하여 buy/sell에 공유한다.
2. **중복 추출 함수 통합**: 거의 동일하던 ``_extract_buy_condition_from_tree`` /
   ``_extract_sell_condition_from_tree`` 를 ``_split_strategy_args`` 하나로 합치고,
   최상위 콤마 탐색(``_find_top_level_comma``)도 1회만 수행.
3. **정규식 사전 컴파일**: 변환에 쓰이는 ~13개 패턴을 모듈 로드 시 1회 ``re.compile``.

출력(JSON)은 원본과 **동일**해야 한다(골든 코퍼스 등가성 테스트로 검증).
"""

from __future__ import annotations

import re

from deap import gp

from src.after.configs.indicator_configs import OHLCV_SOURCES_SET
from src.after.strategy.formatter import (
    filter_used_indicators,
    filter_used_systems,
    update_indicator_names,
    update_system_numbers,
)
from src.after.utils.helpers import extract_base_from_access_name

# --- 사전 컴파일된 정규식 -------------------------------------------------------
_RE_SYSTEM = {
    "buy": re.compile(r"buy_system(\d+)"),
    "sell": re.compile(r"sell_system(\d+)"),
}
_RE_BRACED_QUOTE = re.compile(r"'[^']*\{[^}]*\}[^']*'")
_RE_EMPTY_QUOTE = re.compile(r"''")
_RE_DQUOTE = re.compile(r'"([^"]+)"')

_RE_NOT = re.compile(r"not_\(([^)]+)\)")
_RE_AND = re.compile(r"and_\(([^,]+),\s*([^)]+)\)")
_RE_OR = re.compile(r"or_\(([^,]+),\s*([^)]+)\)")
_RE_AND_PAREN = re.compile(r"and_\(\(([^)]+)\),\s*([^,()]+)\)")
_RE_OR_PAREN = re.compile(r"or_\(\(([^)]+)\),\s*([^,()]+)\)")

_RE_AND_OPEN = re.compile(r"and_\(")
_RE_OR_OPEN = re.compile(r"or_\(")
_RE_NOT_OPEN = re.compile(r"not_\(")
_RE_SQUOTE = re.compile(r"'")

_RE_OPEN_PAREN = re.compile(r"\s*\(\s*")
_RE_CLOSE_PAREN = re.compile(r"\s*\)\s*")
_RE_BOOLOP = re.compile(r"\s*(and|or)\s*")
_RE_BANG_PAREN = re.compile(r"!\s*\(")
_RE_COMMA = re.compile(r",\s*")
_RE_WS = re.compile(r"\s+")


def parse_gp_tree_to_json(individual: gp.PrimitiveTree, condition_manager):
    """최종 트리를 분석하여 JSON 객체로 변환한다."""
    if not isinstance(individual, gp.PrimitiveTree) or individual[0].name != "Strategy":
        return None

    used_indicators = set()
    buy_systems_new = _build_systems(condition_manager.buy_pool, used_indicators)
    sell_systems_new = _build_systems(condition_manager.sell_pool, used_indicators)

    vars_dict = condition_manager.vars_dict

    # 트리 직렬화는 단 1회 (buy/sell 공유)
    buy_system_op, sell_system_op = _analyze_both(individual)

    buy_systems_filtered, buy_mapping = filter_used_systems(buy_systems_new, buy_system_op)
    sell_systems_filtered, sell_mapping = filter_used_systems(
        sell_systems_new, sell_system_op
    )

    buy_system_op_updated = update_system_numbers(buy_system_op, buy_mapping)
    sell_system_op_updated = update_system_numbers(sell_system_op, sell_mapping)

    vars_filtered, indicator_mapping = filter_used_indicators(
        vars_dict, buy_systems_filtered, sell_systems_filtered
    )

    buy_systems_updated = update_indicator_names(buy_systems_filtered, indicator_mapping)
    sell_systems_updated = update_indicator_names(sell_systems_filtered, indicator_mapping)

    return {
        "vars": vars_filtered,
        "buy_systems": buy_systems_updated,
        "buy_system_op": buy_system_op_updated,
        "sell_systems": sell_systems_updated,
        "sell_system_op": sell_system_op_updated,
    }


def _build_systems(pool, used_indicators):
    """buy_pool / sell_pool → systemN 딕셔너리 (원본 두 루프를 하나로 통합)."""
    systems_new = {}
    for i, details in enumerate(pool.values(), 1):
        new_name = f"system{i}"
        systems_new[new_name] = {
            "alias": new_name,
            "left": details["left"],
            "op": details["op"],
            "right": details["right"],
        }
        for side in ("left", "right"):
            base = extract_base_from_access_name(details[side])
            if base not in OHLCV_SOURCES_SET:
                used_indicators.add(base)
    return systems_new


def _analyze_both(individual):
    """트리를 1회 문자열화하여 buy/sell 연산 문자열을 동시에 생성."""
    if len(individual) < 3 or individual[0].name != "Strategy":
        return "", ""
    tree_str = str(individual)  # ← 단 1회 직렬화
    buy_raw, sell_raw = _split_strategy_args(tree_str)
    return (
        _convert_system_names_in_string(buy_raw, "buy"),
        _convert_system_names_in_string(sell_raw, "sell"),
    )


def _find_top_level_comma(tree_str, start_idx):
    """start_idx 이후 첫 최상위(괄호 깊이 0) 콤마 위치. 없으면 -1."""
    paren_count = 0
    for i in range(start_idx, len(tree_str)):
        char = tree_str[i]
        if char == "(":
            paren_count += 1
        elif char == ")":
            paren_count -= 1
        elif char == "," and paren_count == 0:
            return i
    return -1


def _split_strategy_args(tree_str):
    """``Strategy(buy, sell)`` 문자열을 (buy_raw, sell_raw) 로 분리."""
    start_marker = "Strategy("
    start_idx = tree_str.find(start_marker) + len(start_marker)
    comma_idx = _find_top_level_comma(tree_str, start_idx)
    if comma_idx == -1:
        return "", ""
    buy_part = tree_str[start_idx:comma_idx].strip()
    sell_part = tree_str[comma_idx + 1 :].strip()
    if sell_part.endswith(")"):
        sell_part = sell_part[:-1].strip()
    return buy_part, sell_part


def _convert_system_names_in_string(operation_str, system_type):
    """문자열의 시스템 이름을 변환하고 논리 구조를 생성(사전 컴파일 정규식 사용)."""
    result = _RE_SYSTEM[system_type].sub(r"system\1", operation_str)

    result = _RE_BRACED_QUOTE.sub("", result)
    result = _RE_EMPTY_QUOTE.sub("", result)
    result = _RE_DQUOTE.sub(r"\1", result)

    for _ in range(10):
        old_result = result
        result = _RE_NOT.sub(r"!(\1)", result)
        result = _RE_AND.sub(r"(\1 and \2)", result)
        result = _RE_OR.sub(r"(\1 or \2)", result)
        result = _RE_AND_PAREN.sub(r"((\1) and \2)", result)
        result = _RE_OR_PAREN.sub(r"((\1) or \2)", result)
        if result == old_result:
            break

    result = _RE_AND_OPEN.sub(" and ", result)
    result = _RE_OR_OPEN.sub(" or ", result)
    result = _RE_NOT_OPEN.sub("!(", result)
    result = _RE_SQUOTE.sub("", result)

    result = _RE_OPEN_PAREN.sub("(", result)
    result = _RE_CLOSE_PAREN.sub(")", result)
    result = _RE_BOOLOP.sub(r" \1 ", result)
    result = _RE_BANG_PAREN.sub("!(", result)
    result = _RE_COMMA.sub(", ", result)
    result = _RE_WS.sub(" ", result)
    result = result.strip()

    if not result:
        return ""
    return result
