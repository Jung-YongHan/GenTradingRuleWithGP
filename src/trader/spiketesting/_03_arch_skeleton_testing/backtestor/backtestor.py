import datetime
import sys

from bt4.quote.QuoteListener import QuoteListener
from bt4.utils.python_utils import str2dt
from spiketesting._03_arch_skeleton_testing.factory import AbstractFactory, ExecutionMode

from bt4.utils.mylog import init_log

log = init_log()

class BackTestor(QuoteListener):

    def __init__(self, context, markets, start, end, data_type, simul_times, simul_tais):
        self.context = context
        self.markets = markets
        self.market_dfs = []
        self.start_dt = str2dt(start)
        self.end_dt = str2dt(end) if end is not None else datetime.datetime.now()
        self.data_type = data_type
        self.simul_times = simul_times
        self.simul_tais = simul_tais

        ## Original
        # self.local_quote_dispatcher = LocalQuoteDispatcher()
        # self.local_quote_dispatcher.addQuoteListener(self)

        ## Multiprocessor
        exec_mode = self.context.get_attribute("Execution_Mode")
        afactory = AbstractFactory.getFactory(exec_mode)
        self.local_quote_job_distributor = afactory.getQuoteDispatcher()


    def get_target_markets(self):
        return self.markets

    def simulate(self, strategy):
        self.strategy = strategy
        ## Original
        # self.local_quote_dispatcher.process_quote(self.markets,
        #                                                 self.start_dt, self.end_dt, self.simul_times, self.simul_tais, self.data_type)

        self.local_quote_job_distributor.process_local_quote(self.markets,
                                                        self.start_dt, self.end_dt, self.simul_times, self.simul_tais, self.data_type)

    def quote_tai_received(self, time_dt, market_ticks, market_tai):
        self._do_perform(self.strategy, time_dt, market_ticks, market_tai)

    def _do_perform(self, strategy, time_dt, market_ticks, market_tai):
        if bool(market_ticks) and time_dt is not None:
            if not strategy.is_init_trading:
                if strategy.initialize_right_before_trading(time_dt, market_ticks, market_tai):
                    strategy.is_init_trading = True
                else:
                    log.error('initialization failure! This live_trading will be terminated!!')
                    sys.exit(-1)

            strategy.perform(time_dt, market_ticks, market_tai)
        else:
            log.warning('Quote Fetch Failure!: the fetched market data is empty, or the date_time is none.')

