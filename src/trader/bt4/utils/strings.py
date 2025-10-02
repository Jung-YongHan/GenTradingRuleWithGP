from typing import List


def split_source_target_markets(market: str) -> List[str]:
    """
    Notes:
        Binance에서는 source가 '/'뒤에 오기 때문에 split 후 reverse 하여 반환

    Examples:
        Input: "KRW-XRP"
        Output: ["KRW", "XRP"]

        Input: "XRP/USDT"
        Output: ["USDT", "XRP"]
    """
    if '/' in market:
        return list(reversed(market.split('/')))

    return market.split('-')
