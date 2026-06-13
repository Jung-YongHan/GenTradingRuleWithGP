# after/evolution/parallel.py
"""map 전략 (순차 / 멀티프로세싱).

기본은 ``SequentialMap`` — 가벼운 합성 평가기에서는 Pool IPC/pickling 오버헤드가 지배적이고
워커별 RNG·캐시 분리로 비결정적이 되므로, 공정·재현 가능한 벤치마크를 위해 순차가 적합하다.

``PoolMap`` 은 pickling-aware 설계를 시연한다: Pool initializer 로 워커마다 평가기를 1회만
구성하고, 모듈 레벨 ``_worker_evaluate`` 가 pickle 가능한 진입점을 제공한다.
"""

from __future__ import annotations

import multiprocessing
from typing import Callable, Iterable, List


class SequentialMap:
    """내장 map (순차). 기본값."""

    def __call__(self, fn: Callable, items: Iterable) -> List:
        return list(map(fn, items))

    def close(self):
        pass


# --- 멀티프로세싱 경로 (옵션) -------------------------------------------------
_WORKER_EVAL = None  # 워커 프로세스별 평가기 (전역은 pickle 진입점 용도로만 존재)


def _init_worker(evaluator_factory, factory_args):
    """각 워커에서 평가기를 1회 구성(평가기 자체를 매번 pickle 하지 않기 위함)."""
    global _WORKER_EVAL
    _WORKER_EVAL = evaluator_factory(*factory_args)


def _worker_evaluate(individual):
    """pickle 가능한 최상위 진입점."""
    return _WORKER_EVAL.evaluate(individual)


class PoolMap:
    """multiprocessing.Pool 기반 (비결정적; 시연용)."""

    def __init__(self, processes, evaluator_factory, factory_args):
        self._pool = multiprocessing.Pool(
            processes,
            initializer=_init_worker,
            initargs=(evaluator_factory, factory_args),
        )

    def __call__(self, fn: Callable, items: Iterable) -> List:
        # fn 은 무시: 워커는 _worker_evaluate 를 사용
        return self._pool.map(_worker_evaluate, list(items))

    def close(self):
        self._pool.close()
        self._pool.join()
