import asyncio
import json
import pathlib
import ssl
import threading
import time
from abc import ABCMeta, abstractmethod

import jwt
import pandas as pd
import pytz
import redis as redis
import websockets

from bt4 import GlobalProperties as global_prop
from bt4.Constants import CandleType, ExType
from bt4.model.storage_mgr import StrategyStorage
from bt4.quote.QuoteConnector import UniversalQuoteConnector
from bt4.quote.QuoteSupport import Quote
from bt4.utils.exchange_filter import ExFilterFactory
from bt4.utils.exchange_utils import std_2_bithumb_mkt_ids, bithumb_2_std_mkt_id, binance_2_std_mkt_id
from bt4.utils.python_utils import now_dt, str2dt, to_kst_time, dt2str, SingletonInstance, load_class_from_module, \
    from_utc_int_timestamp
from bt4_cfg.websocket_quote_cfg import WS_PARAMS

from bt4.utils.mylog import init_log
log = init_log()

def_num_cdles = 300
def_num_cdles_1h = 5000

class AbstractCoin1M_OHLCV():
    def __init__(self, ex_type, coin):
        self.ex_type = ex_type
        self.coin = coin
        self._1m_open = 0
        self._1m_high = 0
        self._1m_low = 0
        self._1m_close = 0
        self._1m_volume = 0
        self._1m_ask_vol = 0
        self._1m_bid_vol = 0
        self._1m_last_min_dt = now_dt()

        self._1m_df = pd.DataFrame(columns = ["market", "open", "high", "low", "close", "vol"])
        self._3m_df = pd.DataFrame(columns = ["market", "open", "high", "low", "close", "vol"])
        self._5m_df = pd.DataFrame(columns = ["market", "open", "high", "low", "close", "vol"])
        self._15m_df = pd.DataFrame(columns = ["market", "open", "high", "low", "close", "vol"])
        self._30m_df = pd.DataFrame(columns = ["market", "open", "high", "low", "close", "vol"])
        self._1h_df = pd.DataFrame(columns = ["market", "open", "high", "low", "close", "vol"])
        self._4h_df = pd.DataFrame(columns = ["market", "open", "high", "low", "close", "vol"])
        self._1d_df = pd.DataFrame(columns = ["market", "open", "high", "low", "close", "vol"])
        self._tf_dfs = {}
        for tf_idx in range(CandleType.DAYS_0.value, CandleType.DAYS_23.value+1):
            self._tf_dfs[CandleType(tf_idx)] = pd.DataFrame(columns = ["market", "open", "high", "low", "close", "vol"])

        self.lock = threading.Lock()
        self.supported_candles = WS_PARAMS[self.ex_type]["supported_candles"]
        self.ex_filter = ExFilterFactory.instance().get(self.ex_type)

    @abstractmethod
    def parse_trade_json(self, t_json) -> dict:
        pass

    def update(self, trade_json):
        parse_result = self.parse_trade_json(trade_json)

        if WS_PARAMS["common"]["enable_log_tick"]:
            log.info(trade_json)

        if "bulk" in parse_result:
            for unit in parse_result["bulk"]:
                self.update_unit(unit)
        else:
            self.update_unit(parse_result)


    def update_unit(self, parse_result):
        market = parse_result["market"]
        market = self.ex_filter.filter_market_id_after(market) # BTCUSDT -> USDT-BTC
        kst_time_dt = parse_result["trading_dt"]
        trading_price = parse_result["trading_price"]
        trading_volume = parse_result["trading_volume"]
        ask_bid = parse_result["ask_bid"]

        if self._1m_last_min_dt.minute == kst_time_dt.minute :
            if trading_price > self._1m_high :
                self._1m_high = trading_price

            if trading_price < self._1m_low :
                self._1m_low = trading_price

            self._1m_close = trading_price
            self._1m_volume = self._1m_volume + trading_volume

            if ask_bid == "ASK" :
                self._1m_ask_vol = self._1m_ask_vol + trading_volume
            else :
                self._1m_bid_vol = self._1m_bid_vol + trading_volume
        else :
            # log.debug(f"[{dt2str(self._1m_last_min_dt)}]{market=},{self._1m_open=},{self._1m_high=},{self._1m_low=},{self._1m_close=},{self._1m_volume=},{self._1m_ask_vol=},{self._1m_bid_vol=}")
            candle_time_dt = self._1m_last_min_dt.replace(second = 0, microsecond = 0)
            #########----------------------------------------------------------------------------------
            with self.lock:
                if pd.Timestamp(dt2str(candle_time_dt)) in self._1m_df.index:
                    self._1m_df = self._1m_df.drop(pd.Timestamp(dt2str(candle_time_dt)))
                current_df = pd.DataFrame({"market":[market], "open": [self._1m_open], "high": [self._1m_high], "low":[self._1m_low], "close": [self._1m_close],
                                                              "vol": [round(self._1m_volume, 8)]}, index = [dt2str(candle_time_dt)])
                current_df.index = pd.to_datetime(current_df.index)
                if len(self._1m_df) == 0:
                    self._1m_df = current_df
                else:
                    self._1m_df = pd.concat([self._1m_df, current_df])
            #########----------------------------------------------------------------------------------
            # print(self._1m_df.tail(5))

            self._1m_last_min_dt = kst_time_dt
            self._1m_open = trading_price
            self._1m_high = trading_price
            self._1m_low = trading_price
            self._1m_close = trading_price
            self._1m_volume = trading_volume

            if ask_bid == "ASK" :
                self._1m_ask_vol = trading_volume
                self._1m_bid_vol = 0
            else :
                self._1m_bid_vol = trading_volume
                self._1m_ask_vol = 0

    def get_cld_dfs(self, desired_kst_time_dt):
        desired_timestamp = pd.Timestamp(desired_kst_time_dt)
        #########----------------------------------------------------------------------------------
        with self.lock :
            if desired_timestamp not in self._1m_df.index:  ## tick업데이트보다 check하는 시점이 빠르면
                # log.debug(f"[2] Add New {self.coin} in checking time because the data have not been updated yet.")
                self._1m_df.loc[desired_timestamp] = {"market"     : self.coin,
                                                      "open"       : self._1m_open,
                                                      "high"       : self._1m_high,
                                                      "low"        : self._1m_low,
                                                      "close"      : self._1m_close,
                                                      "vol"     : round(self._1m_volume, 8)  # , "ask_vol"    : 0, "bid_vol"    : 0
                                                      }
        #########----------------------------------------------------------------------------------
        cdl_dfs = {}
        cdl_dfs[CandleType.MINUTES_1] = self._1m_df
        self.__update_other_candles__(self._1m_df, cdl_dfs)
        self._1m_df = self._1m_df.tail(def_num_cdles)
        return cdl_dfs

    def __update_other_candles__(self, _1m_df, cdl_dfs):

        self._3m_df = self.__resample_and_update__(self._3m_df, _1m_df, cdl_dfs, "3T", "0T", CandleType.MINUTES_3, def_num_cdles)
        self._5m_df = self.__resample_and_update__(self._5m_df, _1m_df, cdl_dfs, "5T", "0T", CandleType.MINUTES_5, def_num_cdles)
        self._15m_df = self.__resample_and_update__(self._15m_df, _1m_df, cdl_dfs, "15T", "0T", CandleType.MINUTES_15, def_num_cdles)
        self._30m_df = self.__resample_and_update__(self._30m_df, _1m_df, cdl_dfs, "30T", "0T", CandleType.MINUTES_30, def_num_cdles)
        self._1h_df = self.__resample_and_update__(self._1h_df, _1m_df, cdl_dfs, "1H", "0T", CandleType.HOUR, def_num_cdles_1h)
        self._4h_df = self.__resample_and_update__(self._4h_df, _1m_df, cdl_dfs, "4H", "1H", CandleType.HOUR4, def_num_cdles)
        self._1d_df = self.__resample_and_update__(self._1d_df, self._1h_df, cdl_dfs, "1D", "9H", CandleType.DAYS, def_num_cdles)

        for tf_idx in range(CandleType.DAYS_0.value, CandleType.DAYS_23.value + 1):
            hour_offset = tf_idx - CandleType.DAYS_0.value
            self._tf_dfs[CandleType(tf_idx)] = self.__resample_with_base__(self._1h_df, "24H", f"{hour_offset}H").tail(def_num_cdles)

        cdl_dfs.update(self._tf_dfs)
        self.print_logs()

    def print_logs(self, force_print=False):

        if WS_PARAMS["common"]["enable_log_1m"] or force_print == True:
            log.debug(f"1m({len(self._1m_df)}):\r\n{self._1m_df.tail(10)}")

        if WS_PARAMS["common"]["enable_log_remainders"] or force_print == True:
            log.debug(f"3m({len(self._3m_df)}):\r\n{self._3m_df.tail(10)}")
            log.debug(f"5m({len(self._5m_df)}):\r\n{self._5m_df.tail(10)}")
            log.debug(f"15m({len(self._15m_df)}):\r\n{self._15m_df.tail(10)}")
            log.debug(f"30m({len(self._30m_df)}):\r\n{self._30m_df.tail(10)}")
            log.debug(f"1h({len(self._1h_df)}):\r\n{self._1h_df.tail(10)}")
            log.debug(f"4h({len(self._4h_df)}):\r\n{self._4h_df.tail(10)}")
            log.debug(f"1d({len(self._1d_df)}):\r\n{self._1d_df.tail(10)}")

            for tf_idx in range(CandleType.DAYS_0.value, CandleType.DAYS_23.value + 1) :
                if tf_idx == CandleType.DAYS_0.value or tf_idx == CandleType.DAYS_23.value:
                    if CandleType(tf_idx) in self._tf_dfs:
                        log.debug(f"1d-tf {CandleType(tf_idx).name}({len(self._tf_dfs[CandleType(tf_idx)])}):{self._tf_dfs[CandleType(tf_idx)].tail(10)}")

    def __resample_and_update__(self, tgt_df, _1m_df, cdl_dfs, rule, offset, cdl_type, num_cdls) :
        temp_df = self.__resample_with_base__(_1m_df, rule, offset)
        tgt_df.loc[temp_df.tail(1).index[0]] = temp_df.iloc[-1].to_dict()
        cdl_dfs[cdl_type] = tgt_df.tail(num_cdls)
        return tgt_df

    def __update_after_resampled__(self, tgt_df, _1m_df):
        recent_1m_df = _1m_df[tgt_df.tail(1).index[0].strftime('%Y-%m-%d %H:%M:%S'):]
        if len(recent_1m_df) > 0:
            tgt_df.loc[recent_1m_df.tail(1).index[0]] = \
                {"market" : self.coin, "open"   : recent_1m_df.head(1)["open"].item(),
                 "high"   : recent_1m_df["high"].max(), "low"    : recent_1m_df["low"].min(),
                 "close"  : recent_1m_df.tail(1)["close"].item(), "vol"    : recent_1m_df["vol"].sum()}

        return tgt_df

    def recover_candles(self, recovered_cdl_dict):
        self._1m_df = recovered_cdl_dict[CandleType.MINUTES_1]
        self._3m_df = recovered_cdl_dict[CandleType.MINUTES_3]
        self._5m_df = recovered_cdl_dict[CandleType.MINUTES_5]
        self._15m_df = recovered_cdl_dict[CandleType.MINUTES_15]
        self._30m_df = recovered_cdl_dict[CandleType.MINUTES_30]
        self._1h_df = recovered_cdl_dict[CandleType.HOUR]
        self._4h_df = recovered_cdl_dict[CandleType.HOUR4]
        self._1d_df = recovered_cdl_dict[CandleType.DAYS]

        self._tf_dfs = {}
        for tf_idx in range(CandleType.DAYS_0.value, CandleType.DAYS_23.value + 1) :
            self._tf_dfs[CandleType(tf_idx)] = recovered_cdl_dict[CandleType(tf_idx)]

        # recent_row = self._1m_df.tail(1)
        # self._1m_open = recent_row["open"]
        # self._1m_high = recent_row["high"]
        # self._1m_low = recent_row["low"]
        # self._1m_close = recent_row["close"]
        # self._1m_volume = recent_row["vol"]
        # self._1m_ask_vol = 0
        # self._1m_bid_vol = 0
        # self._1m_last_min_dt = now_dt()

    def __resample_with_base__(self, df, rule, offset) :
        r_sampled_df = df.resample(rule, origin = "epoch", offset = offset).agg({
            'market' : 'first', 'open'   : 'first',
            'high'   : 'max', 'low'    : 'min',
            'close'  : 'last','vol' : 'sum'
        })
        r_sampled_df["vol"] = r_sampled_df["vol"].round(8)
        return r_sampled_df

    def calibrate_1m_cdl(self, frozen_df):
        log.debug(f"frozen: {frozen_df.tail(5)}, len : {len(frozen_df)}")
        log.debug(f"1m_df : {self._1m_df.tail(5)}, len : {len(self._1d_df)}")
        self._1m_df = self.__join_df__(self._1m_df, frozen_df)
        # log.debug(f"merge done!  : {self._1m_df.tail(20)}")

    def calibrate_remaining_cdls(self, market_frozen_cdl_dfs):
        for cdl in market_frozen_cdl_dfs:
            market_frozen_cdl_df = market_frozen_cdl_dfs[cdl]
            if cdl == CandleType.MINUTES_3:
                self._3m_df = self.__merge_cdl_df__(cdl, self._3m_df, market_frozen_cdl_df, def_num_cdles)
            elif cdl == CandleType.MINUTES_5:
                self._5m_df = self.__merge_cdl_df__(cdl, self._5m_df, market_frozen_cdl_df, def_num_cdles)
            elif cdl == CandleType.MINUTES_15:
                self._15m_df = self.__merge_cdl_df__(cdl, self._15m_df, market_frozen_cdl_df, def_num_cdles)
            elif cdl == CandleType.MINUTES_30:
                self._30m_df = self.__merge_cdl_df__(cdl, self._30m_df, market_frozen_cdl_df, def_num_cdles)
            elif cdl == CandleType.HOUR:
                self._1h_df = self.__merge_cdl_df__(cdl, self._1h_df, market_frozen_cdl_df, def_num_cdles_1h)
            elif cdl == CandleType.HOUR4:
                self._4h_df = self.__merge_cdl_df__(cdl, self._4h_df, market_frozen_cdl_df, def_num_cdles)
            elif cdl == CandleType.DAYS:
                self._1d_df = self.__merge_cdl_df__(cdl, self._1d_df, market_frozen_cdl_df, def_num_cdles)

    def __merge_cdl_df__(self, cdl, df, market_frozen_cdl_df, num_of_cdl):
        len_before = len(df)
        temp_df = self.__join_df__(df, market_frozen_cdl_df)
        temp_df = temp_df.tail(num_of_cdl)
        len_after = len(temp_df)
        log.debug(f"{cdl.name} len: {len_before} -> {len_after}")
        return temp_df
    def __join_df__(self, tgt_df, frozen_df):
        tgt_df = tgt_df[~tgt_df.index.isin(frozen_df.index)]
        return pd.concat([frozen_df, tgt_df])


