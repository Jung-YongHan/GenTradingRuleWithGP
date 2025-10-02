import datetime

import redis as redis
import threading
import time
import pandas as pd
from kafka import KafkaProducer
from kafka.errors import KafkaTimeoutError

import bt4.GlobalProperties as global_prop
from bt4.Constants import CandleType, ExType
from bt4.quote.QuoteConnector import UniversalQuoteConnector
from bt4.quote.QuoteSupport import Quote, Tick
from bt4.quote.ws_quote_dispatcher_support import WebSocketClientFactory
from bt4.utils.bt4_cli_args import get_websocket_eqd_argument
from bt4.utils.exchange_utils import bithumb_2_uniformed_mkt_ids

from bt4_cfg.websocket_quote_cfg import WS_PARAMS

pd.set_option('display.max_columns', None)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('max_colwidth', None)

from bt4.utils.mylog import init_log
log = init_log()
from bt4.utils.python_utils import now_dt, dt2str, get_1min_before_dt, start_timing, \
    end_n_elapsed_time, dt2str2

def_num_cdles = 300
def_num_cdles_1h = 5000

flag_quote_dispatching = False

def dispatch_task(ws_client) :
    global flag_quote_dispatching

    ## Initialize Kafka
    bootstrap_svr = global_prop.kafka_bootstrap_svr
    producer = KafkaProducer(bootstrap_servers = bootstrap_svr)
    if producer.bootstrap_connected() :
        print(f"Kafka Bootstrap has been connected to {bootstrap_svr}")

    ## Initialize Redis
    quote_redis_ip = global_prop.QUOTE_REDIS_IP_ADDR
    redis_storage = redis.StrictRedis(host = quote_redis_ip, port = global_prop.REDIS_PORT, db = 0)

    while True :

        ## waiting for 2 seconds of each minute
        now = now_dt()
        next_run = now.replace(second = 2, microsecond = 0)

        # If the current time is past the next run time in this minute, schedule for the next minute
        if now >= next_run :
            next_run += datetime.timedelta(minutes = 1)

        sleep_duration = (next_run - now).total_seconds()
        time.sleep(sleep_duration)
        ##
        if not ws_client.flag_quote_fetching:
            log.info(f"[{dt2str(now)}] Waiting for fetching quote from websocket. It will start at the 2nd seconds of the next minute.")
            continue
        ##
        now = now_dt()
        desired_time_dt = get_1min_before_dt(now, True)

        log.debug(f"==" * 100)
        log.debug(f"Processing quote for {desired_time_dt}")
        #############################################################################
        ## 1. Build Quotes
        quote = Quote(desired_time_dt)

        coin_1m_cdl_mgrs = ws_client.get_coin_1m_cdl_mgrs()
        runtime_cdl_dfs = {}
        market_ticks = {}
        for coin in coin_1m_cdl_mgrs:
            coin_1m_cdl = coin_1m_cdl_mgrs[coin]
            market_cdl_dfs = coin_1m_cdl.get_cld_dfs(desired_time_dt)

            for market_cdl in market_cdl_dfs:
                if market_cdl == CandleType.MINUTES_1:
                    recent_tick_list = market_cdl_dfs[market_cdl].iloc[-1].tolist()
                    recent_tick_list = list([float(x) if type(x) != str else x for x in recent_tick_list])
                    recent_tick_list[-1] = round(recent_tick_list[-1], 8)
                    recent_tick_list.insert(0, dt2str2(desired_time_dt))
                    market_ticks[coin] = Tick.from_list(recent_tick_list)

                if market_cdl not in runtime_cdl_dfs:
                    runtime_cdl_dfs[market_cdl] = {}
                runtime_cdl_dfs[market_cdl][coin] = market_cdl_dfs[market_cdl]

        quote.add_quote(ws_client.ex_type, runtime_cdl_dfs, market_ticks)

        #############################################################################
        ## 2. store quote and send request pull through kafka
        # encoded_json = quote.marshal()
        quote_pull_req_channel = global_prop.kafka_channel_quote_pull_request
        log.info(f"STORE QUOTE in Redis at {desired_time_dt}")
        try :
            # 1. update redis for the current quote
            # redis_storage.set(f"{ExType.upbit.name}/quote", encoded_json)
            quote.to_redis()
            # 2. send quote pull request - receive using QuotePullRequestReceiver
            exchange = ws_client.ex_type.name
            time_str = dt2str2(quote.time_dt)
            message = f"{exchange}/{time_str}"
            if flag_quote_dispatching :
                log.info(f"SEND \"{message}\" message through the KAFKA ({quote_pull_req_channel}) channel.")
                producer.send(quote_pull_req_channel, message.encode("utf-8"))
        except KafkaTimeoutError as err :
            log.error(f'KafkaTimeoutError : {err=}')


