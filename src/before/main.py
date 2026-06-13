# main.py

import json
import logging
import multiprocessing
import random
import sys
import time

from deap import base, creator, gp, tools

from src.before.configs.bt4_config import load_bt4_config
from src.before.configs.constants import CPU_COUNT, RANDOM_SEED

# --- 설정 및 모듈 임포트 ---
from src.before.configs.gp_configs import (
    CROSSOVER_PROBABILITY,
    INDICATORS_COUNT,
    INITIAL_CONDITIONS_COUNT,
    MUTATION_PROBABILITY,
    N_GENERATION,
    N_POPULATION,
)
from src.before.domain.condition import ConditionManager
from src.before.gp.evaluator import clear_cache, get_cache_stats, set_bt4_config
from src.before.gp.toolbox import create_primitive_set, create_toolbox
from src.before.strategy.parser import parse_gp_tree_to_json
from src.before.strategy.validator import validate_and_clean_strategy
from src.before.utils.file_handler import save_json_strategy, setup_logging, visualize_tree
from src.before.utils.visualizer import visualize_evolution, visualize_fitness_distribution


def main(pool: multiprocessing.Pool):
    """메인 실행 함수"""
    # 환경 설정
    output_dir = setup_logging()

    # 캐시 초기화
    clear_cache()
    logging.info("전략 평가 캐시 초기화 완료")

    # DEAP 기본 creator 설정
    creator.create("FitnessMax", base.Fitness, weights=(1.0,))
    creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMax)

    # GP 환경 설정
    condition_manager = ConditionManager(INITIAL_CONDITIONS_COUNT, INDICATORS_COUNT)
    pset = create_primitive_set(condition_manager)
    toolbox = create_toolbox(pset, condition_manager, pool)

    # (이하 코드는 이전과 동일)
    # 진화 시작
    pop = toolbox.population(n=N_POPULATION)

    logging.info("✨ 초기 개체군 생성 및 평가 시작...")
    fitnesses = toolbox.map(toolbox.evaluate, pop)
    for ind, fit in zip(pop, fitnesses):
        ind.fitness.values = fit

    logging.info("=" * 60)
    logging.info(
        f"🚀 유전 프로그래밍 진화 시작! "
        f"(세대: {N_GENERATION}, 개체수: {N_POPULATION})"
    )
    logging.info("=" * 60)

    # 진화 시작 시간 기록
    evolution_start_time = time.time()

    # 통계 수집을 위한 리스트
    stats_history = []

    for g in range(N_GENERATION):
        generation_start_time = time.time()

        offspring = toolbox.select(pop, len(pop))
        offspring = list(map(toolbox.clone, offspring))

        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < CROSSOVER_PROBABILITY:
                toolbox.mate(child1, child2)
                del child1.fitness.values, child2.fitness.values
        for mutant in offspring:
            if random.random() < MUTATION_PROBABILITY:
                toolbox.mutate(mutant)
                del mutant.fitness.values

        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        pop[:] = offspring
        fits = [ind.fitness.values[0] for ind in pop]

        # 통계 계산 및 저장
        max_fit = max(fits)
        avg_fit = sum(fits) / len(pop)
        min_fit = min(fits)
        std_fit = (sum((x - avg_fit) ** 2 for x in fits) / len(fits)) ** 0.5

        generation_end_time = time.time()
        generation_duration = generation_end_time - generation_start_time

        stats_history.append(
            {
                "generation": g + 1,
                "max": max_fit,
                "avg": avg_fit,
                "min": min_fit,
                "std": std_fit,
                "duration": generation_duration,
            }
        )

        logging.info(
            f"> 세대 {g+1:02d}: 최고={max_fit:.2f}, "
            f"평균={avg_fit:.2f}, 최저={min_fit:.2f} "
            f"(소요시간: {generation_duration:.2f}초)"
        )

    # 진화 종료 시간 기록 및 소요 시간 계산
    evolution_end_time = time.time()
    evolution_duration = evolution_end_time - evolution_start_time

    # 캐시 통계 출력
    cache_stats = get_cache_stats()
    logging.info("=" * 60)
    logging.info("📦 전략 캐시 통계")
    logging.info(f"   - 캐시된 고유 전략 수: {cache_stats['total_cached']}")
    logging.info(f"   - 캐시 크기: {cache_stats['cache_size_bytes'] / 1024:.2f} KB")

    # 4. 최종 결과 처리
    logging.info("=" * 60)
    logging.info("🏆 최종 최적 전략 탐색 완료!")
    logging.info(
        f"⏱️  진화 소요 시간: {evolution_duration:.2f}초 "
        f"({evolution_duration/60:.2f}분)"
    )

    best_ind = tools.selBest(pop, 1)[0]
    raw_json_strategy = parse_gp_tree_to_json(best_ind, condition_manager)
    final_json_strategy = validate_and_clean_strategy(raw_json_strategy)

    logging.info(f"최적 개체 트리 구조 (크기: {len(best_ind)}):\n{str(best_ind)}")
    logging.info(f"최고 적합도: {best_ind.fitness.values[0]:.2f}")

    # 진화 과정 시각화
    logging.info("=" * 60)
    logging.info("📊 진화 과정 시각화 생성 중...")
    visualize_evolution(stats_history, output_dir)
    visualize_fitness_distribution(pop, output_dir)

    if final_json_strategy:
        json_output = json.dumps(final_json_strategy, indent=4, ensure_ascii=False)
        logging.info(f"[ 최종 JSON 출력 ]\n{json_output}")
        save_json_strategy(final_json_strategy, output_dir)
        visualize_tree(best_ind, output_dir)
    else:
        logging.error(
            "❌ 최종 JSON 생성 실패: 최적 개체가 유효한 'Strategy' 구조가 아닙니다."
        )


if __name__ == "__main__":
    random.seed(RANDOM_SEED)

    # BT4 백테스트 설정 로드 및 전역 설정
    # 여기서 원하는 설정 파일을 선택할 수 있습니다
    bt4_config_file = "base_config.json"  # 다른 파일로 변경 가능

    print("=" * 60)
    print("🔧 BT4 백테스트 설정 로드")
    print("=" * 60)
    try:
        bt4_config = load_bt4_config(bt4_config_file)
        set_bt4_config(bt4_config)
        print(f"✓ 설정 파일 로드 완료: {bt4_config_file}")
        print(f"  - 거래소: {bt4_config.get('ex_type', 'N/A')}")
        bt_start = bt4_config.get("bt_start", "N/A")
        bt_end = bt4_config.get("bt_end", "N/A")
        print(f"  - 기간: {bt_start} ~ {bt_end}")
        print(f"  - 마켓: {', '.join(bt4_config.get('markets', []))}")
        init_bal = bt4_config.get("init_balance", 0)
        print(f"  - 초기자본: {init_bal:,}원")
    except Exception as e:
        print(f"✗ 설정 파일 로드 실패: {e}")
        print("  기본 설정을 사용할 수 없습니다. 프로그램을 종료합니다.")
        sys.exit(1)
    print()

    # 시스템 전체 CPU 개수와 설정된 CPU 개수 출력
    system_cpu_count = multiprocessing.cpu_count()
    used_cpu_count = CPU_COUNT
    print(f"시스템 CPU 개수: {system_cpu_count}")
    print(f"사용할 CPU 개수: {used_cpu_count}")

    with multiprocessing.Pool(used_cpu_count) as pool:
        main(pool)
