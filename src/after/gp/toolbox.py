# after/gp/toolbox.py
"""DEAP PrimitiveSet / Toolbox 빌더.

원본은 ``_condition_manager`` 모듈 전역과 ``_evaluate_with_condition_manager`` 전역 함수로
평가를 우회 연결했다. 여기서는 평가 콜러블을 **인자로 주입**하여 전역 의존을 제거한다
(순차 경로 기준). 멀티프로세싱 경로는 ``evolution/parallel.py`` 에서 별도 처리.
"""

from __future__ import annotations

import operator

from deap import base, creator, gp, tools

from src.after.config import GPConfig
from src.after.domain.types import BuyType, SellType, Strategy

from .operators import custom_crossover, custom_mutation


def create_primitive_set(condition_manager) -> gp.PrimitiveSetTyped:
    """PrimitiveSet 을 생성·구성한다(원본과 동일)."""
    pset = gp.PrimitiveSetTyped("Main", [], object)

    pset.addPrimitive(Strategy, [BuyType, SellType], object)
    pset.addPrimitive(operator.and_, [BuyType, BuyType], BuyType)
    pset.addPrimitive(operator.or_, [BuyType, BuyType], BuyType)
    pset.addPrimitive(operator.not_, [BuyType], BuyType)
    pset.addPrimitive(operator.and_, [SellType, SellType], SellType)
    pset.addPrimitive(operator.or_, [SellType, SellType], SellType)
    pset.addPrimitive(operator.not_, [SellType], SellType)

    for term in condition_manager.buy_pool.keys():
        pset.addTerminal(term, BuyType)
    for term in condition_manager.sell_pool.keys():
        pset.addTerminal(term, SellType)

    return pset


def create_toolbox(pset, cfg: GPConfig, evaluate_fn) -> base.Toolbox:
    """Toolbox 를 생성·구성한다. ``evaluate_fn`` 은 개체→적합도 콜러블."""
    toolbox = base.Toolbox()
    toolbox.register(
        "expr_init",
        gp.genHalfAndHalf,
        pset=pset,
        min_=cfg.initial_min_depth,
        max_=cfg.initial_max_depth,
        type_=object,
    )
    toolbox.register(
        "individual", tools.initIterate, creator.Individual, toolbox.expr_init
    )
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("evaluate", evaluate_fn)
    toolbox.register("select", tools.selTournament, tournsize=cfg.tournament_size)
    toolbox.register("mate", custom_crossover)
    toolbox.register(
        "mutate", custom_mutation, pset=pset, max_mutation_depth=cfg.max_mutation_depth
    )
    return toolbox
