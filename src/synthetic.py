# src/synthetic.py
"""공유 합성(synthetic) 적합도 평가 로직.

실제 적합도 평가는 외부 독점 백테스트 엔진(``bt4_trader``)에 의존하므로 채점 환경에서
재현이 불가능하다. 본 모듈은 과제 지침(synthetic data 기반 재현 버전 허용)에 따라,
전략 JSON만으로 **결정적(deterministic)** 적합도를 계산하는 순수 함수를 제공한다.

설계 원칙
---------
* **순수 함수**: 전역 ``random``/벽시계/IO 사용 안 함. 동일 JSON → 동일 점수
  (전략 캐시가 의미를 가지며, before/after 실행이 동일한 결과를 내도록 보장).
* **공정성**: ``src/before``와 ``src/after`` 가 *같은* 이 함수를 사용한다. 따라서
  벤치마크가 측정하는 차이는 leaf 평가가 아니라 그 주위의 오케스트레이션 코드뿐이다.
* **최적화 지형 존재**: 순수 해시 난수만 쓰면 적합도가 평평해 GP가 개선되지 않는다.
  실제 백테스트처럼 "구조적 보상 + 소량의 결정적 잡음" 형태로 설계하여, 세대가
  진행될수록 best fitness 가 상승하는 의미 있는 곡선이 나오도록 한다.
"""

from __future__ import annotations

import hashlib
import math
from typing import Dict

# 합성 시장이 "선호"하는 연산자 가중치 (실제 백테스트에서 특정 조건 조합이
# 더 수익적인 상황을 모사). 값은 임의지만 고정되어 있어 재현 가능하다.
_OP_WEIGHTS = {
    ">": 1.0,
    ">=": 0.8,
    "<": 1.0,
    "<=": 0.8,
    "==": -0.5,  # 등호 비교는 거래 신호가 드물어 불리하게 모사
    "!=": 0.2,
}


def _hash_unit(payload: str) -> float:
    """문자열을 [0, 1) 구간의 결정적 실수로 매핑."""
    digest = hashlib.sha256(payload.encode("utf-8")).digest()
    # 앞 8바이트를 정수로 → [0, 1)
    value = int.from_bytes(digest[:8], "big")
    return value / float(1 << 64)


def score_strategy(strategy_json: Dict, *, seed: int = 42) -> float:
    """전략 JSON으로부터 결정적 적합도(총수익률 % 모사값)를 계산한다.

    Args:
        strategy_json: parser/validator 를 거친 전략 딕셔너리
            (``vars``, ``buy_systems``, ``buy_system_op``, ``sell_systems``,
            ``sell_system_op`` 키를 가짐).
        seed: 합성 시장 시드. 동일 seed + 동일 JSON → 동일 점수.

    Returns:
        적합도 점수(float). 대략 [-100, 100] 범위.
    """
    if not strategy_json:
        return -1000.0

    buy_systems = strategy_json.get("buy_systems", {})
    sell_systems = strategy_json.get("sell_systems", {})
    variables = strategy_json.get("vars", {})
    buy_op = strategy_json.get("buy_system_op", "") or ""
    sell_op = strategy_json.get("sell_system_op", "") or ""

    # 매수/매도 양쪽에 실제 사용되는 시스템이 없으면 거래가 불가능 → 강한 페널티
    if not buy_systems or not sell_systems:
        return -50.0

    # 1) 구조적 보상: 매수/매도 조건의 균형과 지표 다양성
    n_buy = len(buy_systems)
    n_sell = len(sell_systems)
    n_vars = len(variables)
    balance = 1.0 - abs(n_buy - n_sell) / max(n_buy + n_sell, 1)  # 0~1
    diversity = math.tanh(n_vars / 8.0)  # 지표가 많을수록 1에 수렴

    # 2) 연산자 구성 보상: 선호 연산자가 많을수록 가점
    op_score = 0.0
    n_ops = 0
    for system in list(buy_systems.values()) + list(sell_systems.values()):
        op = system.get("op")
        if op is not None:
            op_score += _OP_WEIGHTS.get(op, 0.0)
            n_ops += 1
    op_score = op_score / n_ops if n_ops else 0.0  # -0.5~1.0

    # 3) 복잡도 페널티: 조건식이 과도하게 길면 과적합 모사로 감점
    complexity = len(buy_op) + len(sell_op)
    complexity_penalty = max(0.0, (complexity - 120) / 40.0)

    # 4) 결정적 잡음: 동일 전략은 항상 같은 값(캐시·재현성), 전략별로는 변동
    canonical = f"{seed}|{buy_op}|{sell_op}|{sorted(variables.keys())}"
    noise = (_hash_unit(canonical) - 0.5) * 12.0  # ±6

    base = 40.0 * balance + 25.0 * diversity + 20.0 * op_score
    return round(base - 10.0 * complexity_penalty + noise, 4)
