# GenTradingRuleWithGP 🧬📈

유전 프로그래밍(Genetic Programming)을 사용하여 거래 전략 규칙을 자동 생성하는 프로젝트입니다. DEAP 라이브러리를 활용하여 기술적 지표 기반의 매수/매도 시스템을 진화시킵니다.

## ✨ 주요 기능

### 🧬 유전 프로그래밍 기반 전략 생성
- **DEAP 프레임워크**: 강력한 GP 알고리즘 구현
- **자동 전략 최적화**: 진화를 통한 전략 개선
- **다양한 연산자**: 교차, 변이, 선택 연산자 커스터마이징
- **강타입 시스템**: BuyType, SellType, Strategy 타입으로 안전한 전략 생성

### 📊 기술적 지표 지원
- **RSI** (Relative Strength Index): 과매수/과매도 신호
- **SMA** (Simple Moving Average): 추세 분석
- **MACD** (Moving Average Convergence Divergence): 모멘텀 분석
- **ATR** (Average True Range): 변동성 측정
- **BBANDS** (Bollinger Bands): 변동성 기반 신호

### 📈 진화 과정 시각화
- **인터랙티브 그래프**: Plotly 기반 실시간 진화 추적
- **세대별 Fitness 추적**: 최고/평균/최저 fitness 변화
- **표준편차 모니터링**: 개체군 다양성 추적
- **Fitness 분포**: 히스토그램으로 최종 개체군 분석
- **트리 구조 시각화**: 최적 전략의 GP 트리 구조

### 🎯 성능 최적화
- **병렬 처리**: Multiprocessing을 통한 평가 가속화
- **메모리 효율성**: 대용량 개체군 처리 최적화
- **시간 측정**: 세대별 및 전체 진화 시간 추적
- **리소스 관리**: CPU 사용량 제어 가능

## 🚀 설치 및 실행

### 환경 요구사항
- Python 3.12+
- 8GB+ RAM (대용량 개체군 처리 시)
- 멀티코어 CPU (병렬 처리 활용)

### 설치
```bash
# 저장소 클론
git clone https://github.com/Jung-YongHan/GenTradingRuleWithGP.git
cd GenTradingRuleWithGP

# 의존성 설치
pip install -r requirements.txt
```

### 실행
```bash
# 메인 프로그램 실행
python src/main.py
```

## 📁 출력 파일

프로그램 실행 후 `logs/YYYY-MM-DD/run_HH-MM-SS/` 디렉토리에 생성됩니다:

### 📊 시각화 파일
- **`evolution.html`**: 진화 과정 인터랙티브 그래프
  - 세대별 fitness 변화 추적
  - 줌, 패닝, 호버 기능 지원
  - 표준편차 및 다양성 지표
- **`evolution.png`**: 진화 과정 정적 이미지 (150 DPI)
- **`fitness_distribution.html`**: 최종 개체군 fitness 분포
- **`fitness_distribution.png`**: Fitness 분포 정적 이미지

### 📋 전략 파일
- **`strategy.json`**: 최적화된 거래 전략 (JSON 형식)
- **`strategy_tree.png`**: 전략 트리 구조 시각화
- **`strategy.log`**: 상세 실행 로그 및 통계

## ⚙️ 설정

### GP 알고리즘 설정 (`src/configs/gp_configs.py`)
```python
N_POPULATION = 1000          # 개체군 크기
N_GENERATION = 50            # 세대 수
CROSSOVER_PROBABILITY = 0.8  # 교차 확률
MUTATION_PROBABILITY = 0.15  # 변이 확률
```

### 트리 구조 설정
```python
INITIAL_MIN_DEPTH = 4        # 초기 최소 깊이
INITIAL_MAX_DEPTH = 10       # 초기 최대 깊이
MAX_MUTATION_DEPTH = 6       # 변이 최대 깊이
MAX_TREE_SIZE = 500          # 최대 트리 크기
```

