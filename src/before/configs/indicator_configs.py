# indicator_configs.py

# --- 유전 프로그래밍 기본 재료 ---
CDL_TYPES = [1, 3, 5, 15, 30, 60, 240, 1440]  # 캔들 타입
SOURCES = ["open", "high", "low", "close", "volume"]  # 소스
OHLCV_SOURCES = ["open", "high", "low", "close", "volume"]  # OHLCV 원시 데이터
OPERATORS = [
    ">",
    ">=",
    "==",
    "!=",
    "<",
    "<=",
]  # 연산자

# --- 지표별 상세 정의 ---
# -------------------------------------------------------------------
# INDICATOR_DEFINITIONS 요약
# - func: 실제로 사용할 지표 함수 이름 (예: "rsi", "sma" 등)
# - param_types: 각 지표별 파라미터 타입 및 범위 정의 (리스트)
#     - type: 파라미터 타입 ("int", "float", "category" 등)
#     - min, max: 파라미터 값의 최소/최대 (type이 int/float일 때)
#     - values: 선택 가능한 값 목록 (type이 category일 때)
#     - name: 파라미터 이름
# - sources: 지표 계산에 필요한 입력 데이터(소스) 정의 (딕셔너리)
#     - count: 필요한 소스의 개수 (예: 1개, 3개 등)
#     - allowed: 선택 가능한 소스 목록 (예: OHLCV 중 어떤 것 사용 가능한지)
#     - fixed: 고정된 소스 조합이 필요한 경우 명시 (예: ["high", "low", "close"])
# - unary: True면 단일 값 반환(단항), False면 여러 값 반환(복수)
# - return_count: (옵션) 복수 반환 시 반환 값의 개수 (예: MACD, BBANDS 등)
# -------------------------------------------------------------------
INDICATOR_DEFINITIONS = {
    "RSI": {
        "func": "rsi",
        "param_types": [{"type": "int", "min": 2, "max": 200, "name": "period"}],
        "sources": {
            "count": 1,
            "allowed": SOURCES,
            "fixed": None,
        },
        "unary": True,
    },
    "SMA": {
        "func": "sma",
        "param_types": [{"type": "int", "min": 1, "max": 500, "name": "period"}],
        "sources": {
            "count": 1,
            "allowed": SOURCES,
            "fixed": None,
        },
        "unary": True,
    },
    "MACD": {
        "func": "macd",
        "param_types": [
            {"type": "int", "min": 1, "max": 50, "name": "fast_period"},
            {"type": "int", "min": 1, "max": 100, "name": "slow_period"},
            {"type": "int", "min": 1, "max": 50, "name": "signal_period"},
        ],
        "sources": {
            "count": 1,
            "allowed": SOURCES,
            "fixed": None,
        },
        "unary": False,
        "return_count": 3,
    },
    "ATR": {
        "func": "atr",
        "param_types": [{"type": "int", "min": 1, "max": 100, "name": "period"}],
        "sources": {
            "count": 3,
            "allowed": None,
            "fixed": ["high", "low", "close"],
        },
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
        "sources": {
            "count": 1,
            "allowed": SOURCES,
            "fixed": None,
        },
        "unary": False,
        "return_count": 3,
    },
}
