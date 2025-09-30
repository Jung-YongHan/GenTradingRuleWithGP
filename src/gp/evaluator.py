# gp/evaluator.py

import random

from config import MAX_TREE_SIZE
from strategy.parser import parse_gp_tree_to_json
from strategy.validator import validate_and_clean_strategy


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

    # 2. Trader로 전달하기 전에 JSON 검증 및 정리
    modified_json = validate_and_clean_strategy(strategy_json)

    # 3. Trader 모듈로 전달하여 적합도 평가
    fitness_score = evaluate_with_trader(modified_json)

    return (fitness_score,)


def evaluate_with_trader(modified_json=None):
    """Trader 모듈을 사용하여 적합도를 평가하는 함수"""
    try:
        # TODO: 실제 Trader 모듈 연동
        return random.uniform(10, 100)
    except Exception as e:
        print(f"Trader 평가 중 오류 발생: {e}")
        return -1000.0
