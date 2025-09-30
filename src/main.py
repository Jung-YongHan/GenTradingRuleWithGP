# main.py

import json
import logging
import random

from deap import base, creator, gp, tools

# --- 설정 및 모듈 임포트 ---
import config
from domain.condition import ConditionManager
from gp.toolbox import create_primitive_set, create_toolbox
from strategy.parser import parse_gp_tree_to_json
from strategy.validator import validate_and_clean_strategy
from utils.file_handler import save_json_strategy, setup_logging, visualize_tree


def main():
    """메인 실행 함수"""
    # 환경 설정
    output_dir = setup_logging()
    random.seed(config.RANDOM_SEED)

    # DEAP 기본 creator 설정
    creator.create("FitnessMax", base.Fitness, weights=(1.0,))
    creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMax)

    # GP 환경 설정
    condition_manager = ConditionManager(
        config.INITIAL_CONDITIONS_COUNT, config.INDICATORS_COUNT
    )
    pset = create_primitive_set(condition_manager)
    toolbox = create_toolbox(pset, condition_manager)

    # (이하 코드는 이전과 동일)
    # 진화 시작
    pop = toolbox.population(n=config.N_POPULATION)

    logging.info("✨ 초기 개체군 생성 및 평가 시작...")
    fitnesses = map(toolbox.evaluate, pop)
    for ind, fit in zip(pop, fitnesses):
        ind.fitness.values = fit

    logging.info("=" * 60)
    logging.info(
        f"🚀 유전 프로그래밍 진화 시작! (세대: {config.N_GENERATION}, 개체수: {config.N_POPULATION})"
    )
    logging.info("=" * 60)

    for g in range(config.N_GENERATION):
        offspring = toolbox.select(pop, len(pop))
        offspring = list(map(toolbox.clone, offspring))

        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < config.CROSSOVER_PROBABILITY:
                toolbox.mate(child1, child2)
                del child1.fitness.values, child2.fitness.values
        for mutant in offspring:
            if random.random() < config.MUTATION_PROBABILITY:
                toolbox.mutate(mutant)
                del mutant.fitness.values

        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        pop[:] = offspring
        fits = [ind.fitness.values[0] for ind in pop]
        logging.info(
            f"> 세대 {g+1:02d}: 최고={max(fits):.2f}, 평균={sum(fits)/len(pop):.2f}"
        )

    # 4. 최종 결과 처리
    logging.info("=" * 60)
    logging.info("🏆 최종 최적 전략 탐색 완료!")

    best_ind = tools.selBest(pop, 1)[0]
    raw_json_strategy = parse_gp_tree_to_json(best_ind, condition_manager)
    final_json_strategy = validate_and_clean_strategy(raw_json_strategy)

    logging.info(f"최적 개체 트리 구조 (크기: {len(best_ind)}):\n{str(best_ind)}")
    logging.info(f"최고 적합도: {best_ind.fitness.values[0]:.2f}")

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
    main()
