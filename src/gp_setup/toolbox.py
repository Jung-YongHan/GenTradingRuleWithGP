# gp_setup/toolbox.py

import operator

from deap import base, creator, gp, tools

from config import INITIAL_MAX_DEPTH, INITIAL_MIN_DEPTH
from gp_setup.domain import BuyType, SellType, Strategy
# ✨ 수정된 임포트
from gp_setup.genetics import custom_crossover, custom_mutation
from utils.parsing import eval_func


def create_primitive_set(condition_manager):
    """PrimitiveSet을 생성하고 구성합니다."""
    pset = gp.PrimitiveSetTyped("Main", [], object)
    pset.addPrimitive(Strategy, [BuyType, SellType], object)
    pset.addPrimitive(operator.and_, [BuyType, BuyType], BuyType)
    pset.addPrimitive(operator.or_, [BuyType, BuyType], BuyType)
    pset.addPrimitive(operator.not_, [BuyType], BuyType)
    pset.addPrimitive(operator.and_, [SellType, SellType], SellType)
    pset.addPrimitive(operator.or_, [SellType, SellType], SellType)
    pset.addPrimitive(operator.not_, [SellType], SellType)

    for term in condition_manager.buy_pool.keys(): pset.addTerminal(term, BuyType) 
    for term in condition_manager.sell_pool.keys(): pset.addTerminal(term, SellType)
    return pset

def create_toolbox(pset):
    """Toolbox를 생성하고 구성합니다."""
    toolbox = base.Toolbox()
    toolbox.register("expr_init", gp.genHalfAndHalf, pset=pset, min_=INITIAL_MIN_DEPTH, max_=INITIAL_MAX_DEPTH, type_=object)
    toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.expr_init)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    
    toolbox.register("evaluate", eval_func)
    toolbox.register("select", tools.selTournament, tournsize=3)
    toolbox.register("mate", custom_crossover)
    toolbox.register("mutate", custom_mutation, pset=pset)
    
    return toolbox