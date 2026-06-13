# after/evolution/stats.py
"""세대 통계 (A. 단일 패스 + B. lazy 입력 + C. 책임 분리).

원본 main() 은 ``fits`` 리스트를 만든 뒤 ``max``/``min``/``sum`` 으로 3번, 표준편차에서
다시 1번, 총 4번 순회했다(2-pass 표준편차). 여기서는 통계 계산을 ``StatsCollector`` 로
분리하고, 합/제곱합/최대/최소를 **단일 패스**로 누적한다. 입력은 리스트가 아니라
이터러블이어도 되므로(제너레이터 친화) 중간 리스트 없이 처리 가능.

표준편차는 원본과 동일하게 **모집단 표준편차(÷n)** 를 사용한다.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True, slots=True)
class GenerationStats:
    """한 세대의 적합도 통계(불변)."""

    generation: int
    max: float
    avg: float
    min: float
    std: float
    duration: float = 0.0


class StatsCollector:
    """적합도 이터러블을 단일 패스로 요약."""

    def summarize(
        self, fits: Iterable[float], generation: int, duration: float = 0.0
    ) -> GenerationStats:
        n = 0
        total = 0.0
        sum_sq = 0.0
        mx = -math.inf
        mn = math.inf
        for x in fits:  # 단일 패스
            n += 1
            total += x
            sum_sq += x * x
            if x > mx:
                mx = x
            if x < mn:
                mn = x
        if n == 0:
            return GenerationStats(generation, 0.0, 0.0, 0.0, 0.0, duration)
        mean = total / n
        var = sum_sq / n - mean * mean
        std = math.sqrt(var) if var > 0.0 else 0.0
        return GenerationStats(generation, mx, mean, mn, std, duration)
