# after/evaluation/protocols.py
"""평가기 인터페이스 (C. Protocol 로 인터페이스 명확화).

원본은 평가가 ``evaluate_with_trader`` 함수 + 모듈 전역 ``_bt4_adapter`` 에 하드코딩되어
있어, 평가 방식을 교체하려면 함수 본문을 수정해야 했다. 여기서는 구조적 타이핑(Protocol)
으로 인터페이스를 명시한다 → 합성/실거래 백테스트를 상속 없이 교체 가능.
"""

from __future__ import annotations

from typing import Dict, Protocol, runtime_checkable


@runtime_checkable
class BacktestEvaluator(Protocol):
    """전략 JSON 을 받아 적합도(float)를 반환하는 평가기."""

    def evaluate(self, strategy_json: Dict) -> float: ...
