# utils/helpers.py

import re


def extract_base_indicator_name(indicator_name):
    """지표 이름에서 숫자를 제거하여 원본 지표 이름을 추출합니다.

    Examples:
        RSI1 -> RSI
        MACD2 -> MACD
        SMA10 -> SMA
    """
    # 숫자로 끝나는 패턴을 찾아서 제거
    match = re.match(r"^(.+?)(\d+)$", indicator_name)
    if match:
        return match.group(1)
    return indicator_name


def extract_base_from_access_name(access_name):
    """접근 이름에서 기본 지표 이름을 추출

    Examples:
        MACD1[0] -> MACD1
        RSI1 -> RSI1
        close -> close
    """
    if "[" in access_name:
        return access_name.split("[")[0]
    return access_name
