# 사용 방법

## 🚀 빠른 시작

### 1단계: 환경 변수 설정

```bash
export BT4_TRADER_PATH=/home/tako/Documents/yonghan/bt4_trader
```

### 2단계: 설정 파일 선택

`src/main.py` 파일을 열어서 원하는 설정 파일을 선택:

```python
if __name__ == "__main__":
    # 이 부분을 수정하여 설정 파일 선택
    bt4_config_file = "base_config.json"  # 원하는 파일명으로 변경
```

### 3단계: GP 실행

```bash
python src/main.py
```

---

## 📁 설정 파일 관리

### 설정 파일 위치
모든 백테스트 설정 파일은 `configs/bt4/` 디렉토리에 저장됩니다.

### 현재 사용 가능한 설정 파일
- `base_config.json` - 기본 설정

### 새 설정 파일 추가 방법

1. `configs/bt4/` 디렉토리에 새 JSON 파일 생성
   ```bash
   cp configs/bt4/base_config.json configs/bt4/my_config.json
   ```

2. 원하는 파라미터 수정
   ```json
   {
     "stgy_name": "MyStrategy",
     "bt_start": "2020-01-01T00:00:00",
     "bt_end": "2023-12-31T23:59:59",
     "markets": ["KRW-BTC", "KRW-ETH"],
     "init_balance": 10000000,
     ...
   }
   ```

3. `main.py`에서 파일명 변경
   ```python
   bt4_config_file = "my_config.json"
   ```

---

## 🔧 주요 설정 파라미터

### 백테스트 기본 설정
- `bt_start`: 백테스트 시작 시간 (ISO 8601 형식)
- `bt_end`: 백테스트 종료 시간
- `markets`: 거래할 마켓 리스트
- `cdl_type`: 캔들 간격 (분 단위, 1440 = 1일)
- `init_balance`: 초기 자본금

### 거래 전략 설정
- `fixed.trade_ratio`: 거래 비율 (0.0 ~ 1.0)
- `stop_loss.ratio`: 손절 비율 (음수)
- `take_profit.ratio`: 익절 비율 (양수)
- `trailing_stop.ratio`: 트레일링 스톱 비율

자세한 설명은 `configs/bt4/README.md` 참고

---

## 💡 동작 방식

### 전역 설정 방식

```
1. main.py 시작
   ↓
2. JSON 설정 파일 로드 (load_bt4_config)
   ↓
3. 전역 변수에 설정 저장 (set_bt4_config)
   ↓
4. GP 실행 시작
   ↓
5. 각 개체 평가 시 전역 설정 사용
   ├─ evaluator.py의 evaluate_with_trader()
   ├─ 전역 _bt4_config 사용
   └─ BT4BacktestAdapter로 백테스트
```

### 장점
- 설정을 한 번만 로드
- 모든 개체 평가에 동일한 설정 적용
- 설정 변경이 쉬움 (main.py에서 파일명만 변경)
- 성능 최적화 (싱글톤 패턴)

---

## 📊 실행 예시

### 기본 설정으로 실행

```bash
# 1. 환경 변수 설정
export BT4_TRADER_PATH=/home/tako/Documents/yonghan/bt4_trader

# 2. GP 실행
python src/main.py
```

실행 시 출력:
```
============================================================
🔧 BT4 백테스트 설정 로드
============================================================
✓ 설정 파일 로드 완료: base_config.json
  - 거래소: N/A
  - 기간: 2018-10-01T08:59:00 ~ 2022-11-25T08:59:00
  - 마켓: KRW-BTC
  - 초기자본: 10,000,000원

시스템 CPU 개수: 8
사용할 CPU 개수: 4
============================================================
✨ 초기 개체군 생성 및 평가 시작...
...
```

### 다른 설정으로 실행

1. `configs/bt4/my_strategy.json` 생성
2. `src/main.py` 수정:
   ```python
   bt4_config_file = "my_strategy.json"
   ```
3. 실행:
   ```bash
   python src/main.py
   ```

---

## 🐛 문제 해결

### 설정 파일 로드 실패

**오류:**
```
✗ 설정 파일 로드 실패: 설정 파일을 찾을 수 없습니다: ...
```

**해결:**
1. 파일 경로 확인
2. 파일 이름 확인 (대소문자 구분)
3. JSON 형식 검증

### BT4 설정이 초기화되지 않음

**오류:**
```
RuntimeError: BT4 설정이 초기화되지 않았습니다.
```

**해결:**
1. `main.py`의 설정 로드 부분이 올바른지 확인
2. `set_bt4_config()`가 호출되는지 확인

### BT4_TRADER_PATH 오류

**오류:**
```
ImportError: bt4_trader를 찾을 수 없습니다: ...
```

**해결:**
```bash
# 경로 확인
echo $BT4_TRADER_PATH
ls $BT4_TRADER_PATH

# 재설정
export BT4_TRADER_PATH=/correct/path/to/bt4_trader
```

---

## 📝 참고 문서

- **설정 파일 상세**: `configs/bt4/README.md`
- **통합 가이드**: `docs/INTEGRATION_GUIDE.md`
- **테스트 방법**: `tests/README.md`
- **설정 가이드**: `SETUP.md`