class UPBIT_Coin1M_OHLCV(AbstractCoin1M_OHLCV):
    def __init__(self, coin):
        super(UPBIT_Coin1M_OHLCV, self).__init__(ExType.upbit, coin)

    def parse_trade_json(self, t_json) -> dict:
        tt_dt = str2dt(f"{t_json['td']}T{t_json['ttm']}")
        tt_dt = pytz.utc.localize(tt_dt)
        kst_time_dt = to_kst_time(tt_dt)  # Convert UST -> KST

        parse_result = {
            "market"        : t_json["cd"],
            "trading_dt" : kst_time_dt,
            "trading_price" : t_json["tp"],
            "trading_volume" : t_json["tv"],
            "ask_bid" : t_json["ab"]
        }
        return parse_result


class BITHUMB_Coin1M_OHLCV(AbstractCoin1M_OHLCV):
    def __init__(self, coin):
        super(BITHUMB_Coin1M_OHLCV, self).__init__(ExType.bithumb, coin)

    def parse_trade_json(self, t_json) -> dict :
        parse_result = {}
        tjson_list = []
        for unit in t_json["content"]["list"]:
            td = unit["contDtm"].split(" ")[0]
            ttm = unit["contDtm"].split(" ")[1].split(".")[0]
            tt_dt = str2dt(f"{td}T{ttm}")
            unit_parse_result = {
                "market"         : bithumb_2_std_mkt_id(unit["symbol"]),
                "trading_dt"     : tt_dt,
                "trading_price"  : float(unit["contPrice"]),
                "trading_volume" : float(unit["contQty"]),
                "ask_bid"        : "ASK" if unit["buySellGb"] == "1" else "BID"
            }
            tjson_list.append(unit_parse_result)
        parse_result["bulk"] = tjson_list

        return parse_result

