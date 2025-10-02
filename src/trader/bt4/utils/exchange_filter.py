from bt4.utils.exchange_utils import std_2_uniformed_mkt_id, std_2_uniformed_mkt_ids, uniformed_2_std_mkt_id, \
    uniformed_2_std_mkt_ids, std_2_binance_mkt_id, std_2_binance_mkt_ids, binance_2_std_mkt_id, binance_2_std_mkt_ids
from bt4.utils.python_utils import SingletonInstance, load_class_from_module, from_utc_int_timestamp, TIME_FORMAT


class ExFilterFactory(SingletonInstance):
    def __init__(self):
        pass

    def get(self, ex_type):
        filter_cls = ex_type.value + '_ExFilter'
        return load_class_from_module(self.__module__, filter_cls)


class DefaultExFilter:
    """
    CCXT를 처리하는데 있어서 Exchange마다 ccxt처리시 trade전 혹은 후에 공통적으로 처리해주어야 할것 모음
    case 1) Market id를 standard -> uniformed market id로 변환 혹은 역변환 (bithumb의 경우에만, upbit은 안해도됨)
            (KRW-BTC -> BTC/KRW) -> trade -> (BTC/KRW -> KRW-BTC)
    case 2) volume을 소수점 8자리 round 하거나 혹은 안하거나 (bithumb의 경우에만, upbit은 안해도됨)
    default에는 안함
    """

    def __init__(self):
        pass

    def filter_market_id_before(self, market):
        return market

    def filter_market_ids_before(self, markets):
        return markets

    def filter_market_id_after(self, market):
        return market

    def filter_market_ids_after(self, markets):
        return markets

    def filter_market_ids_in_df(self, df):
        df["market"] = df["market"].apply(uniformed_2_std_mkt_id)
        return df

    def filter_market_ids_in_dfs(self, dfs):
        for market in dfs :  ## convert BTC/KRW -> KRW-BTC in key and its dataframe
            std_mkt_id = uniformed_2_std_mkt_id(market)
            mkt_df = dfs[market]
            mkt_df = self.filter_market_ids_in_df(mkt_df)
            dfs[std_mkt_id] = mkt_df
            del dfs[market]
        return dfs

    def filter_volume(self, volume):
        return volume

class upbit_ExFilter(DefaultExFilter):

    def __init__(self) :
        super(upbit_ExFilter, self).__init__()


class bithumb_ExFilter(DefaultExFilter) :

    def __init__(self) :
        super(bithumb_ExFilter, self).__init__()

    def filter_market_id_before(self, market):
        """
        KRW-BTC -> BTC/KRW
        :param market:
        :return:
        """
        return std_2_uniformed_mkt_id(market)

    def filter_market_ids_before(self, markets):
        """
        [KRW-BTC -> BTC/KRW]xN
        :param market:
        :return:
        """
        return std_2_uniformed_mkt_ids(markets)

    def filter_market_id_after(self, market):
        """
        BTC/KRW -> KRW-BTC
        :param market:
        :return:
        """
        return uniformed_2_std_mkt_id(market)

    def filter_market_ids_after(self, markets):
        """
        [BTC/KRW -> KRW-BTC] x N
        :param market:
        :return:
        """
        return uniformed_2_std_mkt_ids(markets)

    def filter_volume(self, volume) :
        return round(volume, 8)

class binance_ExFilter(DefaultExFilter) :
    def __init__(self) :
        super(binance_ExFilter, self).__init__()

    def filter_market_id_before(self, market):
        """
        USDT-BTC -> BTCUSDT
        :param market:
        :return:
        """
        return std_2_binance_mkt_id(market)

    def filter_market_ids_before(self, markets):
        """
        [USDT-BTC -> BTCUSDT] x N
        :param market:
        :return:
        """
        return std_2_binance_mkt_ids(markets)

    def filter_market_id_after(self, market):
        """
        BTCUSDT -> USDT-BTC
        :param market:
        :return:
        """
        return binance_2_std_mkt_id(market)

    def filter_market_ids_after(self, markets):
        """
        [BTCUSDT -> USDT-BTC] x N
        :param market:
        :return:
        """
        return binance_2_std_mkt_ids(markets)
