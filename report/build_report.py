#!/usr/bin/env python
"""results/ 의 실측 데이터를 읽어 report.html 을 생성한다.

이후 headless Chrome 으로 report.html → report.pdf 로 변환한다(build_pdf.sh 참고).
한글은 시스템 폰트(Apple SD Gothic Neo)로 렌더링된다.
"""
from __future__ import annotations

import base64
import csv
import json
import os
import statistics

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(ROOT, "results")
HERE = os.path.dirname(os.path.abspath(__file__))

# --- 메타 (표지) ------------------------------------------------------------
STUDENT_ID = os.environ.get("STUDENT_ID", "[학번을 입력하세요]")
STUDENT_NAME = os.environ.get("STUDENT_NAME", "정용한")


def load_rows():
    with open(os.path.join(RESULTS, "benchmark_results.csv")) as f:
        return list(csv.DictReader(f))


def load_env():
    with open(os.path.join(RESULTS, "env.json")) as f:
        return json.load(f)


def img_b64(name):
    path = os.path.join(RESULTS, name)
    if not os.path.exists(path):
        return ""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def fnum(r, k):
    return float(r[k])


def pair(rows, target, variant, n_cond=None, n_pop=None):
    for r in rows:
        if r["target"].startswith(target) and r["variant"] == variant:
            if n_cond is not None and r["n_conditions"] != str(n_cond):
                continue
            if n_pop is not None and r["n_population"] != str(n_pop):
                continue
            return r
    return None


def avg_speedup(rows, target):
    b = [fnum(r, "time_mean_s") for r in rows if r["target"].startswith(target) and r["variant"] == "before"]
    a = [fnum(r, "time_mean_s") for r in rows if r["target"].startswith(target) and r["variant"] == "after"]
    return statistics.mean(b) / statistics.mean(a) if a else 0.0


def micro_table(rows, target, label):
    conds = sorted({int(r["n_conditions"]) for r in rows if r["target"].startswith(target) and r["n_conditions"]})
    out = []
    for c in conds:
        b = pair(rows, target, "before", n_cond=c)
        a = pair(rows, target, "after", n_cond=c)
        if not (b and a):
            continue
        bm, am = fnum(b, "time_mean_s") * 1000, fnum(a, "time_mean_s") * 1000
        bs, as_ = fnum(b, "time_std_s") * 1000, fnum(a, "time_std_s") * 1000
        bmem, amem = int(b["peak_mem_bytes"]) // 1024, int(a["peak_mem_bytes"]) // 1024
        out.append(
            f"<tr><td>{c}</td>"
            f"<td>{bm:.3f} ± {bs:.3f}</td><td>{am:.3f} ± {as_:.3f}</td>"
            f"<td class='hl'>{bm/am:.2f}×</td>"
            f"<td>{bmem} / {amem}</td>"
            f"<td>{b['result_equal_before']}</td></tr>"
        )
    return "\n".join(out)


def macro_table(rows):
    cells = sorted(
        {(int(r["n_population"]), int(r["n_generation"])) for r in rows if r["benchmark_kind"] == "macro"}
    )
    out = []
    for (p, g) in cells:
        b = pair(rows, "evolution", "before", n_pop=p)
        a = pair(rows, "evolution", "after", n_pop=p)
        # n_pop 중복 가능 → generation 으로 추가 구분
        b = next((r for r in rows if r["target"] == "evolution" and r["variant"] == "before" and r["n_population"] == str(p) and r["n_generation"] == str(g)), None)
        a = next((r for r in rows if r["target"] == "evolution" and r["variant"] == "after" and r["n_population"] == str(p) and r["n_generation"] == str(g)), None)
        if not (b and a):
            continue
        bm, am = fnum(b, "time_mean_s") * 1000, fnum(a, "time_mean_s") * 1000
        bs, as_ = fnum(b, "time_std_s") * 1000, fnum(a, "time_std_s") * 1000
        bmem, amem = int(b["peak_mem_bytes"]) // 1024, int(a["peak_mem_bytes"]) // 1024
        out.append(
            f"<tr><td>{p} × {g}</td>"
            f"<td>{bm:.1f} ± {bs:.1f}</td><td>{am:.1f} ± {as_:.1f}</td>"
            f"<td class='hl'>{bm/am:.2f}×</td>"
            f"<td>{bmem} / {amem}</td>"
            f"<td>{b['cache_unique']}</td>"
            f"<td>{b['result_equal_before']}</td></tr>"
        )
    return "\n".join(out)


