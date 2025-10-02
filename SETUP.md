# BT4 Trader 통합 설정 가이드

## 빠른 시작

### 1. 환경 변수 설정

bt4_trader 프로젝트의 경로를 환경 변수로 설정합니다:

```bash
# 방법 1: export 명령 사용
export BT4_TRADER_PATH=/home/tako/Documents/yonghan/bt4_trader

# 방법 2: .bashrc 또는 .zshrc에 추가
echo 'export BT4_TRADER_PATH=/home/tako/Documents/yonghan/bt4_trader' >> ~/.bashrc
source ~/.bashrc
```

### 2. 테스트 실행

통합이 정상적으로 작동하는지 테스트:

```bash
# 기본 테스트
python tests/test_bt4_adapter.py

# 다른 설정으로 테스트
python tests/test_bt4_adapter.py test_config_short_term.json
```

### 3. GP 실행

BT4 평가를 사용하여 GP 실행:

```bash
python src/main.py
```

## 프로젝트 구조

```
GenTradingRuleWithGP/
├── src/
│   ├── adapters/                    # 🆕 BT4 어댑터
│   │   ├── __init__.py
│   │   └── bt4_adapter.py          # BT4 통합 어댑터
│   ├── configs/
│   │   ├── bt4_config.py           # 🆕 BT4 설정 로더
│   │   └── ...
│   ├── gp/
│   │   ├── evaluator.py            # 🔄 BT4 어댑터 사용
│   │   └── ...
│   └── ...
├── configs/                         # 🆕 설정 파일 디렉토리
│   └── bt4/
│       ├── base_config.json        # 기본 설정
│       ├── test_config_short_term.json
│       ├── test_config_multi_market.json
│       ├── test_config_conservative.json
│       └── README.md
├── tests/                           # 🆕 테스트 디렉토리
│   ├── __init__.py
│   ├── test_bt4_adapter.py         # 통합 테스트
│   └── README.md
├── docs/                            # 🆕 문서 디렉토리
│   └── INTEGRATION_GUIDE.md        # 상세 가이드
└── SETUP.md                         # 이 파일
```

## 주요 변경사항

### 1. 새로 추가된 파일

#### 어댑터 레이어
- `src/adapters/bt4_adapter.py`: GP와 BT4 간 브릿지
- `src/configs/bt4_config.py`: 설정 파일 로더

#### 설정 파일
- `configs/bt4/base_config.json`: 기본 백테스트 설정
- `configs/bt4/test_config_*.json`: 다양한 테스트 시나리오

#### 테스트
- `tests/test_bt4_adapter.py`: 통합 테스트 스크립트

#### 문서
- `docs/INTEGRATION_GUIDE.md`: 상세한 통합 가이드
- `configs/bt4/README.md`: 설정 파일 가이드
- `tests/README.md`: 테스트 가이드

### 2. 수정된 파일

#### src/gp/evaluator.py
- `evaluate_with_trader()` 함수 구현
- BT4BacktestAdapter를 싱글톤 패턴으로 사용
- 실제 백테스트 평가 수행

## 사용 시나리오

### 시나리오 1: 빠른 개발 테스트

짧은 기간, 적은 마켓으로 빠르게 테스트:

```bash
python tests/test_bt4_adapter.py test_config_short_term.json
```

### 시나리오 2: 다중 마켓 전략

여러 마켓에서 작동하는 강건한 전략 찾기:

```bash
# configs/bt4/test_config_multi_market.json 사용
python src/main.py
```

### 시나리오 3: 보수적 전략

낮은 리스크, 안정적인 수익 추구:

```bash
# configs/bt4/test_config_conservative.json 사용
python src/main.py
```

### 시나리오 4: 커스텀 설정

자신만의 설정 파일 생성:

```bash
# 1. 새 설정 파일 생성
cp configs/bt4/base_config.json configs/bt4/my_config.json

# 2. 설정 수정
nano configs/bt4/my_config.json

# 3. 테스트
python tests/test_bt4_adapter.py my_config.json
```

## 커스터마이징

### 적합도 함수 변경

`src/adapters/bt4_adapter.py`의 `_calculate_fitness()` 메서드를 수정:

```python
def _calculate_fitness(self, ctx, result_df) -> float:
    """커스텀 적합도 함수"""
    # 총 수익률
    total_return = ...
    
    # 샤프 비율
    sharpe_ratio = ...
    
    # 최대 낙폭 (MDD)
    mdd = ...
    
    # 승률
    win_rate = ...
    
    # 복합 점수
    fitness = (
        total_return * 0.4 +
        sharpe_ratio * 10 * 0.3 +
        (100 - mdd) * 0.2 +
        win_rate * 0.1
    )
    
    return fitness
```

### 새 설정 파일 추가

1. `configs/bt4/` 디렉토리에 JSON 파일 생성
2. 필요한 파라미터 설정
3. 코드에서 `load_bt4_config('your_config.json')` 호출

## 문제 해결

### BT4_TRADER_PATH 오류

```bash
# 경로 확인
echo $BT4_TRADER_PATH

# 디렉토리 존재 확인
ls $BT4_TRADER_PATH

# 올바른 경로로 다시 설정
export BT4_TRADER_PATH=/correct/path/to/bt4_trader
```

### Import 오류

```bash
# bt4_trader 의존성 설치
cd $BT4_TRADER_PATH
pip install -r requirements.txt

# GP 프로젝트 의존성 재설치
cd /home/tako/Documents/yonghan/GenTradingRuleWithGP
pip install -e .
```

### 백테스트 느림

1. 짧은 기간 설정 사용 (`test_config_short_term.json`)
2. 적은 마켓 수로 테스트
3. GP 파라미터 조정 (개체 수, 세대 수 감소)

## 다음 단계

1. ✅ 환경 설정 완료
2. ✅ 테스트 실행
3. 📝 설정 파일 커스터마이징
4. 📝 적합도 함수 최적화
5. 📝 GP 파라미터 튜닝
6. 📝 실전 전략 생성

## 참고 문서

- [통합 가이드](docs/INTEGRATION_GUIDE.md): 상세한 통합 방법
- [설정 파일 가이드](configs/bt4/README.md): 설정 파일 작성법
- [테스트 가이드](tests/README.md): 테스트 방법
- [어댑터 소스](src/adapters/bt4_adapter.py): 구현 세부사항

## 연락처

문제가 발생하면 다음을 확인하세요:
1. 환경 변수가 올바르게 설정되었는지
2. bt4_trader가 독립적으로 작동하는지
3. 로그 파일에서 구체적인 오류 메시지 확인

