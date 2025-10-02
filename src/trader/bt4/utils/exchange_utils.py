

def std_2_bithumb_mkt_ids(mkt_id_coins):
    """
    KRW-BTC -> BTC_KRW
    :param coins:
    :return:
    """
    converted = []
    for coin in mkt_id_coins:
        parts = coin.split("-")
        converted.append(f"{parts[1]}_{parts[0]}")
    return converted

def std_2_uniformed_mkt_ids(std_mkt_ids):
    """
    KRW-BTC -> BTC/KRW
    :param coins:
    :return:
    """
    converted = []
    for coin in std_mkt_ids:
        converted.append(std_2_uniformed_mkt_id(coin))
    return converted

def std_2_uniformed_mkt_id(std_mkt_id):
    if "-" in std_mkt_id:
        parts = std_mkt_id.split("-")
        return f"{parts[1]}/{parts[0]}"
    else:
        return std_mkt_id

def std_2_binance_mkt_id(std_mkt_id):
    """
    USDT-BTC -> BTCUSDT
    :param std_mkt_id:
    :return:
    """
    if "-" in std_mkt_id:
        parts = std_mkt_id.split("-")
        return f"{parts[1]}{parts[0]}"
    else:
        return std_mkt_id

def std_2_binance_mkt_ids(std_mkt_ids):
    """
    (BTCUSDT -> USDT-BTC)xn
    :param uniformed_mkt_id:
    :return:
    """
    converted = []
    for coin in std_mkt_ids :
        converted.append(std_2_binance_mkt_id(coin))
    return converted


def uniformed_2_std_mkt_ids(uniformed_mkt_ids):
    """
    (BTC/KRW -> KRW-BTC)xn
    :param uniformed_mkt_id:
    :return:
    """
    converted = []
    for coin in uniformed_mkt_ids :
        converted.append(uniformed_2_std_mkt_id(coin))
    return converted

def uniformed_2_std_mkt_id(uniformed_mkt_id):
    """
    BTC/KRW -> KRW-BTC
    :param uniformed_mkt_id:
    :return:
    """
    if "/" in uniformed_mkt_id:
        parts = uniformed_mkt_id.split("/")
        return f"{parts[1]}-{parts[0]}"
    else:
        return uniformed_mkt_id

def bithumb_2_std_mkt_ids(bithumb_coins):
    """
    (BTC_KRW -> KRW-BTC)xN
    :param coins:
    :return:
    """
    converted = []
    for coin in bithumb_coins:
        converted.append(bithumb_2_std_mkt_id(coin))
    return converted

def bithumb_2_std_mkt_id(bithumb_coin):
    """
    BTC_KRW -> KRW-BTC
    :param bithumb_coin:
    :return:
    """
    if "_" in bithumb_coin:
        parts = bithumb_coin.split("_")
        return f"{parts[1]}-{parts[0]}"
    else:
        return bithumb_coin


def bithumb_2_uniformed_mkt_ids(std_mkt_id_list):
    """
    (KRW-BTC -> BTC/KRW)xn
    for ccxt
    :param std_mkt_id_list:
    :return:
    """
    uniformed_mkt_ids = []
    for mkt_id in std_mkt_id_list:
        uniformed_mkt_ids.append(bithumb_2_uniformed_mkt_id(mkt_id))
    return uniformed_mkt_ids

def bithumb_2_uniformed_mkt_id(std_mkt_id):
    """
    KRW-BTC -> BTC/KRW
    :param std_mkt_id:
    :return:
    """
    if "-" in std_mkt_id:
        parts = std_mkt_id.split("-")
        return f"{parts[1]}/{parts[0]}"
    else:
        return std_mkt_id


def binance_2_std_mkt_ids(binance_coins):
    """
    (BTCUSDT -> USDT-BTC)xN
    :param coins:
    :return:
    """
    converted = []
    for coin in binance_coins:
        converted.append(binance_2_std_mkt_id(coin))
    return converted

def binance_2_std_mkt_id(binance_coin):
    """
    (BTCUSDT -> USDT-BTC)
    :param binance_coin:
    :return:
    """
    if binance_coin.endswith("USDT"):
        parts = binance_coin[:-4]
        return f"USDT-{parts}"
    else:
        return binance_coin