def helper_row(rows):
    b = pair(rows, "extract_base", "before")
    a = pair(rows, "extract_base", "after")
    bm, am = fnum(b, "time_mean_s") * 1000, fnum(a, "time_mean_s") * 1000
    return f"{bm:.2f} ms", f"{am:.2f} ms", f"{bm/am:.1f}×"


def main():
    rows = load_rows()
    env = load_env()

    sp_parse = avg_speedup(rows, "parse_gp_tree_to_json")
    sp_val = avg_speedup(rows, "validate_and_clean_strategy")
    sp_helper = avg_speedup(rows, "extract_base")
    sp_macro = avg_speedup(rows, "evolution")
    hb, ha, hsp = helper_row(rows)

    html = TEMPLATE.format(
        student_id=STUDENT_ID,
        student_name=STUDENT_NAME,
        os=env["os"],
        python=env["python"],
        cpu=f"{env['processor']} ({env['cpu_count']} cores)",
        deap=env["deap"],
        numpy=env["numpy"],
        pandas=env["pandas"],
        mp=env["mp_start_method"],
        seed=env["seed"],
        repeats=env["repeats"],
        warmup=env["warmup"],
        commit=env["git_commit"],
        timestamp=env["timestamp"],
        sp_parse=f"{sp_parse:.2f}",
        sp_val=f"{sp_val:.2f}",
        sp_helper=f"{sp_helper:.1f}",
        sp_macro=f"{sp_macro:.2f}",
        micro_parse_tbl=micro_table(rows, "parse_gp_tree_to_json", "parse"),
        micro_val_tbl=micro_table(rows, "validate_and_clean_strategy", "validate"),
        macro_tbl=macro_table(rows),
        helper_before=hb,
        helper_after=ha,
        helper_sp=hsp,
        img_parse=img_b64("micro_parse.png"),
        img_macro=img_b64("macro_evolution.png"),
        img_speedup=img_b64("speedup.png"),
    )
    out = os.path.join(HERE, "report.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print("wrote", out)


TEMPLATE = r"""<!DOCTYPE html>
<html lang="ko"><head><meta charset="utf-8">
<style>
@page {{ size: A4; margin: 18mm 16mm; }}
* {{ box-sizing: border-box; }}
body {{ font-family: "Apple SD Gothic Neo","AppleGothic","Noto Sans KR",sans-serif;
  font-size: 10.5pt; line-height: 1.6; color: #1a1a1a; }}
h1 {{ font-size: 17pt; border-bottom: 3px solid #2c3e50; padding-bottom:6px; margin-top: 26px; }}
h2 {{ font-size: 13pt; color: #2c3e50; margin-top: 20px; border-left: 4px solid #3498db; padding-left: 8px; }}
h3 {{ font-size: 11.5pt; color: #34495e; margin-top: 14px; }}
code, pre {{ font-family: "SFMono-Regular",Menlo,Consolas,monospace; font-size: 8.8pt; }}
pre {{ background: #f6f8fa; border: 1px solid #e1e4e8; border-radius: 6px; padding: 10px 12px;
  overflow-x: auto; line-height: 1.45; }}
.cmt {{ color: #6a737d; }}
.kw {{ color: #d73a49; }}
table {{ border-collapse: collapse; width: 100%; margin: 10px 0; font-size: 9.3pt; }}
th, td {{ border: 1px solid #d0d7de; padding: 5px 8px; text-align: center; }}
th {{ background: #2c3e50; color: #fff; }}
tr:nth-child(even) td {{ background: #f6f8fa; }}
td.hl {{ font-weight: 700; color: #1a7f37; }}
.lead {{ background:#eef6fb; border:1px solid #cfe6f5; border-radius:8px; padding:10px 14px; }}
.cover {{ text-align:center; padding-top: 150px; }}
.cover .t {{ font-size: 24pt; font-weight: 800; color:#2c3e50; }}
.cover .s {{ font-size: 13pt; color:#555; margin-top: 10px; }}
.cover .m {{ margin-top: 80px; font-size: 12pt; line-height: 2.0; }}
.pb {{ page-break-before: always; }}
img {{ max-width: 100%; border:1px solid #e1e4e8; border-radius:6px; margin: 8px 0; }}
.kpi {{ display:flex; gap:10px; margin: 12px 0; }}
.kpi div {{ flex:1; background:#f0f9f4; border:1px solid #b7e0c4; border-radius:8px; padding:10px; text-align:center; }}
.kpi .v {{ font-size: 18pt; font-weight:800; color:#1a7f37; }}
.kpi .l {{ font-size: 8.5pt; color:#555; }}
ul, ol {{ margin: 6px 0 6px 0; padding-left: 22px; }}
li {{ margin: 3px 0; }}
small {{ color:#6a737d; }}
</style></head><body>

<div class="cover">
  <div class="t">유전 프로그래밍 거래규칙 생성기<br>코드 성능·구조 개선</div>
  <div class="s">— Python 자료구조·제너레이터·클래스 설계·데코레이터·벤치마크 적용 —</div>
  <div class="m">
    <b>과목</b> : 파이썬 프로그래밍<br>
    <b>대상 코드</b> : GenTradingRuleWithGP (DEAP 기반 GP 거래전략 생성)<br>
    <b>학번</b> : {student_id}<br>
    <b>이름</b> : {student_name}<br>
    <b>제출일</b> : 2026-06-21
  </div>
</div>

<div class="pb"></div>
<h1>1. 연구 코드 소개</h1>
<div class="lead">본 과제는 본인 연구에서 사용하는 <b>GenTradingRuleWithGP</b> 코드를 대상으로 한다.
DEAP 유전 프로그래밍(GP)으로 기술적 지표 기반 매수/매도 규칙 트리를 진화시켜, 수익을 내는
거래 전략을 자동 탐색하는 파이프라인이다.</div>

<h2>1.1 연구 맥락과 파이프라인 위치</h2>
<ul>
<li><b>입력</b>: 지표/조건 풀 크기, GP 하이퍼파라미터(개체수·세대·교차·변이율·트리 깊이), 백테스트 설정.</li>
<li><b>처리</b>: ① 지표·조건 풀 생성(<code>ConditionManager</code>) → ② 강타입 GP 트리 진화
(선택·교차·변이) → ③ 각 개체(트리)를 전략 JSON으로 <b>파싱</b> → ④ <b>검증/정리</b> →
⑤ 백테스트로 적합도 평가 → ⑥ 캐시.</li>
<li><b>출력</b>: 최적 전략 JSON, 진화 곡선/적합도 분포 시각화, 로그.</li>
<li><b>파이프라인 위치</b>: 전략 <i>탐색(search)</i> 단계. 평가 1회는 외부 백테스트 엔진
(BullTrader, bt4) 호출이며, 개체수×세대만큼 수만~수십만 번 반복된다.</li>
</ul>

<h2>1.2 개선 대상으로 선택한 이유</h2>
<ul>
<li>진화 루프가 <b>핫 루프</b>다. 개체마다 파싱·검증·해시·캐시가 반복되어, 평가 외
오케스트레이션 코드의 비용이 전체 실행시간에 직접 누적된다.</li>
<li>실제 적합도 평가(bt4)는 외부 독점 엔진과 시장 데이터에 의존해 <b>재현이 불가능</b>하다.
과제 지침(synthetic 허용)에 따라, 평가 leaf 를 <b>결정적 합성 평가기</b>로 대체하여 GP
루프 전체를 재현 가능하게 만들고, 최적화 대상은 그 주위의 <b>파이썬 코드 구조</b>로 한정했다
(데이터·모델 축소가 아닌 코드 구조 개선).</li>
</ul>

<h1 class="pb">2. 기존 코드의 문제점 분석</h1>
<table>
<tr><th>분류</th><th>위치</th><th>문제</th></tr>
<tr><td>중복 연산</td><td>strategy/parser.py</td><td><code>str(individual)</code>(트리 직렬화, O(N))를 buy/sell용으로 <b>개체당 2회</b> 호출</td></tr>
<tr><td>정규식 재컴파일</td><td>parser/formatter/helpers</td><td>변환·추출 정규식(~13개)을 <b>호출마다</b> 인라인 <code>re.sub</code>/<code>re.match</code></td></tr>
<tr><td>코드 중복</td><td>parser.py</td><td>buy/sell 추출 함수가 슬라이스 한 줄만 다르고 동일(괄호 스캔 복붙)</td></tr>
<tr><td>자료구조</td><td>indicator_configs.py</td><td><code>OHLCV_SOURCES</code>가 <b>list</b> → membership test O(n)이 피연산자마다 반복</td></tr>
<tr><td>SRP 위반</td><td>main.py</td><td><code>main()</code> 한 함수(~130줄)에 설정·상태·루프·통계·로깅·시각화·저장 혼재</td></tr>
<tr><td>반복 순회</td><td>main.py</td><td>세대 통계에서 <code>fits</code> 리스트를 4회 순회(2-pass 표준편차)</td></tr>
<tr><td>전역 상태</td><td>gp/evaluator.py</td><td><code>_strategy_cache</code>/<code>_bt4_config</code>/<code>_bt4_adapter</code>가 모듈 전역 → 테스트·실험조건 변경 곤란</td></tr>
<tr><td>재현성</td><td>requirements.txt</td><td>conda <code>@ file://</code> 경로 다수 → 타 환경 <code>pip install</code> 불가</td></tr>
</table>

<h1 class="pb">3. 적용한 수업 개념과 선택 근거</h1>
<p>지침 5.2의 A~D 네 범주를 모두 적용했다(≥3 요건 초과). 각 선택의 <b>근거</b>를 함께 기술한다.</p>

<h2>A. 자료구조 및 복잡도</h2>
<ul>
<li><b>frozenset</b>: <code>OHLCV_SOURCES</code> 멤버십을 list(O(n))→frozenset(O(1)). 지배 연산이
"피연산자가 OHLCV인가" 판정이라, 개체·조건마다 반복되는 선형탐색을 상수시간으로.
<code>random.choice</code> 가 필요한 곳은 인덱싱 가능한 순서 리스트를 유지(난수열 보존).</li>
<li><b>defaultdict(list)</b>: 지표 그룹화의 <code>if k not in d: d[k]=[]</code> 관용구 제거.</li>
<li><b>단일 패스 통계</b>: 합·제곱합·최대·최소를 한 번에 누적(2-pass→1-pass). 모집단 표준편차(÷n) 보존.</li>
</ul>

<h2>B. 이터레이터 · 제너레이터 · Lazy</h2>
<ul>
<li><b>진화 루프를 제너레이터로</b>: <code>EvolutionRunner.run()</code>이 세대별 통계를
<code>yield</code> → 호출부가 lazy 소비(실시간 로깅/조기종료). 중간 리스트 불필요.</li>
<li><b>lazy genexpr</b>: 적합도를 리스트로 materialize 하지 않고 제너레이터로 단일 패스 통계에 투입.</li>
<li><b>중복 루프 통합</b>: 파서의 buy/sell 시스템 생성 루프를 하나의 헬퍼로 통합.</li>
</ul>

<h2>C. 클래스 설계 · 단일책임원칙</h2>
<ul>
<li><b>GPConfig</b> <code>@dataclass(frozen=True, slots=True)</code>: 흩어진 전역 상수를 불변 설정
객체로. <code>frozen</code>=재현성 보장, <code>slots</code>=메모리·오타 방지, <code>replace</code>로 크기 스윕.</li>
<li><b>책임 분리</b>: <code>EvolutionRunner</code>(루프)·<code>StatsCollector</code>(통계)·
<code>EvolutionState</code>(상태)·<code>StrategyEvaluator</code>(파싱→검증→캐시→평가)·
파일/시각화 유틸로 분해. <code>main()</code>은 ~40줄 조립으로 축소.</li>
<li><b>Protocol + Factory</b>: <code>BacktestEvaluator(Protocol)</code> 인터페이스 →
<code>Synthetic</code>/<code>BT4</code> 두 구현을 <code>make_evaluator(name)</code> 로 교체. 평가 방식
변경이 <b>호출부 한 줄</b>로 가능(원래는 함수 본문 수정 필요).</li>
</ul>

<h2>D. 데코레이터</h2>
<ul>
<li><b>functools.lru_cache</b>: 순수 헬퍼 <code>extract_base_indicator_name</code> 등. 지표 이름이
반복 등장 → 적중률 높아 정규식/문자열 연산을 건너뜀.</li>
<li><b>cache_by_hash</b>(stateful·parameterized): 전략 <b>내용 해시</b> 기반 캐시. lru_cache가
인자 identity로 캐싱해 매번 새 트리 객체엔 무의미한 반면, 서로 다른 트리도 동일 전략이면 적중.</li>
<li><b>validate_individual</b>(가드)·<b>retry</b>(불안정 외부 평가)·<b>timeit/log_call</b>(계측,
플래그로 no-op 토글). 모두 <code>functools.wraps</code>로 메타데이터 보존.</li>
</ul>

<h1 class="pb">4. 개선 과정 (핵심 변경)</h1>

<h2>4.1 파서: 트리 직렬화 1회 + 중복 제거 + 정규식 사전 컴파일</h2>
<pre><span class="cmt"># BEFORE — buy/sell 각각 str(individual) 호출(2회), 정규식 인라인</span>
buy_op  = _analyze_tree_structure(individual, "buy")   <span class="cmt"># str(individual) (1)</span>
sell_op = _analyze_tree_structure(individual, "sell")  <span class="cmt"># str(individual) (2)</span>
result = re.sub(rf"{{system_type}}_system(\d+)", r"system\1", s)  <span class="cmt"># 매 호출 컴파일</span></pre>
<pre><span class="cmt"># AFTER — 1회 직렬화 후 공유, 정규식은 모듈 로드 시 컴파일</span>
_RE_SYSTEM = {{"buy": re.compile(r"buy_system(\d+)"), "sell": re.compile(r"sell_system(\d+)")}}
<span class="kw">def</span> _analyze_both(individual):
    tree_str = str(individual)            <span class="cmt"># ← 단 1회</span>
    buy_raw, sell_raw = _split_strategy_args(tree_str)   <span class="cmt"># 괄호 스캔도 1회</span>
    <span class="kw">return</span> _convert(buy_raw, "buy"), _convert(sell_raw, "sell")</pre>

<h2>4.2 거대한 main() → 제너레이터 기반 Runner (SRP)</h2>
<pre><span class="cmt"># BEFORE — main() 안에 루프·통계·로깅·시각화·저장 혼재</span>
<span class="kw">for</span> g <span class="kw">in</span> range(N_GENERATION):
    offspring = ...; <span class="cmt"># 선택/교차/변이</span>
    fits = [ind.fitness.values[0] <span class="kw">for</span> ind <span class="kw">in</span> pop]  <span class="cmt"># 리스트</span>
    max_fit=max(fits); avg=sum(fits)/len(pop); std=(sum((x-avg)**2 ...))  <span class="cmt"># 4회 순회</span>
    logging.info(...); stats_history.append({{...}})</pre>
<pre><span class="cmt"># AFTER — 루프는 통계를 yield, 호출부는 lazy 소비</span>
<span class="kw">class</span> EvolutionRunner:
    <span class="kw">def</span> run(self) -> Iterator[GenerationStats]:
        <span class="kw">for</span> g <span class="kw">in</span> range(cfg.n_generation):
            ...  <span class="cmt"># 선택/교차/변이/평가</span>
            <span class="kw">yield</span> self.stats.summarize(self.state.fitness_values(), g+1, dur)  <span class="cmt"># lazy genexpr, 1-pass</span></pre>

<h2>4.3 캐시: 전역 dict → 인스턴스 + 내용 해시 데코레이터</h2>
<pre><span class="kw">def</span> cache_by_hash(hash_fn):  <span class="cmt"># parameterized + stateful 데코레이터</span>
    <span class="kw">def</span> deco(func):
        @functools.wraps(func)
        <span class="kw">def</span> wrapper(self, payload, *a, **k):
            key = hash_fn(payload)
            <span class="kw">if</span> key <span class="kw">in</span> self._cache: self._hits += 1; <span class="kw">return</span> self._cache[key]
            self._misses += 1; r = func(self, payload, *a, **k); self._cache[key]=r; <span class="kw">return</span> r
        <span class="kw">return</span> wrapper
    <span class="kw">return</span> deco</pre>

<h2>4.4 고려했으나 적용하지 않은 대안 · trade-off</h2>
<ul>
<li><b>Welford 1-pass 표준편차</b>: 수치 안정성은 우수하나 원소당 연산↑. 현재 값 범위에선
<code>sum/sumsq</code> 단일 패스로 충분 → 후자 채택(대안 명시).</li>
<li><b>multiprocessing Pool</b>: 합성 평가기는 가벼워 IPC/pickling 오버헤드가 지배적이고
워커별 RNG·캐시 분리로 <b>비결정적</b>이 된다. 공정·재현 벤치마크를 위해 순차를 기본으로 하되,
pickling-aware <code>PoolMap</code>(Pool initializer)은 시연용으로 구현.</li>
<li><b>deepcopy 검증</b>: 메모리·시간 증가만 유발. 원본의 shallow <code>copy()</code> 의미 보존.</li>
</ul>

<h1 class="pb">5. 최적화 결과</h1>
<div class="kpi">
  <div><div class="v">{sp_parse}×</div><div class="l">parse (평균)</div></div>
  <div><div class="v">{sp_val}×</div><div class="l">validate (평균)</div></div>
  <div><div class="v">{sp_helper}×</div><div class="l">extract (lru_cache)</div></div>
  <div><div class="v">{sp_macro}×</div><div class="l">전체 진화 (평균)</div></div>
</div>

<h2>5.1 마이크로벤치: parse_gp_tree_to_json (입력 크기별)</h2>
<table>
<tr><th>n_conditions</th><th>before (ms)</th><th>after (ms)</th><th>speedup</th><th>peak KB (b/a)</th><th>출력 동일</th></tr>
{micro_parse_tbl}
</table>
<img src="data:image/png;base64,{img_parse}">

<h2>5.2 마이크로벤치: validate_and_clean_strategy</h2>
<table>
<tr><th>n_conditions</th><th>before (ms)</th><th>after (ms)</th><th>speedup</th><th>peak KB (b/a)</th><th>출력 동일</th></tr>
{micro_val_tbl}
</table>

<h2>5.3 마이크로벤치: extract_base_indicator_name (5만 회 호출)</h2>
<p>지표 이름이 반복 등장하는 분포에서 <b>lru_cache</b> 효과. before {helper_before} → after {helper_after}
(<b class="hl">{helper_sp}</b> 향상).</p>

<h2 class="pb">5.4 매크로벤치: 전체 진화 (합성 평가기, 순차)</h2>
<table>
<tr><th>개체수 × 세대</th><th>before (ms)</th><th>after (ms)</th><th>speedup</th><th>peak KB (b/a)</th><th>고유 전략</th><th>궤적 동일</th></tr>
{macro_tbl}
</table>
<img src="data:image/png;base64,{img_macro}">
<img src="data:image/png;base64,{img_speedup}">

<h2>5.5 구조·재사용성 개선</h2>
<table>
<tr><th>항목</th><th>before</th><th>after</th></tr>
<tr><td><code>main()</code> 라인수</td><td>~130줄(다중 책임)</td><td>~40줄(조립)</td></tr>
<tr><td>평가 방식 교체</td><td>함수 본문 수정</td><td>호출부 1줄(<code>make_evaluator</code>)</td></tr>
<tr><td>설정 변경</td><td>전역 상수 직접 수정</td><td><code>GPConfig</code> 필드/<code>replace</code></td></tr>
<tr><td>캐시 상태</td><td>모듈 전역</td><td>인스턴스(테스트·병렬 안전)</td></tr>
<tr><td>파서 추출 함수</td><td>2개 중복</td><td>1개 통합</td></tr>
<tr><td>정규식 컴파일</td><td>호출마다</td><td>모듈 로드 1회</td></tr>
</table>

<h1 class="pb">6. 결과 해석 및 한계</h1>
<h2>6.1 왜 이런 결과가 나왔는가</h2>
<ul>
<li><b>extract_* {helper_sp}</b>: 가장 큰 향상. 동일 인자 재호출이 매우 잦아 lru_cache 적중률이
높고, 정규식 매칭 자체를 건너뛴다. 입력 다양성이 낮을수록 효과가 크다(캐시의 본질).</li>
<li><b>parse {sp_parse}×</b>: <code>str(individual)</code> 2→1회가 핵심 기여. 트리가 클수록 직렬화
비중이 커져 효과가 두드러진다. 단, 파서 비용의 상당 부분은 buy/sell 풀 전체를 순회하는
<code>_build_systems</code>(O(n_conditions))라, str 절감만으로 2배가 되진 않는다 → 1.2배대가 타당.</li>
<li><b>전체 진화 {sp_macro}×</b>: 입력 크기와 무관하게 일정한 비율의 향상. 파싱·검증·헬퍼가
세대마다 누적되므로, 마이크로 향상이 전체로 안정적으로 전이된 결과.</li>
<li><b>메모리</b>: 큰 규모(p300×g30)에서 peak이 소폭 감소(1949→1887KB). 중간 리스트 제거
(lazy genexpr)·중복 객체 감소의 효과지만, 지배 메모리는 개체군 자체라 절감폭은 제한적.</li>
</ul>
<h2>6.2 한계와 trade-off</h2>
<ul>
<li><b>복잡도↑</b>: 클래스·Protocol·데코레이터 도입으로 파일 수가 늘었다. 소규모 1회 실행에는
과한 구조일 수 있으나, 반복 실험·확장·테스트에서 회수된다.</li>
<li><b>데코레이터 오버헤드</b>: 항상 켜진 <code>@timeit/@log_call</code>은 핫패스에 프레임을 더해
벤치마크를 오염시킬 수 있어, 플래그로 no-op 토글하도록 설계했다.</li>
<li><b>합성 평가기</b>: 실제 bt4 백테스트가 아니므로 절대 성능이 아닌 <b>코드 구조</b> 비교에
초점. 실 엔진에선 평가 leaf 가 지배적이라 오케스트레이션 향상 비중은 작아질 수 있다(동일
인터페이스로 교체 가능하게 설계).</li>
<li><b>추가 개선 여지</b>: 파서를 문자열 재파싱이 아닌 트리 순회 기반으로 재작성하면 정규식
파이프라인 자체를 제거할 수 있다(가장 큰 잠재 이득). 캐시 직렬화 비용(<code>json.dumps</code>)도
구조적 키로 대체 가능.</li>
</ul>

<h1 class="pb">부록. 측정 환경 및 재현</h1>
<table>
<tr><th>항목</th><th>값</th></tr>
<tr><td>OS</td><td>{os}</td></tr>
<tr><td>Python</td><td>{python}</td></tr>
<tr><td>CPU</td><td>{cpu}</td></tr>
<tr><td>주요 라이브러리</td><td>deap {deap}, numpy {numpy}, pandas {pandas}</td></tr>
<tr><td>multiprocessing start</td><td>{mp} (벤치마크는 순차)</td></tr>
<tr><td>random seed</td><td>{seed} (고정)</td></tr>
<tr><td>반복/워밍업</td><td>repeats={repeats}, warmup={warmup}</td></tr>
<tr><td>git commit</td><td>{commit}</td></tr>
<tr><td>측정 시각</td><td>{timestamp}</td></tr>
</table>
<p><small>재현: <code>uv venv --python 3.11 && uv pip install -r requirements.txt</code> 후
<code>python benchmark/run_benchmark.py</code>. 모든 행에서 before/after 출력·궤적 동일성(회귀
게이트)을 assert 한다. 전/후 코드는 <code>src/before</code>, <code>src/after</code> 로 분리.</small></p>

</body></html>"""


if __name__ == "__main__":
    main()
