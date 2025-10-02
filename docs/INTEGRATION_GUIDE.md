# BT4 Trader 통합 가이드

이 문서는 GenTradingRuleWithGP 프로젝트에 bt4_trader를 통합하는 방법을 설명합니다.

## 목차

1. [개요](#개요)
2. [통합 방식](#통합-방식)
3. [설치 및 설정](#설치-및-설정)
4. [사용 방법](#사용-방법)
5. [설정 파일 관리](#설정-파일-관리)
6. [테스트](#테스트)
7. [문제 해결](#문제-해결)

## 개요

### 통합 아키텍처

```
GP 프로젝트 (메인)
├── GP 엔진 (전략 생성)
│   └── 유전 알고리즘으로 트레이딩 전략 생성
│
├── 어댑터 레이어
│   └── BT4BacktestAdapter (브릿지 역할)
│
└── BT4 Trader (평가 도구)
    └── 생성된 전략을 백테스트하여 적합도 평가
```

### 주요 구성 요소

1. **BT4BacktestAdapter** (`src/adapters/bt4_adapter.py`)
   - GP 전략 JSON을 bt4_trader 형식으로 변환
   - 백테스트 실행 및 결과 수집
   - 적합도 점수 계산

2. **설정 관리자** (`src/configs/bt4_config.py`)
   - JSON 기반 설정 파일 로드
   - 다양한 백테스트 시나리오 지원

3. **Evaluator** (`src/gp/evaluator.py`)
   - GP 개체 평가 시 BT4 어댑터 호출
   - 캐시를 통한 중복 평가 방지

## 통합 방식

### 방식 1: 상대 경로 (개발 환경 권장)

디렉토리 구조:
```
/home/tako/Documents/yonghan/
├── GenTradingRuleWithGP/    # GP 프로젝트
└── bt4_trader/               # BT4 프로젝트
```

설정:
```bash
export BT4_TRADER_PATH=/home/tako/Documents/yonghan/bt4_trader
```

### 방식 2: Git 서브모듈 (배포 환경 권장)

```bash
cd GenTradingRuleWithGP
git submodule add <bt4_trader_repo_url> external/bt4_trader
git submodule update --init --recursive
export BT4_TRADER_PATH=$(pwd)/external/bt4_trader
```

### 방식 3: 심볼릭 링크

```bash
cd GenTradingRuleWithGP
ln -s /path/to/bt4_trader external/bt4_trader
export BT4_TRADER_PATH=$(pwd)/external/bt4_trader
```

## 설치 및 설정

### 1. 환경 변수 설정

`.env` 파일 생성:
```bash
cp .env.example .env
```

`.env` 파일 수정:
```bash
# 자신의 bt4_trader 경로로 수정
BT4_TRADER_PATH=/home/tako/Documents/yonghan/bt4_trader
```

### 2. 환경 변수 로드

실행 전에 환경 변수를 로드해야 합니다:

```bash
# 방법 1: source 명령 사용
source .env

# 방법 2: export 직접 실행
export BT4_TRADER_PATH=/path/to/bt4_trader

# 방법 3: 실행 시 직접 지정
BT4_TRADER_PATH=/path/to/bt4_trader python src/main.py
```

### 3. 의존성 확인

bt4_trader의 의존성이 설치되어 있는지 확인:
```bash
cd $BT4_TRADER_PATH
pip install -r requirements.txt
```

## 사용 방법

### 기본 사용 (main.py)

GP 프로그램을 실행하면 자동으로 bt4_trader가 사용됩니다:

```bash
python src/main.py
```

내부적으로 다음 과정이 진행됩니다:
1. GP가 전략 생성
2. `evaluator.py`의 `eval_func` 호출
3. `evaluate_with_trader` 함수가 BT4 어댑터 사용
4. 백테스트 실행 후 적합도 반환

### 직접 사용 (프로그래밍)

```python
from src.adapters.bt4_adapter import BT4BacktestAdapter
from src.configs.bt4_config import load_bt4_config

# 1. 설정 로드
config = load_bt4_config('base_config.json')

# 2. 어댑터 생성
adapter = BT4BacktestAdapter(config)

# 3. GP 전략 정의
strategy = {
    "vars": {
        "SMA1": {
            "func": "SMA",
            "params": [20],
            "cdl_type": "period",
            "sources": ["close"],
            "unary": False
        }
    },
    "buy_systems": {
        "system1": {
            "alias": "system1",
            "left": "SMA1",
            "op": ">",
            "right": "close"
        }
    },
    "buy_system_op": "system1",
    "sell_systems": {
        "system1": {
            "alias": "system1",
            "left": "SMA1",
            "op": "<",
            "right": "close"
        }
    },
    "sell_system_op": "system1"
}

# 4. 평가
fitness = adapter.evaluate_strategy(strategy)
print(f"적합도: {fitness}")
```

## 설정 파일 관리

### 설정 파일 위치

모든 백테스트 설정 파일은 `configs/bt4/` 디렉토리에 저장됩니다.

### 기본 제공 설정 파일

1. **base_config.json**: 기본 설정 (1년, 2개 마켓)
2. **test_config_short_term.json**: 단기 테스트 (3개월, 1시간봉)
3. **test_config_multi_market.json**: 다중 마켓 (6개 마켓)
4. **test_config_conservative.json**: 보수적 전략 (5% 포지션)

### 새 설정 파일 추가

1. `configs/bt4/` 디렉토리에 새 JSON 파일 생성
2. 다음 형식으로 작성:

```json
{
  "description": "나만의 설정",
  "ex_type": "upbit",
  "bt_start": "2024-01-01 00:00:00",
  "bt_end": "2024-12-31 23:59:59",
  "markets": ["KRW-BTC"],
  "initial_balance": 10000000,
  "fee_rate": 0.0005,
  "position_size": 0.1,
  "candle_interval": "1d",
  "max_positions": 5,
  "stgy_name": "MyStrategy"
}
```

3. 코드에서 사용:

```python
config = load_bt4_config('my_config.json')
```

### 설정 파일 목록 확인

```python
from src.configs.bt4_config import list_available_configs

configs = list_available_configs()
print(configs)
# ['base_config.json', 'test_config_short_term.json', ...]
```

## 테스트

### 통합 테스트 실행

```bash
# 기본 설정으로 테스트
python tests/test_bt4_adapter.py

# 특정 설정으로 테스트
python tests/test_bt4_adapter.py test_config_short_term.json
```

### 테스트 출력 예시

```
============================================================
BT4 어댑터 통합 테스트
============================================================

[1/4] 설정 파일 로드: base_config.json
  ✓ 설정 로드 완료
  - 거래소: upbit
  - 기간: 2024-01-01 ~ 2024-12-31
  - 마켓: KRW-BTC, KRW-ETH

[2/4] BT4 어댑터 생성
  ✓ 어댑터 생성 완료

[3/4] 샘플 GP 전략 생성
  ✓ 샘플 전략 생성 완료

[4/4] 전략 평가 실행
  ✓ 평가 완료
  - 적합도 점수: 15.32%
```

## 문제 해결

### 1. ImportError: bt4_trader를 찾을 수 없습니다

**원인**: `BT4_TRADER_PATH` 환경 변수가 설정되지 않았거나 잘못된 경로

**해결**:
```bash
# 경로 확인
ls $BT4_TRADER_PATH

# 없다면 올바른 경로로 설정
export BT4_TRADER_PATH=/correct/path/to/bt4_trader
```

### 2. 백테스트 실행 오류

**원인**: bt4_trader 데이터베이스 또는 설정 문제

**해결**:
1. bt4_trader가 정상 작동하는지 독립적으로 테스트
2. 데이터베이스에 해당 기간의 데이터가 있는지 확인
3. bt4_trader 로그 확인

### 3. 느린 평가 속도

**원인**: 매 평가마다 백테스트 실행

**해결**:
1. 캐시 활용 (evaluator.py에 이미 구현됨)
2. 짧은 백테스트 기간 사용 (개발 시)
3. 병렬 처리 (main.py의 multiprocessing 활용)

### 4. 메모리 부족

**원인**: 많은 전략을 동시 평가

**해결**:
1. GP 파라미터 조정 (N_POPULATION, N_GENERATION 감소)
2. 캐시 주기적으로 정리
3. 더 작은 마켓/기간으로 테스트

## 고급 활용

### 커스텀 적합도 함수

`bt4_adapter.py`의 `_calculate_fitness` 메서드를 수정하여 다양한 지표 활용:

```python
def _calculate_fitness(self, ctx, result_df) -> float:
    """커스텀 적합도 계산"""
    if result_df is None or len(result_df) == 0:
        return -1000.0
    
    # 총 수익률
    total_return = ...
    
    # 샤프 비율 계산
    sharpe_ratio = ...
    
    # MDD 계산
    mdd = ...
    
    # 복합 적합도
    fitness = total_return * 0.5 + sharpe_ratio * 0.3 - mdd * 0.2
    
    return fitness
```

### 다중 설정 동시 평가

여러 설정으로 동시에 평가하여 강건한 전략 찾기:

```python
from src.configs.bt4_config import list_available_configs, load_bt4_config
from src.adapters.bt4_adapter import BT4BacktestAdapter

# 모든 설정으로 평가
total_fitness = 0
for config_name in list_available_configs():
    config = load_bt4_config(config_name)
    adapter = BT4BacktestAdapter(config)
    fitness = adapter.evaluate_strategy(strategy)
    total_fitness += fitness

# 평균 적합도
avg_fitness = total_fitness / len(list_available_configs())
```

## 참고 자료

- [BT4 설정 파일 상세](../configs/bt4/README.md)
- [테스트 가이드](../tests/README.md)
- [어댑터 소스 코드](../src/adapters/bt4_adapter.py)

