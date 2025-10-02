from datetime import timedelta
from os.path import join, dirname

from bt4.Constants import CandleType, QItem
from bt4.strategy.Strategy import AbstractHedgingStrategy
from bt4.strategy.bulk_support import ProgressMgr, build_desc
from bt4.utils.market_utils import compute_sell_timeframes
from bt4.utils.python_utils import flatten, split_hour_min
import pandas as pd
from bt4.quote.QuoteSupport import Tick
import talib
import os
from bt4.utils.mylog import init_log
from bt4.utils.stopwatch import StopWatch

log = init_log()

class AbstractBulkHedgingStrategy(AbstractHedgingStrategy):

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
        # build all data frame for each timeframe
        bt_cdl_type = self.context.backtestor.candle_type  ## Fixed for the timeframe (시간대투자)
        base_cdl_dfs = cld_mgr.cdl_dfs[bt_cdl_type]

        var_cdl_types = self.get_var_candle_types()
        if CandleType.DAYS not in var_cdl_types :
            var_cdl_types.append(CandleType.DAYS)
        if CandleType.MINUTES_1 not in var_cdl_types :
            var_cdl_types.append(CandleType.MINUTES_1)

        if bt_cdl_type not in var_cdl_types:
            var_cdl_types.append(bt_cdl_type)

        var_cdl_dfs = {}
        for market in base_cdl_dfs:
            var_cdl_dfs[market] = {}
            for var_cdl_type in var_cdl_types:
                if var_cdl_type != CandleType.DAYS_TF.value:
                    var_cdl_dfs[market][var_cdl_type] = cld_mgr.cdl_dfs[var_cdl_type][market]

        self.adj_buy_cdl_tf = self.__adjust_times__(self.buy_timeframes, bt_cdl_type)   ## 8:59 -> 9:00, -1h -> 8:00 (because 1 timecandle)
        self.adj_buy_sell_tf, self.adj_sell_buy_tf, self.adj_sell_cdl_tf = \
            compute_sell_timeframes(self.adj_buy_cdl_tf, self.buy_sell_time_gap, False)

        # add 9:0 to make var_cdl_dfs[market] always contains 9:0
        adj_set = set(self.adj_buy_cdl_tf + self.adj_sell_cdl_tf)
        adj_set.add("8:0")
        self.cdl_tf_list = list(adj_set)

        mkt_total_row = super(AbstractBulkHedgingStrategy, self).__get_total_tai_row_in_bulk__(base_cdl_dfs)
        pm = ProgressMgr(tr_sum_id, mkt_total_row, base_cdl_dfs.keys())

        for market in base_cdl_dfs:
            for bs_tf in self.cdl_tf_list:
                bs_hour = int(bs_tf.split(":")[0])
                if bs_tf not in var_cdl_dfs[market]:
                    adj_hour = (bs_hour + 1) % 24
                    df = self.__resample_dataframe__(base_cdl_dfs[market], bt_cdl_type, adj_hour)
                    df.index = df.index + pd.Timedelta(hours=23)
                    var_cdl_dfs[market][CandleType[f"DAYS_{adj_hour}"]] = df


        elapsed_time = sw.stop()
        log.info(f"Stopwatch: Preparing Dataframe => {elapsed_time}")
        sw.start()

        elapsed_time = sw_total.stop()
        pm.update_preparation_progress(elapsed_time)

        ## Constants : Candle 중심으로 하루의 종가인 오전 9시 Close를 받아들이는 Candle시점이 다름
        self.close_hour, self.close_minute = self.__compute_close_time__(9, bt_cdl_type)

        ## 2. make variables for each market
        result_df = pd.DataFrame()
        for market in base_cdl_dfs:
            market_df = base_cdl_dfs[market]

            ## 2.-1 Filtering only for 8 hour (Strategy dependent)
            filter_out_hour_min = self.get_filter_hour_min_in_base_cdl(market_df)
            if filter_out_hour_min is not None :
                market_df = market_df.loc[filter_out_hour_min]

            if mkt_total_row < 6:
                log.error(f"ERROR: Number of Candle data({mkt_total_row}) of {market} is lower than 6. Backtesting has been stopped."
                          f"Check the Backtesting Period.")
                return

            log.info(f"Stopwatch: Computing TAI - Market: {market} Total : {mkt_total_row} rows")
            sw.start()

            ## 2.0 make_variables
            def compute_tais(row):
                nonlocal var_cdl_dfs
                nonlocal bt_cdl_type
                nonlocal sw, elapsed_time_from_beginning

                var_mkt_cdl_dfs = {}

                for mkt_cdl in var_cdl_dfs[market]:
                    recent_cdl_time = self.__compute_recent_cdl_time__(row.name, bt_cdl_type, CandleType(mkt_cdl))
                    if CandleType(mkt_cdl).value > bt_cdl_type.value:
                        var_mkt_cdl_dfs[mkt_cdl] = var_cdl_dfs[market][mkt_cdl][:recent_cdl_time]
                        mkt_1m_df = var_cdl_dfs[market][CandleType.MINUTES_1]
                        if recent_cdl_time != row.name:
                            open_till, high_till, low_till, close_till, vol_till = self.__extract_till__(var_mkt_cdl_dfs, mkt_1m_df, mkt_cdl, bt_cdl_type, row.name)
                            var_mkt_cdl_dfs[mkt_cdl] = pd.concat([var_mkt_cdl_dfs[mkt_cdl], \
                                                       pd.DataFrame({"market":market, "open": [open_till], "high": [high_till], "low": [low_till], \
                                                                     "close": [close_till], "vol": [vol_till]}, index = [row.name])])
                    else:
                        till_time = recent_cdl_time + pd.Timedelta(minutes = bt_cdl_type.value -1)
                        var_mkt_cdl_dfs[mkt_cdl] = var_cdl_dfs[market][mkt_cdl][:till_time]

                # for vol5 variable
                adj_close_hour = (self.close_hour + 1) % 24
                tf_close_cdl = CandleType[f"DAYS_{adj_close_hour}"]
                vol_df = var_mkt_cdl_dfs[tf_close_cdl]
                ## compute vol5
                vol5 = 0
                if len(vol_df) > 6:
                    vol_df["yes_high"] = vol_df["high"].shift(1)
                    vol_df["yes_low"] = vol_df["low"].shift(1)
                    vol_df["volatility"] = (vol_df["yes_high"] - vol_df["yes_low"]) / vol_df["open"]

                    vol5 = talib.SMA(vol_df["volatility"], timeperiod = 5).iloc[-1]
                else:
                    vol5 = 0

                adj_hour = (row.name.hour + 1) % 24
                tf_adj_cdl = CandleType[f"DAYS_{adj_hour}"]
                tf_df = var_mkt_cdl_dfs[tf_adj_cdl][:row.name]
                if len(tf_df) > 6:
                    returns = self.calculate_tai(var_mkt_cdl_dfs, tf_adj_cdl, tf_adj_cdl)
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
            result_df = pd.concat([result_df, market_df], axis = 1)

        for market in base_cdl_dfs :
            buy_system = self.get_buy_system(result_df, market)
            result_df[f"{market}_buy_system"] = None
            result_df[f"{market}_buy_system"] = result_df[f"{market}_buy_system"].astype(bool)
            result_df.loc[(buy_system == True), f"{market}_buy_system"] = True
            result_df.loc[~(buy_system == True), f"{market}_buy_system"] = False

            result_df.loc[(result_df[f"{market}_buy_system"] == True), f"{market}_order"] = "BUY"

            sell_system = self.get_sell_system(result_df, market)
            result_df[f"{market}_sell_system"] = None
            result_df[f"{market}_sell_system"] = result_df[f"{market}_sell_system"].astype(bool)
            result_df.loc[(sell_system==True), f"{market}_sell_system"] = True
            result_df.loc[~(sell_system==True), f"{market}_sell_system"] = False
            result_df.loc[(result_df[f"{market}_buy_system"] == False) & (result_df[f"{market}_sell_system"] == True), f"{market}_order"] = "SELL"
            # result_df = pd.concat([result_df, market_df], axis = 1)

            elapsed_time = sw.stop()
            log.info(f"Stopwatch: Computing TAI - Market: {market} Total : {mkt_total_row} rows Done. =>  {elapsed_time}")
            sw.start()

        root_dir = dirname(dirname(dirname(__file__)))
        file_name = join(root_dir, f"log/{os.getpid()}.csv")
        result_df.to_csv(file_name)
        # print(result_df.head(50))

        elapsed_time = sw.stop()
        log.info(f"Stopwatch: Write Intermediate Result in Log =>  {elapsed_time}")
        elapsed_time_from_beginning = sw_total.stop()
        pm.update_before_settle_progress(elapsed_time, elapsed_time_from_beginning)
        sw.start()

        is_initialized = False
        ## 3. compute asset management
        def process_statistics(row, markets):
            nonlocal is_initialized

            market_ticks = {}
            for market in markets:
                tick = Tick(row.name, market, row[f"{market}_open"], row[f"{market}_high"], row[f"{market}_low"], row[f"{market}_close"], row[f"{market}_vol"])
                market_ticks[market] = tick

            if not is_initialized:
                super(AbstractBulkHedgingStrategy, self).process_settle(row.name, market_ticks)
                self.__process_rebalance__(row, market_ticks, markets)
                is_initialized = True

            if row.name.hour == self.close_hour and row.name.minute == self.close_minute:
                self.__process_rebalance__(row, market_ticks, markets)

            time_pdt = pd.to_datetime(row.name)

            time_str = f"{row.name.hour}:{row.name.minute}"
            is_buy_time = True if time_str in self.adj_buy_cdl_tf else False
            is_sell_time = True if time_str in self.adj_sell_cdl_tf else False

            for market in markets:
                tick = market_ticks[market]
                if is_buy_time:
                    recovered_time = row.name + pd.Timedelta(minutes = 59)
                    expected_buy_timeframe_str = self.__zero_padding_hour_minutes__(recovered_time)
                    buy_trade_result = self.asset_mgmt.get_opened_buy_position(market, expected_buy_timeframe_str)

                    if buy_trade_result is None:
                        if is_buy_time and row[f"{market}_order"] == "BUY":
                            desc = build_desc(row, market, "BUY")
                            super(AbstractBulkHedgingStrategy, self).process_enter_long_position(market, tick, tick.close, desc, \
                                                                                                 expected_buy_timeframe_str)

                if is_sell_time:
                    recovered_time = row.name + pd.Timedelta(minutes = 59)
                    recovered_sell_time_str = self.__zero_padding_hour_minutes__(recovered_time)

                    matched_buy_timeframe_str = self.sell_buy_tf[recovered_sell_time_str]
                    matched_buy_trade_result = self.asset_mgmt.get_opened_buy_position(market,
                                                                                       matched_buy_timeframe_str)

                    if matched_buy_trade_result is not None :
                        ##################################################################################
                        if (self.stop_loss_param is not None) or (self.trailing_stop_params is not None) \
                                or (self.take_profit_params is not None) :
                            mkt_1m_df = var_cdl_dfs[market][CandleType.MINUTES_1]
                            _1day_before_time = row.name + pd.Timedelta(minutes = (bt_cdl_type.value - 1))
                            _1day_start_time = matched_buy_trade_result.date + pd.Timedelta(minutes = bt_cdl_type.value)
                            from_buy_to_now_df = mkt_1m_df[_1day_start_time :_1day_before_time]

                        ### Handle Stop_loss
                        stop_loss_signal = False
                        if self.stop_loss_param is not None :
                            stop_loss_signal, sl_price, sl_log = \
                                super(AbstractBulkHedgingStrategy, self).__handle_stop_loss_in_bulk__(matched_buy_trade_result,
                                                                                              from_buy_to_now_df, _1day_start_time, _1day_before_time)

                        if stop_loss_signal :
                            super(AbstractBulkHedgingStrategy, self).process_exit_long_position(matched_buy_trade_result,
                                                                                            market, tick,
                                                                                            sl_price, sl_log,
                                                                                            matched_buy_timeframe_str)

                        # ### Handle Take Profit
                        take_profit_signal = False
                        if self.take_profit_params is not None :
                            take_profit_signal, ts_price, ts_log = \
                                super(AbstractBulkHedgingStrategy, self).__handle_take_profit_in_bulk__(matched_buy_trade_result, from_buy_to_now_df,
                                                                                                        _1day_start_time, _1day_before_time)
                        if take_profit_signal :
                            super(AbstractBulkHedgingStrategy, self).process_exit_long_position(matched_buy_trade_result,
                                                                                            market, tick,
                                                                                            tick.close, ts_log,
                                                                                            matched_buy_timeframe_str)

                        # ### Handle Trailing_stop
                        trailing_stop_signal = False
                        if self.trailing_stop_params is not None :
                            cur_price = row[f"{market}_close"]
                            trailing_stop_signal, ts_price, tss_log = \
                                super(AbstractBulkHedgingStrategy, self).__handle_tailing_stop_in_bulk__(matched_buy_trade_result, from_buy_to_now_df, _1day_start_time,
                                                                                                         _1day_before_time, cur_price)
                        if trailing_stop_signal :
                            super(AbstractBulkHedgingStrategy, self).process_exit_long_position(matched_buy_trade_result,
                                                                                            market, tick,
                                                                                            ts_price, tss_log,
                                                                                            matched_buy_timeframe_str)

                        if stop_loss_signal or take_profit_signal or trailing_stop_signal :
                            continue

                        if row[f"{market}_order"] == "SELL":
                            desc = build_desc(row, market, "SELL")
                            super(AbstractBulkHedgingStrategy, self).process_exit_long_position(matched_buy_trade_result, market, tick, tick.close, desc, matched_buy_timeframe_str)

            if row.name.hour == self.close_hour and row.name.minute == self.close_minute:
                super(AbstractBulkHedgingStrategy, self).process_settle(row.name, market_ticks)

        result_df.apply(process_statistics, axis=1, args=(base_cdl_dfs.keys(),))

        elapsed_time = sw.stop()
        log.info(f"Stopwatch: Settle Profit and Loss =>  {elapsed_time}")
        elapsed_time_from_beginning = sw_total.stop()
        log.info(f"Stopwatch: All Processing Time ==> {elapsed_time_from_beginning}")
        pm.update_after_settle_progress(elapsed_time, elapsed_time_from_beginning)

    def __extract_till__(self, var_mkt_cdl_dfs, mkt_1m_df, mkt_cdl, bt_cdl_type, till_pdt):

        if (len(var_mkt_cdl_dfs[mkt_cdl]) == 0) or (var_mkt_cdl_dfs[mkt_cdl].head(1).index[0] > till_pdt):
            return 0,0,0,0,0

        start_pdt = var_mkt_cdl_dfs[mkt_cdl][:till_pdt].tail(1).index[0] + pd.Timedelta(minutes = mkt_cdl)
        end_pdt = till_pdt + pd.Timedelta(minutes = bt_cdl_type.value-1)

        today_1m_df = mkt_1m_df[start_pdt:end_pdt]
        if len(today_1m_df) == 0 :
            return 0, 0, 0, 0, 0

        today_open = today_1m_df.head(1)["open"].item()
        today_high = today_1m_df["high"].max()
        today_low = today_1m_df["low"].min()
        today_close = today_1m_df.tail(1)["close"].item()
        today_vol = today_1m_df["vol"].sum()
        return today_open, today_high, today_low, today_close, today_vol

    def __compute_recent_cdl_time__(self, now_timestamp, bt_cdl_type, mkt_cdl) :
        recent_cdl_time = now_timestamp
        if mkt_cdl.value > bt_cdl_type.value:
            if mkt_cdl == CandleType.DAYS:
                if now_timestamp.hour >= 9 and now_timestamp.minute >= 0:
                    recent_cdl_time = pd.Timestamp(now_timestamp - pd.Timedelta(days = 1))
                else:
                    recent_cdl_time = pd.Timestamp(now_timestamp - pd.Timedelta(days = 2))
                recent_cdl_time = recent_cdl_time.replace(hour = 9, minute = 0, second = 0, microsecond = 0)
            elif mkt_cdl == CandleType.HOUR4:
                hour_gap = pd.Timestamp(now_timestamp - pd.Timedelta(hours = 1)).hour % 4
                recent_cdl_time = now_timestamp - pd.Timedelta(hours = hour_gap) - pd.Timedelta(hours = 4)
                recent_cdl_time = recent_cdl_time.replace(minute = 0, second = 0, microsecond = 0)
            elif mkt_cdl == CandleType.HOUR:
                recent_cdl_time = now_timestamp - pd.Timedelta(hours = 1)
                recent_cdl_time = recent_cdl_time.replace(minute = 0, second = 0, microsecond = 0)
            elif mkt_cdl == CandleType.MINUTES_30:
                recent_cdl_time = now_timestamp - pd.Timedelta(minutes = (30 + now_timestamp.minute % 30))
            elif mkt_cdl == CandleType.MINUTES_15:
                recent_cdl_time = now_timestamp - pd.Timedelta(minutes = (15 + now_timestamp.minute % 15))
            elif mkt_cdl == CandleType.MINUTES_5:
                recent_cdl_time = now_timestamp - pd.Timedelta(minutes = (5 + now_timestamp.minute % 5))
            elif mkt_cdl == CandleType.MINUTES_3:
                recent_cdl_time = now_timestamp - pd.Timedelta(minutes = (3 + now_timestamp.minute % 3))

        return recent_cdl_time

    def __zero_padding_hour_minutes__(self, time_pd):
        h_zero_padding = "0" if time_pd.hour < 10 else ""
        m_zero_padding = "0" if time_pd.minute < 10 else ""
        return f"{h_zero_padding}{time_pd.hour}:{m_zero_padding}{time_pd.minute}"

    def __process_rebalance__(self, row, market_ticks, markets):
        market_vol5 = {}
        for market in markets:
            market_vol5[market] = row[f"{market}_vol5"]
        self.asset_mgmt.append_supplements(market_vol5)
        if self.enable_asset_rebalance :
            self.asset_mgmt.rebalance(market_ticks)

    def __resample_dataframe__(self, src_df, tgt_cdl, base_hour):
        resample_period = '24h'
        if tgt_cdl == CandleType.DAYS:
            resample_period = '24h'

        resampled_df = src_df.resample(resample_period, origin = 'epoch', offset = timedelta(hours = base_hour)). \
        agg({QItem.market.value: 'first', QItem.open.value: 'first',
             QItem.high.value: 'max', QItem.low.value: 'min',
             QItem.close.value: 'last', QItem.vol.value: 'sum'})
        return resampled_df

    def __compute_close_time__(self, close_hour, bt_cdl_type):
        today_pt = pd.Timestamp('today').replace(hour = close_hour, minute = 0, second = 0, microsecond = 0)
        close_time_pt = today_pt - pd.Timedelta(minutes = bt_cdl_type.value)
        return close_time_pt.hour, close_time_pt.minute

    def __get_buy_market_df__(self, market_df, market):
        return market_df[(((market_df.index.hour.isin([int(time.split(':')[0]) for time in self.adj_buy_cdl_tf])) & \
                                 (market_df.index.minute.isin([int(time.split(':')[1]) for time in self.adj_buy_cdl_tf]))))]

    def __get_sell_market_df__(self, market_df, market):
        return market_df[(((market_df.index.hour.isin([int(time.split(':')[0]) for time in self.adj_sell_cdl_tf])) & \
                           (market_df.index.minute.isin([int(time.split(':')[1]) for time in self.adj_sell_cdl_tf]))))]

    ## Strategy Dependent -> Override this method for specifying all candles for the strategy
    def get_filter_hour_min_in_base_cdl(self, market_df) :
        '''
            This method can cover all changes of the
        :param market_df:
        :return:
        '''
        return (((market_df.index.hour.isin([int(time.split(':')[0]) for time in self.adj_buy_cdl_tf])) & \
                 (market_df.index.minute.isin([int(time.split(':')[1]) for time in self.adj_buy_cdl_tf])))) | \
            (((market_df.index.hour.isin([int(time.split(':')[0]) for time in self.adj_sell_cdl_tf])) & \
              (market_df.index.minute.isin([int(time.split(':')[1]) for time in self.adj_sell_cdl_tf])))) | \
            ((market_df.index.hour == 8) & (market_df.index.minute == 0))

    def __adjust_times__(self, buy_timeframes, cdl_type) :
        '''
        "08:59" -> "09:00"
        :param buy_timeframes:
        :return:
        '''
        adj_buy_tfs = []
        for buy_tf in buy_timeframes :
            buy_tf_hour = int(buy_tf.split(':')[0])
            buy_tf_min = int(buy_tf.split(':')[1])
            today_pt = pd.Timestamp('today').replace(hour = buy_tf_hour, minute = buy_tf_min, second = 0,
                                                     microsecond = 0)
            adj_buy_tf = today_pt + pd.Timedelta(minutes = 1) - pd.Timedelta(minutes = cdl_type.value)
            adj_buy_tfs.append(f"{adj_buy_tf.hour}:{adj_buy_tf.minute}")
        return adj_buy_tfs

    def __not__(self, df_ser):
        col_name = df_ser.name
        df = pd.DataFrame({col_name: df_ser}, index=df_ser.index)
        df[f"{col_name}_tmp"] = df[col_name]
        df.loc[(df[f"{col_name}_tmp"] == True), f"{col_name}_not"] = False
        df.loc[(df[f"{col_name}_tmp"] == False), f"{col_name}_not"] = True
        df.drop([f"{col_name}_tmp"], axis=1, inplace = True)
        return df[f"{col_name}_not"]

    def __get_cdl_time_of_usr_time__(self, usr_time, cdl_type):
        usr_hour, usr_min = split_hour_min(usr_time)
        today_pt = pd.Timestamp('today').replace(hour = usr_hour, minute = usr_min, second = 0, microsecond = 0)
        close_time_pt = today_pt - pd.Timedelta(minutes = (cdl_type.value - 1))
        return close_time_pt.hour, close_time_pt.minute


    ##################################################################################
    ## Abstract Methods

    def set_time_variables(self):
        pass

    def calculate_tai(self, var_mkt_cdl_dfs, tf_adj_cdl, time_pts):
        pass

    def get_tai_names(self):
        pass


    def get_buy_system(self, market_df, market):
        pass

    def get_sell_system(self, market_df, market):
        pass

