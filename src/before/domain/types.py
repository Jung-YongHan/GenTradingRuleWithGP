# domain/types.py

# --- GP의 핵심 타입 정의 ---


class BuyType:
    """매수 조건 또는 규칙 타입"""

    pass


class SellType:
    """매도 조건 또는 규칙 타입"""

    pass


def Strategy(buy_logic: BuyType, sell_logic: SellType):
    """전략 타입"""
    return (buy_logic, sell_logic)
