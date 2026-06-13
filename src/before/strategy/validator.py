# strategy/validator.py

from src.before.configs.indicator_configs import OHLCV_SOURCES


def validate_and_clean_strategy(strategy_json):
    """전략 JSON을 검증하고 정리하는 함수"""
    modified_json = strategy_json.copy()

    # 1. 지표 검증 및 정리
    modified_json = _validate_and_clean_indicators(modified_json)

    # 2. 조건 검증 및 정리
    modified_json = _validate_and_clean_conditions(modified_json)

    return modified_json


def _validate_and_clean_indicators(strategy_json):
    """지표 데이터를 검증하고 정리하는 함수"""
    if "vars" not in strategy_json:
        return strategy_json

    cleaned_vars = {}
    for indicator_name, indicator_data in strategy_json["vars"].items():
        if _is_valid_indicator(indicator_data):
            cleaned_vars[indicator_name] = indicator_data

    strategy_json["vars"] = cleaned_vars
    return strategy_json


def _validate_and_clean_conditions(strategy_json):
    """조건 데이터를 검증하고 정리하는 함수"""
    for system_type in ["buy_systems", "sell_systems"]:
        if system_type not in strategy_json:
            continue

        cleaned_systems = {}
        for system_name, system_data in strategy_json[system_type].items():
            if _is_valid_condition(system_data, strategy_json.get("vars", {})):
                cleaned_systems[system_name] = system_data

        strategy_json[system_type] = cleaned_systems

    return strategy_json


def _is_valid_indicator(indicator_data):
    """지표 데이터가 유효한지 검증하는 함수"""
    required_fields = ["func", "params", "cdl_type", "sources", "unary"]
    return all(field in indicator_data for field in required_fields)


def _is_valid_condition(condition_data, vars_dict):
    """조건 데이터가 유효한지 검증하는 함수"""
    required_fields = ["alias", "left", "op", "right"]
    if not all(field in condition_data for field in required_fields):
        return False

    left_valid = _is_valid_operand(condition_data["left"], vars_dict)
    right_valid = _is_valid_operand(condition_data["right"], vars_dict)
    return left_valid and right_valid


def _is_valid_operand(operand, vars_dict):
    """피연산자가 유효한지 검증하는 함수"""
    if operand in OHLCV_SOURCES:
        return True

    if "[" in operand:
        base_name = operand.split("[")[0]
        return base_name in vars_dict
    else:
        return operand in vars_dict
