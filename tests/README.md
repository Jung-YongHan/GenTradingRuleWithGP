# 테스트 가이드

이 디렉토리는 GP 프로젝트와 bt4_trader 통합을 테스트하기 위한 스크립트들을 포함합니다.

## 테스트 스크립트

### test_bt4_adapter.py

BT4 어댑터의 기능을 테스트하는 스크립트입니다.

#### 기본 사용법

```bash
# 기본 설정으로 테스트
python tests/test_bt4_adapter.py

# 특정 설정 파일로 테스트
python tests/test_bt4_adapter.py test_config_short_term.json

# 다른 설정 파일로 테스트
python tests/test_bt4_adapter.py test_config_multi_market.json
```

#### 환경 변수 설정

bt4_trader 프로젝트의 경로를 환경 변수로 지정할 수 있습니다:

```bash
# 일회성 실행
BT4_TRADER_PATH=/path/to/bt4_trader python tests/test_bt4_adapter.py

# 환경 변수 설정 후 실행
export BT4_TRADER_PATH=/home/tako/Documents/yonghan/bt4_trader
python tests/test_bt4_adapter.py
```

#### 테스트 항목

1. **설정 파일 로딩 테스트**
   - 사용 가능한 모든 설정 파일 목록 확인
   - 각 설정 파일 로드 테스트

2. **BT4 어댑터 테스트**
   - 설정 파일 로드
   - 어댑터 생성
   - 샘플 전략 생성
   - 백테스트 실행 및 적합도 평가

#### 예상 출력

```
============================================================
BT4 어댑터 통합 테스트
============================================================
프로젝트 루트: /home/tako/Documents/yonghan/GenTradingRuleWithGP
BT4_TRADER_PATH: /home/tako/Documents/yonghan/bt4_trader

============================================================
1. 설정 파일 로딩 테스트
============================================================

사용 가능한 설정 파일: 4개
  - base_config.json
  - test_config_conservative.json
  - test_config_multi_market.json
  - test_config_short_term.json

설정 파일 로드 테스트:
  ✓ base_config.json: GP 백테스트를 위한 기본 설정
  ✓ test_config_conservative.json: 보수적인 전략 테스트용 설정
  ✓ test_config_multi_market.json: 다중 마켓 테스트용 설정
  ✓ test_config_short_term.json: 단기 트레이딩 테스트용 설정

============================================================
2. BT4 어댑터 테스트 - base_config.json
============================================================

[1/4] 설정 파일 로드: base_config.json
  ✓ 설정 로드 완료
  - 거래소: upbit
  - 기간: 2024-01-01 00:00:00 ~ 2024-12-31 23:59:59
  - 마켓: KRW-BTC, KRW-ETH
  - 초기자본: 10,000,000원

[2/4] BT4 어댑터 생성
  ✓ 어댑터 생성 완료

[3/4] 샘플 GP 전략 생성
  ✓ 샘플 전략 생성 완료
  - 지표 수: 3
  - 매수 조건: system1 and system2
  - 매도 조건: system1 or system2

[4/4] 전략 평가 실행
  (백테스트 실행 중... 시간이 걸릴 수 있습니다)
  ✓ 평가 완료
  - 적합도 점수: 15.32
  ✓ 성공: 양의 수익률 (15.32%)

============================================================
테스트 완료!
============================================================
```

## 커스텀 테스트 작성

새로운 테스트를 추가하려면:

1. 이 디렉토리에 새 Python 파일 생성 (예: `test_my_feature.py`)
2. `test_bt4_adapter.py`를 참고하여 테스트 코드 작성
3. 실행: `python tests/test_my_feature.py`

### 예제: 간단한 테스트

```python
# tests/test_simple.py

import sys
from pathlib import Path

# 프로젝트 루트 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.adapters.bt4_adapter import BT4BacktestAdapter
from src.configs.bt4_config import load_bt4_config

# 설정 로드
config = load_bt4_config('base_config.json')

# 어댑터 생성
adapter = BT4BacktestAdapter(config)

# 전략 정의
strategy = {
    "vars": {...},
    "buy_systems": {...},
    "buy_system_op": "...",
    "sell_systems": {...},
    "sell_system_op": "..."
}

# 평가
fitness = adapter.evaluate_strategy(strategy)
print(f"Fitness: {fitness}")
```

## 문제 해결

### ImportError: bt4_trader를 찾을 수 없습니다

**해결 방법:**
- `BT4_TRADER_PATH` 환경 변수가 올바르게 설정되어 있는지 확인
- bt4_trader 프로젝트가 지정된 경로에 존재하는지 확인

```bash
export BT4_TRADER_PATH=/path/to/bt4_trader
```

### FileNotFoundError: 설정 파일을 찾을 수 없습니다

**해결 방법:**
- `configs/bt4/` 디렉토리에 설정 파일이 있는지 확인
- 파일 이름이 올바른지 확인 (대소문자 구분)

### 백테스트 실행 오류

**해결 방법:**
- bt4_trader의 데이터베이스 설정이 올바른지 확인
- 백테스트 기간에 해당하는 데이터가 존재하는지 확인
- bt4_trader의 로그를 확인하여 구체적인 오류 파악

## 추가 자료

- [BT4 설정 파일 가이드](../configs/bt4/README.md)
- [어댑터 구현 상세](../src/adapters/bt4_adapter.py)

