# after/evolution/runner.py
"""진화 루프 (B. 제너레이터 + C. 책임 분리).

원본 ``main()`` 은 진화 루프·통계·로깅·시각화·저장을 한 함수에 담았다. 여기서는
``EvolutionRunner.run()`` 이 **세대별 통계를 yield 하는 제너레이터**다. 호출부는 통계를
lazy 하게 소비하거나(실시간 로깅), ``list(runner.run())`` 으로 한 번에 모을 수 있고,
조기 종료(early stop)도 자연스럽다.

DEAP 연산자(selTournament/cxOnePoint/genHalfAndHalf)는 전역 ``random`` 에 바인딩되므로,
재현성은 호출부가 ``random.seed`` 를 한 번 호출해 확보한다(원본과 동일한 난수열 보장).
이것이 병렬 경로가 비결정적인 이유이기도 하다.
"""

from __future__ import annotations

import random
from time import perf_counter
from typing import Iterator

from src.after.config import GPConfig
from src.after.evolution.parallel import SequentialMap
from src.after.evolution.state import EvolutionState
from src.after.evolution.stats import GenerationStats, StatsCollector


class EvolutionRunner:
    """GP 진화를 구동하고 세대별 통계를 산출한다."""

    def __init__(self, cfg: GPConfig, toolbox, map_strategy=None, stats_collector=None):
        self.cfg = cfg
        self.toolbox = toolbox
        self.map = map_strategy or SequentialMap()
        self.stats = stats_collector or StatsCollector()
        self.state: EvolutionState | None = None

    def run(self) -> Iterator[GenerationStats]:
        cfg = self.cfg
        tb = self.toolbox

        # 초기 개체군 생성·평가
        pop = tb.population(n=cfg.n_population)
        for ind, fit in zip(pop, self.map(tb.evaluate, pop)):
            ind.fitness.values = fit
        self.state = EvolutionState(pop)

        for g in range(cfg.n_generation):
            t0 = perf_counter()

            offspring = tb.select(pop, len(pop))
            offspring = list(map(tb.clone, offspring))

            for child1, child2 in zip(offspring[::2], offspring[1::2]):
                if random.random() < cfg.crossover_probability:
                    tb.mate(child1, child2)
                    del child1.fitness.values, child2.fitness.values
            for mutant in offspring:
                if random.random() < cfg.mutation_probability:
                    tb.mutate(mutant)
                    del mutant.fitness.values

            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            for ind, fit in zip(invalid_ind, self.map(tb.evaluate, invalid_ind)):
                ind.fitness.values = fit

            pop[:] = offspring
            self.state.population = pop
            self.state.generation = g + 1

            duration = perf_counter() - t0
            # lazy 제너레이터를 단일 패스 collector 로 → 중간 리스트 없음
            yield self.stats.summarize(self.state.fitness_values(), g + 1, duration)

    @property
    def best(self):
        if self.state is None:
            raise RuntimeError("run() 을 먼저 소비해야 합니다.")
        return self.state.best
