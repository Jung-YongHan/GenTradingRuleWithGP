# src/after/benchmark_entry.py
"""벤치마크용 진입점 (최적화 *후* 코드).

``src/before/benchmark_entry.py`` 와 **동일한 시그니처/반환 형태**를 제공하여, 벤치마크
하니스가 before/after 를 1:1로 비교할 수 있게 한다. 내부적으로는 리팩터된 클래스 구조
(GPConfig / make_evaluator / StrategyEvaluator / EvolutionRunner)를 사용한다.

재현성: DEAP 연산자가 전역 ``random`` 을 사용하므로, before 와 동일한 난수열을 위해
``random.seed`` 를 동일 시점(설정 생성 전, 조건풀 생성 전)에서 호출한다.
"""

from __future__ import annotations

import random

from src.after.config import GPConfig
from src.after.domain.condition import ConditionManager
from src.after.evaluation.registry import make_evaluator
from src.after.evaluation.strategy_evaluator import StrategyEvaluator
from src.after.evolution.runner import EvolutionRunner
from src.after.gp.toolbox import create_primitive_set, create_toolbox


def build_pipeline(cfg: GPConfig, evaluator_name: str = "synthetic"):
    """설정으로부터 (condition_manager, strategy_evaluator, toolbox) 를 조립."""
    condition_manager = ConditionManager(
        cfg.initial_conditions_count, cfg.indicators_count
    )
    backtest = make_evaluator(evaluator_name, cfg)
    strategy_evaluator = StrategyEvaluator(
        backtest, condition_manager, max_tree_size=cfg.max_tree_size
    )
    pset = create_primitive_set(condition_manager)
    toolbox = create_toolbox(pset, cfg, strategy_evaluator.evaluate)
    return condition_manager, strategy_evaluator, toolbox


def run_evolution(
    *,
    n_population: int,
    n_generation: int,
    n_conditions: int,
    n_indicators: int,
    seed: int = 42,
):
    """최적화 후 코드로 GP 진화를 실행하고 결과 요약을 반환한다(IO 없음)."""
    random.seed(seed)
    cfg = GPConfig(
        indicators_count=n_indicators,
        initial_conditions_count=n_conditions,
        n_population=n_population,
        n_generation=n_generation,
        random_seed=seed,
    )
    _, strategy_evaluator, toolbox = build_pipeline(cfg, "synthetic")

    runner = EvolutionRunner(cfg, toolbox)
    stats_history = list(runner.run())  # 제너레이터를 한 번에 materialize
    best = runner.best
    cache = strategy_evaluator.cache_stats()

    return {
        "stats_history": [
            {
                "generation": s.generation,
                "max": s.max,
                "avg": s.avg,
                "min": s.min,
                "std": s.std,
            }
            for s in stats_history
        ],
        "best_fitness": best.fitness.values[0],
        "max_trajectory": [s.max for s in stats_history],
        "cache_total": cache["total_cached"],
        "cache_hits": cache["hits"],
        "cache_misses": cache["misses"],
    }
