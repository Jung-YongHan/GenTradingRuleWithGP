import gc
import os
import sys
import threading

import redis

import bt4.GlobalProperties as global_prop
from bt4.Constants import QUOTE_MODE
from bt4.common.AdminCtrlReq import AdminCtrlReq
from bt4.core.bt_lt_comm import filter_out_unused_markets, is_my_tick
from bt4.quote.ExchangeQuoteDispatcher import QuoteReceiver, ExchangeQuoteDispatcher, QuotePullRequestReceiver
from bt4.quote.QuoteListener import QuoteListener, QuotePullRequestListener
from bt4.quote.QuoteSupport import Quote
from bt4.utils.kafka_support import AdminCtrlListener, AdminCtrlMsgReceiver
from bt4.utils.memory_profiler import MemoryProfiler
from bt4.utils.mylog import init_log
from bt4.utils.python_utils import load_class_from_module, conv_hr_min_str_time_to_int, str2dt2

log = init_log()

class StrategyLiveTrader (QuotePullRequestListener, QuoteListener, AdminCtrlListener):

    def __init__(self, usr_id, markets, cdl_type, tr_times, quote_mode=QUOTE_MODE.SELF):
        self.usr_id = usr_id
        self.markets = markets
        self.market_dfs = []
        self.cdl_type = cdl_type
        self.tr_times = tr_times
        self.tr_int_times = conv_hr_min_str_time_to_int(tr_times)

        self.quote_mode = quote_mode
        if self.quote_mode == QUOTE_MODE.REDIS_KAFKA:
            self.quote_pr_receiver = QuotePullRequestReceiver()
            quote_redis_ip = global_prop.QUOTE_REDIS_IP_ADDR
            log.info(f"try to connecting to redis server : {quote_redis_ip}:{global_prop.REDIS_PORT}")
            self.redis = redis.StrictRedis(host = quote_redis_ip, port = global_prop.REDIS_PORT, db = 0)
        elif self.quote_mode == QUOTE_MODE.KAFKA:
            self.quote_receiver = QuoteReceiver()

        ######################################
        ### Memory profiling
        self.mem_profiling = True
        if self.mem_profiling:
            self.mem_profiler = MemoryProfiler()

        # os.environ["MOTOR_MAX_WORKERS"] = "1"

    def start_auto_trading(self, strategy):
        if self.mem_profiling:
            self.mem_profiler.take_1st_snapshot()

        log.info(f'Start Auto Trading in pid({os.getpid()})')
        self.strategy = strategy
        if self.quote_mode == QUOTE_MODE.REDIS_KAFKA:
            self.quote_pr_receiver.add_quote_pull_req_receiver(self)
            self.start_in_thread(self.quote_pr_receiver, 'Quote Pull Request Receiver')
        elif self.quote_mode == QUOTE_MODE.KAFKA:
            self.quote_receiver.add_quote_receiver(self)
            self.start_in_thread(self.quote_receiver, 'Quote Receiver')
        elif self.quote_mode == QUOTE_MODE.SELF:
            self.start_self_mode_auto_trading(strategy)
        else:
            log.error(f"Quote Mode should be one of the followings {QUOTE_MODE.REDIS_KAFKA.value},{QUOTE_MODE.KAFKA.value}, and {QUOTE_MODE.SELF.value}.")
            return

        self.admin_ctrl_rver = AdminCtrlMsgReceiver(global_prop.kafka_channel_admin_control)
        self.admin_ctrl_rver.add_message_listener(self)
        self.admin_ctrl_rver.daemon = True
        self.start_in_thread(self.admin_ctrl_rver, 'Admin Control Msg Receiver')

        if self.quote_mode == QUOTE_MODE.REDIS_KAFKA:
            self.quote_pr_receiver.join()
        elif self.quote_mode == QUOTE_MODE.KAFKA:
            self.quote_receiver.join()

        log.info(f'Main Thread wait.. Joined! This thread and Process will be terminated!')
        if self.mem_profiling :
            self.mem_profiler.take_2nd_snapshot_and_show_topN(20)
            self.mem_profiler.print_mem_usage()

    def start_in_thread(self, receiver, receiver_name):
        receiver.start()
        log.info(f'{receiver_name} Thread has been started!')
        log.info(f'{receiver_name} Thread wait..!')


    ## for bt4 only
    def do_pull_quote(self, ex_type, time_str):
        if ex_type != self.strategy.ex_type:
            log.info(f"Filter out pull request from {ex_type.value}")
            return

        log.info(f"quote pull request for quote of \"{ex_type.name}/{time_str}\"")
        # loaded_json = self.redis.get(f"{ex_type.name}/quote")
        # quote = Quote.unmarshal(loaded_json)
        includes = {}
        includes[ex_type] = list(self.markets)
        time_dt = str2dt2(time_str)

        # Always fetch quote for initial execution of strategy
        if self.strategy.is_init_trading:
            # For general execution, pass fetching quote when it is not my time tick
            #######################################################
            ## For executing without filtering out my ticks, comment the following three lines.
            # if not is_my_tick(time_dt, self.cdl_type, self.tr_times, self.tr_int_times) :
            #     log.info(f"This time tick({time_dt}) is filtered out because {time_dt} is not in trading time list {self.tr_times} or candle type {self.cdl_type.name}.")
            #     return
            pass
        else:
            post_mkt = self.strategy.asset_mgmt.ex_conn.get_post_market()
            if post_mkt not in includes[ex_type] :
                includes[ex_type].append(post_mkt)


        ## Fetch quote from redis and execute strategy
        received_quote = Quote.from_redis(time_dt, self.redis, includes)

        ## execute bt2 and bt4 strategy in the same way
        self.quote_received(received_quote)

        if self.mem_profiling :
            self.mem_profiler.take_2nd_snapshot_and_show_topN(20)
            self.mem_profiler.print_mem_usage()

    ## for bt2 and bt4
    def quote_received(self, quote):
        # quote = filter_out_unused_markets(quote,[self.strategy.ex_type], quote_markets)
        self._do_perform(self.strategy, quote)

        quote.clean_memory()
        gc.collect()

    def _do_perform(self, strategy, quote):
        if quote is not None:
            if not strategy.is_init_trading:
                if strategy.init_trading(quote):
                    strategy.is_init_trading = True
                else:
                    err_msg = 'initialization failure! This live_trading will be terminated!!'
                    log.error(err_msg)
                    raise RuntimeError(err_msg)

            time_dt = quote.get_time()
            ## 1. handle admin control
            if len(strategy.admin_req_list) > 0:
                strategy.process_admin_ctrl(quote)

            ## 2. update balance and market ticks
            # TODO: The following code is for updating balance state for every time tick,
            #  currently, the code has been blocked because the memory issue.
            #  But, if the only tick data in the quote can be fetched from Redis, the code can be unblocked. (STKIM, JOONG-GI) at 2025.07.20
            # strategy.update_trade_n_balance_state(time_dt, quote.get_market_ticks(strategy.ex_type))

            ## 3. call strategy's perform when the candle is in their own period.
            strategy.perform(quote)

            # if is_my_tick(time_dt, self.cdl_type, self.tr_times, self.tr_int_times) :
            #     strategy.perform(quote)
            # else :
            #     log.info(
            #         f"This time tick({time_dt}) is filtered out because {time_dt} is not in trading time list {self.tr_times} or candle type {self.cdl_type.name}.")


        else:
            log.warning('Quote Fetch Failure!: the fetched market data is empty, or the date_time is none.')

    def start_self_mode_auto_trading(self, strategy):
        eqd = ExchangeQuoteDispatcher(QUOTE_MODE.SELF)
        eqd.addQuoteListener(self)
        eqd.process_quote()

    def ctrl_msg_received(self, msg_json):
        log.info(f'StrategyLiveTrader:: admin_control message has been received : {msg_json}')
        if self.usr_id == msg_json[AdminCtrlReq.KEY_USR_ID]:
            admin_req = msg_json['admin_req']
            admin_req_obj = load_class_from_module(AdminCtrlReq.__module__, admin_req)
            admin_req_obj.set_params_with_dict(msg_json)
            self.strategy.post_admin_request(admin_req_obj)