class BINANCE_Coin1M_OHLCV(AbstractCoin1M_OHLCV):
    def __init__(self, coin):
        super(BINANCE_Coin1M_OHLCV, self).__init__(ExType.binance, coin)

    def parse_trade_json(self, t_json) -> dict :
        """
        {'e': 'trade',
        'E': 1736597159252,    # 이벤트 발생 시간
        's': 'BTCUSDT',        # symbol
        't': 4396931678,       # 고유 ID
        'p': '94564.08000000', # 가격
        'q': '0.00006000',     # 수량
        'T': 1736597159252,    # 체결시간 -> 우리는 이것을 사용
        'm': True,             # True - BID, False - ASK
        'M': True}
        :param t_json:
        :return:
        """

        parse_result = {
            "market"     : t_json["s"],
            "trading_dt" : from_utc_int_timestamp(t_json["T"]),
            "trading_price" : float(t_json["p"]),
            "trading_volume" : float(t_json["q"]),
            "ask_bid" : "BID" if t_json["m"] else "ASK"
        }
        return parse_result


class Coin1MFactory(SingletonInstance):
    def __init__(self):
        pass

    def create_coin1m_ohlcv(self, ex_type, coin):
        conn_class_name = f"{ex_type.name.upper()}_Coin1M_OHLCV"
        kwarg = {"coin" : coin}
        return load_class_from_module(self.__module__, conn_class_name, **kwarg)


