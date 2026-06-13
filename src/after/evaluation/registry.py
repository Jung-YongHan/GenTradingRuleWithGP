# after/evaluation/registry.py
"""평가기 Factory / Registry (C. Factory 패턴으로 교체 가능하게 구성).

문자열 이름으로 평가기를 생성한다. 새 평가기를 추가하려면 레지스트리에 한 줄만 등록하면
되고, 호출부(main/benchmark)는 ``make_evaluator("synthetic", cfg)`` 처럼 이름만 바꿔
실험 조건을 교체할 수 있다.
"""

from __future__ import annotations

from src.after.config import GPConfig
from src.after.evaluation.protocols import BacktestEvaluator
from src.after.evaluation.synthetic import SyntheticBacktestEvaluator


def _make_synthetic(cfg: GPConfig, **kwargs) -> BacktestEvaluator:
    return SyntheticBacktestEvaluator(seed=cfg.random_seed)


def _make_bt4(cfg: GPConfig, *, bt4_config=None, **kwargs) -> BacktestEvaluator:
    from src.after.evaluation.bt4 import BT4BacktestEvaluator

    return BT4BacktestEvaluator(bt4_config or {})


EVALUATOR_REGISTRY = {
    "synthetic": _make_synthetic,
    "bt4": _make_bt4,
}


def make_evaluator(name: str, cfg: GPConfig, **kwargs) -> BacktestEvaluator:
    """이름으로 평가기를 생성한다(기본 'synthetic')."""
    try:
        factory = EVALUATOR_REGISTRY[name]
    except KeyError:
        raise ValueError(
            f"알 수 없는 평가기 '{name}'. 사용 가능: {list(EVALUATOR_REGISTRY)}"
        ) from None
    return factory(cfg, **kwargs)
