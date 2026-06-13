# after/decorators.py
"""부가 로직(횡단 관심사)을 핵심 연구 로직과 분리하는 데코레이터 모음 (D).

설계 원칙
---------
* 모든 데코레이터는 ``functools.wraps`` 로 원본 함수의 메타데이터(__name__, __doc__,
  시그니처)를 보존한다.
* ``@timeit`` / ``@log_call`` 같은 계측 데코레이터는 호출 1회당 파이썬 프레임을 추가하므로,
  ~10만 회 호출되는 핫패스에 항상 켜두면 벤치마크 자체를 오염시킨다. 따라서 **모듈 플래그로
  no-op 토글**할 수 있게 만들어, 측정이 필요할 때만 켠다(보고서에서 오버헤드를 정량화).
* 예외를 삼키거나 시그니처를 망가뜨리지 않는다.
"""

from __future__ import annotations

import functools
import logging
import time
from typing import Callable

# --- 계측 on/off 전역 플래그 ---------------------------------------------------
TIMING_ENABLED = False
LOGGING_ENABLED = False

# @timeit 가 측정한 누적 시간을 함수 이름별로 모아두는 싱크
TIMING_RECORDS: dict[str, list[float]] = {}


def timeit(func: Callable) -> Callable:
    """함수 실행 시간을 ``TIMING_RECORDS`` 에 누적한다.

    ``TIMING_ENABLED`` 가 False 면 래핑하지 않고 원본을 그대로 반환하여 오버헤드 0.
    """
    if not TIMING_ENABLED:
        return func

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            elapsed = time.perf_counter() - start
            TIMING_RECORDS.setdefault(func.__qualname__, []).append(elapsed)

    return wrapper


def log_call(func: Callable) -> Callable:
    """DEBUG 레벨로 함수 진입/종료를 기록. ``LOGGING_ENABLED`` False 면 no-op."""
    if not LOGGING_ENABLED:
        return func

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logging.debug("→ %s", func.__qualname__)
        result = func(*args, **kwargs)
        logging.debug("← %s", func.__qualname__)
        return result

    return wrapper


def retry(times: int = 3, exceptions: tuple = (Exception,), default=None):
    """불안정한 외부 호출용 재시도 데코레이터 (parameterized).

    ``times`` 회까지 재시도하고, 끝내 실패하면 ``default`` 를 반환한다.
    합성 평가기처럼 예외를 던지지 않는 경로에서는 추가 비용이 사실상 없다(첫 시도 성공).
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:  # noqa: BLE001 - 의도적으로 광범위
                    last_exc = exc
                    logging.warning(
                        "%s 실패 (%d/%d): %s", func.__qualname__, attempt, times, exc
                    )
            logging.error("%s 최종 실패: %s", func.__qualname__, last_exc)
            return default

        return wrapper

    return decorator


def validate_individual(penalty: float = -1000.0):
    """GP 개체 유효성 가드 데코레이터 (parameterized).

    ``eval_func``/operators/parser 에 반복되던
    ``if not individual or individual[0].name != "Strategy": return (penalty,)``
    가드를 한 곳으로 모은다. 데코레이트된 메서드는 ``(self, individual, ...)`` 형태를 가정.
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self, individual, *args, **kwargs):
            if not individual or individual[0].name != "Strategy":
                return (penalty,)
            return func(self, individual, *args, **kwargs)

        return wrapper

    return decorator


def cache_by_hash(hash_fn: Callable):
    """내용 해시 기반 stateful 캐싱 데코레이터 (parameterized + stateful).

    ``functools.lru_cache`` 와의 차이(보고서 비교 포인트):
    * ``lru_cache`` 는 *호출 인자의 identity/동등성* 으로 캐싱한다. GP 개체(트리)는
      매번 새 객체라 인자 기반 캐싱이 무의미하다.
    * 본 데코레이터는 *내용(전략 JSON)의 해시* 로 캐싱한다. 서로 다른 트리라도 동일한
      정규화 JSON으로 귀결되면 같은 키 → 캐시 적중(GP에서 흔히 발생).
    * 캐시는 인스턴스(``self._cache``)에 저장되고, ``self._hits``/``self._misses`` 로
      적중률 통계를 노출한다. 크기 제한이 없으므로(eviction 없음) 적중률이 극대화된다.

    데코레이트 대상: ``func(self, payload, ...) -> value`` 형태의 메서드.
    인스턴스는 ``_cache: dict``, ``_hits: int``, ``_misses: int`` 속성을 가져야 한다.
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self, payload, *args, **kwargs):
            key = hash_fn(payload)
            if key is not None and key in self._cache:
                self._hits += 1
                return self._cache[key]
            self._misses += 1
            result = func(self, payload, *args, **kwargs)
            if key is not None:
                self._cache[key] = result
            return result

        return wrapper

    return decorator
