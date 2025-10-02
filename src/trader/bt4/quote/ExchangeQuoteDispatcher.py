import copy
import datetime
import sys
from datetime import timedelta

import redis
from kafka import KafkaProducer
from kafka.errors import KafkaTimeoutError

from bt4.quote.QuoteConnector import UniversalQuoteConnector
from bt4.quote.QuoteListener import QuotePullRequestListener
from bt4.quote.QuoteSupport import Quote, Tick
from bt4.quote import QuoteListener
from bt4.utils.kafka_support import KafkaHandler
from bt4.utils.python_utils import get_1min_before_dt, get_1min_after_dt, \
    dt2str, create_dt_at, start_timing, end_n_elapsed_time, from_utc_int_timestamp, TIME_FORMAT
from bt4.utils.mylog import init_log
from bt4.utils.pandas_utils import remove_last_row, remove_first_row, append_new_row, insert_dummy_last_row
from bt4.utils.market_utils import is_update_time_of_candle
import bt4.GlobalProperties as global_prop
from bt4.Constants import QUOTE_MODE, CandleType, QItem, ExType
import time
import pandas as pd

from bt4_cfg.quote_conf import QUOTE_PARAMS
log = init_log()


class ExchangeQuoteDispatcher:
    def __init__(self, quote_mode):
        self.quote_mode = quote_mode
        self.initialize()

    def initialize(self):
        self.exchanges = QUOTE_PARAMS['exchanges']
        self.uq_connector = UniversalQuoteConnector.instance()
        self.time_ex = self.exchanges[len(self.exchanges)-1]
        self.def_num_cdles = 300

        self.runtime_cdlmgrs = {}
        __start_up_quote_loading_time = start_timing()
        for exchange in self.exchanges:
            self.runtime_cdlmgrs[exchange] = RuntimeCandleMgr(exchange, self.uq_connector, self.def_num_cdles)
        log.debug(end_n_elapsed_time(__start_up_quote_loading_time, '0-Loading Previous Quotes'))

        if self.quote_mode == QUOTE_MODE.REDIS_KAFKA:
            ## initialize kafka
            bootstrap_svr = global_prop.kafka_bootstrap_svr
            self.producer = KafkaProducer(bootstrap_servers=bootstrap_svr)
            if self.producer.bootstrap_connected():
                print('Kafka Bootstrap has been connected to {bootstrap_svr}')
            ## initialize redis
            quote_redis_ip = global_prop.QUOTE_REDIS_IP_ADDR
            self.rds = redis.StrictRedis(host = quote_redis_ip, port = global_prop.REDIS_PORT, db = 0)
        elif self.quote_mode == QUOTE_MODE.KAFKA:
            bootstrap_svr = global_prop.kafka_bootstrap_svr
            self.producer = KafkaProducer(bootstrap_servers=bootstrap_svr)
            if self.producer.bootstrap_connected():
                print('Kafka Bootstrap has been connected to {bootstrap_svr}')
        elif self.quote_mode == QUOTE_MODE.SELF:
            self.quote_listeners = []
        else:
            log.error(f"This quote mode {self.quote_mode} does not support! "
                      f"Set the quote mode among the {QUOTE_MODE.REDIS_KAFKA.value}, {QUOTE_MODE.KAFKA.value},"
                      f"{QUOTE_MODE.SELF}.")
            return

    def process_quote(self) :
        last_svr_time_tp = self.uq_connector.fetch_time(self.time_ex)
        if last_svr_time_tp is not None :
            svr_korea_dt = from_utc_int_timestamp(last_svr_time_tp, True)
        else :
            svr_korea_dt = datetime.datetime.now().astimezone()

        while True :
            __time_all_process = start_timing()
            # 1. fetch server time
            print(f'server_time: {svr_korea_dt}')
            desired_dt = get_1min_before_dt(svr_korea_dt, True)
            __time_fetching = start_timing()
            last_svr_time_tp = self.uq_connector.fetch_time(self.time_ex)

            # 2. load 1minute quote from all exchanges
            # TODO: Need to change asyncio (stkim)
            ex_1m_quote_dfs = {}
            for exchange in self.exchanges:
                _1m_quote_dfs = self.runtime_cdlmgrs[exchange].fetch_quote_at(desired_dt)
                ex_1m_quote_dfs[exchange] = _1m_quote_dfs

            if last_svr_time_tp is not None :
                svr_korea_dt = from_utc_int_timestamp(last_svr_time_tp, True)
                now_dt = datetime.datetime.now().astimezone()
                log.debug(end_n_elapsed_time(__time_fetching, '1-Fetching Quote'))
                log.debug(f'# Fetched server time:{dt2str(svr_korea_dt)}, @local time({dt2str(now_dt)})')

                # 3. update runtime dfs and make market ticks for each exchange
                __time_update_1m = start_timing()
                ex_runtime_dfs = {}
                ex_market_ticks = {}
                for exchange in ex_1m_quote_dfs:
                    _1m_quote_dfs = ex_1m_quote_dfs[exchange]
                    if _1m_quote_dfs is not None:
                        runtime_dfs = self.runtime_cdlmgrs[exchange].handle_1m_quote(_1m_quote_dfs, desired_dt)
                        ex_runtime_dfs[exchange] = runtime_dfs

                        market_ticks = self.runtime_cdlmgrs[exchange].build_market_ticks_from_df(_1m_quote_dfs)
                        ex_market_ticks[exchange] = market_ticks
                    else:
                        log.error(f'Fetched 1 Minute Data of {exchange} is None!!!!!!!')
                        log.debug(f'# Fetched server time:{dt2str(svr_korea_dt)}, @local time({dt2str(now_dt)})')
                log.debug(end_n_elapsed_time(__time_update_1m, '2-Updating 1M Quote for 1D, 4H, 1H, H0..23'))
                ##########################################################################
                # 3. dispatch quote
                __time_sending_kafka = start_timing()
                self.dispatch_quote(desired_dt, ex_runtime_dfs, ex_market_ticks)
                log.debug(end_n_elapsed_time(__time_sending_kafka, '3-Sending Quote Through Kafka'))

                # 4. append new quote after new quote has been added for next quote update
                for exchange in ex_1m_quote_dfs :
                    self.runtime_cdlmgrs[exchange].replicate_last_n_remove_first_for_new_update(desired_dt)

                log.debug(end_n_elapsed_time(__time_all_process, '4-All Fetching Process'))

                now_dt = datetime.datetime.now()
                log.debug(f'Time Gap : Local Now: {dt2str(now_dt)} , svr_time: {dt2str(svr_korea_dt)}')
                if (now_dt - svr_korea_dt).total_seconds() > 5 :  # When the gap btw svr time and local time is grater than 5 sec,
                    svr_korea_dt = now_dt  # replace the svr time into local now
                    svr_sec = svr_korea_dt.second
                    log.debug(
                        f'SVR time({dt2str(svr_korea_dt)}) is replaced with local now({dt2str(now_dt)}), due to tie time gap.')
                else :
                    svr_sec = svr_korea_dt.second

                sleep_time = 62.0 - svr_sec
                log.info(
                    f'sleep for {sleep_time} sec. to fetch quote and dispatch it to strategies. svrtime:{dt2str(svr_korea_dt)}.')
                if sleep_time < 0 :
                    sleep_time = 1
                time.sleep(sleep_time)

                svr_korea_dt = get_1min_after_dt(svr_korea_dt)
            else :
                svr_korea_dt = get_1min_after_dt(datetime.datetime.now().astimezone())
                log.debug(f'sleep for 60 sec. due to Server Time is None!')
                time.sleep(60)


    def dispatch_quote(self, time_dt, ex_runtime_dfs, ex_market_ticks) :
        ex_runtime_dfs = self.__filter_out_hourly_runtime_dfs__(ex_runtime_dfs)

        quote = Quote(time_dt)
        for exchange in ex_runtime_dfs:
            quote.add_quote(exchange, ex_runtime_dfs[exchange], ex_market_ticks[exchange])

        encoded_json = quote.marshal()

        if self.quote_mode == QUOTE_MODE.REDIS_KAFKA :
            bootstrap_svr = global_prop.kafka_bootstrap_svr
            quote_pull_req_channel = global_prop.kafka_channel_quote_pull_request
            log.debug(f"STORE QUOTE(Redis, size) : {sys.getsizeof(encoded_json)}")
            log.debug(f'SEND KAFKA ({quote_pull_req_channel}) in ({bootstrap_svr})')
            try :
                # 1. update redis for the current quote
                # TODO: stkim: 2024-07-18 it's now only for upbit.
                exchange = ExType.upbit.name
                self.rds.set(f"{exchange}/quote", encoded_json)
                # 2. send quote pull request - receive using QuotePullRequestReceiver
                time_str = dt2str(quote.time_dt)
                message = f"{exchange}/{time_str}"
                self.producer.send(quote_pull_req_channel, message.encode("utf-8"))
            except KafkaTimeoutError as err :
                log.error(f'KafkaTimeoutError : {err=}')

        elif self.quote_mode == QUOTE_MODE.KAFKA :
            bootstrap_svr = global_prop.kafka_bootstrap_svr
            channel = global_prop.kafka_channel_quote
            log.debug(f'SEND KAFKA ({channel}) in ({bootstrap_svr})')
            try :
                print(f'size : {sys.getsizeof(encoded_json)}')
                # send quote -  - receive using QuoteReceiver
                self.producer.send(channel, encoded_json)
            except KafkaTimeoutError as err :
                log.error(f'KafkaTimeoutError : {err=}')

        elif self.quote_mode == QUOTE_MODE.SELF :
            process_quotes(encoded_json, self.quote_listeners)

    def addQuoteListener(self, listener: QuoteListener):
        if self.quote_listeners is not None:
            self.quote_listeners.append(listener)

    def __filter_out_hourly_runtime_dfs__(self, ex_runtime_dfs) :
        copied_ex_runtime_dfs = copy.deepcopy(ex_runtime_dfs)

        for exchange in copied_ex_runtime_dfs :
            cp_ex_runtime_dfs = copied_ex_runtime_dfs[exchange]
            hour_cp_ex_runtime_dfs = cp_ex_runtime_dfs[CandleType.HOUR]
            for market in hour_cp_ex_runtime_dfs :
                hour_cp_ex_runtime_dfs[market] = hour_cp_ex_runtime_dfs[market].tail(self.def_num_cdles)

        return copied_ex_runtime_dfs


