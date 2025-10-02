import unittest

import redis

from bt4.Constants import ExType
from bt4.quote.QuoteSupport import Quote
from bt4.quote.upbit_websocket_quote_dispatcher import Coin1M_OHLCV
import bt4.GlobalProperties as global_prop

class MyTestCase(unittest.TestCase) :
    def test_recover_runtime_cdl_from_redis(self) :
        coins = ["KRW-BTC"]
        coin_1m_cdl_mgrs = {}
        for coin in coins:
            coin_1m_cdl_mgrs[coin] = Coin1M_OHLCV(coin)

        quote_redis_ip = global_prop.QUOTE_REDIS_IP_ADDR
        redis_storage = redis.StrictRedis(host = quote_redis_ip, port = global_prop.REDIS_PORT, db = 0)

        ex_type = ExType.upbit
        loaded_json = redis_storage.get(f"{ex_type.name}/quote")
        quote = Quote.unmarshal(loaded_json)

        cdl_market_dict = quote.ex_quote[ex_type]
        market_cdl_dict = {}
        for cdl in cdl_market_dict:
            for market in cdl_market_dict[cdl]:
                if market not in market_cdl_dict:
                    market_cdl_dict[market] = {}
                market_cdl_dict[market][cdl] = cdl_market_dict[cdl][market]

        ## Print
        for market in market_cdl_dict :
            coin_1m_cdl_mgrs[market].print_logs(True)

        if set(coins) == set(market_cdl_dict.keys()):
            for market in market_cdl_dict:
                coin_1m_cdl_mgrs[market].recover_candles(market_cdl_dict[market])
        else:
            print("Error: Requested coins and Redis stored coins are different!")

        ## Print
        for market in market_cdl_dict :
            coin_1m_cdl_mgrs[market].print_logs(True)






if __name__ == '__main__' :
    unittest.main()
