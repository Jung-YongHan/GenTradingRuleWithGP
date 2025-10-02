import copy
import unittest

from talib import abstract
import bt4.GlobalProperties as global_prop
from bt4.Constants import CandleType, ExType, QItem
from bt4.core.gen_support import get_nary_vars, is_nary_vars, call_func
from bt4.quote.QuoteMgr import QuoteStorageMgr
from bt4.quote.QuoteSupport import Quote
from bt4.quote.TAIMgr import TAIMgr
from bt4.utils.python_utils import str2dt, now_dt, flatten

import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('max_colwidth', None)

class MyTestCase(unittest.TestCase):

    def test_tai_mgr_unary(self):

        markets = ('KRW-BTC', 'KRW-ETH', 'KRW-XRP')
        start_dt = str2dt('2018-10-01T00:00:00')
        end_dt = str2dt('2018-12-01T00:00:00')
        cdl_types_needed = [CandleType.DAYS, CandleType.HOUR]
        simul_storage = QuoteStorageMgr(markets, cdl_types_needed)

        cdl_runtime_dfs = {}
        for cdl_type in cdl_types_needed:
            q_df = simul_storage.load_quote_in_range(ExType.upbit, markets, start_dt, 200, cdl_type)
            cdl_runtime_dfs[cdl_type] = copy.deepcopy(q_df)

        time_dt = now_dt()
        quote = Quote(time_dt)
        quote.add_quote(ExType.upbit, cdl_runtime_dfs, None)
        # quote.print()

        tmgr = TAIMgr(quote, ExType.upbit)
        ma5 = tmgr.get_unary('sma', [5], CandleType.HOUR, [QItem.close], True)
        for market in ma5:
            if not market.endswith('_raw'):
                print(f'{market} => {ma5[market]}')
            else:
                print(f'{market} raw => {ma5[market]}')

    def test_tai_mgr_biary(self):
        cdl_types_needed = [CandleType.DAYS, CandleType.HOUR]
        markets = ('KRW-BTC', 'KRW-ETH', 'KRW-XRP')
        simul_storage = QuoteStorageMgr(markets, cdl_types_needed)
        start_dt = str2dt('2018-10-01T00:00:00')

        cdl_runtime_dfs = {}
        for cdl_type in cdl_types_needed:
            q_df = simul_storage.load_quote_in_range(ExType.upbit, markets, start_dt, 200, cdl_type)
            cdl_runtime_dfs[cdl_type] = copy.deepcopy(q_df)

        time_dt = now_dt()
        quote = Quote(time_dt)
        quote.add_quote(ExType.upbit, cdl_runtime_dfs, None)
        # quote.print()

        tmgr = TAIMgr(quote, ExType.upbit)
        bbands = tmgr.get_nary('bbands', [5, 2.0, 2.0, 0], CandleType.DAYS, [QItem.close])
        for market in bbands:
            if not market.endswith('_raw'):
                print(f'{market} => {bbands[market]}')
            else:
                print(f'{market} raw => {bbands[market]}')

    def test_tai_mgr_cascaded_tai(self):
        cdl_types_needed = [CandleType.DAYS, CandleType.HOUR]
        markets = ('KRW-BTC', 'KRW-ETH', 'KRW-XRP')
        simul_storage = QuoteStorageMgr(markets, cdl_types_needed)

        start_dt = str2dt('2018-10-01T00:00:00')

        cdl_runtime_dfs = {}
        for cdl_type in cdl_types_needed:
            q_df = simul_storage.load_quote_in_range(ExType.upbit, markets, start_dt, 200, cdl_type)
            cdl_runtime_dfs[cdl_type] = copy.deepcopy(q_df)

        time_dt = now_dt()
        quote = Quote(time_dt)
        quote.add_quote(ExType.upbit, cdl_runtime_dfs, None)
        # quote.print()

        tmgr = TAIMgr(quote, ExType.upbit)
        vol = tmgr.get_unary('vol', [], CandleType.HOUR, [QItem.open, QItem.high, QItem.low], True)
        for market in vol:
            if not market.endswith('_raw'):
                print(f'{market} => {vol[market]}')
                raw_input = vol[market+'_raw']
                vol5 = tmgr.call_talib_unary('sma', [5], [raw_input])
                print(f'{vol5}')

    def test_tai_mgr_cascade_tai_in_bulk(self):
        cdl_types_needed = [CandleType.DAYS, CandleType.HOUR]
        markets = ('KRW-BTC', )
        simul_storage = QuoteStorageMgr(markets, cdl_types_needed)

        start_dt = str2dt('2018-10-01T00:00:00')

        cdl_runtime_dfs = {}
        var_mkt_cdl_dfs = {}
        for cdl_type in cdl_types_needed:
            q_df = simul_storage.load_quote_in_range(ExType.upbit, markets, start_dt, 200, cdl_type)
            cdl_runtime_dfs[cdl_type] = copy.deepcopy(q_df)
            for market in q_df:
                var_mkt_cdl_dfs[cdl_type] = q_df[market]


        ma, ma_raw = call_func("sma", var_mkt_cdl_dfs, 1440, ["close"], [3], locals())
        print(f"{ma=}, {ma_raw=}")


        ma2, ma_raw2 = call_func("sma", var_mkt_cdl_dfs, 1440, ["close"], [3], locals())
        print(f"{ma2=}, {ma_raw2=}")

        rsi, rsi_raw = call_func("rsi", var_mkt_cdl_dfs, 1440, ["close"], [14], locals())
        print(f"{rsi=}, {rsi_raw=}")
        rsi2, rsi_raw2 = call_func("rsi", var_mkt_cdl_dfs, 1440, ["close"], [14], locals())
        print(f"{rsi2=}, {rsi_raw2=}")

        ma_rsi, ma_rsi_raw = call_func("sma", var_mkt_cdl_dfs, 1440, ["rsi"], [14], locals())
        print(f"{ma_rsi=}, {ma_rsi_raw=}")

        # up_ma_rsi, up_ma_rsi_raw = call_func("up_divergent", var_mkt_cdl_dfs, 1440, ["ma_rsi"], [24], locals())
        # print(f"{up_ma_rsi=}, {up_ma_rsi_raw=}")

        macd, macd_sig, macd_histo, macd_raw, macd_sig_raw, macd_histo_raw = call_func("macd", var_mkt_cdl_dfs, 1440, ["close"], [6, 19, 6], locals())
        print(f"{macd=}, {macd_sig=}, {macd_histo=}, {macd_raw=}, {macd_sig_raw=}, {macd_histo_raw=}")

        trb_0, trb_1, trb_0_raw, trb_1_raw = call_func("trb", var_mkt_cdl_dfs, 1440, ["high", "low"], [24], locals())
        print(f"{trb_0=}, {trb_0_raw=}, {trb_1=}, {trb_1_raw=}")

        ma_trb_1, ma_trb_1_raw = call_func("sma", var_mkt_cdl_dfs, 1440, ["trb_1"], [3], locals())
        print(f"{ma_trb_1=}, {ma_trb_1_raw=}")

        ret_list = [ma, rsi, ma_rsi, up_ma_rsi, macd, trb_0, ma_trb_1]
        returns = flatten(ret_list)
        print(f"{returns=}")

    def call_func(self, func_name, dfs, cdl_type_val, sources, params, local_vars):
        market_df = dfs[cdl_type_val]
        input_list = []
        for src_col in sources:
            if src_col in market_df.columns:
                temp_float = market_df[src_col].astype(float)
                input_list.append(temp_float.to_numpy())
            else:
                local_var = f"{src_col}_raw"
                if local_var in local_vars:
                    input_list.append(local_vars[local_var])
                else:
                    print(f"{local_var} does not exist in the data set. ")

        tmgr = TAIMgr()
        if is_nary_vars(func_name):
            result = tmgr.call_talib_nary(func_name, params, input_list, True)
        else:
            result = tmgr.call_talib_unary(func_name, params, input_list, True)
        return flatten(result)


    def test_spread(self):
        cdl_types_needed = [CandleType.DAYS, CandleType.HOUR]
        markets = ('KRW-BTC',"KRW-ETH")
        simul_storage = QuoteStorageMgr(markets, cdl_types_needed)

        # start_dt = str2dt('2018-11-22T08:59:00')  ## Bullish = True
        # start_dt = str2dt('2018-12-17T08:59:00') ## Bullish = True
        start_dt = str2dt('2019-02-25T08:59:00')
        # start_dt = str2dt('2019-02-09T08:59:00') ## Bullish = True

        cdl_runtime_dfs = {}
        var_mkt_cdl_dfs = {}
        for cdl_type in cdl_types_needed :
            q_df = simul_storage.load_quote_in_range(ExType.upbit, markets, start_dt, 200, cdl_type)
            cdl_runtime_dfs[cdl_type] = copy.deepcopy(q_df)
            for market in q_df :
                var_mkt_cdl_dfs[cdl_type] = q_df[market]

        data = var_mkt_cdl_dfs[CandleType.DAYS]["close"][-25 :]
        print(f"{ data=}")

        quote = Quote(now_dt())
        quote.add_quote(ExType.upbit, cdl_runtime_dfs, None)
        global_prop.cur_quote = quote

        spread, spread_raw = call_func("spread", var_mkt_cdl_dfs, 1440, ["close"], [ExType.upbit, "KRW-BTC", "KRW-ETH", 50], locals())

        print(f"{spread=}, {spread_raw=}")


    def test_bullish_reversal(self):
        cdl_types_needed = [CandleType.DAYS, CandleType.HOUR]
        markets = ('KRW-BTC',)
        simul_storage = QuoteStorageMgr(markets, cdl_types_needed)

        # start_dt = str2dt('2018-11-22T08:59:00')  ## Bullish = True
        # start_dt = str2dt('2018-12-17T08:59:00') ## Bullish = True
        start_dt = str2dt('2019-02-25T08:59:00')
        # start_dt = str2dt('2019-02-09T08:59:00') ## Bullish = True

        cdl_runtime_dfs = {}
        var_mkt_cdl_dfs = {}
        for cdl_type in cdl_types_needed :
            q_df = simul_storage.load_quote_in_range(ExType.upbit, markets, start_dt, 200, cdl_type)
            cdl_runtime_dfs[cdl_type] = copy.deepcopy(q_df)
            for market in q_df :
                var_mkt_cdl_dfs[cdl_type] = q_df[market]

        data = var_mkt_cdl_dfs[CandleType.DAYS]["close"][-25:]
        print(f"{ data=}")

        rsi, rsi_raw = call_func("rsi", var_mkt_cdl_dfs, 1440, ["close"], [14], locals())
        print(f"{ rsi_raw=}")
        is_bullish_reversal, is_bullish_reversal_raw = call_func("bullish_reversal", var_mkt_cdl_dfs, 1440, ["rsi"], [15], locals())
        print(f"{is_bullish_reversal=}, {is_bullish_reversal_raw=}")

        bband_0, bband_1, bband_2, bband_0_raw, bband_1_raw, bband_2_raw = call_func("bbands", var_mkt_cdl_dfs, 1440, ["close"], [25, 2.0, 2.0, 0], locals())
        print(f"{bband_2_raw=}")
        is_bullish_reversal, is_bullish_reversal_raw = call_func("bullish_reversal", var_mkt_cdl_dfs, 1440, ["bband[2]"], [15], locals())
        print(f"{is_bullish_reversal=}, {is_bullish_reversal_raw=}")

    def test_bearish_reversal(self):
        cdl_types_needed = [CandleType.DAYS, CandleType.HOUR]
        markets = ('KRW-BTC',)
        simul_storage = QuoteStorageMgr(markets, cdl_types_needed)

        # start_dt = str2dt('2018-11-22T08:59:00')  ## Bullish = True
        # start_dt = str2dt('2018-12-17T08:59:00') ## Bullish = True
        start_dt = str2dt('2019-04-23T08:59:00')
        # start_dt = str2dt('2019-02-09T08:59:00') ## Bullish = True

        cdl_runtime_dfs = {}
        var_mkt_cdl_dfs = {}
        for cdl_type in cdl_types_needed :
            q_df = simul_storage.load_quote_in_range(ExType.upbit, markets, start_dt, 200, cdl_type)
            cdl_runtime_dfs[cdl_type] = copy.deepcopy(q_df)
            for market in q_df :
                var_mkt_cdl_dfs[cdl_type] = q_df[market]

        data = var_mkt_cdl_dfs[CandleType.DAYS]["close"][-25:]
        print(f"{data=}")

        rsi, rsi_raw = call_func("rsi", var_mkt_cdl_dfs, 1440, ["close"], [14], locals())
        print(f"{rsi_raw=}")
        is_bearish_reversal, is_bearish_reversal_raw = call_func("bearish_reversal", var_mkt_cdl_dfs, 1440, ["rsi"], [15], locals())
        print(f"{is_bearish_reversal=}, {is_bearish_reversal_raw=}")

        bband_0, bband_1, bband_2, bband_0_raw, bband_1_raw, bband_2_raw = call_func("bbands", var_mkt_cdl_dfs, 1440, ["close"], [25, 2.0, 2.0, 0], locals())
        print(f"{bband_0_raw=}")
        is_bearish_reversal, is_bearish_reversal_raw = call_func("bearish_reversal", var_mkt_cdl_dfs, 1440, ["bband[0]"], [15], locals())
        print(f"{is_bearish_reversal=}, {is_bearish_reversal_raw=}")

    def test_up_breakout(self):
        cdl_types_needed = [CandleType.DAYS, CandleType.HOUR]
        markets = ('KRW-BTC',)
        simul_storage = QuoteStorageMgr(markets, cdl_types_needed)

        # start_dt = str2dt('2019-03-29T08:59:00') # False
        start_dt = str2dt('2019-01-14T08:59:00')  # False

        cdl_runtime_dfs = {}
        var_mkt_cdl_dfs = {}
        for cdl_type in cdl_types_needed :
            q_df = simul_storage.load_quote_in_range(ExType.upbit, markets, start_dt, 200, cdl_type)
            cdl_runtime_dfs[cdl_type] = copy.deepcopy(q_df)
            for market in q_df :
                var_mkt_cdl_dfs[cdl_type] = q_df[market]

        data = var_mkt_cdl_dfs[CandleType.DAYS]["close"][-25:]
        print(f"{data=}")

        rsi, rsi_raw = call_func("rsi", var_mkt_cdl_dfs, 1440, ["close"], [14], locals())
        print(f"{rsi_raw=}")
        is_up_breakout_val, is_up_breakout_val_raw = call_func("up_breakout_val", var_mkt_cdl_dfs, 1440, ["rsi"], [70, 5], locals())
        print(f"{is_up_breakout_val=}, {is_up_breakout_val_raw=}")

        bband_0, bband_1, bband_2, bband_0_raw, bband_1_raw, bband_2_raw = call_func("bbands", var_mkt_cdl_dfs, 1440, ["close"], [25, 2.0, 2.0, 0], locals())
        print(f"{bband_0_raw=}")
        is_up_breakout_vals, is_up_breakout_vals_raw = call_func("up_breakout_vals", var_mkt_cdl_dfs, 1440, ["close", "bband[2]"], [5], locals())
        print(f"{is_up_breakout_vals=}, {is_up_breakout_vals_raw=}")


    def test_down_breakout(self):
        cdl_types_needed = [CandleType.DAYS, CandleType.HOUR]
        markets = ('KRW-BTC',)
        simul_storage = QuoteStorageMgr(markets, cdl_types_needed)

        # start_dt = str2dt('2019-03-29T08:59:00') # False
        start_dt = str2dt('2019-01-14T08:59:00')  # False

        cdl_runtime_dfs = {}
        var_mkt_cdl_dfs = {}
        for cdl_type in cdl_types_needed :
            q_df = simul_storage.load_quote_in_range(ExType.upbit, markets, start_dt, 200, cdl_type)
            cdl_runtime_dfs[cdl_type] = copy.deepcopy(q_df)
            for market in q_df :
                var_mkt_cdl_dfs[cdl_type] = q_df[market]

        data = var_mkt_cdl_dfs[CandleType.DAYS]["close"][-25:]
        print(f"{data=}")

        rsi, rsi_raw = call_func("rsi", var_mkt_cdl_dfs, 1440, ["close"], [14], locals())
        print(f"{rsi_raw=}")

        is_down_breakout_val, is_down_breakout_val_raw = call_func("down_breakout_val", var_mkt_cdl_dfs, 1440, ["rsi"],[70, 5], locals())
        print(f"{is_down_breakout_val=}, {is_down_breakout_val_raw=}")

        bband_0, bband_1, bband_2, bband_0_raw, bband_1_raw, bband_2_raw = call_func("bbands", var_mkt_cdl_dfs, 1440, ["close"], [25, 2.0, 2.0, 0], locals())
        print(f"{bband_0_raw=}")

        is_down_breakout_vals, is_down_breakout_vals_raw = call_func("down_breakout_vals", var_mkt_cdl_dfs, 1440, ["close", "bband[2]"], [5], locals())
        print(f"{is_down_breakout_vals=}, {is_down_breakout_vals_raw=}")






if __name__ == '__main__':
    unittest.main()
