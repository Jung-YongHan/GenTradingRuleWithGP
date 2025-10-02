import sys
import datetime
import pandas as pd

from bt4 import GlobalProperties
from bt4.Constants import R
from bt4.core.BulkQuoteLoader import BulkQuoteLoader
from bt4.core.bt_lt_comm import filter_out_unused_markets
from bt4.quote.QuoteListener import QuoteListener

from bt4.quote.LocalQuoteDispatcher import LocalQuoteDispatcher
from bt4.utils.mylog import init_log

pd.set_option('display.max_columns', None)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('max_colwidth', None)

log = init_log()

r = R()


class Backtestor(QuoteListener):

    def __init__(self, markets, start_str, end_str, candle_type, tr_times, quote_providers, cld_type_needed=None):
        self.markets = markets
        self.market_dfs = []
        self.start_pdt = pd.to_datetime(start_str)
        self.end_pdt = pd.to_datetime(end_str) if end_str is not None else pd.to_datetime(datetime.datetime.now())
        self.quote_providers = quote_providers
        self.candle_type = candle_type
        self.tr_times = tr_times

        ## 1. load all necessary quote with the type of dataframe
        if GlobalProperties.enable_bulk:
            self.bulk_quote_loader = BulkQuoteLoader(self.markets, self.start_pdt, self.end_pdt, self.quote_providers, cld_type_needed)
        else:   ## comment to disable LocalQuoteDispatcher (2024-12-20)
            self.local_quote_dispatcher = LocalQuoteDispatcher(self.markets, self.start_pdt, self.end_pdt, self.quote_providers, cld_type_needed)
            self.local_quote_dispatcher.addQuoteListener(self)

    def start_backtesting(self, strategy):
        self.strategy = strategy

        ## 2. request process bulk_quote
        if GlobalProperties.enable_bulk:
            self.strategy.process_bulk_quote(self.bulk_quote_loader, self.start_pdt, self.end_pdt)
        else:  ## comment to disable LocalQuoteDispatcher (2024-12-20)
            self.local_quote_dispatcher.process_quote(self.tr_times, self.candle_type)

    def quote_received(self, quote):
        quote = filter_out_unused_markets(quote, self.quote_providers, self.markets)
        self._do_perform(self.strategy, quote)

    def _do_perform(self, strategy, quote):

        if quote is not None:
            if not strategy.is_init_trading:
                if strategy.init_trading(quote):
                    strategy.is_init_trading = True
                else:
                    log.error('initialization failure! This live_trading will be terminated!!')
                    sys.exit(-1)

            strategy.perform(quote)
        else:
            log.warning('Quote Fetch Failure!: the fetched market data is empty, or the date_time is none.')

