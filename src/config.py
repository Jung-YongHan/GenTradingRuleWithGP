# config.py

import operator

# --- 유전 프로그래밍 기본 재료 ---
INDICATORS = ["RSI", "SMA", "MACD", "ATR", "BB"]
NUM_INDICATOR_PARAMS = [5, 10, 14, 20, 30, 50, 100, 150, 200]
SOURCES = ["open", "high", "low", "close", "volume"]
OPS = [operator.gt, operator.ge, operator.eq, operator.ne, operator.lt, operator.le]
INITIAL_CONDITIONS_COUNT = 50

# --- 진화 파라미터 ---
N_POP = 100
N_GEN = 20
CXPB = 0.8
MUTPB = 0.15

# --- 트리 구조 파라미터 ---
INITIAL_MIN_DEPTH = 2
INITIAL_MAX_DEPTH = 6
MUTATION_MAX_DEPTH = 4
MAX_TREE_SIZE = 100

# --- 파일 및 폴더 이름 ---
LOG_DIR = "logs"