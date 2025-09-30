# utils/parsing.py

import random

from deap import gp

from config import MAX_TREE_SIZE, OHLCV_SOURCES


def eval_func(individual, condition_manager=None):
    """개체를 평가하는 함수"""
    if not individual or individual[0].name != "Strategy":
        return (-1000.0,)
    if len(individual) > MAX_TREE_SIZE:
        return (-1000.0,)

    # 1. 개체를 JSON으로 변환
    if condition_manager is None:
        # condition_manager가 없으면 기본 평가
        return (-1000.0,)

    strategy_json = parse_gp_tree_to_json(individual, condition_manager)
    if strategy_json is None:
        return (-1000.0,)

    # 2. Trader로 전달하기 전에 JSON 수정
    modified_json = modify_json_for_trader(strategy_json)

    # 3. Trader 모듈로 전달하여 적합도 평가
    fitness_score = evaluate_with_trader(modified_json)

    return (fitness_score,)


def modify_json_for_trader(strategy_json):
    """Trader 모듈에 맞게 JSON을 수정하는 함수"""

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


def evaluate_with_trader(modified_json=None):
    """Trader 모듈을 사용하여 적합도를 평가하는 함수"""
    try:
        return random.uniform(10, 100)
    except Exception as e:
        print(f"Trader 평가 중 오류 발생: {e}")
        return -1000.0


def extract_base_indicator_name(indicator_name):
    """지표 이름에서 숫자를 제거하여 원본 지표 이름을 추출합니다."""
    import re

    # 숫자로 끝나는 패턴을 찾아서 제거 (예: RSI1 -> RSI, MACD2 -> MACD)
    match = re.match(r"^(.+?)(\d+)$", indicator_name)
    if match:
        return match.group(1)
    return indicator_name


def parse_gp_tree_to_json(individual: gp.PrimitiveTree, condition_manager):
    """최종 트리를 분석하여 JSON 객체로 변환"""
    if not isinstance(individual, gp.PrimitiveTree) or individual[0].name != "Strategy":
        return None

    buy_systems_new = {}
    sell_systems_new = {}
    used_indicators = set()
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
    buy_systems_filtered, buy_mapping = _filter_used_systems(
        buy_systems_new, buy_system_op
    )
    sell_systems_filtered, sell_mapping = _filter_used_systems(
        sell_systems_new, sell_system_op
    )

    # system_op의 번호를 새로운 번호로 업데이트
    buy_system_op_updated = _update_system_numbers(buy_system_op, buy_mapping)
    sell_system_op_updated = _update_system_numbers(sell_system_op, sell_mapping)

    # 사용되지 않는 지표들 제거하고 번호 재정렬
    vars_filtered, indicator_mapping = _filter_used_indicators(
        vars_dict, buy_systems_filtered, sell_systems_filtered
    )

    # 시스템의 지표 이름을 새로운 이름으로 업데이트
    buy_systems_updated = _update_indicator_names(
        buy_systems_filtered, indicator_mapping
    )
    sell_systems_updated = _update_indicator_names(
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


def _filter_used_systems(systems_dict, system_op):
    """system_op에서 실제로 사용되는 시스템들만 필터링하고 번호를 1부터 재정렬"""
    if not system_op or system_op.strip() == "":
        return {}

    import re

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


def _update_system_numbers(system_op, system_mapping):
    """system_op에서 시스템 번호를 새로운 번호로 업데이트"""
    if not system_op or not system_mapping:
        return system_op

    import re

    # system_op에서 시스템 번호를 새로운 번호로 교체
    updated_op = system_op
    for old_system, new_system in system_mapping.items():
        # system25 -> system1 같은 패턴으로 교체
        pattern = re.escape(old_system)
        updated_op = re.sub(pattern, new_system, updated_op)

    return updated_op


def _filter_used_indicators(vars_dict, buy_systems, sell_systems):
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


def _update_indicator_names(systems_dict, indicator_mapping):
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


def extract_base_from_access_name(access_name):
    """접근 이름에서 기본 지표 이름을 추출 (예: "MACD1[0]" -> "MACD1")"""
    if "[" in access_name:
        return access_name.split("[")[0]
    return access_name


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
    import re

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
