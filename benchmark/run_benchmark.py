#!/usr/bin/env python
"""최적화 전(before) vs 후(after) 벤치마크 하니스.

측정 항목
--------
* 마이크로벤치: 핫 함수(parse / validate / get_strategy_hash / extract_*)를 입력 크기별로,
  warm-up 후 여러 번 반복 측정(평균/표준편차/최소). tracemalloc 으로 peak 메모리를 별도 패스로 측정.
* 매크로벤치: 전체 GP 진화(합성 평가기, 순차)를 (개체수×세대) 그리드로 측정. before/after 가
  동일 시드에서 **동일한 best-fitness 궤적**을 내는지 회귀 게이트로 검증.

before/after 는 별도 패키지(``src.before.*`` / ``src.after.*``)이므로 한 프로세스에서 동시
import 가능하다. DEAP ``creator`` 클래스는 프로세스당 1회만 생성한다.

출력: ``results/benchmark_results.csv`` , ``results/env.json`` , ``results/*.png``
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import platform
import statistics
import sys
import time
import tracemalloc

# 저장소 루트를 import 경로에 추가
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import random  # noqa: E402

from deap import base, creator, gp  # noqa: E402

RESULTS_DIR = os.path.join(ROOT, "results")


# ----------------------------------------------------------------------------- 공통 유틸
def ensure_creator():
    if not hasattr(creator, "FitnessMax"):
        creator.create("FitnessMax", base.Fitness, weights=(1.0,))
    if not hasattr(creator, "Individual"):
        creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMax)


def lib_version(name):
    try:
        from importlib.metadata import version

        return version(name)
    except Exception:
        return "N/A"


def git_commit():
    import subprocess

    try:
        return subprocess.check_output(
            ["git", "-C", ROOT, "rev-parse", "--short", "HEAD"],
            stderr=subprocess.DEVNULL,
        ).decode().strip()
    except Exception:
        return "N/A"


def capture_env(seed, repeats, warmup, timestamp):
    return {
        "os": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor() or platform.machine(),
        "python": sys.version.split()[0],
        "cpu_count": os.cpu_count(),
        "mp_start_method": __import__("multiprocessing").get_start_method(),
        "deap": lib_version("deap"),
        "numpy": lib_version("numpy"),
        "pandas": lib_version("pandas"),
        "git_commit": git_commit(),
        "timestamp": timestamp,
        "seed": seed,
        "repeats": repeats,
        "warmup": warmup,
    }


def timed(fn, repeats, warmup):
    """warm-up 후 repeats 회 측정 → (mean, pstdev, min) 초."""
    for _ in range(warmup):
        fn()
    samples = []
    for _ in range(repeats):
        t0 = time.perf_counter()
        fn()
        samples.append(time.perf_counter() - t0)
    mean = statistics.mean(samples)
    std = statistics.pstdev(samples) if len(samples) > 1 else 0.0
    return mean, std, min(samples)


def peak_memory(fn):
    """tracemalloc 으로 peak 메모리(bytes) 측정 (타이밍과 분리된 패스)."""
    tracemalloc.start()
    fn()
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return peak


# ----------------------------------------------------------------------------- 픽스처
def build_condition_managers(n_conditions, n_indicators, seed):
    """동일 시드로 before/after condition_manager 를 만든다(내용 동일)."""
    import src.before.domain.condition as bc
    import src.after.domain.condition as ac

    random.seed(seed)
    before_cm = bc.ConditionManager(n_conditions, n_indicators)
    random.seed(seed)
    after_cm = ac.ConditionManager(n_conditions, n_indicators)
    return before_cm, after_cm


def build_strategy_individuals(before_cm, n_want, seed):
    """before 툴박스로 Strategy-루트 개체를 n_want 개 수집."""
    from src.before.gp.toolbox import create_primitive_set, create_toolbox

    pset = create_primitive_set(before_cm)
    tb = create_toolbox(pset, before_cm, None)
    random.seed(seed)
    collected = []
    while len(collected) < n_want:
        pop = tb.population(n=max(64, n_want * 8))
        collected.extend(ind for ind in pop if ind[0].name == "Strategy")
    return collected[:n_want]


# ----------------------------------------------------------------------------- 마이크로벤치
def micro_parse(rows, sizes, n_individuals, repeats, warmup, seed):
    from src.before.strategy.parser import parse_gp_tree_to_json as b_parse
    from src.after.strategy.parser import parse_gp_tree_to_json as a_parse

    for (n_cond, n_ind) in sizes:
        before_cm, after_cm = build_condition_managers(n_cond, n_ind, seed)
        batch = build_strategy_individuals(before_cm, n_individuals, seed + 1)

        def run_before():
            for ind in batch:
                b_parse(ind, before_cm)

        def run_after():
            for ind in batch:
                a_parse(ind, after_cm)

        # 등가성 확인
        equal = all(
            b_parse(ind, before_cm) == a_parse(ind, after_cm) for ind in batch
        )

        for variant, fn in (("before", run_before), ("after", run_after)):
            mean, std, mn = timed(fn, repeats, warmup)
            mem = peak_memory(fn)
            rows.append(
                dict(
                    benchmark_kind="micro",
                    target="parse_gp_tree_to_json",
                    variant=variant,
                    n_indicators=n_ind,
                    n_conditions=n_cond,
                    tree_depth="",
                    n_population="",
                    n_generation="",
                    repeats=repeats,
                    warmup=warmup,
                    time_mean_s=mean,
                    time_std_s=std,
                    time_min_s=mn,
                    peak_mem_bytes=mem,
                    cache_mode="",
                    cache_hits="",
                    cache_misses="",
                    cache_unique="",
                    best_fitness="",
                    result_equal_before=equal,
                )
            )
        print(f"[micro parse] cond={n_cond} ind={n_ind} equal={equal}")


def micro_validate(rows, sizes, n_individuals, repeats, warmup, seed):
    from src.before.strategy.parser import parse_gp_tree_to_json as b_parse
    from src.before.strategy.validator import validate_and_clean_strategy as b_val
    from src.after.strategy.validator import validate_and_clean_strategy as a_val

    for (n_cond, n_ind) in sizes:
        before_cm, _ = build_condition_managers(n_cond, n_ind, seed)
        batch = build_strategy_individuals(before_cm, n_individuals, seed + 1)
        jsons = [b_parse(ind, before_cm) for ind in batch]
        jsons = [j for j in jsons if j is not None]

        def run_before():
            for j in jsons:
                b_val(j)

        def run_after():
            for j in jsons:
                a_val(j)

        equal = all(b_val(j) == a_val(j) for j in jsons)
        for variant, fn in (("before", run_before), ("after", run_after)):
            mean, std, mn = timed(fn, repeats, warmup)
            rows.append(
                dict(
                    benchmark_kind="micro",
                    target="validate_and_clean_strategy",
                    variant=variant,
                    n_indicators=n_ind,
                    n_conditions=n_cond,
                    tree_depth="",
                    n_population="",
                    n_generation="",
                    repeats=repeats,
                    warmup=warmup,
                    time_mean_s=mean,
                    time_std_s=std,
                    time_min_s=mn,
                    peak_mem_bytes=peak_memory(fn),
                    cache_mode="",
                    cache_hits="",
                    cache_misses="",
                    cache_unique="",
                    best_fitness="",
                    result_equal_before=equal,
                )
            )
        print(f"[micro validate] cond={n_cond} ind={n_ind} equal={equal}")


def micro_helpers(rows, repeats, warmup, seed):
    """extract_base_indicator_name: 반복 등장하는 지표 이름에 대한 lru_cache 효과."""
    from src.before.utils.helpers import extract_base_indicator_name as b_ex
    from src.after.utils.helpers import extract_base_indicator_name as a_ex

    rng = random.Random(seed)
    names = [f"{t}{rng.randint(1, 50)}" for t in ("RSI", "SMA", "MACD", "ATR", "BBANDS")]
    # 반복 호출 분포 (동일 이름이 자주 재등장 → 캐시 적중)
    calls = [rng.choice(names) for _ in range(50_000)]

    def run_before():
        for c in calls:
            b_ex(c)

    def run_after():
        for c in calls:
            a_ex(c)

    equal = all(b_ex(c) == a_ex(c) for c in names)
    for variant, fn in (("before", run_before), ("after", run_after)):
        mean, std, mn = timed(fn, repeats, warmup)
        rows.append(
            dict(
                benchmark_kind="micro",
                target="extract_base_indicator_name(50k calls)",
                variant=variant,
                n_indicators="",
                n_conditions="",
                tree_depth="",
                n_population="",
                n_generation="",
                repeats=repeats,
                warmup=warmup,
                time_mean_s=mean,
                time_std_s=std,
                time_min_s=mn,
                peak_mem_bytes=peak_memory(fn),
                cache_mode="warm",
                cache_hits="",
                cache_misses="",
                cache_unique="",
                best_fitness="",
                result_equal_before=equal,
            )
        )
    print(f"[micro helpers] extract_base_indicator_name equal={equal}")


# ----------------------------------------------------------------------------- 매크로벤치
def macro_evolution(rows, grid, repeats, warmup, seed, n_conditions, n_indicators):
    from src.before.benchmark_entry import run_evolution as before_run
    from src.after.benchmark_entry import run_evolution as after_run

    for (n_pop, n_gen) in grid:
        kw = dict(
            n_population=n_pop,
            n_generation=n_gen,
            n_conditions=n_conditions,
            n_indicators=n_indicators,
            seed=seed,
        )
        # 회귀 게이트: 동일 시드에서 best-fitness 궤적 동일?
        b_res = before_run(**kw)
        a_res = after_run(**kw)
        equal = b_res["max_trajectory"] == a_res["max_trajectory"]
        assert equal, f"궤적 불일치! pop={n_pop} gen={n_gen}"

        for variant, runner, res in (
            ("before", before_run, b_res),
            ("after", after_run, a_res),
        ):
            mean, std, mn = timed(lambda r=runner: r(**kw), repeats, warmup)
            mem = peak_memory(lambda r=runner: r(**kw))
            rows.append(
                dict(
                    benchmark_kind="macro",
                    target="evolution",
                    variant=variant,
                    n_indicators=n_indicators,
                    n_conditions=n_conditions,
                    tree_depth="",
                    n_population=n_pop,
                    n_generation=n_gen,
                    repeats=repeats,
                    warmup=warmup,
                    time_mean_s=mean,
                    time_std_s=std,
                    time_min_s=mn,
                    peak_mem_bytes=mem,
                    cache_mode="",
                    cache_hits=res.get("cache_hits", ""),
                    cache_misses=res.get("cache_misses", ""),
                    cache_unique=res.get("cache_total", ""),
                    best_fitness=res["best_fitness"],
                    result_equal_before=equal,
                )
            )
        print(f"[macro] pop={n_pop} gen={n_gen} equal={equal}")


# ----------------------------------------------------------------------------- 출력
CSV_FIELDS = [
    "benchmark_kind", "target", "variant", "n_indicators", "n_conditions",
    "tree_depth", "n_population", "n_generation", "repeats", "warmup",
    "time_mean_s", "time_std_s", "time_min_s", "peak_mem_bytes", "cache_mode",
    "cache_hits", "cache_misses", "cache_unique", "best_fitness",
    "result_equal_before",
]


def write_csv(rows, path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


def make_plots(rows, outdir):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    # 1) parse: n_conditions 별 시간 (before vs after)
    parse_rows = [r for r in rows if r["target"] == "parse_gp_tree_to_json"]
    if parse_rows:
        conds = sorted({r["n_conditions"] for r in parse_rows})
        fig, ax = plt.subplots(figsize=(8, 5))
        for variant in ("before", "after"):
            ys = [
                next(
                    r["time_mean_s"]
                    for r in parse_rows
                    if r["variant"] == variant and r["n_conditions"] == c
                )
                for c in conds
            ]
            es = [
                next(
                    r["time_std_s"]
                    for r in parse_rows
                    if r["variant"] == variant and r["n_conditions"] == c
                )
                for c in conds
            ]
            ax.errorbar(conds, ys, yerr=es, marker="o", capsize=4, label=variant)
        ax.set_xlabel("n_conditions (buy/sell pool size)")
        ax.set_ylabel("parse time per batch (s)")
        ax.set_title("parse_gp_tree_to_json: before vs after")
        ax.legend()
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        fig.savefig(os.path.join(outdir, "micro_parse.png"), dpi=150)
        plt.close(fig)

    # 2) macro: 개체수별 진화 시간
    macro_rows = [r for r in rows if r["benchmark_kind"] == "macro"]
    if macro_rows:
        pops = sorted({r["n_population"] for r in macro_rows})
        fig, ax = plt.subplots(figsize=(8, 5))
        for variant in ("before", "after"):
            ys = [
                statistics.mean(
                    [
                        r["time_mean_s"]
                        for r in macro_rows
                        if r["variant"] == variant and r["n_population"] == p
                    ]
                )
                for p in pops
            ]
            ax.plot(pops, ys, marker="s", label=variant)
        ax.set_xlabel("n_population")
        ax.set_ylabel("evolution time (s)")
        ax.set_title("Full evolution: before vs after")
        ax.legend()
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        fig.savefig(os.path.join(outdir, "macro_evolution.png"), dpi=150)
        plt.close(fig)

    # 3) speedup 막대
    fig, ax = plt.subplots(figsize=(8, 5))
    labels, speedups = [], []
    for target in ("parse_gp_tree_to_json", "validate_and_clean_strategy",
                   "extract_base_indicator_name(50k calls)", "evolution"):
        b = [r["time_mean_s"] for r in rows if r["target"] == target and r["variant"] == "before"]
        a = [r["time_mean_s"] for r in rows if r["target"] == target and r["variant"] == "after"]
        if b and a:
            labels.append(target.split("(")[0][:18])
            speedups.append(statistics.mean(b) / statistics.mean(a))
    if labels:
        ax.bar(labels, speedups, color="#3498db")
        ax.axhline(1.0, color="gray", linestyle="--")
        ax.set_ylabel("speedup (before / after)")
        ax.set_title("Average speedup (x)")
        ax.tick_params(axis="x", rotation=20)
        for i, v in enumerate(speedups):
            ax.text(i, v, f"{v:.2f}x", ha="center", va="bottom")
        fig.tight_layout()
        fig.savefig(os.path.join(outdir, "speedup.png"), dpi=150)
        plt.close(fig)


# ----------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true", help="작은 그리드로 빠르게")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--repeats", type=int, default=7)
    ap.add_argument("--warmup", type=int, default=2)
    args = ap.parse_args()

    ensure_creator()
    os.makedirs(RESULTS_DIR, exist_ok=True)

    if args.quick:
        micro_sizes = [(50, 100), (200, 400)]
        macro_grid = [(50, 8), (100, 12)]
        macro_repeats = 3
        n_individuals = 30
    else:
        micro_sizes = [(50, 100), (200, 400), (500, 1000)]
        macro_grid = [(50, 10), (100, 20), (200, 20), (300, 30)]
        macro_repeats = 5
        n_individuals = 50

    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    rows = []

    print("=== 마이크로벤치: parse ===")
    micro_parse(rows, micro_sizes, n_individuals, args.repeats, args.warmup, args.seed)
    print("=== 마이크로벤치: validate ===")
    micro_validate(rows, micro_sizes, n_individuals, args.repeats, args.warmup, args.seed)
    print("=== 마이크로벤치: helpers ===")
    micro_helpers(rows, args.repeats, args.warmup, args.seed)
    print("=== 매크로벤치: evolution ===")
    macro_evolution(rows, macro_grid, macro_repeats, 1, args.seed, 100, 200)

    csv_path = os.path.join(RESULTS_DIR, "benchmark_results.csv")
    write_csv(rows, csv_path)
    env = capture_env(args.seed, args.repeats, args.warmup, timestamp)
    with open(os.path.join(RESULTS_DIR, "env.json"), "w", encoding="utf-8") as f:
        json.dump(env, f, indent=2, ensure_ascii=False)
    make_plots(rows, RESULTS_DIR)

    print(f"\n✓ 결과 저장: {csv_path}")
    print(f"✓ 환경 정보: {os.path.join(RESULTS_DIR, 'env.json')}")
    print(f"✓ 플롯: {RESULTS_DIR}/*.png")


if __name__ == "__main__":
    main()
