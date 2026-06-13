# after/strategy/validator.py
"""전략 JSON 검증/정리.

최적화: 피연산자 OHLCV 여부 판정을 ``OHLCV_SOURCES_SET`` (frozenset) 으로 O(1) 처리.
shallow ``dict.copy()`` 의미는 원본과 동일하게 보존(중첩 leaf dict 는 공유)한다.
"""

from __future__ import annotations

from src.after.configs.indicator_configs import OHLCV_SOURCES_SET

# 필수 필드 집합 (frozenset; all(...) 검사에 사용)
_INDICATOR_REQUIRED = ("func", "params", "cdl_type", "sources", "unary")
_CONDITION_REQUIRED = ("alias", "left", "op", "right")


def validate_and_clean_strategy(strategy_json):
    """전략 JSON을 검증하고 정리한다."""
    modified_json = strategy_json.copy()  # shallow copy (원본과 동일 의미)
    modified_json = _validate_and_clean_indicators(modified_json)
    modified_json = _validate_and_clean_conditions(modified_json)
    return modified_json


def _validate_and_clean_indicators(strategy_json):
    if "vars" not in strategy_json:
        return strategy_json
    strategy_json["vars"] = {
        name: data
        for name, data in strategy_json["vars"].items()
        if _is_valid_indicator(data)
    }
    return strategy_json


def _validate_and_clean_conditions(strategy_json):
    vars_dict = strategy_json.get("vars", {})
    for system_type in ("buy_systems", "sell_systems"):
        if system_type not in strategy_json:
            continue
        strategy_json[system_type] = {
            name: data
            for name, data in strategy_json[system_type].items()
            if _is_valid_condition(data, vars_dict)
        }
    return strategy_json


def _is_valid_indicator(indicator_data):
    return all(field in indicator_data for field in _INDICATOR_REQUIRED)


def _is_valid_condition(condition_data, vars_dict):
    if not all(field in condition_data for field in _CONDITION_REQUIRED):
        return False
    return _is_valid_operand(condition_data["left"], vars_dict) and _is_valid_operand(
        condition_data["right"], vars_dict
    )


def _is_valid_operand(operand, vars_dict):
    if operand in OHLCV_SOURCES_SET:  # O(1) frozenset membership
        return True
    if "[" in operand:
        base_name = operand.split("[", 1)[0]
        return base_name in vars_dict
    return operand in vars_dict
