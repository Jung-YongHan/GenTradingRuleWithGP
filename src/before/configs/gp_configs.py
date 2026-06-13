# gp_configs.py

INDICATORS_COUNT = 1000  # 초기 지표 개수
INITIAL_CONDITIONS_COUNT = 500  # 초기 조건 개수

# --- 진화 파라미터 ---
N_POPULATION = 1000  # 개체군 크기
N_GENERATION = 50  # 세대 수
CROSSOVER_PROBABILITY = 0.8  # 교차 확률
MUTATION_PROBABILITY = 0.15  # 변이 확률

# --- 트리 구조 파라미터 ---
INITIAL_MIN_DEPTH = 4  # 초기 최소 깊이
INITIAL_MAX_DEPTH = 10  # 초기 최대 깊이
MAX_MUTATION_DEPTH = 6  # 변이 최대 깊이
MAX_TREE_SIZE = 500  # 최대 트리 크기
