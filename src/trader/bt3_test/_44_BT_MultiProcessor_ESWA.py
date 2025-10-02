import multiprocessing as mp
import re
import sys
import unittest
from datetime import datetime

# from multiprocessing import cpu_count
from multiprocessing.pool import Pool
from os.path import dirname, join

import pandas as pd

import bt4.exec.BullTraderMain as bm
import bt4.utils.mylog as log_module
from bt4.Constants import CandleType, QItem, R
from bt4.core.Interceptors import HandleType, TrendStgyHdgeInterceptor
from bt4.utils.mylog import init_log

log_module.log_mode = "simulator"
log = init_log()


def start_backtest(agrs):
    result_dic = agrs[0]
    si = TrendStgyHdgeInterceptor(HandleType.Instant_Stream)
    si.update_params(result_dic)
    bm.main(sys.argv, si)
    return si.get_results()


class MultiProcessorPollCryptoLong(unittest.TestCase):
    def run_multi_backtest(self, args):
        pool = Pool(self.num_cpus)
        results = pool.imap(start_backtest, args)
        pool.close()
        pool.join()

        whole_df = pd.DataFrame()
        for result in results:
            tmep_df = pd.DataFrame(result[1], index=["1"])
            whole_df = pd.concat([whole_df, tmep_df])
            print("df:", result[0], result[1])

        now = datetime.now()
        nowDatetime = now.strftime("%Y-%m-%dT%H_%M_%S")
        root_dir = dirname(dirname(__file__))
        self.file_name = join(root_dir, f"report/multi_exec_{nowDatetime}_eswa_param_optim")
        csv_file_name = self.file_name + ".csv"
        # whole_df.to_csv(csv_file_name)

        whole_df["model"] = [
            d[re.search("model", d).end() + 2 : re.search("model", d).end() + len("model") + 9] for d in whole_df["params"]
        ]
        whole_df["pred_len"] = [d[re.search("pred_len", d).end() + 2 : re.search("pred_len", d).end() + 6] for d in whole_df["params"]]
        whole_df["tick"] = [d[re.search("tick", d).end() + 2 : re.search("tick", d).end() + 9] for d in whole_df["params"]]

        whole_df["last_bal"] = whole_df["last_bal"].astype(float) / 10_000_000
        whole_df = whole_df[
            ["s_period", "params", "model", "pred_len", "tick", "last_bal", "mdd", "sharp_index", "num_of_trades", "trade_win_rate"]
        ]

        whole_df = whole_df.transpose()
        whole_df.to_csv(csv_file_name)
        print(whole_df)
        print("테스트 완료!!!!!!")

    def get_candle_type(self, tick):
        if tick == "day":
            return CandleType.DAYS
        elif tick == "hour":
            return CandleType.HOUR
        elif tick == "hour4":
            return CandleType.HOUR4
        elif tick == "min30":
            return CandleType.MINUTES_30
        else:
            raise

    def get_test_start_time(self, tick):
        if tick == "day":
            return "2022-04-01T08:59:00"
        elif tick == "hour4":
            return "2022-04-01T04:59:00"
        elif tick == "hour":
            return "2022-04-01T00:59:00"
        elif tick == "min30":
            return "2022-04-01T00:29:00"
        else:
            raise

    def get_test_end_time(self, tick):
        if tick == "day":
            return "2023-05-14T08:59:00"
        elif tick == "hour4":
            return "2023-05-14T16:59:00"
        elif tick == "hour":
            return "2023-05-14T17:59:00"
        elif tick == "min30":
            return "2023-05-14T15:29:00"
        else:
            raise

    def get_bt_time(self, tick):
        if tick == "day":
            return ["08:59"]

        elif tick == "hour4":
            return ["08:59", "12:59", "16:59", "20:59", "00:59", "04:59"]

        elif tick == "hour":
            return [
                "07:59",
                "08:59",
                "09:59",
                "10:59",
                "11:59",
                "12:59",
                "13:59",
                "14:59",
                "15:59",
                "16:59",
                "17:59",
                "18:59",
                "19:59",
                "20:59",
                "21:59",
                "22:59",
                "23:59",
                "00:59",
                "01:59",
                "02:59",
                "03:59",
                "04:59",
                "05:59",
                "06:59",
            ]

        elif tick == "min30":
            time_list = []
            for min in "29 59".split():
                for time in range(24):
                    time_temp = str(time) if time > 10 else f"0{time}"
                    time_list.append(f"{time_temp}:{min}")
            return time_list
        else:
            raise

    def get_pred_len(self, tick):
        if tick == "day":
            return [3, 6, 12, 24, 36]
        else:
            return [6, 12, 24, 48, 96]

    # @unittest.skip('Tested')
    def test_run_multi_backtest_model(self):
        tgt_ex = "upbit"
        cfg_prefix = f"bt3_config.{tgt_ex}."
        conf = "eswa_vol_multiprocess"
        vol_targets = [
            0.99,
        ]
        timeframes_list = [["08:59"]]
        timegaps_list = [0]
        r = R()

        market_list = [
            # ('KRW-BTC',),
            ("KRW-ETH",),
            # ('KRW-XRP',),
        ]

        # TICK_LIST = ['day', 'hour4', 'hour', 'min30']
        TICK_LIST = ["day"]

        # MA_LIST = [3, 5, 10, 20]
        MA_LIST = [20]
        IS_USE_TAI = True
        IS_USE_MODEL = True
        self.num_cpus = len(self.get_pred_len(TICK_LIST[0])) * len(TICK_LIST) * len(MA_LIST)
        ntask = 1

        task = []
        for markets in market_list:
            for TICK in TICK_LIST:
                for timeframes in timeframes_list:
                    for timegap in timegaps_list:
                        for vol in vol_targets:
                            for MA in MA_LIST:
                                for PRED_LEN in self.get_pred_len(TICK):
                                    params_tobe_updated = {}

                                    #############################
                                    conf_path = cfg_prefix + conf
                                    sys.argv = ["BullTraderMain", "backtestor", "-conf", conf_path]
                                    params_tobe_updated["conf"] = conf
                                    #############################

                                    params_tobe_updated[r.OP.MARKET] = markets
                                    params_tobe_updated[r.OP.BT.START] = self.get_test_start_time(TICK)
                                    params_tobe_updated[r.OP.BT.END] = self.get_test_end_time(TICK)
                                    params_tobe_updated[r.OP.BT.CANDLE_TYPE] = self.get_candle_type(TICK)
                                    params_tobe_updated[r.OP.BT.TIME] = self.get_bt_time(TICK)

                                    params_tobe_updated[r.AM.AM_TIMEFRAMES] = timeframes
                                    params_tobe_updated[r.AM.AM_VOL_TARGET] = vol
                                    strategy_param = {}
                                    params_tobe_updated[r.STGY.PARAMS] = strategy_param
                                    strategy_param["timeframes"] = params_tobe_updated[r.AM.AM_TIMEFRAMES]
                                    strategy_param["timegap"] = timegap

                                    strategy_param["ma3"] = ["sma", [3], self.get_candle_type(TICK), [QItem.close]]
                                    strategy_param["ma5"] = ["sma", [5], self.get_candle_type(TICK), [QItem.close]]
                                    strategy_param["ma10"] = ["sma", [10], self.get_candle_type(TICK), [QItem.close]]
                                    strategy_param["ma20"] = ["sma", [20], self.get_candle_type(TICK), [QItem.close]]

                                    strategy_param["market"] = markets[0].split('-')[1]
                                    strategy_param["is_use_model"] = IS_USE_MODEL
                                    strategy_param["is_use_tai"] = IS_USE_TAI
                                    strategy_param["pred_len"] = PRED_LEN
                                    strategy_param["tick"] = TICK
                                    strategy_param["candle_type"] = self.get_candle_type(TICK)

                                    ########################################
                                    strategy_param["tai_single_ma"] = ["sma", [MA], self.get_candle_type(TICK), [QItem.close]]
                                    # strategy_param['tai_golden_ma'] = ['sma', [MA], self.get_candle_type(TICK), [QItem.close]]
                                    # strategy_param['tai_macd_tf'] = ['macd', [12, 26, 9], self.get_candle_type(TICK), [QItem.close]]
                                    # strategy_param['tai_rsi_tf'] = ['rsi', [14], self.get_candle_type(TICK), [QItem.close]]
                                    # strategy_param['tai_ccl_tf'] = ['CCI',[],self.get_candle_type(TICK),[QItem.high, QItem.low, QItem.close],-50,-50,]
                                    # strategy_param['tai_bb_close_tf'] = [
                                    #     'bbands',
                                    #     [20, 2.0, 2.0, 0],
                                    #     self.get_candle_type(TICK),
                                    #     [QItem.close],
                                    # ]
                                    ########################################

                                    task.append((params_tobe_updated, ntask))
                                    ntask = ntask + 1

        self.run_multi_backtest(task)


if __name__ == "__main__":
    mp.set_start_method("spawn")
    unittest.main()
