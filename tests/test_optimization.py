"""최적화 전/후 동작 등가성 및 핵심 속성 검증.

실행: ``.venv/bin/python -m pytest tests/test_optimization.py -v``
"""

from __future__ import annotations

import os
import random
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from deap import base, creator, gp  # noqa: E402

if not hasattr(creator, "FitnessMax"):
    creator.create("FitnessMax", base.Fitness, weights=(1.0,))
if not hasattr(creator, "Individual"):
    creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMax)


def _make_cms(n_cond, n_ind, seed):
    import src.before.domain.condition as bc
    import src.after.domain.condition as ac

    random.seed(seed)
    b = bc.ConditionManager(n_cond, n_ind)
    random.seed(seed)
    a = ac.ConditionManager(n_cond, n_ind)
    return b, a


def _strategy_individuals(before_cm, n, seed):
    from src.before.gp.toolbox import create_primitive_set, create_toolbox

    pset = create_primitive_set(before_cm)
    tb = create_toolbox(pset, before_cm, None)
    random.seed(seed)
    out = []
    while len(out) < n:
        pop = tb.population(n=400)
        out.extend(i for i in pop if i[0].name == "Strategy")
    return out[:n]


def test_parser_equivalence():
    """after 파서 출력이 before 와 byte-identical(dict equality)."""
    from src.before.strategy.parser import parse_gp_tree_to_json as b_parse
    from src.after.strategy.parser import parse_gp_tree_to_json as a_parse

    before_cm, after_cm = _make_cms(40, 60, seed=7)
    inds = _strategy_individuals(before_cm, 40, seed=123)
    assert inds, "Strategy-rooted 개체가 없음"
    for ind in inds:
        assert b_parse(ind, before_cm) == a_parse(ind, after_cm)


def test_validator_equivalence():
    from src.before.strategy.parser import parse_gp_tree_to_json as b_parse
    from src.before.strategy.validator import validate_and_clean_strategy as b_val
    from src.after.strategy.validator import validate_and_clean_strategy as a_val

    before_cm, _ = _make_cms(40, 60, seed=7)
    inds = _strategy_individuals(before_cm, 30, seed=123)
    for ind in inds:
        j = b_parse(ind, before_cm)
        if j is not None:
            assert b_val(j) == a_val(j)


def test_synthetic_deterministic():
    """동일 JSON → 동일 점수 (재현성/캐시 전제)."""
    from src.synthetic import score_strategy

    js = {
        "vars": {"RSI1": {}, "SMA1": {}},
        "buy_systems": {"system1": {"op": ">"}},
        "sell_systems": {"system1": {"op": "<"}},
        "buy_system_op": "system1",
        "sell_system_op": "system1",
    }
    assert score_strategy(js, seed=42) == score_strategy(js, seed=42)
    # 시드가 다르면 (일반적으로) 다른 점수
    assert score_strategy(js, seed=1) != score_strategy(js, seed=999)


def test_strategy_evaluator_cache():
    """StrategyEvaluator 가 동일 전략 재평가 시 캐시 적중."""
    from src.after.config import GPConfig
    from src.after.evaluation.registry import make_evaluator
    from src.after.evaluation.strategy_evaluator import StrategyEvaluator

    _, after_cm = _make_cms(40, 60, seed=7)
    inds = _strategy_individuals_after(after_cm, 30, seed=123)
    cfg = GPConfig()
    se = StrategyEvaluator(make_evaluator("synthetic", cfg), after_cm)
    for ind in inds:
        se.evaluate(ind)
    # 같은 개체들을 다시 평가하면 모두 캐시 적중
    hits_before = se._hits
    for ind in inds:
        se.evaluate(ind)
    assert se._hits > hits_before
    stats = se.cache_stats()
    assert stats["total_cached"] >= 1


def _strategy_individuals_after(after_cm, n, seed):
    from src.after.gp.toolbox import create_primitive_set, create_toolbox
    from src.after.config import GPConfig

    pset = create_primitive_set(after_cm)
    tb = create_toolbox(pset, GPConfig(), lambda ind: (0.0,))
    random.seed(seed)
    out = []
    while len(out) < n:
        pop = tb.population(n=400)
        out.extend(i for i in pop if i[0].name == "Strategy")
    return out[:n]


def test_macro_trajectory_equal():
    """before/after 전체 진화의 best-fitness 궤적이 동일(회귀 게이트)."""
    from src.before.benchmark_entry import run_evolution as b_run
    from src.after.benchmark_entry import run_evolution as a_run

    kw = dict(n_population=60, n_generation=10, n_conditions=20, n_indicators=30, seed=42)
    b = b_run(**kw)
    a = a_run(**kw)
    assert b["max_trajectory"] == a["max_trajectory"]
    assert b["best_fitness"] == a["best_fitness"]


if __name__ == "__main__":
    test_parser_equivalence()
    test_validator_equivalence()
    test_synthetic_deterministic()
    test_strategy_evaluator_cache()
    test_macro_trajectory_equal()
    print("ALL TESTS PASSED")
