# after/config.py
"""실행 설정과 런타임 상태의 분리 (C. 클래스 설계 / 단일책임원칙).

최적화 전에는 ``configs/gp_configs.py`` / ``configs/constants.py`` 에 모듈 전역 상수로
설정이 흩어져 있어, 실험 조건을 바꾸려면 소스를 직접 수정해야 했고 한 실행 안에서
여러 설정을 동시에 다룰 수 없었다.

여기서는 설정을 **불변(frozen) dataclass** 로 명시한다.
* ``frozen=True``: 실행 도중 설정이 바뀌지 않음을 타입 수준에서 보장(재현성).
* ``slots=True``: ``__dict__`` 제거로 인스턴스 메모리 절감 + 오타 속성 방지.
* ``dataclasses.replace`` 로 일부 필드만 바꾼 새 설정을 손쉽게 파생(벤치마크 크기 스윕).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class GPConfig:
    """유전 프로그래밍 실행 설정 (불변)."""

    # 조건/지표 풀 크기
    indicators_count: int = 1000
    initial_conditions_count: int = 500

    # 진화 파라미터
    n_population: int = 1000
    n_generation: int = 50
    crossover_probability: float = 0.8
    mutation_probability: float = 0.15
    tournament_size: int = 3

    # 트리 구조 파라미터
    initial_min_depth: int = 4
    initial_max_depth: int = 10
    max_mutation_depth: int = 6
    max_tree_size: int = 500

    # 실행 환경
    random_seed: int = 42
    cpu_count: int = 10
    use_multiprocessing: bool = False  # 기본 순차(재현성·공정 벤치마크)
    log_dir: str = "logs"


@dataclass(frozen=True, slots=True)
class SyntheticConfig:
    """합성 평가기 설정 (불변)."""

    seed: int = 42
