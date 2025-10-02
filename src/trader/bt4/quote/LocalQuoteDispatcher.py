import sys

from bt4 import GlobalProperties
from bt4.core.bt_lt_comm import is_my_tick
from bt4.quote.QuoteConnector import UniversalQuoteConnector
from bt4.quote.QuoteMgr import QuoteStorageMgr
from bt4.utils.python_utils import conv_hr_min_str_time_to_int
from bt4.utils.mylog import init_log
from bt4.Constants import CandleType
from collections import OrderedDict
from bt4.utils.pandas_utils import remove_last_row, remove_first_row, insert_dummy_last_row
from bt4.utils.market_utils import is_update_time_of_candle
from bt4.quote.QuoteSupport import Quote, Tick
import time
import pandas as pd
import copy

pd.options.mode.chained_assignment = None

log = init_log()


class LocalRuntimeCandleMgr:
    def __init__(self, ex_type, markets, cdl_types_needed):
        self.ex_type = ex_type

        self.markets = markets
        self.cdl_types_needed = cdl_types_needed
        self.timeframe_hours = [x for x in range(0, 24)]

        self.quote_storage = QuoteStorageMgr(self.markets, self.cdl_types_needed)

        self.cdl_types_needed, self.enable_timeframe = self.__validate_cdl_types_needed(self.cdl_types_needed)
        self.cdl_runtime_dfs = {}
        for cdl_type in self.cdl_types_needed:
            self.cdl_runtime_dfs[cdl_type] = {}

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

    def load_prev_quotes(self, start_pdt):
        ####################################################################
        ## 1. load the last quotes
        for cdl_type in self.cdl_types_needed :
            self.cdl_runtime_dfs[cdl_type] = copy.deepcopy(self.init_runtime_quote(self.markets, start_pdt, 2000, cdl_type))

    def init_runtime_quote(self, markets, start_pdt, num_caldles, cdl_type):
        return self.quote_storage.load_quote_in_range(self.ex_type, markets, start_pdt, num_caldles, cdl_type)

    def load_1m_quotes(self, start_pdt, end_pdt):
        return self.quote_storage.load_quote_in_range2(self.ex_type, self.markets, start_pdt, end_pdt, CandleType.MINUTES_1)

    def handle_1m_quote(self, _1m_dfs, time_pdt):
        self.update_quotes(time_pdt, _1m_dfs)

        # 2. compute ta indicators
        if self.enable_timeframe :
            _1h_timeframe_quote = self.quote_storage.extract_timeframe_quotes(
                self.ex_type, self.cdl_runtime_dfs[CandleType.HOUR], self.timeframe_hours)

        market_quotes = {'markets' : self.markets}
        market_quotes.update(self.__make_name_dfs_dict__(self.cdl_runtime_dfs))
        if self.enable_timeframe :
            market_quotes.update(self.__make_name_dfs_dict__(_1h_timeframe_quote))
            self.cdl_runtime_dfs.update(_1h_timeframe_quote)
        return self.cdl_runtime_dfs

    def __make_name_dfs_dict__(self, cdl_runtime_dfs) :
        name_dfs_dict = {}
        for cdl_type in cdl_runtime_dfs :
            name_dfs_dict[cdl_type.name] = cdl_runtime_dfs[cdl_type]
        return name_dfs_dict

    def update_quotes(self, time_pdt, _1m_market_df):
        for cdl_type in self.cdl_types_needed:
            runtime_dfs = self.cdl_runtime_dfs[cdl_type]
            if cdl_type != CandleType.MINUTES_1:
                is_update_time = is_update_time_of_candle(cdl_type, time_pdt)
                if is_update_time:
                    self._remove_last_row(runtime_dfs)
                    self._fetch_n_append_quote(runtime_dfs, time_pdt, cdl_type)
                else:
                    self._update_min_quote(runtime_dfs, _1m_market_df)
            else:  ## for 1 Minutes Candles
                self._fetch_n_append_quote(runtime_dfs, time_pdt, cdl_type)

    def replicate_last_n_remove_first_for_new_update(self, dt_korea):
        for cdl_type in self.cdl_types_needed:
            runtime_dfs = self.cdl_runtime_dfs[cdl_type]
            if cdl_type != CandleType.MINUTES_1:
                is_update_time = is_update_time_of_candle(cdl_type, dt_korea)
                if is_update_time:
                    self._insert_dummy_last_row(runtime_dfs)
                    self._remove_first_row(runtime_dfs)

            else:  ## for 1 Minutes Candles
                self._remove_first_row(runtime_dfs)

    def _remove_last_row(self, dfs):
        for market in dfs:
            remove_last_row(dfs[market])

    def _insert_dummy_last_row(self, dfs):
        for market in dfs:
            dfs[market] = insert_dummy_last_row(dfs[market])

    def _remove_first_row(self, dfs):
        for market in dfs:
            remove_first_row(dfs[market])

    def _fetch_n_append_quote(self, runtime_dfs, time_pdt, cdl_type):
        # market_dfs = self.quote_storage.load_quote_in_range(self.ex_type, runtime_dfs.keys(), time_pdt, 1, cdl_type)
        market_dfs = self.quote_storage.load_and_fill_quote_to_end(self.ex_type, runtime_dfs, time_pdt, cdl_type)

        for market in market_dfs:
            df = market_dfs[market]
            if df is not None and len(df) > 0:
                concat_df = pd.concat([runtime_dfs[market], df], axis = 0)

                if cdl_type == CandleType.DAYS:
                    tail_limit = 350
                elif cdl_type == CandleType.MINUTES_1:
                    tail_limit = 8000
                else:
                    tail_limit = 2000

                runtime_dfs[market] = concat_df.tail(tail_limit)
            else:
                runtime_dfs[market] = pd.concat([pd.DataFrame({}, index=['dummy']), runtime_dfs[market]], axis=0)

    def _update_min_quote(self, dfs, _1m_market_df):
        for market in dfs:
            if market in _1m_market_df.market.values.tolist():
                last_row_df = _1m_market_df[_1m_market_df.market == market].iloc[0]
                dfs[market].iloc[-1] = last_row_df

    def build_market_ticks(self, _1m_simul_dfs, time_pdt):
        market_ticks = {}
        _1m_dfs = pd.DataFrame()
        for market in _1m_simul_dfs :
            _1m_market_df = _1m_simul_dfs[market]
            _1m_market_sel_df = _1m_market_df.loc[_1m_market_df.index == time_pdt]
            _1m_dfs = pd.concat([_1m_dfs, _1m_market_sel_df], axis = 0)
            if _1m_market_sel_df is not None and not _1m_market_sel_df.empty :
                data_list = [time_pdt]
                data_list.extend(_1m_market_sel_df.to_numpy()[0])
                tick2 = Tick.from_list(data_list)
                market_ticks[market] = tick2
        return market_ticks, _1m_dfs

