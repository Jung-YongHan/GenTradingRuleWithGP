# after/main.py
"""최적화 후 메인 실행 (오케스트레이션 전용).

원본 ``main()`` 의 ~130줄(설정·상태·진화 루프·통계·로깅·시각화·저장 혼재)을, 책임이
분리된 컴포넌트들의 *조립*으로 축소했다. 진화 루프 자체는 ``EvolutionRunner.run()``
제너레이터가 담당하며, 여기서는 세대별 통계를 lazy 하게 소비해 로깅만 한다.
"""

from __future__ import annotations

import json
import logging
import random

from deap import base, creator, gp

from src.after.benchmark_entry import build_pipeline
from src.after.config import GPConfig
from src.after.evolution.runner import EvolutionRunner
from src.after.strategy.parser import parse_gp_tree_to_json
from src.after.strategy.validator import validate_and_clean_strategy
from src.after.utils.file_handler import (
    save_json_strategy,
    setup_logging,
    visualize_tree,
)
from src.after.utils.visualizer import (
    visualize_evolution,
    visualize_fitness_distribution,
)


def _ensure_creator():
    """DEAP creator 클래스는 프로세스당 1회만 생성."""
    if not hasattr(creator, "FitnessMax"):
        creator.create("FitnessMax", base.Fitness, weights=(1.0,))
    if not hasattr(creator, "Individual"):
        creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMax)


def main(cfg: GPConfig, evaluator_name: str = "synthetic") -> None:
    output_dir = setup_logging()
    _ensure_creator()
    random.seed(cfg.random_seed)

    condition_manager, strategy_evaluator, toolbox = build_pipeline(cfg, evaluator_name)
    runner = EvolutionRunner(cfg, toolbox)

    logging.info("=" * 60)
    logging.info(
        "🚀 GP 진화 시작 (세대: %d, 개체수: %d, 평가기: %s)",
        cfg.n_generation,
        cfg.n_population,
        evaluator_name,
    )
    logging.info("=" * 60)

    # 제너레이터를 lazy 하게 소비하며 세대별 로깅
    stats_history = []
    for s in runner.run():
        stats_history.append(
            {
                "generation": s.generation,
                "max": s.max,
                "avg": s.avg,
                "min": s.min,
                "std": s.std,
                "duration": s.duration,
            }
        )
        logging.info(
            "> 세대 %02d: 최고=%.2f, 평균=%.2f, 최저=%.2f (소요: %.3f초)",
            s.generation,
            s.max,
            s.avg,
            s.min,
            s.duration,
        )

    best_ind = runner.best
    cache = strategy_evaluator.cache_stats()
    logging.info("=" * 60)
    logging.info(
        "📦 캐시: 고유=%d, 적중=%d, 미스=%d",
        cache["total_cached"],
        cache["hits"],
        cache["misses"],
    )
    logging.info("🏆 최고 적합도: %.2f (트리 크기: %d)", best_ind.fitness.values[0], len(best_ind))

    raw_json = parse_gp_tree_to_json(best_ind, condition_manager)
    final_json = validate_and_clean_strategy(raw_json) if raw_json else None

    logging.info("📊 시각화 생성 중...")
    visualize_evolution(stats_history, output_dir)
    visualize_fitness_distribution(runner.state.population, output_dir)

    if final_json:
        logging.info(
            "[ 최종 JSON ]\n%s", json.dumps(final_json, indent=4, ensure_ascii=False)
        )
        save_json_strategy(final_json, output_dir)
        visualize_tree(best_ind, output_dir)
    else:
        logging.error("❌ 최적 개체가 유효한 'Strategy' 구조가 아닙니다.")


if __name__ == "__main__":
    # 데모 설정(빠른 실행). 운영 규모는 GPConfig 기본값(1000×50) 참고.
    demo_cfg = GPConfig(
        indicators_count=200,
        initial_conditions_count=100,
        n_population=300,
        n_generation=30,
    )
    main(demo_cfg, evaluator_name="synthetic")