### 성능 설정 (`src/configs/constants.py`)
```python
CPU_COUNT = 10               # 사용할 CPU 코어 수
RANDOM_SEED = 42             # 재현 가능한 결과를 위한 시드
```

## 🏗️ 프로젝트 구조

```
GenTradingRuleWithGP/
├── src/
│   ├── main.py                    # 메인 실행 파일
│   ├── configs/                   # 설정 파일들
│   │   ├── constants.py           # 전역 상수
│   │   ├── gp_configs.py          # GP 알고리즘 설정
│   │   └── indicator_configs.py   # 기술적 지표 정의
│   ├── domain/                    # 도메인 모델
│   │   ├── condition.py           # 조건 관리자
│   │   ├── indicator.py           # 지표 생성 및 관리
│   │   └── types.py              # 강타입 시스템
│   ├── gp/                       # 유전 프로그래밍
│   │   ├── evaluator.py          # 적합도 평가 함수
│   │   ├── operators.py          # GP 연산자 (교차/변이)
│   │   └── toolbox.py            # DEAP 툴박스 설정
│   ├── strategy/                 # 전략 관련
│   │   ├── formatter.py          # 전략 포맷팅
│   │   ├── parser.py             # GP 트리 → JSON 변환
│   │   └── validator.py          # 전략 유효성 검사
│   └── utils/                    # 유틸리티
│       ├── file_handler.py       # 파일 처리 및 로깅
│       └── visualizer.py         # 시각화 모듈
├── logs/                         # 실행 결과 저장
├── notebooks/                    # Jupyter 노트북 (실험용)
├── requirements.txt              # 의존성 목록
└── README.md                     # 프로젝트 문서
```

## 📊 시각화 예시

### 진화 과정 그래프
```
세대별 Fitness 변화:
🟢 최고 Fitness: 95.67 → 98.23 → 99.45
🔵 평균 Fitness: 72.34 → 78.91 → 82.15
🔴 최저 Fitness: 45.12 → 52.67 → 58.23
🟣 표준편차: 12.45 → 8.92 → 6.78
```

### Fitness 분포 히스토그램
최종 세대의 개체군이 어떤 fitness 값들로 분포되어 있는지 확인할 수 있습니다.

## 🔧 핵심 라이브러리

- **`deap==1.4.3`**: 유전 프로그래밍 프레임워크
- **`plotly==6.3.0`**: 인터랙티브 시각화
- **`numpy==2.3.3`**: 수치 계산
- **`pandas==2.3.2`**: 데이터 처리
- **`pydot==4.0.1`**: 트리 구조 시각화

## 🚨 성능 고려사항

### Multiprocessing 최적화
- **현재 상황**: 평가 함수가 가벼워서 multiprocessing 오버헤드가 큼
- **해결책**: `CPU_COUNT`를 1로 설정하여 순차 실행 권장
- **향후 계획**: 실제 Trader 연동 시 multiprocessing 재활성화

### 메모리 관리
- **개체군 크기**: 1000개 이상 시 메모리 사용량 주의
- **트리 크기**: `MAX_TREE_SIZE`로 복잡도 제한
- **가비지 컬렉션**: fitness 값 삭제로 메모리 정리

## 🔮 향후 계획

### 단기 목표
- [ ] **Trader 모듈 연동**: 실제 백테스팅을 통한 적합도 평가
- [ ] **더 많은 지표**: Stochastic, Williams %R, CCI 등 추가
- [ ] **실시간 모니터링**: 진화 과정 실시간 시각화

### 장기 목표
- [ ] **실시간 거래**: 생성된 전략의 실시간 적용
- [ ] **앙상블 전략**: 여러 전략의 조합
- [ ] **딥러닝 통합**: GP + 신경망 하이브리드 접근법

## 🤝 기여하기

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이센스

이 프로젝트는 MIT 라이센스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 📞 연락처

- **개발자**: Jung YongHan
- **이메일**: [이메일 주소]
- **GitHub**: [GitHub 프로필]

---

**⭐ 이 프로젝트가 도움이 되었다면 Star를 눌러주세요!**