class AbstractWSClient(metaclass=ABCMeta):

    def __init__(self, ex_type, coins):
        self.ex_type = ex_type
        self.coins = coins

        self.running = True
        self.flag_quote_fetching = False
        self.coin_1m_cdl_mgrs = {}

        self.uri = WS_PARAMS[self.ex_type]["uri"]

        if len(self.coins) == 0:
            binance_coins = UniversalQuoteConnector.instance().get_available_markets(self.ex_type)
            self.coins = ExFilterFactory.instance().get(self.ex_type).filter_market_ids_after(binance_coins)
            if len(self.coins) > 150:
                log.info(f"The number of coins is {len(self.coins)}, which is too many. Top 150 coins has been selected")
                self.coins = self.coins[:150]

        for coin in self.coins :
            self.coin_1m_cdl_mgrs[coin] = Coin1MFactory.instance().create_coin1m_ohlcv(self.ex_type, coin)

    async def connect(self):

        while self.running :
            try :
                auth_type = WS_PARAMS[self.ex_type]["auth_type"]
                if auth_type is not None:
                    auth_handle = self.handle_authentication()
                else:
                    auth_handle = {}

                async with websockets.connect(self.uri, **auth_handle, ping_interval = 60) as websocket :

                    subscribe_msg = self.generate_subscription_msg(self.coins)  ## override
                    await websocket.send(json.dumps(subscribe_msg))
                    log.debug(f"Connected to {self.ex_type.value.upper()} WebSocket.")

                    while self.running :
                        response = await websocket.recv()
                        trade_json = json.loads(response)
                        if self.is_trade_msg(trade_json) :
                            coin = self.get_coin_name(trade_json)               ## override
                            if coin not in self.coin_1m_cdl_mgrs :
                                self.coin_1m_cdl_mgrs[coin] = Coin1MFactory.instance().create_coin1m_ohlcv(self.ex_type, coin)
                            self.coin_1m_cdl_mgrs[coin].update(trade_json)
                            self.flag_quote_fetching = True

            except (websockets.ConnectionClosed, websockets.InvalidURI, websockets.InvalidHandshake) as e :
                self.flag_quote_fetching = False
                log.debug(f"{self.flag_quote_fetching=} is set to be False, because websocket has been crashed!.")
                log.debug(f"Connection error: {e}. Reconnecting in 5 seconds...")
                # self.recover_runtime_cdl_from_redis()
                await asyncio.sleep(5)
            except Exception as e :
                self.flag_quote_fetching = False
                log.debug(f"{self.flag_quote_fetching=} is set to be False, because websocket has been crashed!.")
                log.debug(f"Etc. Error: {e}. Reconnecting in 5 seconds ...")
                # self.recover_runtime_cdl_from_redis()
                await asyncio.sleep(5)


    @abstractmethod
    def handle_authentication(self) -> dict:
        pass

    @abstractmethod
    def generate_subscription_msg(self, coins) :
        pass

    @abstractmethod
    def get_coin_name(self, trade_json) :
        pass

    def is_trade_msg(self, trade_json):
        return True
    def start(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.connect())

    def stop(self):
        self.running = False

    def get_coin_1m_cdl_mgrs(self) :
        return self.coin_1m_cdl_mgrs


    def calibrates(self, frozen_dfs) :
        for coin in self.coin_1m_cdl_mgrs :
            self.coin_1m_cdl_mgrs[coin].calibrate_1m_cdl(frozen_dfs[coin])


    def calibrate_remaining_cdls(self, market_frozen_cdl_dfs) :
        for coin in self.coin_1m_cdl_mgrs :
            self.coin_1m_cdl_mgrs[coin].calibrate_remaining_cdls(market_frozen_cdl_dfs[coin])

    def recover_runtime_cdl_from_redis(self) :
        """
        [[TODO]]
        :param self:
        :return:
        """
        log.info(f"Start to recover runtime candles from Redis!!")
        quote_redis_ip = global_prop.QUOTE_REDIS_IP_ADDR
        redis_storage = redis.StrictRedis(host = quote_redis_ip, port = global_prop.REDIS_PORT, db = 0)

        ex_type = self.ex_type
        loaded_json = redis_storage.get(f"{ex_type.name}/quote")
        quote = Quote.unmarshal(loaded_json)

        cdl_market_dict = quote.ex_quote[ex_type]
        market_cdl_dict = {}
        for cdl in cdl_market_dict :
            for market in cdl_market_dict[cdl] :
                if market not in market_cdl_dict :
                    market_cdl_dict[market] = {}
                market_cdl_dict[market][cdl] = cdl_market_dict[cdl][market]

        ## Print
        for market in market_cdl_dict :
            self.coin_1m_cdl_mgrs[market].print_logs(True)

        if set(self.coins) == set(market_cdl_dict.keys()) :
            for market in market_cdl_dict :
                self.coin_1m_cdl_mgrs[market].recover_candles(market_cdl_dict[market])
        else :
            print("Error: Requested coins and Redis stored coins are different!")

        ## Print
        for market in market_cdl_dict :
            self.coin_1m_cdl_mgrs[market].print_logs(True)

        log.info(f"Recovering runtime candles done!!")