class RuntimeCandleMgr:
    def __init__(self, exchange, uq_connector, def_num_cdles):
        self.exchange = exchange
        self.uq_connector = uq_connector
        self.def_num_cdles = def_num_cdles

        uqc = UniversalQuoteConnector()
        self.markets = QUOTE_PARAMS[self.exchange]['markets'] if len(QUOTE_PARAMS[self.exchange]['markets']) != 0\
            else uqc.get_available_markets(self.exchange)
        self.cdl_types_needed = QUOTE_PARAMS[self.exchange]['cdl_types_needed'] if len(QUOTE_PARAMS[self.exchange]['cdl_types_needed']) != 0 \
            else [CandleType.MINUTES_1, CandleType.MINUTES_3, CandleType.MINUTES_5, CandleType.MINUTES_15, CandleType.MINUTES_30, CandleType.HOUR, CandleType.HOUR4, CandleType.DAYS_TF, CandleType.DAYS]

        self.cdl_runtime_dfs = {}
        for cdl_type in self.cdl_types_needed:
            self.cdl_runtime_dfs[cdl_type] = {}

        self.timeframe_hours = [x for x in range(0,24)]
        self.load_past_quote()

    def fetch_quote_at(self, desired_dt):
        return self.uq_connector.fetch_quote_at(self.exchange, self.markets, desired_dt)

    def load_past_quote(self):
        now_dt = datetime.datetime.now()

        for cdl_type in self.cdl_types_needed:
            if cdl_type == CandleType.DAYS_TF:
                continue

            num_of_cdls = self.def_num_cdles
            if cdl_type == CandleType.HOUR:
                num_of_cdls = 5000

            fetched_dfs = self.uq_connector.fetch_quote_num_candles(self.exchange, self.markets, num_of_cdls, cdl_type=cdl_type)

            self.cdl_runtime_dfs[cdl_type] = fetched_dfs

            if cdl_type != CandleType.MINUTES_1:
                is_update_time = is_update_time_of_candle(cdl_type, now_dt)
                if not is_update_time:
                    self.__insert_dummy_last_row(fetched_dfs)


    def __insert_dummy_last_row(self, dfs):
        for market in dfs:
            dfs[market] = insert_dummy_last_row(dfs[market])

    def print_dfs(self, dfs_name, dfs):
        # log.debug(f'###################### {dfs_name}')
        print(f'[[{self.exchange}]] ###################### {dfs_name}')
        for market in dfs:
            # log.debug(f'### {market=} ')
            # log.debug(dfs[market][['candle_date_time_kst', 'opening_price', 'trade_price']].tail(5))
            print(f'[[{self.exchange}]] ### {market=} ')
            print(dfs[market].tail(5))

    def handle_1m_quote(self, _1m_quote_dfs, desired_dt):
        log.debug(_1m_quote_dfs.head(10))

        self.__fetch_n_update_append_quotes(_1m_quote_dfs, desired_dt)

        # 2. compute ta indicators
        _1h_timeframe_quote = self.uq_connector.extract_timeframe_quotes(self.exchange,
                                                                         self.cdl_runtime_dfs[
                                                                             CandleType.HOUR],
                                                                         self.timeframe_hours)

        market_quotes = {'markets' : self.markets}
        market_quotes.update(self.__make_name_dfs_dict__(self.cdl_runtime_dfs))
        market_quotes.update(self.__make_name_dfs_dict__(_1h_timeframe_quote))
        self.cdl_runtime_dfs.update(_1h_timeframe_quote)

        #### Print
        # for cdl_type in self.cdl_runtime_dfs :
        #     self.print_dfs(cdl_type.name, self.cdl_runtime_dfs[cdl_type])

        return self.cdl_runtime_dfs

    def __make_name_dfs_dict__(self, cdl_runtime_dfs):
        name_dfs_dict = {}
        for cdl_type in cdl_runtime_dfs:
            name_dfs_dict[cdl_type.name] = cdl_runtime_dfs[cdl_type]
        return name_dfs_dict

    def __fetch_n_update_append_quotes(self, _1m_quote_dfs, desired_dt):
        for cdl_type in self.cdl_types_needed:
            runtime_dfs = self.cdl_runtime_dfs[cdl_type]
            if cdl_type != CandleType.MINUTES_1:
                is_update_time = is_update_time_of_candle(cdl_type, desired_dt)
                if is_update_time:
                    self.__remove_last_row(runtime_dfs)
                    self.__fetch_n_append_quote(runtime_dfs, desired_dt, cdl_type)
                else:
                    self.__update_min_quote(runtime_dfs, _1m_quote_dfs)
            else:  ## for 1 Minutes Candles
                self.__fetch_n_append_quote(runtime_dfs, desired_dt, cdl_type)

    def __remove_last_row(self, dfs):
        for market in dfs:
            remove_last_row(dfs[market])

    def __fetch_n_append_quote(self, dfs, desired_dt, cdl_type=CandleType.DAYS):
        prev_candle_dt = self.compute_prev_candle_dt(desired_dt, cdl_type)

        for market in dfs:
            df = self.uq_connector.fetch_tick_quote(self.exchange, market, 2, cdl_type=cdl_type)

            if df is not None and len(df) >= 1:
                df_for_time = df[df.index == pd.to_datetime(prev_candle_dt)]
                if len(df_for_time) > 0:
                    dfs[market] = append_new_row(dfs[market], df_for_time.iloc[0], False)
            else:
                log.error(f'Fetching {market} {cdl_type} error')

    def __update_min_quote(self, runtime_dfs, _1m_quote_dfs):
        for market in runtime_dfs:
            if _1m_quote_dfs[QItem.market.value].isin([market]).any():
                _1m_market_df = _1m_quote_dfs[_1m_quote_dfs.market == market]
                remove_last_row(runtime_dfs[market])
                last_row_df = _1m_market_df[_1m_market_df.index == _1m_market_df.index.max()]
                runtime_dfs[market] = pd.concat([runtime_dfs[market], last_row_df], axis=0)
            else:
                log.warning(f'WARNING: {market} data is missing in _1m_quote_dfs.')

    def compute_prev_candle_dt(self, desired_dt, data_type):
        if data_type == CandleType.DAYS:
            p_cdl_end_dt = create_dt_at(desired_dt.year, desired_dt.month, desired_dt.day, 8, 59, 0)
            if desired_dt >= p_cdl_end_dt:
                p_cdl_dt = desired_dt - timedelta(days=1)
            else:
                p_cdl_dt = desired_dt - timedelta(days=2)
            return create_dt_at(p_cdl_dt.year, p_cdl_dt.month, p_cdl_dt.day, 9, 0, 0)

        elif data_type == CandleType.HOUR4:
            p_cdl_start_dt = create_dt_at(desired_dt.year, desired_dt.month, desired_dt.day, 0, 59, 0)
            p_cdl_end_dt = create_dt_at(desired_dt.year, desired_dt.month, desired_dt.day, 4, 58, 0)
            midnight_dt = create_dt_at(desired_dt.year, desired_dt.month, desired_dt.day, 0, 0, 0)
            if desired_dt >= p_cdl_start_dt and desired_dt <= p_cdl_end_dt:  # if current time is 0:59~4:58, then prev day: 21:00:00
                p_cdl_day = desired_dt - timedelta(days=1)
                return create_dt_at(p_cdl_day.year, p_cdl_day.month, p_cdl_day.day, 21, 0, 0)
            elif desired_dt >= midnight_dt and desired_dt < p_cdl_start_dt:  # if current time is 00:00~00:58, then prev day: 21:00:00
                p_cdl_day = desired_dt - timedelta(days=1)
                return create_dt_at(p_cdl_day.year, p_cdl_day.month, p_cdl_day.day, 17, 0, 0)
            else:
                p_cdl_day = desired_dt + timedelta(minutes=1)
                hour = 4 * (((p_cdl_day.hour - 1) // 4) - 1) + 1
                return create_dt_at(p_cdl_day.year, p_cdl_day.month, p_cdl_day.day, hour, 0, 0)

        if data_type == CandleType.HOUR:
            p_cdl_dt = desired_dt + timedelta(minutes=1) - timedelta(hours=1)
            return create_dt_at(p_cdl_dt.year, p_cdl_dt.month, p_cdl_dt.day, p_cdl_dt.hour, 0, 0)
        elif data_type == CandleType.MINUTES_30:
            p_cdl_dt = desired_dt + timedelta(minutes=1) - timedelta(minutes=30)
            return create_dt_at(p_cdl_dt.year, p_cdl_dt.month, p_cdl_dt.day, p_cdl_dt.hour, p_cdl_dt.minute, 0)
        elif data_type == CandleType.MINUTES_15:
            p_cdl_dt = desired_dt + timedelta(minutes=1) - timedelta(minutes=15)
            return create_dt_at(p_cdl_dt.year, p_cdl_dt.month, p_cdl_dt.day, p_cdl_dt.hour, p_cdl_dt.minute, 0)
        elif data_type == CandleType.MINUTES_10:
            p_cdl_dt = desired_dt + timedelta(minutes=1) - timedelta(minutes=10)
            return create_dt_at(p_cdl_dt.year, p_cdl_dt.month, p_cdl_dt.day, p_cdl_dt.hour, p_cdl_dt.minute, 0)
        elif data_type == CandleType.MINUTES_5:
            p_cdl_dt = desired_dt + timedelta(minutes=1) - timedelta(minutes=5)
            return create_dt_at(p_cdl_dt.year, p_cdl_dt.month, p_cdl_dt.day, p_cdl_dt.hour, p_cdl_dt.minute, 0)
        elif data_type == CandleType.MINUTES_3:
            p_cdl_dt = desired_dt + timedelta(minutes=1) - timedelta(minutes=3)
            return create_dt_at(p_cdl_dt.year, p_cdl_dt.month, p_cdl_dt.day, p_cdl_dt.hour, p_cdl_dt.minute, 0)
        elif data_type == CandleType.MINUTES_1:
            return desired_dt

    def replicate_last_n_remove_first_for_new_update(self, desired_dt):
        self.__replicate_last_n_remove_first_for_new_update(desired_dt)

    def __replicate_last_n_remove_first_for_new_update(self, dt_korea):
        for cdl_type in self.cdl_types_needed:
            runtime_dfs = self.cdl_runtime_dfs[cdl_type]
            if cdl_type != CandleType.MINUTES_1:
                is_update_time = is_update_time_of_candle(cdl_type, dt_korea)
                if is_update_time:
                    # self.__replicate_last_row(runtime_dfs)
                    self.__insert_dummy_last_row(runtime_dfs)
                    self.__remove_first_row(runtime_dfs)
            else:  ## for 1 Minutes Candles
                self.__remove_first_row(runtime_dfs)

    def __remove_first_row(self, dfs):
        for market in dfs:
            remove_first_row(dfs[market])

    def build_market_ticks_from_df(self, _1m_quote_dfs):
        market_ticks = {}
        if _1m_quote_dfs is not None :
            for market in _1m_quote_dfs['market'].unique() :
                market_df = _1m_quote_dfs[_1m_quote_dfs['market'] == market]
                data_list = [market_df.index[0].to_pydatetime().strftime(TIME_FORMAT)]
                data_list.extend(market_df.to_numpy()[0])
                tick2 = Tick.from_list(data_list)
                market_ticks[market] = tick2
        return market_ticks


class QuoteReceiver(KafkaHandler):
    def __init__(self):
        super(QuoteReceiver, self).__init__(global_prop.kafka_channel_quote)
        self.q_receivers = []

    def add_quote_receiver(self, receiver):
        self.q_receivers.append(receiver)

    def process_message(self, message):
        # if message.topic == global_prop.kafka_channel_quote:
        process_quotes(message, self.q_receivers)


def process_quotes(encoded_message, q_receivers):

    if encoded_message is not None:
        quote = Quote.unmarshal(encoded_message)
        for q_receiver in q_receivers:
            # q_receiver.quote_tai_received(time_dt, selected_ticks, selected_market_tais)
            q_receiver.quote_received(quote)
    else:
        log.error('KAFKA ERROR: No Delivered JSON MESSAGE!!')


class QuotePullRequestReceiver(KafkaHandler):
    def __init__(self):
        super(QuotePullRequestReceiver, self).__init__(global_prop.kafka_channel_quote_pull_request)
        self.quote_pull_req_receivers = []

    def add_quote_pull_req_receiver(self, qpr_receiver:QuotePullRequestListener):
        self.quote_pull_req_receivers.append(qpr_receiver)

    def process_message(self, message):
        msg = message.decode('utf-8')
        ex_type = ExType(msg.split("/")[0])
        time_str = msg.split("/")[1]

        log.debug(f"quote pull request(exchange, time):{ex_type}, {time_str}")
        for qpr_receiver in self.quote_pull_req_receivers:
            qpr_receiver.do_pull_quote(ex_type, time_str)


