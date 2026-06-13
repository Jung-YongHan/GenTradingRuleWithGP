# src/before/benchmark_entry.py
"""벤치마크용 진입점 (최적화 *전* 코드).

``main.py`` 의 진화 루프를 **그대로(verbatim)** 옮겨오되, 로깅/시각화/파일 저장 등
측정과 무관한 부수효과(IO)만 제거했다. 측정되는 연산(선택·교차·변이·평가·통계)은
원본 ``main()`` 과 동일하므로, 이 함수로 측정한 시간/메모리는 최적화 전 오케스트레이션
코드의 비용을 충실히 반영한다.

DEAP 의 ``creator`` 클래스(FitnessMax/Individual)는 프로세스당 한 번만 생성해야 하므로
여기서 만들지 않고, 호출하는 벤치마크 하니스가 한 번만 생성한다.
"""

from __future__ import annotations

import random

from src.before.configs.gp_configs import (
    CROSSOVER_PROBABILITY,
    MUTATION_PROBABILITY,
)
from src.before.domain.condition import ConditionManager
from src.before.gp.evaluator import clear_cache, get_cache_stats, set_bt4_config
from src.before.gp.toolbox import create_primitive_set, create_toolbox
from deap import tools


def run_evolution(
    *,
    n_population: int,
    n_generation: int,
    n_conditions: int,
    n_indicators: int,
    seed: int = 42,
):
    """최적화 전 코드로 GP 진화를 실행하고 결과 요약을 반환한다(IO 없음)."""
    random.seed(seed)
    set_bt4_config({"random_seed": seed})
    clear_cache()

    condition_manager = ConditionManager(n_conditions, n_indicators)
    pset = create_primitive_set(condition_manager)
    toolbox = create_toolbox(pset, condition_manager, pool=None)  # 순차 map

    # --- 이하 main() 의 진화 루프와 동일 ---
    pop = toolbox.population(n=n_population)
    fitnesses = toolbox.map(toolbox.evaluate, pop)
    for ind, fit in zip(pop, fitnesses):
        ind.fitness.values = fit

    stats_history = []
    for g in range(n_generation):
        offspring = toolbox.select(pop, len(pop))
        offspring = list(map(toolbox.clone, offspring))

        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < CROSSOVER_PROBABILITY:
                toolbox.mate(child1, child2)
                del child1.fitness.values, child2.fitness.values
        for mutant in offspring:
            if random.random() < MUTATION_PROBABILITY:
                toolbox.mutate(mutant)
                del mutant.fitness.values

        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        pop[:] = offspring
        fits = [ind.fitness.values[0] for ind in pop]

        max_fit = max(fits)
        avg_fit = sum(fits) / len(pop)
        min_fit = min(fits)
        std_fit = (sum((x - avg_fit) ** 2 for x in fits) / len(fits)) ** 0.5
        stats_history.append(
            {
                "generation": g + 1,
                "max": max_fit,
                "avg": avg_fit,
                "min": min_fit,
                "std": std_fit,
            }
        )

    best_ind = tools.selBest(pop, 1)[0]
    cache_stats = get_cache_stats()
    return {
        "stats_history": stats_history,
        "best_fitness": best_ind.fitness.values[0],
        "max_trajectory": [s["max"] for s in stats_history],
        "cache_total": cache_stats["total_cached"],
    }
