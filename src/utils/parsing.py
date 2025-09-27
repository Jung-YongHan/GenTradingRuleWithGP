# utils/parsing.py

import json
import random

from deap import gp

from config import MAX_TREE_SIZE


def eval_func(individual):
    """개체를 평가하는 함수"""
    if not individual or individual[0].name != 'Strategy':
        return -1000.0,
    if len(individual) > MAX_TREE_SIZE:
        return -100.0,
    return random.uniform(10, 100),

def parse_gp_tree_to_json(individual, condition_manager):
    """최종 트리를 분석하여 JSON 객체로 변환"""
    if not isinstance(individual, gp.PrimitiveTree) or individual[0].name != 'Strategy':
        return None

    buy_subtree_slice = individual.searchSubtree(1)
    buy_tree = gp.PrimitiveTree(individual[buy_subtree_slice])
    sell_tree = gp.PrimitiveTree(individual[buy_subtree_slice.stop:])

    buy_op_str = str(buy_tree) if len(buy_tree) > 0 else "NO_LOGIC"
    sell_op_str = str(sell_tree) if len(sell_tree) > 0 else "NO_LOGIC"

    buy_systems_obj = {node.name: condition_manager.buy_pool[node.name] for node in buy_tree if isinstance(node, gp.Terminal)}
    sell_systems_obj = {node.name: condition_manager.sell_pool[node.name] for node in sell_tree if isinstance(node, gp.Terminal)}

    dynamic_vars = {
        f"{details['indicator']}_{details['param']}": details['param'] 
        for details in {**buy_systems_obj, **sell_systems_obj}.values()
    }

    return {
        "vars": dynamic_vars, "buy_systems": buy_systems_obj, "buy_system_op": buy_op_str,
        "sell_systems": sell_systems_obj, "sell_system_op": sell_op_str
    }