# gp/evaluator.py

import hashlib
import json

from src.before.configs.gp_configs import MAX_TREE_SIZE
from src.before.strategy.parser import parse_gp_tree_to_json
from src.before.strategy.validator import validate_and_clean_strategy

# 전략 평가 결과를 저장하는 캐시
_strategy_cache = {}

# BT4 백테스트 설정 (main.py에서 설정)
_bt4_config = None
_bt4_adapter = None


def get_strategy_hash(strategy_json):
    """전략 JSON을 해시값으로 변환하여 고유 키 생성"""
    try:
        # JSON을 정렬된 문자열로 변환하여 일관된 해시 생성
        strategy_str = json.dumps(strategy_json, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(strategy_str.encode()).hexdigest()
    except Exception:
        return None


def get_cache_stats():
    """캐시 통계 반환"""
    return {
        "total_cached": len(_strategy_cache),
        "cache_size_bytes": sum(
            len(str(k)) + len(str(v)) for k, v in _strategy_cache.items()
        ),
    }


def clear_cache():
    """캐시 초기화"""
    global _strategy_cache
    _strategy_cache.clear()


def set_bt4_config(config):
    """
    BT4 백테스트 설정을 전역으로 설정
    main.py에서 한 번만 호출하여 설정

    Args:
        config: bt4_config.py에서 로드한 설정 딕셔너리
    """
    global _bt4_config, _bt4_adapter
    _bt4_config = config
    # 설정이 변경되면 어댑터도 재생성
    _bt4_adapter = None


def eval_func(individual, condition_manager=None):
    """개체를 평가하는 함수"""
    if not individual or individual[0].name != "Strategy":
        return (-1000.0,)
    if len(individual) > MAX_TREE_SIZE:
        return (-1000.0,)

    # 1. 개체를 JSON으로 변환
    if condition_manager is None:
        # condition_manager가 없으면 기본 평가
        return (-1000.0,)

    strategy_json = parse_gp_tree_to_json(individual, condition_manager)
    if strategy_json is None:
        return (-1000.0,)

    # 2. Trader로 전달하기 전에 JSON 검증 및 정리
    modified_json = validate_and_clean_strategy(strategy_json)

    # 3. 캐시 확인 - 이미 평가된 전략인지 확인
    strategy_hash = get_strategy_hash(modified_json)
    if strategy_hash is not None and strategy_hash in _strategy_cache:
        # 캐시에서 결과 반환
        return (_strategy_cache[strategy_hash],)

    # 4. Trader 모듈로 전달하여 적합도 평가
    fitness_score = evaluate_with_trader(modified_json)

    # 5. 평가 결과를 캐시에 저장
    if strategy_hash is not None:
        _strategy_cache[strategy_hash] = fitness_score

    return (fitness_score,)


def evaluate_with_trader(modified_json=None):
    """적합도를 평가하는 함수.

    원본은 외부 ``bt4_trader`` 백테스트 엔진을 호출했으나, 채점/재현 환경에서는
    해당 엔진을 사용할 수 없으므로 공유 합성 평가기(``src.synthetic``)로 대체한다.
    이 한 줄(leaf 평가)만 synthetic 으로 바뀌었을 뿐, 캐시/해싱/파싱/검증 등
    그 주위의 오케스트레이션 로직은 원본과 동일하다. (src/after 도 동일한 합성
    평가기를 사용하므로 before/after 비교가 공정하다.)
    """
    from src.synthetic import score_strategy

    try:
        # _bt4_config 는 합성 시장 시드로만 사용한다(없으면 기본 42).
        seed = 42
        if isinstance(_bt4_config, dict):
            seed = int(_bt4_config.get("random_seed", 42))
        return score_strategy(modified_json, seed=seed)
    except Exception as e:
        print(f"평가 중 오류 발생: {e}")
        import traceback

        traceback.print_exc()
        return -1000.0
