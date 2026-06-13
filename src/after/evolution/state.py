# after/evolution/state.py
"""진화 런타임 상태 (C. config 와 state 분리).

설정(GPConfig, 불변)과 달리, 진화 중 변하는 값(현재 개체군·세대 번호)을 담는다.
``fitness_values`` 는 **lazy 제너레이터**를 반환하여 통계 계산 시 중간 리스트를 만들지 않는다.
"""

from __future__ import annotations

from typing import Iterator

from deap import tools


class EvolutionState:
    """진화 런타임 상태(가변)."""

    __slots__ = ("population", "generation")

    def __init__(self, population):
        self.population = population
        self.generation = 0

    def fitness_values(self) -> Iterator[float]:
        """개체군 적합도를 lazy 하게 산출(중간 리스트 없음)."""
        return (ind.fitness.values[0] for ind in self.population)

    @property
    def best(self):
        return tools.selBest(self.population, 1)[0]
