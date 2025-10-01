# GenTradingRuleWithGP

유전 프로그래밍(Genetic Programming)을 사용하여 거래 전략 규칙을 자동 생성하는 프로젝트입니다.

## 주요 기능

### 1. 유전 프로그래밍 기반 전략 생성
- DEAP 라이브러리를 활용한 GP 알고리즘 구현
- 다양한 기술적 지표를 활용한 매수/매도 시스템 생성
- 자동 전략 최적화

### 2. 기술적 지표 지원
- RSI (Relative Strength Index)
- SMA (Simple Moving Average)
- MACD (Moving Average Convergence Divergence)
- ATR (Average True Range)
- BBANDS (Bollinger Bands)

### 3. 진화 과정 시각화 ✨
- **세대별 Fitness 진화 과정**: 최고/평균/최저 fitness 추적 그래프
- **Fitness 표준편차**: 개체군 다양성 모니터링
- **최종 개체군 분포**: 히스토그램으로 fitness 분포 시각화
- 인터랙티브 HTML 그래프 자동 생성 (Plotly 사용)

### 4. 결과 출력
- 최적화된 전략을 JSON 형식으로 저장
- GP 트리 구조 시각화 (PNG)
- 상세 실행 로그 기록

## 설치 방법

```bash
# 저장소 클론
git clone https://github.com/Jung-YongHan/GenTradingRuleWithGP.git
cd GenTradingRuleWithGP

# 의존성 설치
pip install -r requirements.txt
```

## 사용 방법

```bash
# 메인 프로그램 실행
python3 src/main.py
```

## 출력 파일

프로그램을 실행하면 `logs/YYYY-MM-DD/run_HH-MM-SS/` 디렉토리에 다음 파일들이 생성됩니다:

### 시각화 파일
- `evolution.html`: GP 진화 과정 인터랙티브 그래프 (Plotly)
  - 세대별 최고/평균/최저 fitness 추적
  - Fitness 표준편차 변화
  - 줌, 패닝 등 인터랙티브 기능 지원
- `evolution.png`: 진화 과정 정적 이미지 (PNG, 150 DPI)
- `fitness_distribution.html`: 최종 개체군의 fitness 분포 히스토그램 (Plotly)
- `fitness_distribution.png`: Fitness 분포 정적 이미지 (PNG, 150 DPI)

### 전략 파일
- `strategy.json`: 최적화된 거래 전략 (JSON 형식)
- `strategy_tree.png`: 전략 트리 구조 시각화
- `strategy.log`: 상세 실행 로그

## 설정

`src/config.py`에서 다음 파라미터를 조정할 수 있습니다:

```python
# 진화 파라미터
N_POPULATION = 100          # 개체군 크기
N_GENERATION = 20           # 세대 수
CROSSOVER_PROBABILITY = 0.8  # 교차 확률
MUTATION_PROBABILITY = 0.15  # 변이 확률

# 트리 구조 파라미터
INITIAL_MIN_DEPTH = 2       # 초기 최소 깊이
INITIAL_MAX_DEPTH = 6       # 초기 최대 깊이
MAX_MUTATION_DEPTH = 4      # 변이 최대 깊이
MAX_TREE_SIZE = 100         # 최대 트리 크기
```

## 시각화 예시

### 진화 과정 그래프
세대별로 개체군의 fitness가 어떻게 진화하는지 실시간으로 확인할 수 있습니다:
- 🟢 **최고 Fitness**: 가장 우수한 개체의 성능
- 🔵 **평균 Fitness**: 전체 개체군의 평균 성능
- 🔴 **최저 Fitness**: 가장 낮은 성능
- 🟣 **표준편차**: 개체군의 다양성 지표

### Fitness 분포
최종 세대의 개체군이 어떤 fitness 값들로 분포되어 있는지 히스토그램으로 확인할 수 있습니다.

## 프로젝트 구조

```
GenTradingRuleWithGP/
├── src/
│   ├── main.py              # 메인 실행 파일
│   ├── config.py            # 설정 파일
│   ├── domain/              # 도메인 모델
│   │   └── condition.py
│   ├── gp/                  # GP 알고리즘
│   │   ├── evaluator.py
│   │   ├── operators.py
│   │   └── toolbox.py
│   ├── strategy/            # 전략 관련
│   │   ├── formatter.py
│   │   ├── parser.py
│   │   └── validator.py
│   └── utils/               # 유틸리티
│       ├── file_handler.py
│       └── visualizer.py    # 시각화 모듈
├── logs/                    # 실행 결과 저장 디렉토리
├── requirements.txt
└── README.md
```

## 라이브러리

- `deap==1.4.3`: 유전 프로그래밍 프레임워크
- `plotly==6.3.0`: 인터랙티브 시각화
- `numpy==2.3.3`: 수치 계산
- `pandas==2.3.2`: 데이터 처리
- `pydot==4.0.1`: 트리 시각화

## 라이센스

이 프로젝트는 MIT 라이센스 하에 배포됩니다.