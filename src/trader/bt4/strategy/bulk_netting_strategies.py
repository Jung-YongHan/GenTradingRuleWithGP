from datetime import timedelta
from os.path import join, dirname

from bt4.Constants import CandleType, QItem
from bt4.strategy.Strategy import AbstractNettingStrategy
from bt4.strategy.bulk_support import ProgressMgr, build_desc
from bt4.utils.python_utils import split_hour_min
import pandas as pd
import numpy as np
from bt4.quote.QuoteSupport import Tick
import talib
import os
from bt4.utils.mylog import init_log
from bt4.utils.stopwatch import StopWatch

log = init_log()


class AbstractBulkNettingStrategy(AbstractNettingStrategy):

    def process_bulk_quote(self, bulk_quote_loader, start_pdt, end_pdt):

        ## tr_sum_id exists in PostgreSQL Report Storage
        tr_sum_id = self.report.result_storage.tr_sum_id

        sw_total = StopWatch()
        sw_total.start()

        sw = StopWatch()
        sw.start()

        cld_mgr = bulk_quote_loader.get_bulk_cdlmgr(self.ex_type)

        ## 0. Config (Strategy dependent)
        self.set_time_variables()

        ## 0.1 Candle Type (Common)
        bt_cdl_type = self.context.backtestor.candle_type
        base_cdl_dfs = cld_mgr.cdl_dfs[bt_cdl_type]
        var_cdl_types = self.get_var_candle_types()
        if CandleType.DAYS not in var_cdl_types:
            var_cdl_types.append(CandleType.DAYS)
        if CandleType.MINUTES_1 not in var_cdl_types:
            var_cdl_types.append(CandleType.MINUTES_1)

        if bt_cdl_type not in var_cdl_types:
            var_cdl_types.append(bt_cdl_type)
        var_cdl_dfs = {}
        for market in base_cdl_dfs:
            var_cdl_dfs[market] = {}
            for var_cdl_type in var_cdl_types:
                var_cdl_dfs[market][var_cdl_type] = cld_mgr.cdl_dfs[var_cdl_type][market]

        ## Constants : Candle 중심으로 하루의 종가인 오전 9시 Close를 받아들이는 Candle시점이 다름
        self.close_hour, self.close_minute = self.__compute_close_time__(9, bt_cdl_type)

        elapsed_time = sw.stop()
        log.info(f"Stopwatch: Preparing Dataframe => {elapsed_time}")
        sw.start()

        mkt_total_row = super(AbstractBulkNettingStrategy, self).__get_total_tai_row_in_bulk__(base_cdl_dfs)
        pm = ProgressMgr(tr_sum_id, mkt_total_row, base_cdl_dfs.keys())

        elapsed_time = sw_total.stop()
        pm.update_preparation_progress(elapsed_time)

        ## 2. make variables for each market
        result_df = pd.DataFrame()

        for market in base_cdl_dfs:
            market_df = base_cdl_dfs[market]

            ## 2.-1 Filtering only for 8 hour (Strategy dependent)
            filter_out_hour_min = self.get_filter_hour_min_in_base_cdl(market_df)
            if filter_out_hour_min is not None:
                market_df = market_df.loc[filter_out_hour_min]

            total_row = len(market_df)
            if total_row < 6:
                log.error(f"ERROR: Number of Candle data({total_row}) of {market} is lower than 6. Backtesting has been stopped."
                          f"Check the Backtesting Period.")
                return
            log.info(f"Stopwatch: Computing TAI - Market: {market} Total : {total_row} rows")
            sw.start()

            ## 2.0 make_variables
            def compute_tais(row):
                nonlocal var_cdl_dfs
                nonlocal bt_cdl_type
                nonlocal sw, elapsed_time_from_beginning

                var_mkt_cdl_dfs = {}
                for mkt_cdl in var_cdl_dfs[market]:
                    if CandleType(mkt_cdl).value > bt_cdl_type.value:
                        recent_mkt_cdl_time = row.name - pd.Timedelta(minutes = mkt_cdl)
                        var_mkt_cdl_dfs[mkt_cdl] = var_cdl_dfs[market][mkt_cdl][:recent_mkt_cdl_time]

                        self.__fill_remaining_mkt_cdl_till__(market, var_mkt_cdl_dfs, var_cdl_dfs[market], mkt_cdl, bt_cdl_type, row.name)
                    else:
                        recent_mkt_cdl_time = row.name + pd.Timedelta(minutes = bt_cdl_type.value - 1 )
                        var_mkt_cdl_dfs[mkt_cdl] = var_cdl_dfs[market][mkt_cdl][:recent_mkt_cdl_time]

                vol_df = var_mkt_cdl_dfs[CandleType.DAYS]

                ## compute vol5
                vol5 = 0
                if len(vol_df) > 6:
                    vol_df["yes_high"] = vol_df["high"].shift(1)
                    vol_df["yes_low"] = vol_df["low"].shift(1)
                    vol_df["volatility"] = (vol_df["yes_high"] - vol_df["yes_low"]) / vol_df["open"]
                    vol5 = talib.SMA(vol_df["volatility"], timeperiod = 5).iloc[-1]
                else:
                    vol5 = 0

                ## compute TAIs
                if len(var_mkt_cdl_dfs[bt_cdl_type]) > 6:
                    returns = self.calculate_tai(var_mkt_cdl_dfs)
                else:
                    returns = tuple([0]*len(self.get_tai_names()))
                ret_list = list(returns)
                ret_list.append(vol5)

                elapsed_time = sw.stop()
                elapsed_time_from_beginning = sw_total.stop()
                pm.update_tai_calculation_progress(market, elapsed_time_from_beginning, elapsed_time_from_beginning)
                sw.start()

                return tuple(ret_list)

            tai_names = self.get_tai_names()
            tai_names.append("vol5")
            market_df[tai_names] = market_df.apply(compute_tais, axis=1, result_type='expand')

            ## 2.1 extract dataframe ranging from start_pdt to end_pdt
            ## rename columns (Fixed)
            old_new_col_name_dic = {}
            for col in market_df.columns :
                old_new_col_name_dic[col] = f"{market}_{col}"
            market_df.rename(columns = old_new_col_name_dic, inplace = True)

            market_df = market_df[start_pdt:end_pdt]
            result_df = pd.concat([result_df, market_df], axis=1)

        for market in base_cdl_dfs :
            ########### buy
            buy_system = self.get_buy_system(result_df, market)
            result_df[f"{market}_buy_system"] = None
            result_df[f"{market}_buy_system"] = result_df[f"{market}_buy_system"].astype(bool)
            result_df.loc[(buy_system == True), f"{market}_buy_system"] = True
            result_df.loc[~(buy_system == True), f"{market}_buy_system"] = False

            result_df.loc[(result_df[f"{market}_buy_system"] == True), f"{market}_order"] = "BUY"

            ########### sell
            sell_system = self.get_sell_system(result_df, market)
            result_df[f"{market}_sell_system"] = None
            result_df[f"{market}_sell_system"] = result_df[f"{market}_sell_system"].astype(bool)
            result_df.loc[(sell_system == True), f"{market}_sell_system"] = True
            result_df.loc[~(sell_system == True), f"{market}_sell_system"] = False
            result_df.loc[(result_df[f"{market}_buy_system"] == False) & (result_df[f"{market}_sell_system"] == True) , f"{market}_order"] = "SELL"
            # result_df = pd.concat([result_df, market_df], axis = 1)

            log.info(f"Stopwatch: Computing TAI - Market: {market} Total : {total_row} rows Done. =>  {sw.stop()}")
            sw.start()

        # result_df.replace('nan', np.nan, inplace = True)
        # result_df.ffill(inplace = True)

        root_dir = dirname(dirname(dirname(__file__)))
        file_name = join(root_dir, f"log/{os.getpid()}.csv")
        result_df.to_csv(file_name)

        elapsed_time = sw.stop()
        log.info(f"Stopwatch: Write Intermediate Result in Log =>  {elapsed_time}")
        elapsed_time_from_beginning = sw_total.stop()
        pm.update_before_settle_progress(elapsed_time, elapsed_time_from_beginning)
        sw.start()

        is_initialized = False
        ## 3. compute asset management
        def process_statistics(row, markets):
            nonlocal is_initialized
            nonlocal var_cdl_dfs
            nonlocal bt_cdl_type

            market_ticks = {}
            for market in markets:
                tick = Tick(row.name, market, row[f"{market}_open"], row[f"{market}_high"], row[f"{market}_low"], row[f"{market}_close"], row[f"{market}_vol"])
                market_ticks[market] = tick

            if not is_initialized:
                super(AbstractBulkNettingStrategy, self).process_settle(row.name, market_ticks)
                self.__process_rebalance__(row, market_ticks, markets)
                is_initialized = True

            if row.name.hour == self.close_hour and row.name.minute == self.close_minute:
                self.__process_rebalance__(row, market_ticks, markets)

            for market in markets:
                tick = market_ticks[market]
                buy_trade_result = self.asset_mgmt.get_opened_buy_position(market)
                if buy_trade_result is None:
                    if row[f"{market}_order"] == "BUY":
                        desc = build_desc(row, market, "BUY")
                        super(AbstractBulkNettingStrategy, self).process_enter_long_position(market, tick, tick.close, desc)
                else:
                    ########################################################################################################
                    ## Handle Stop Loss, Take Profit and Trailing Stop
                    if (self.stop_loss_param is not None) or (self.trailing_stop_params is not None) \
                            or (self.take_profit_params is not None):
                        mkt_1m_df = var_cdl_dfs[market][CandleType.MINUTES_1]
                        _1m_before_time = row.name + pd.Timedelta(minutes = (bt_cdl_type.value - 1))
                        _1m_start_time = buy_trade_result.date + pd.Timedelta(minutes = bt_cdl_type.value)
                        from_buy_to_now_df = mkt_1m_df[_1m_start_time:_1m_before_time]

                    ## Handle Stop Loss
                    stop_loss_signal = False
                    if self.stop_loss_param is not None :
                        stop_loss_signal, sl_close, sl_log = super(AbstractBulkNettingStrategy, self).__handle_stop_loss_in_bulk__(buy_trade_result, from_buy_to_now_df, _1m_start_time, _1m_before_time)

                        if stop_loss_signal:
                            super(AbstractBulkNettingStrategy, self).process_exit_long_position(buy_trade_result, market, tick, sl_close, sl_log)

                    ## Handle Take Profit
                    take_profit_signal = False
                    if self.take_profit_params is not None :
                        take_profit_signal, ts_price, ts_log = super(AbstractBulkNettingStrategy, self).__handle_take_profit_in_bulk__(buy_trade_result, from_buy_to_now_df, _1m_start_time, _1m_before_time)
                    if take_profit_signal :
                        super(AbstractNettingStrategy, self).process_exit_long_position(buy_trade_result,
                                                                                        market, tick,
                                                                                        tick.close, ts_log)
                    ## Handle Trailing Stop
                    trailing_stop_signal = False
                    if self.trailing_stop_params is not None :
                        cur_price = row[f"{market}_close"]
                        trailing_stop_signal, ts_price, tss_log = super(AbstractBulkNettingStrategy, self).__handle_tailing_stop_in_bulk__(buy_trade_result, from_buy_to_now_df, _1m_start_time, _1m_before_time, cur_price)
                    if trailing_stop_signal :
                        super(AbstractBulkNettingStrategy, self).process_exit_long_position(buy_trade_result,
                                                                                        market, tick,
                                                                                        ts_price, tss_log)
                    if stop_loss_signal or take_profit_signal or trailing_stop_signal:
                        continue
                    ########################################################################################################
                    if row[f"{market}_order"] == "SELL":
                        desc = build_desc(row, market, "SELL")
                        super(AbstractBulkNettingStrategy, self).process_exit_long_position(buy_trade_result, market, tick, tick.close, desc)

            if row.name.hour == self.close_hour and row.name.minute == self.close_minute:
                super(AbstractBulkNettingStrategy, self).process_settle(row.name, market_ticks)

        result_df.apply(process_statistics, axis=1, args=(base_cdl_dfs.keys(),))

        elapsed_time = sw.stop()
        log.info(f"Stopwatch: Settle Profit and Loss =>  {elapsed_time}")
        elapsed_time_from_beginning = sw_total.stop()
        log.info(f"Stopwatch: All Processing Time ==> {elapsed_time_from_beginning}")
        pm.update_after_settle_progress(elapsed_time, elapsed_time_from_beginning)

    def __fill_remaining_mkt_cdl_till__(self, market, var_mkt_cdl_dfs, var_cdl_dfs, mkt_cdl, bt_cdl_type, till_pdt):

        _1m_df = var_cdl_dfs[CandleType.MINUTES_1]

        if var_cdl_dfs[mkt_cdl].head(1).index[0] > till_pdt:
            return
        if len(var_mkt_cdl_dfs[mkt_cdl]) <= 0:
            return

        start_pdt = var_mkt_cdl_dfs[mkt_cdl].tail(1).index[0] + pd.Timedelta(minutes = mkt_cdl)
        end_pdt = till_pdt + pd.Timedelta(minutes = bt_cdl_type.value-1)

        today_1m_df = _1m_df[start_pdt:end_pdt]
        if len(today_1m_df) == 0 :
            return
        today_open = today_1m_df.head(1)["open"].item()
        today_high = today_1m_df["high"].max()
        today_low = today_1m_df["low"].min()
        today_close = today_1m_df.tail(1)["close"].item()
        today_vol = today_1m_df["vol"].sum()

        var_mkt_cdl_dfs[mkt_cdl] = pd.concat([var_mkt_cdl_dfs[mkt_cdl], \
                                              pd.DataFrame(
                                                  {"market" : market, "open" : [today_open], "high" : [today_high],
                                                   "low"    : [today_low], \
                                                   "close"  : [today_close], "vol" : [today_vol]}, index = [till_pdt])])


    def __process_rebalance__(self, row, market_ticks, markets):
        market_vol5 = {}
        for market in markets:
            market_vol5[market] = row[f"{market}_vol5"]
        self.asset_mgmt.append_supplements(market_vol5)
        if self.enable_asset_rebalance :
            self.asset_mgmt.rebalance(market_ticks)


    def __resample_dataframe__(self, src_df, tgt_cdl, base_hour):
        resample_period = '24H'
        if tgt_cdl == CandleType.DAYS:
            resample_period = '24H'

        resampled_df = src_df.resample(resample_period, origin = 'epoch', offset = timedelta(hours = base_hour)). \
        agg({QItem.market.value: 'first', QItem.open.value: 'first',
             QItem.high.value: 'max', QItem.low.value: 'min',
             QItem.close.value: 'last', QItem.vol.value: 'sum'})
        return resampled_df

    def __compute_close_time__(self, close_hour, bt_cdl_type):
        today_pt = pd.Timestamp('today').replace(hour = close_hour, minute = 0, second = 0, microsecond = 0)
        close_time_pt = today_pt - pd.Timedelta(minutes = bt_cdl_type.value)
        return close_time_pt.hour, close_time_pt.minute

    def __get_cdl_time_of_usr_time__(self, usr_time, cdl_type):
        usr_hour, usr_min = split_hour_min(usr_time)
        today_pt = pd.Timestamp('today').replace(hour = usr_hour, minute = usr_min, second = 0, microsecond = 0)
        close_time_pt = today_pt - pd.Timedelta(minutes = (cdl_type.value - 1))
        return close_time_pt.hour, close_time_pt.minute
    ##################################################################################
    ## Abstract Methods
    def set_time_variables(self):
        pass

    def get_tai_names(self):
        pass

    def calculate_tai(self, past_df):
        pass

    def get_buy_system(self, market_df, market):
        pass

    def get_sell_system(self, market_df, market):
        pass

    ## Strategy Dependent -> Override this method for specifying all candles for the strategy
    def get_filter_hour_min_in_base_cdl(self, market_df):
        pass

    def get_var_candle_types(self):
        pass