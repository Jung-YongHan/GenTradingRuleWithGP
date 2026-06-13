# after/utils/helpers.py
"""지표 이름 파싱 유틸리티 (최적화).

최적화 포인트
-------------
* **정규식 사전 컴파일**: ``extract_base_indicator_name`` 의 패턴을 모듈 로드 시 1회
  ``re.compile`` 한다(원본은 호출마다 ``re.match`` 인라인).
* **``functools.lru_cache``** (D): 두 함수 모두 **순수 함수**이고 인자가 짧은 문자열이며
  지표 이름이 개체·피연산자마다 반복 등장한다. 따라서 동일 인자 재호출이 매우 잦아
  캐시 적중률이 높다 → 정규식/문자열 연산을 건너뛴다.
"""

from __future__ import annotations

import re
from functools import lru_cache

# 모듈 로드 시 1회만 컴파일 (호출마다 재컴파일 제거)
_BASE_NAME_RE = re.compile(r"^(.+?)(\d+)$")


@lru_cache(maxsize=None)
def extract_base_indicator_name(indicator_name: str) -> str:
    """지표 이름에서 끝 숫자를 제거해 원본 이름을 추출한다.

    Examples: RSI1 -> RSI, MACD2 -> MACD, SMA10 -> SMA
    """
    match = _BASE_NAME_RE.match(indicator_name)
    if match:
        return match.group(1)
    return indicator_name


@lru_cache(maxsize=None)
def extract_base_from_access_name(access_name: str) -> str:
    """접근 이름에서 기본 지표 이름을 추출한다.

    Examples: MACD1[0] -> MACD1, RSI1 -> RSI1, close -> close
    """
    if "[" in access_name:
        return access_name.split("[", 1)[0]
    return access_name