class UPBIT_WSClient(AbstractWSClient):
    def __init__(self):
        self.ex_type = ExType.upbit
        log.info("Upbit WSClient Initialization")
        self.__load_usr_api_key__0()

        self.usr_id = WS_PARAMS[self.ex_type]["auth_extra"]["usr_id"]
        coins = WS_PARAMS[self.ex_type]["markets"]

        super(UPBIT_WSClient, self).__init__(self.ex_type, coins)
        daily_key_loading_thread = threading.Thread(target = self.__load_usr_api_key__)
        daily_key_loading_thread.start()

    def __load_usr_api_key__(self) :
        while True:
            log.info(f"loading usr_api_key of {self.usr_id} for upbit on the daily basis...")
            self.__load_usr_api_key__0()
            log.info(f"sleeping for a day for next loading usr_api_key...")
            time.sleep(60 * 60 * 24)
            # time.sleep(60)


    def __load_usr_api_key__0(self):
        self.usr_id = WS_PARAMS[self.ex_type]["auth_extra"]["usr_id"]
        am = StrategyStorage.instance().load_usr_api_key(self.usr_id, "upbit")

        self.access_key = am.access_key
        self.secret_key = am.secret_key



    def handle_authentication(self) -> dict:
        token = self.__generate_jwt_token__()
        headers = {
            'Authorization' : f'Bearer {token}'
        }

        kwarg = {
            "extra_headers" : headers
        }
        return kwarg


    def __generate_jwt_token__(self) :
        payload = {
            'access_key' : self.access_key,
            'nonce'      : int(time.time() * 1000)
        }
        token = jwt.encode(payload, self.secret_key, algorithm = 'HS256')
        return token

    def generate_subscription_msg(self, coins) :
        subscribe_msg = [
            {"ticket" : "test"},
            {"type" : "trade", "codes" : coins},
            {"format" : "SIMPLE"}
        ]
        return subscribe_msg

    def get_coin_name(self, trade_json) :
        return trade_json["cd"]


