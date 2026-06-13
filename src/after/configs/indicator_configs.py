# after/configs/indicator_configs.py
"""기술적 지표 정의 및 GP 기본 재료.

최적화(A. 자료구조): membership test 가 잦은 ``OHLCV_SOURCES`` 를 list 와 더불어
``frozenset`` 으로도 제공한다. 파서/검증/포매터에서 ``x in OHLCV_SOURCES`` 가
피연산자마다 호출되는데, list 는 O(n) 선형탐색인 반면 frozenset 은 O(1) 해시탐색이다.
``random.choice`` 처럼 인덱싱이 필요한 곳에서는 기존 순서 리스트를 그대로 쓴다.
"""

# --- 유전 프로그래밍 기본 재료 ---
CDL_TYPES = [1, 3, 5, 15, 30, 60, 240, 1440]  # 캔들 타입
SOURCES = ["open", "high", "low", "close", "volume"]  # 소스 (random.choice 용 순서 보존)
OHLCV_SOURCES = ["open", "high", "low", "close", "volume"]  # OHLCV 원시 데이터
OHLCV_SOURCES_SET = frozenset(OHLCV_SOURCES)  # O(1) membership test 용
OPERATORS = [">", ">=", "==", "!=", "<", "<="]  # 연산자 (random.choice 용)

# --- 지표별 상세 정의 (원본과 동일) ---
INDICATOR_DEFINITIONS = {
    "RSI": {
        "func": "rsi",
        "param_types": [{"type": "int", "min": 2, "max": 200, "name": "period"}],
        "sources": {"count": 1, "allowed": SOURCES, "fixed": None},
        "unary": True,
    },
    "SMA": {
        "func": "sma",
        "param_types": [{"type": "int", "min": 1, "max": 500, "name": "period"}],
        "sources": {"count": 1, "allowed": SOURCES, "fixed": None},
        "unary": True,
    },
    "MACD": {
        "func": "macd",
        "param_types": [
            {"type": "int", "min": 1, "max": 50, "name": "fast_period"},
            {"type": "int", "min": 1, "max": 100, "name": "slow_period"},
            {"type": "int", "min": 1, "max": 50, "name": "signal_period"},
        ],
        "sources": {"count": 1, "allowed": SOURCES, "fixed": None},
        "unary": False,
        "return_count": 3,
    },
    "ATR": {
        "func": "atr",
        "param_types": [{"type": "int", "min": 1, "max": 100, "name": "period"}],
        "sources": {"count": 3, "allowed": None, "fixed": ["high", "low", "close"]},
        "unary": True,
    },
    "BBANDS": {
        "func": "bbands",
        "param_types": [
            {"type": "int", "min": 1, "max": 200, "name": "period"},
            {"type": "float", "min": 0.1, "max": 5.0, "name": "std_dev_up"},
            {"type": "float", "min": 0.1, "max": 5.0, "name": "std_dev_down"},
            {"type": "category", "values": [0, 1, 2], "name": "ma_type"},
        ],
        "sources": {"count": 1, "allowed": SOURCES, "fixed": None},
        "unary": False,
        "return_count": 3,
    },
}

# 자주 쓰는 파생 자료구조도 모듈 로드 시 1회 계산해 둔다.
INDICATOR_NAMES = list(INDICATOR_DEFINITIONS.keys())  # random.choice 용
