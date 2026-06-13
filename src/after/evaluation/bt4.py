# after/evaluation/bt4.py
"""실거래 백테스트 평가기 (BacktestEvaluator 구현).

원본 ``src/adapters/bt4_adapter.py`` 를 감싼다. 단, bt4_adapter 는 **import 시점**에
외부 엔진(``../../../bt4_trader``)을 찾지 못하면 ``ImportError`` 를 던지므로, 모듈을
import 하는 것만으로 전체 파이프라인이 죽지 않도록 **지연 import**(메서드 내부)한다.

불안정한 외부 서브프로세스 백테스트가 일시적으로 실패할 수 있으므로 ``@retry`` 를 적용
(합성 경로에는 영향 없음 — 인터페이스 대칭과 견고성 시연 목적).
"""

from __future__ import annotations

from typing import Dict

from src.after.decorators import retry


class BT4BacktestEvaluator:
    """bt4_trader 백테스트 엔진 기반 평가기(외부 의존)."""

    def __init__(self, bt4_config: Dict):
        self.bt4_config = bt4_config
        self._adapter = None  # 지연 생성

    def _ensure_adapter(self):
        if self._adapter is None:
            # 지연 import: 외부 엔진이 없으면 여기서만 실패
            from src.adapters.bt4_adapter import BT4BacktestAdapter

            self._adapter = BT4BacktestAdapter(self.bt4_config)
        return self._adapter

    @retry(times=3, default=-1000.0)
    def evaluate(self, strategy_json: Dict) -> float:
        adapter = self._ensure_adapter()
        return adapter.evaluate_strategy(strategy_json)