class LocalQuoteDispatcher:
    def __init__(self, markets, start_pdt, end_pdt, quote_providers, cdl_types_needed):
        self.start_pdt = start_pdt
        self.end_pdt = end_pdt
        self.quote_providers = quote_providers
        self.cdl_types_needed = cdl_types_needed

        self.quote_listeners = []
        self.local_rt_cdlmgrs = {}
        for ex_type in self.quote_providers:
            self.local_rt_cdlmgrs[ex_type] = LocalRuntimeCandleMgr(ex_type, markets, self.cdl_types_needed)
            self.local_rt_cdlmgrs[ex_type].load_prev_quotes(start_pdt)

    def process_quote(self, tr_times, cdl_type=CandleType.MINUTES_1):

        tr_int_times = conv_hr_min_str_time_to_int(tr_times)
        ####################################################################
        ## 2. load 1min data
        ex_1m_simul_dfs = {}
        time_pdts = None
        for ex_type in self.quote_providers:
            ex_1m_simul_dfs[ex_type] = self.local_rt_cdlmgrs[ex_type].load_1m_quotes(self.start_pdt, self.end_pdt)
            if time_pdts is None:
                for market in ex_1m_simul_dfs[ex_type]:
                    time_pdts = ex_1m_simul_dfs[ex_type][market].index

        bt_exec_start_time = time.time()
        ####################################################################
        for time_pdt in time_pdts:
            if GlobalProperties.bt_emergency_stop:  # When Emergency Stop is enabled.
                log.info(f"Emergency Stop has been enabled! This backtesting will be immediately terminated.")
                break

            if not is_my_tick(time_pdt, cdl_type, tr_times, tr_int_times):
                continue

            ex_market_ticks = {}
            ex_cdl_runtime_dfs = {}
            ex_1m_dfs = {}
            for ex_type in self.quote_providers :
                ex_market_ticks[ex_type], ex_1m_dfs[ex_type] = self.local_rt_cdlmgrs[ex_type].build_market_ticks(ex_1m_simul_dfs[ex_type], time_pdt)
                ex_cdl_runtime_dfs[ex_type] = self.local_rt_cdlmgrs[ex_type].handle_1m_quote(ex_1m_dfs[ex_type], time_pdt)

            # 3. dispatch quote
            self.fire_quote(time_pdt, ex_cdl_runtime_dfs, ex_market_ticks)

            for ex_type in self.quote_providers :
                self.local_rt_cdlmgrs[ex_type].replicate_last_n_remove_first_for_new_update(time_pdt)

        bt_exec_end_time = time.time()
        bt_elapsed_time = bt_exec_end_time - bt_exec_start_time
        log.debug(f'Backtesting Elapsed time:{bt_elapsed_time} sec!')


    # def is_simul_time(self, time_dt, simul_times):
    #     for s_time in simul_times:
    #         if s_time[0] == time_dt.hour and s_time[1] == time_dt.minute:
    #             return True
    #     return False


    def fire_quote(self, time_pdt, ex_cdl_runtime_dfs, ex_market_ticks):
        quote = Quote(time_pdt)
        for ex_type in ex_cdl_runtime_dfs:
            quote.add_quote(ex_type, ex_cdl_runtime_dfs[ex_type], ex_market_ticks[ex_type])

        for listener in self.quote_listeners:
            listener.quote_received(quote)

    def addQuoteListener(self, listener):
        if self.quote_listeners is not None:
            self.quote_listeners.append(listener)