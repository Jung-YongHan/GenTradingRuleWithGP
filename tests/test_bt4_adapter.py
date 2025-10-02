# tests/test_bt4_adapter.py

"""
BT4 어댑터 테스트 스크립트

사용법:
    # 기본 설정으로 테스트
    python tests/test_bt4_adapter.py

    # 특정 설정 파일로 테스트
    python tests/test_bt4_adapter.py test_config_short_term.json

    # 환경 변수로 bt4_trader 경로 지정
    BT4_TRADER_PATH=/path/to/bt4_trader python tests/test_bt4_adapter.py
"""

import os
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.adapters.bt4_adapter import BT4BacktestAdapter
from src.configs.bt4_config import list_available_configs, load_bt4_config


def create_sample_gp_strategy():
    """테스트용 샘플 GP 전략 생성"""
    return {
        "vars": {
            "SMA1": {
                "func": "SMA",
                "params": [20],
                "cdl_type": "period",
                "sources": ["close"],
                "unary": False,
            },
            "SMA2": {
                "func": "SMA",
                "params": [50],
                "cdl_type": "period",
                "sources": ["close"],
                "unary": False,
            },
            "RSI1": {
                "func": "RSI",
                "params": [14],
                "cdl_type": "period",
                "sources": ["close"],
                "unary": True,
            },
        },
        "buy_systems": {
            "system1": {"alias": "system1", "left": "SMA1", "op": ">", "right": "SMA2"},
            "system2": {"alias": "system2", "left": "RSI1", "op": "<", "right": "30"},
        },
        "buy_system_op": "system1 and system2",
        "sell_systems": {
            "system1": {"alias": "system1", "left": "SMA1", "op": "<", "right": "SMA2"},
            "system2": {"alias": "system2", "left": "RSI1", "op": ">", "right": "70"},
        },
        "sell_system_op": "system1 or system2",
    }


def test_config_loading():
    """설정 파일 로딩 테스트"""
    print("=" * 60)
    print("1. 설정 파일 로딩 테스트")
    print("=" * 60)

    # 사용 가능한 설정 파일 목록 출력
    configs = list_available_configs()
    print(f"\n사용 가능한 설정 파일: {len(configs)}개")
    for config_name in configs:
        print(f"  - {config_name}")

    # 각 설정 파일 로드 테스트
    print("\n설정 파일 로드 테스트:")
    for config_name in configs:
        try:
            config = load_bt4_config(config_name)
            print(f"  ✓ {config_name}: {config.get('description', 'N/A')}")
        except Exception as e:
            print(f"  ✗ {config_name}: 오류 - {e}")

    print()


def test_adapter_with_config(config_name: str):
    """특정 설정 파일로 어댑터 테스트"""
    print("=" * 60)
    print(f"2. BT4 어댑터 테스트 - {config_name}")
    print("=" * 60)

    try:
        # 설정 로드
        print(f"\n[1/4] 설정 파일 로드: {config_name}")
        config = load_bt4_config(config_name)
        print(f"  ✓ 설정 로드 완료")
        print(f"  - 거래소: {config.get('ex_type')}")
        print(f"  - 기간: {config.get('bt_start')} ~ {config.get('bt_end')}")
        print(f"  - 마켓: {', '.join(config.get('markets', []))}")
        print(f"  - 초기자본: {config.get('initial_balance'):,}원")

        # 어댑터 생성
        print(f"\n[2/4] BT4 어댑터 생성")
        adapter = BT4BacktestAdapter(config)
        print(f"  ✓ 어댑터 생성 완료")

        # 샘플 전략 생성
        print(f"\n[3/4] 샘플 GP 전략 생성")
        strategy = create_sample_gp_strategy()
        print(f"  ✓ 샘플 전략 생성 완료")
        print(f"  - 지표 수: {len(strategy.get('vars', {}))}")
        print(f"  - 매수 조건: {strategy.get('buy_system_op', 'N/A')}")
        print(f"  - 매도 조건: {strategy.get('sell_system_op', 'N/A')}")

        # 전략 평가
        print(f"\n[4/4] 전략 평가 실행")
        print("  (백테스트 실행 중... 시간이 걸릴 수 있습니다)")
        fitness = adapter.evaluate_strategy(strategy)
        print(f"  ✓ 평가 완료")
        print(f"  - 적합도 점수: {fitness:.2f}")

        if fitness > 0:
            print(f"  ✓ 성공: 양의 수익률 ({fitness:.2f}%)")
        elif fitness == -1000.0:
            print(f"  ✗ 실패: 평가 오류 발생")
        else:
            print(f"  - 음의 수익률 ({fitness:.2f}%)")

        print("\n" + "=" * 60)
        print("테스트 완료!")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"\n✗ 테스트 실패: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """메인 테스트 함수"""
    # 명령행 인자로 설정 파일 지정 가능
    if len(sys.argv) > 1:
        config_name = sys.argv[1]
    else:
        config_name = "base_config.json"

    print("\n" + "=" * 60)
    print("BT4 어댑터 통합 테스트")
    print("=" * 60)
    print(f"프로젝트 루트: {project_root}")
    print(f"BT4_TRADER_PATH: {os.environ.get('BT4_TRADER_PATH', '(환경변수 미설정)')}")
    print()

    # 1. 설정 파일 로딩 테스트
    test_config_loading()

    # 2. 어댑터 테스트
    success = test_adapter_with_config(config_name)

    return 0 if success else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
