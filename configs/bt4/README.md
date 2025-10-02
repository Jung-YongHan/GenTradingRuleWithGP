# BT4 백테스트 설정 파일

이 디렉토리는 GP 전략을 bt4_trader로 평가할 때 사용하는 백테스트 설정 파일들을 저장합니다.

## 사용 방법

### main.py에서 설정 파일 변경

`src/main.py` 파일의 `if __name__ == "__main__"` 부분에서 설정 파일을 선택할 수 있습니다:

```python
if __name__ == "__main__":
    # 원하는 설정 파일 선택
    bt4_config_file = "base_config.json"  # 이 부분을 변경
    
    bt4_config = load_bt4_config(bt4_config_file)
    set_bt4_config(bt4_config)
    # ...
```

## 설정 파일 형식

bt4_trader의 설정 형식을 따릅니다:

```json
{
  "stgy_name": "전략이름",
  "module_name": "모듈이름",
  "bt_start": "2018-10-01T08:59:00",
  "bt_end": "2022-11-25T08:59:00",
  "markets": ["KRW-BTC"],
  "cdl_type": 1440,
  "init_balance": 10000000,
  "slippage": 0.005,
  "bt_times": ["00:59", "04:59", "08:59", "12:59", "16:59", "20:59"],
  "vars": {},
  "buy_systems": {},
  "sell_systems": {}
}
```

## 주요 파라미터 설명

### 필수 파라미터
- `stgy_name`: 전략 이름
- `module_name`: 모듈 이름 (stgy_name과 동일하게 설정)
- `bt_start`: 백테스트 시작 시간 (ISO 8601 형식)
- `bt_end`: 백테스트 종료 시간 (ISO 8601 형식)
- `markets`: 거래할 마켓 리스트 (예: ["KRW-BTC", "KRW-ETH"])
- `cdl_type`: 캔들 타입 (분 단위, 예: 1440 = 1일)
- `init_balance`: 초기 자본금

### 선택 파라미터
- `slippage`: 슬리피지 (기본값: 0.005)
- `bt_times`: 백테스트 실행 시간 (기본값: 4시간마다)

### 거래 전략 파라미터
- `vola`: 변동성 타겟팅
  - `support`: 사용 여부 (true/false)
  - `vol_tgt`: 목표 변동성 (예: 0.04)

- `timeframe`: 타임프레임 설정
  - `support`: 사용 여부
  - `timeframes`: 거래 시간대
  - `timegap`: 시간 간격

- `fixed`: 고정 비율 거래
  - `support`: 사용 여부
  - `hdge`: 헤지 여부
  - `trade_ratio`: 거래 비율 (0.0 ~ 1.0)

- `weighted`: 가중치 거래
  - `support`: 사용 여부
  - `top_n`: 상위 N개 종목 가중치 (예: [0.6, 0.3, 0.1])

- `stop_loss`: 손절매
  - `support`: 사용 여부
  - `ratio`: 손절 비율 (예: -0.04)

- `trailing_stop`: 트레일링 스톱
  - `support`: 사용 여부
  - `ratio`: 트레일링 스톱 비율 (예: -0.02)

- `take_profit`: 익절
  - `support`: 사용 여부
  - `ratio`: 익절 비율 (예: 0.07)

## 새 설정 파일 추가

1. 이 디렉토리에 새로운 JSON 파일 생성
2. 위 형식에 맞춰 설정 작성
3. `main.py`에서 파일 이름 지정

## 예제

### 보수적 전략 (장기 투자)
```json
{
  "bt_start": "2020-01-01T00:00:00",
  "bt_end": "2023-12-31T23:59:59",
  "markets": ["KRW-BTC", "KRW-ETH"],
  "cdl_type": 1440,
  "init_balance": 10000000,
  "fixed": {
    "support": true,
    "trade_ratio": 0.3
  },
  "stop_loss": {
    "support": true,
    "ratio": -0.1
  }
}
```

### 공격적 전략 (단기 트레이딩)
```json
{
  "bt_start": "2023-01-01T00:00:00",
  "bt_end": "2023-12-31T23:59:59",
  "markets": ["KRW-BTC"],
  "cdl_type": 60,
  "init_balance": 5000000,
  "fixed": {
    "support": true,
    "trade_ratio": 0.8
  },
  "stop_loss": {
    "support": true,
    "ratio": -0.05
  },
  "take_profit": {
    "support": true,
    "ratio": 0.1
  }
}
```

## 주의사항

- `vars`, `buy_systems`, `sell_systems`는 GP가 자동으로 생성하므로 설정 파일에 포함하지 않아도 됩니다
- `bt_start`와 `bt_end`는 데이터가 존재하는 기간이어야 합니다
- `markets`는 거래소에 존재하는 마켓이어야 합니다
- GP 실행 시 설정 파일의 내용이 전역으로 설정되어 모든 개체 평가에 사용됩니다