class BITHUMB_WSClient(AbstractWSClient):
    def __init__(self):
        self.ex_type = ExType.bithumb
        log.info("Bithumb WSClient Initialization")
        coins = WS_PARAMS[self.ex_type]["markets"]

        super(BITHUMB_WSClient, self).__init__(self.ex_type, coins)

    def handle_authentication(self) -> dict:
        return None

    def generate_subscription_msg(self, coins) :
        bithumb_mkt_ids = std_2_bithumb_mkt_ids(self.coins)
        subscribe_msg = {
            "type"    : "transaction",
            "symbols" : bithumb_mkt_ids
        }
        return subscribe_msg

    def get_coin_name(self, trade_json) :
        return bithumb_2_std_mkt_id(trade_json["content"]["list"][0]["symbol"])

    def is_trade_msg(self, trade_json):
        return "content" in trade_json


class BINANCE_WSClient(AbstractWSClient):
    def __init__(self):
        self.ex_type = ExType.binance
        self.ssl_path = WS_PARAMS[self.ex_type]["auth_extra"]["ssl_path"]
        coins = WS_PARAMS[self.ex_type]["markets"]
        super(BINANCE_WSClient, self).__init__(self.ex_type, coins)

    def handle_authentication(self) -> dict:
        ssl_context = ssl.create_default_context()
        self_signed_cert = pathlib.Path(__file__).with_name(self.ssl_path)
        ssl_context.load_verify_locations(self_signed_cert)
        kwarg = {
            "ssl": ssl_context
        }
        return kwarg

    def generate_subscription_msg(self, coins) :
        params = []
        eff = ExFilterFactory.instance().get(self.ex_type)
        for coin in coins:
            conv_coin = eff.filter_market_id_before(coin) # USDT-BTC -> BTCUSDT
            params.append(f"{conv_coin.lower()}@trade")

        subscribe_msg = {
            "method": "SUBSCRIBE",
            "params": params,
            "id": 1}
        return subscribe_msg

    def is_trade_msg(self, trade_json):
        return "e" in trade_json


    def get_coin_name(self, trade_json) :
        return binance_2_std_mkt_id(trade_json["s"])


class WebSocketClientFactory(SingletonInstance):
    def __init__(self):
        pass

    def create_client(self, ex_type):
        conn_class_name = f"{ex_type.name.upper()}_WSClient"
        return load_class_from_module(self.__module__, conn_class_name)
