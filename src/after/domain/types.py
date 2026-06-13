# after/domain/types.py
#
# GP 핵심 타입 정의. **원본과 반드시 동일하게 유지**한다.
# 파서가 DEAP 트리의 문자열 표현(따옴표로 감싼 str terminal)에 의존하므로,
# 타입/terminal 표현을 바꾸면 파서의 따옴표 처리 정규식이 깨진다.


class BuyType:
    """매수 조건 또는 규칙 타입"""

    pass


class SellType:
    """매도 조건 또는 규칙 타입"""

    pass


def Strategy(buy_logic: BuyType, sell_logic: SellType):
    """전략 타입"""
    return (buy_logic, sell_logic)
