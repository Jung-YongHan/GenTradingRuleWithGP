from bt4.Constants import CandleType
from bt4.quote.QuoteMgr import QuoteStorageMgr
from bt4.utils.mylog import init_log
import sys
import copy
import pandas as pd

log = init_log()
class LocalBulkCandleMgr:
    def __init__(self, ex_type, markets, cdl_types_needed) :
        self.ex_type = ex_type

        self.markets = markets
        self.cdl_types_needed = cdl_types_needed
        self.timeframe_hours = [x for x in range(0, 24)]

        self.quote_storage = QuoteStorageMgr(self.markets, self.cdl_types_needed)

        self.cdl_types_needed, self.enable_timeframe = self.__validate_cdl_types_needed(self.cdl_types_needed)
        self.cdl_dfs = {}
        for cdl_type in self.cdl_types_needed :
            self.cdl_dfs[cdl_type] = {}

    def __validate_cdl_types_needed(self, cdl_types_needed):
        enable_timeframe = False
        if cdl_types_needed is not None:
            if CandleType.DAYS_TF in cdl_types_needed and \
                CandleType.HOUR not in cdl_types_needed:
                    log.error('In order to set CandleType.DAYS_TF into \'CDL_TYPES_NEEDED\' in strategy\'s config, '
                              'CandleType.HOUR should also be set in \'CDL_TYPES_NEEDED\'.')
                    sys.exit(-1)
            if CandleType.DAYS_TF in cdl_types_needed:
                enable_timeframe = True
                cdl_types_needed.remove(CandleType.DAYS_TF)

            return cdl_types_needed, enable_timeframe
        else:
            return [CandleType.DAYS, CandleType.HOUR], enable_timeframe

    def load_bulk_quotes(self, start_pdt, end_pdt):
        for cdl_type in self.cdl_types_needed :
            sstart_pdt = self.quote_storage.get_candle_start_pdt(cdl_type, start_pdt, 2000)
            self.cdl_dfs[cdl_type] = self.quote_storage.load_quote_in_range2(self.ex_type, self.markets, sstart_pdt, end_pdt, cdl_type)

    def get_cdl_types_needed(self):
        return self.cdl_types_needed

class BulkQuoteLoader:

    def __init__(self, markets, start_pdt, end_pdt, quote_providers, cdl_types_needed):
        self.markets =  markets
        self.start_pdt = start_pdt
        self.end_pdt = end_pdt
        self.quote_providers = quote_providers
        self.cdl_types_needed = cdl_types_needed

        self.local_bulk_cdlmgr = {}

        for ex_type in self.quote_providers:
            self.local_bulk_cdlmgr[ex_type] = LocalBulkCandleMgr(ex_type, markets, self.cdl_types_needed)
            self.local_bulk_cdlmgr[ex_type].load_bulk_quotes(start_pdt, end_pdt)

    def get_bulk_cdlmgr(self, ex_type):
        return self.local_bulk_cdlmgr[ex_type]