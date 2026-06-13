# after/evaluation/strategy_evaluator.py
"""전략 평가 오케스트레이션 (C. 전역 상태 → 인스턴스 캡슐화 + D. 데코레이터).

원본 ``gp/evaluator.py`` 는 캐시(``_strategy_cache``)·설정(``_bt4_config``)·어댑터를 모듈
전역으로 두어, 동시에 여러 설정을 다루기 어렵고 테스트 시 전역을 초기화해야 했다. 여기서는
``StrategyEvaluator`` 인스턴스가 캐시와 평가기를 보유한다.

* ``@validate_individual``: 루트가 ``Strategy`` 가 아닌 개체에 페널티(가드 중앙화).
* ``@cache_by_hash``: 전략 JSON 내용 해시 기반 캐싱(서로 다른 트리도 동일 전략이면 적중).
"""

from __future__ import annotations

import hashlib
import json
from typing import Dict, Tuple

from src.after.decorators import cache_by_hash, validate_individual
from src.after.evaluation.protocols import BacktestEvaluator
from src.after.strategy.parser import parse_gp_tree_to_json
from src.after.strategy.validator import validate_and_clean_strategy


def get_strategy_hash(strategy_json: Dict):
    """전략 JSON을 정렬 직렬화하여 SHA-256 고유 키 생성(원본과 동일)."""
    try:
        strategy_str = json.dumps(strategy_json, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(strategy_str.encode()).hexdigest()
    except Exception:
        return None


class StrategyEvaluator:
    """파싱 → 검증 → (내용 해시) 캐시 → 평가기 위임."""

    def __init__(
        self,
        evaluator: BacktestEvaluator,
        condition_manager,
        max_tree_size: int = 500,
        penalty: float = -1000.0,
    ):
        self._evaluator = evaluator
        self._condition_manager = condition_manager
        self._max_tree_size = max_tree_size
        self._penalty = penalty
        # cache_by_hash 데코레이터가 사용하는 상태
        self._cache: dict = {}
        self._hits = 0
        self._misses = 0

    @validate_individual()  # 루트가 Strategy 가 아니면 (penalty,) 반환
    def evaluate(self, individual) -> Tuple[float]:
        if len(individual) > self._max_tree_size:
            return (self._penalty,)
        strategy_json = parse_gp_tree_to_json(individual, self._condition_manager)
        if strategy_json is None:
            return (self._penalty,)
        modified_json = validate_and_clean_strategy(strategy_json)
        return (self._score(modified_json),)

    @cache_by_hash(get_strategy_hash)
    def _score(self, strategy_json: Dict) -> float:
        return self._evaluator.evaluate(strategy_json)

    # --- 캐시 통계/관리 ---
    def cache_stats(self) -> Dict:
        return {
            "total_cached": len(self._cache),
            "hits": self._hits,
            "misses": self._misses,
            "cache_size_bytes": sum(
                len(str(k)) + len(str(v)) for k, v in self._cache.items()
            ),
        }

    def clear_cache(self) -> None:
        self._cache.clear()
        self._hits = 0
        self._misses = 0
