import redis

from bt4.Constants import ExType, CandleType
from bt4.quote.ExchangeQuoteDispatcher import QuoteReceiver, QuotePullRequestReceiver
from bt4.quote.QuoteListener import QuoteListener, QuotePullRequestListener
from bt4.quote.QuoteSupport import Quote

import bt4.GlobalProperties as global_prop
import pandas as pd

monitor_WQD = True
class Websocket_EQD_QuoteValidator (QuoteListener, QuotePullRequestListener) :

    def __init__(self):
        if not monitor_WQD :
            quote_receiver = QuoteReceiver()
            quote_receiver.add_quote_receiver(self)
            quote_receiver.start()

        qpr_receiver = QuotePullRequestReceiver()
        qpr_receiver.add_quote_pull_req_receiver(self)
        qpr_receiver.start()

        self.kafka_quote = None
        self.websocket_quote = None

        quote_redis_ip = global_prop.QUOTE_REDIS_IP_ADDR
        self.redis = redis.StrictRedis(host = quote_redis_ip, port = global_prop.REDIS_PORT, db = 0)

    def quote_received(self, quote):
        self.kafka_quote = quote
        if self.websocket_quote is not None:
            print("compare two quote in kafka thread!")
            compare_result, problem = self.compare(self.kafka_quote, self.websocket_quote)
            if not compare_result:
                print("Two Quotes are different!!")
                # print(problem)
            else:
                print("Two Quotes are Same!!")
            self.kafka_quote = None
            self.websocket_quote = None
        else:
            print("Wait for receiving Websocket_quote!")

    def do_pull_quote(self, ex_type, time_str) :
        loaded_json = self.redis.get(f"{ex_type.name}/quote")
        self.websocket_quote = Quote.unmarshal(loaded_json)

        if monitor_WQD :
            w_mkt_ticks = self.websocket_quote.ex_market_ticks[ExType.upbit]
            print(f"market ticks: {w_mkt_ticks['KRW-BTC']}")

            ex_cdl_dfs = self.websocket_quote.ex_quote[ExType.upbit]

            for cdl in ex_cdl_dfs:
                if cdl in [CandleType.MINUTES_1, CandleType.MINUTES_3, CandleType.MINUTES_5,
                           CandleType.MINUTES_15, CandleType.MINUTES_30, CandleType.HOUR,
                           CandleType.HOUR4, CandleType.DAYS, CandleType.DAYS_0, CandleType.DAYS_23]:
                    # if cdl in [CandleType.MINUTES_1] :
                    for market in ex_cdl_dfs[cdl]:
                        print(f"{cdl.name} - len ({len(ex_cdl_dfs[cdl][market])}): {ex_cdl_dfs[cdl][market].tail(10)}")
        else:
            if self.kafka_quote is not None:
                print("compare two quote in websocket thread!")
                compare_result, problem = self.compare(self.kafka_quote, self.websocket_quote)
                if not compare_result:
                    print("Two Quotes are different!!")
                    # print(problem)
                else:
                    print("Two Quotes are Same!!")
                self.kafka_quote = None
                self.websocket_quote = None
            else:
                print("Wait for receiving Kafka_quote!")

    def compare(self, k_quote, w_quote ):
        compare_result = True
        problem = ""
        if k_quote.time_dt != w_quote.time_dt:
            problem = problem + f"diff time_dt: {k_quote.time_dt=}, {w_quote.time_dt=}"
            compare_result = False

        k_mkt_ticks = k_quote.ex_market_ticks[ExType.upbit]
        w_mkt_ticks = w_quote.ex_market_ticks[ExType.upbit]
        tgt_markets = w_mkt_ticks.keys()
        tgt_market = next(iter(tgt_markets))
        k_mkt_tics_str = f"{k_mkt_ticks[tgt_market]}"
        w_mkt_tics_str = f"{w_mkt_ticks[tgt_market]}"
        print(f"Market Ticks " + "==" * 50)
        print(f"k_mkt ticks: {k_mkt_tics_str}")
        print(f"w_mkt ticks: {w_mkt_tics_str}")
        if  f"{k_mkt_tics_str}" != w_mkt_tics_str:
            problem = problem + f"\r\nk_mkt ticks : {k_mkt_tics_str}, w_mkt_ticks {w_mkt_tics_str}"
            print(f"two market ticks are different!! : {problem}")
            compare_result = False, problem

        k_ex_quote = k_quote.ex_quote[ExType.upbit]
        w_ex_quote = w_quote.ex_quote[ExType.upbit]

        print("==" * 50)
        for cdl in w_ex_quote:
            if cdl in [CandleType.MINUTES_1, CandleType.MINUTES_3, CandleType.MINUTES_5,
                                      CandleType.MINUTES_15, CandleType.MINUTES_30, CandleType.HOUR,
                                      CandleType.HOUR4, CandleType.DAYS, CandleType.DAYS_0, CandleType.DAYS_23]:
            # if cdl in [CandleType.MINUTES_1] :
                compare_result, problem1 = self.__print_ex_candle_diff__(w_ex_quote, k_ex_quote, tgt_market, cdl)
                problem = problem + "\r\n" + problem1

        return compare_result, problem

    def __print_ex_candle_diff__(self, w_ex_quote, k_ex_quote, tgt_market, cdl_type):
        print("--"*30)
        k_cdl_df = k_ex_quote[cdl_type][tgt_market]
        print(f"Kafka     ExQuoteDispatcher ({cdl_type.name}) - {len(k_cdl_df)}")
        # print(k_1m_cdl_df.tail(5))

        w_cdl_df = w_ex_quote[cdl_type][tgt_market]
        print(f"Websocket ExQuoteDispatcher ({cdl_type.name}) - {len(w_cdl_df)}")
        # print(w_1m_cdl_df.tail(5))

        is_two_dfs_same = w_cdl_df.equals(k_cdl_df)
        if not is_two_dfs_same :
            w_cdl_diff_df, k_cdl_diff_df = self.__get_difference__(w_cdl_df, k_cdl_df)
            if not(w_cdl_diff_df.empty and k_cdl_diff_df.empty):
                msg = "Same" if is_two_dfs_same else "Different"
                print(f"## compare candles: {cdl_type.name} ==> {msg}")
                print(f"w_cdl_diff_df : {w_cdl_diff_df}")
                print(f"k_cdl_diff_df : {k_cdl_diff_df}")
                return False, f"w_cdl_diff_df: {w_cdl_diff_df}, k_cdl_diff_df: {k_cdl_diff_df}"
        print("Two candles are same!")
        return True, ""


    def __get_difference__(self, df1, df2) :
        common_index = df1.index.intersection(df2.index)
        diff_index = common_index[(df1.loc[common_index] != df2.loc[common_index]).any(axis = 1)]

        # diff_index = df1.ne(df2).any(axis = 1)
        df1_diff = df1.loc[diff_index]
        df2_diff = df2.loc[diff_index]
        return df1_diff, df2_diff


if __name__ == '__main__' :
    Websocket_EQD_QuoteValidator()