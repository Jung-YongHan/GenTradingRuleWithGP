from bt4.Constants import ExType


class MarketID :
    def __init__(self, ex_type, mkt_id) :
        """

        :param ex_type:
        :param original_mkt_id: id from ccxt.fetch_markets()
        """
        self.ex_type = ex_type
        self.mkt_id = mkt_id

    def get_universal_id(self) :
        """
        return KRW-BTC form
        :return:
        """
        if self.ex_type == ExType.bithumb :
            return "KRW-" + self.mkt_id
        else :
            return self.mkt_id

    def get_mkt_id(self) :
        """
        original form => upbit KRW-BTC, bithumb BTC, binance BTCUSDT
        :return:
        """
        return self.mkt_id

    def get_quote_id(self) :
        """
        return upbit KRW-BTC, bithumb BTC_KRW, binance BTCUSDT
        :return:
        """
        if self.ex_type == ExType.bithumb :
            return self.mkt_id + "_KRW"
        else :
            return self.mkt_id