def calibrate_1m_cdl_task(ws_client):
    markets = ws_client.coins

    __time_all_process = start_timing()

    market_dfs = UniversalQuoteConnector.instance().fetch_quote_num_candles(ws_client.ex_type, markets, def_num_cdles,
                                                                            CandleType.MINUTES_1)

    ws_client.calibrates(market_dfs)
    log.debug(f"all markets: {market_dfs.keys()}")
    print(end_n_elapsed_time(__time_all_process, 'calibrating 1m cdl task'))

def calibrate_remaining_cdls_task(ex_type, ws_client):
    global flag_quote_dispatching
    log.debug(f"#### start complete_remainders")
    __time_all_process = start_timing()
    markets = ws_client.coins
    # candle_types = [CandleType.MINUTES_3, ]

    candle_types = list(set(WS_PARAMS[ex_type]["supported_candles"]) - set([CandleType.MINUTES_1]))

    market_candles = {}
    for cdl_type in candle_types:
        num_cdles = def_num_cdles if cdl_type != CandleType.HOUR else def_num_cdles_1h
        if cdl_type != CandleType.DAYS_TF:

            fetched_dfs = UniversalQuoteConnector.instance().fetch_quote_num_candles(ws_client.ex_type, markets, num_cdles,
                                                                                     cdl_type = cdl_type)
        for market in markets:
            if market not in market_candles:
                market_candles[market] = {}
            market_candles[market][cdl_type] = fetched_dfs[market]
    ws_client.calibrate_remaining_cdls(market_candles)
    log.debug(end_n_elapsed_time(__time_all_process, 'calibrating all remaining cdl task!'))

    log.info("Now Service Ready! Sending Candle Pull Request will start!")
    flag_quote_dispatching = True


def ws_main(args):
    arg_map = get_websocket_eqd_argument()
    ex_type = arg_map["ex_type"]
    ws_client = WebSocketClientFactory.instance().create_client(ex_type)

    # 웹소켓 클라이언트를 위한 스레드 생성
    websocket_thread = threading.Thread(target = ws_client.start)
    websocket_thread.start()

    # 주기적 작업을 위한 스레드 생성
    periodic_dispatch_thread = threading.Thread(target = dispatch_task, args = (ws_client,))
    periodic_dispatch_thread.start()
    log.info("Calibrating 1m candles will start after 120 sec.")
    time.sleep(120)  # After two minutes, it starts calibrating quotes.

    log.info("Calibrating 1m candles start now!")
    calibrate_thread = threading.Thread(target = calibrate_1m_cdl_task, args = (ws_client,))
    calibrate_thread.start()

    log.info("Calibrating remaining candles candles will start after 120 sec.")
    time.sleep(120)  # After two minutes, it starts calibrating remaining candles.

    log.info("Calibrating remaining candles start now!")
    complete_remainders_thread = threading.Thread(target = calibrate_remaining_cdls_task,
                                                  args = (ex_type, ws_client,))
    complete_remainders_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        ws_client.stop()
        websocket_thread.join()
        periodic_dispatch_thread.join()
        calibrate_thread.join()
        complete_remainders_thread.join()
        log.debug("Stopped.")



##########################################################################
if __name__ == '__main__':
    import sys
    ws_main(sys.argv[1 :])