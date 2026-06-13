# after/evaluation/synthetic.py
"""합성 백테스트 평가기 (BacktestEvaluator 구현).

공유 모듈 ``src.synthetic.score_strategy`` 에 위임한다. before/after 가 같은 점수 함수를
사용하므로 벤치마크가 측정하는 차이는 오케스트레이션 코드뿐이다(공정성).
``@retry`` 는 합성 경로에선 사실상 무영향(예외를 던지지 않음)이지만, 동일 인터페이스의
실거래 경로(bt4)와의 대칭을 위해 두지 않고 여기서는 생략한다.
"""

from __future__ import annotations

from typing import Dict

from src.synthetic import score_strategy


class SyntheticBacktestEvaluator:
    """결정적 합성 적합도 평가기."""

    def __init__(self, seed: int = 42):
        self.seed = seed

    def evaluate(self, strategy_json: Dict) -> float:
        return score_strategy(strategy_json, seed=self.seed)
