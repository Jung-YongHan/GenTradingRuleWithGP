# config.py

import operator

# --- 랜덤 시드 ---
RANDOM_SEED = 20

# --- 유전 프로그래밍 기본 재료 ---
INDICATORS = ["RSI", "SMA", "MACD", "ATR", "BB"]  # 지표
INDICATOR_PARAMS = [5, 10, 14, 20, 30, 50, 100, 150, 200]  # 지표 파라미터
SOURCES = ["open", "high", "low", "close", "volume"]  # 소스
OPERATORS = [
    operator.gt,
    operator.ge,
    operator.eq,
    operator.ne,
    operator.lt,
    operator.le,
]  # 연산자
INITIAL_CONDITIONS_COUNT = 50  # 초기 조건 개수


# --- 진화 파라미터 ---
N_POPULATION = 100  # 개체군 크기
N_GENERATION = 20  # 세대 수
CROSSOVER_PROBABILITY = 0.8  # 교차 확률
MUTATION_PROBABILITY = 0.15  # 변이 확률

# --- 트리 구조 파라미터 ---
INITIAL_MIN_DEPTH = 2  # 초기 최소 깊이
INITIAL_MAX_DEPTH = 6  # 초기 최대 깊이
MAX_MUTATION_DEPTH = 4  # 변이 최대 깊이
MAX_TREE_SIZE = 100  # 최대 트리 크기

# --- 파일 및 폴더 이름 ---
LOG_DIR = "logs"  # 로그 폴더
