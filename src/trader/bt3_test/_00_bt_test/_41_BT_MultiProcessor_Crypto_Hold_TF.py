import copy
import unittest
import sys

from bt4.utils.mylog import init_log
import bt4.utils.mylog as log_module
import bt4.exec.BullTraderMain as bm
from bt4.core.Interceptors import HandleType, TrendStgyHdgeInterceptor
from bt4.Constants import R, CandleType, QItem
from os.path import dirname, join
from datetime import datetime
import multiprocessing as mp
from multiprocessing import Process, Manager
import time
log_module.log_mode = 'simulator'
log = init_log()
import pandas as pd


def startSimulation(result_dic, simul_num):
    params_tobe_updated = result_dic[f'params_tobe_updated_{simul_num}']
    si = TrendStgyHdgeInterceptor(HandleType.Instant_Stream)
    si.update_params(params_tobe_updated)
    bm.main(sys.argv, si)
    stream_list, _result_dic = si.get_results()
    key = f'list_{simul_num}'
    result_dic[key] = stream_list
    key = f'dic_{simul_num}'
    result_dic[key] = _result_dic

class MultiProcessor_MultiStgy_Hdg(unittest.TestCase):

    # @unittest.skip("Tested")
    # Total Execution Times: 4x3x2x4 = 64 Times
    def test_bull_trader_multiple_strategies(self):

        # 전체: 2018 / 10 / 1(close: 737만)~2023 / 01 / 10(close: 2191만)
        # 상승장: 2020 / 10 / 1(close: 1244만)~2021 / 11 / 09(close: 8085만만)
        # 횡보장: 2018 / 10 / 1(close: 737만)~2020 / 10 / 31(close: 1560만)
        # 하락장: 2021 / 11 / 09(close: 8085만)~2023 / 01 / 10(close: 2091만)

        simul_starts = [ '2019-01-01T08:59:00']
        simul_ends   = [ '2024-04-30T08:59:00']
        # simul_starts = ['2018-10-01T08:59:00', '2020-10-01T08:59:00', '2018-10-01T08:59:00', '2021-11-09T08:59:00']
        # simul_ends = ['2023-03-15T08:59:00', '2021-11-09T08:59:00', '2020-10-31T08:59:00', '2023-03-15T08:59:00']

        tgt_ex = 'upbit'
        cfg_prefix = f'bt3_config.{tgt_ex}.'

        # conf = 'sws_day_hdg_vol'
        # conf = 'sws_day_hdg_vol_bitholder_tai'
        conf = '_migrated_sws_day_hdg_vol_bitholder_tai'
        # markets =  ('KRW-BTC', 'KRW-ETH', 'KRW-XRP')
        # markets =  ('KRW-ETH', )
        markets =  ('KRW-BTC', )

        # vol_targets = [0.04, 0.03, 0.02]
        vol_targets = [0.99, ]

        _1st_tf = [x for x in range(0 ,  6)]
        _1st_tf.append('X')
        _2nd_tf = [x for x in range(6 , 12)]
        _2nd_tf.append('X')
        _3rd_tf = [x for x in range(12, 18)]
        _3rd_tf.append('X')
        _4th_tf = [x for x in range(18, 23+1)]
        _4th_tf.append('X')

        timeframes_list = []
        for tf1 in _1st_tf:
            tflist1 = []
            if tf1 != 'X':
                tflist1.append(f'0{tf1}:59')
            for tf2 in _2nd_tf:
                tflist2 = copy.deepcopy(tflist1)
                if tf2 != 'X' :
                    tflist2.append(f'{tf2}:59' if tf2 >= 10 else f'0{tf2}:59')
                for tf3 in _3rd_tf:
                    tflist3 = copy.deepcopy(tflist2)
                    if tf3 != 'X' :
                        tflist3.append(f'{tf3}:59')
                    for tf4 in _4th_tf:
                        tflist4 = copy.deepcopy(tflist3)
                        if tf4 != 'X' :
                            tflist4.append(f'{tf4}:59')
                        if len(tflist4) > 0:
                            timeframes_list.append(tflist4)

        # timegaps_list = [0, 1, 2, 3]
        timegaps_list = [0]
        rsi_list = [30, 40, 50, 60, 70]
        cci_list = [-50, -60, -70, -80, -90]
        macd_list = [0]
        bb_list = [  3.0]

        ma_period_1 = [x for x in range(2, 5)]
        ma_period_2 = [x for x in range(5, 10)]
        ma_period_3 = [x for x in range(11, 20)]
        ma_period_4 = [x for x in range(20, 30)]

        params_tobe_updated = {}
        r = R()

        mp.set_start_method('spawn')

        procs = []
        simul_num = 0
        start = time.time()

        dataframe = pd.DataFrame()

        now = datetime.now()
        nowDatetime = now.strftime('%Y-%m-%dT%H_%M_%S')
        root_dir = dirname(dirname(dirname(__file__)))
        self.file_name = join(root_dir, f'report/multi_exec_{nowDatetime}_sws_param_optim')
        csv_file_name = self.file_name + '.csv'

        max_task = mp.cpu_count() - 5
        ntask = 1
        with Manager() as manager:
            comm_channel_dic = manager.dict()

            for s_start, s_end in zip(simul_starts, simul_ends):
                params_tobe_updated[r.OP.BT.START] = s_start
                params_tobe_updated[r.OP.BT.END] = s_end

                #############################
                conf_path = cfg_prefix + conf
                sys.argv = ['BullTraderMain', 'bt', '-conf', conf_path]
                params_tobe_updated['conf'] = conf

                #############################
                params_tobe_updated[r.OP.MARKET] = markets

                for vol in vol_targets:
                    params_tobe_updated[r.AM.AM_VOL_TARGET] = vol

                    for timegap in timegaps_list:
                        strategy_param = {}
                        params_tobe_updated[r.STGY.PARAMS] = strategy_param
                        for cci in cci_list:
                            strategy_param['tai_ccl_tf'] = ['CCI', [], CandleType.DAYS_TF, [QItem.high, QItem.low, QItem.close], cci, cci]
                        # for rsi in rsi_list:
                        #     strategy_param['tai_rsi_tf'] = ['rsi', [14], CandleType.DAYS_TF, [QItem.close], rsi, rsi]

                        # for ma1 in ma_period_1:
                        #     strategy_param['tai_ma1_tf'] = ['sma', [ma1], CandleType.DAYS_TF, [QItem.close]]
                        #     for ma2 in ma_period_2:
                        #         strategy_param['tai_ma2_tf'] = ['sma', [ma2], CandleType.DAYS_TF, [QItem.close]]
                        #         for ma3 in ma_period_3:
                        #             strategy_param['tai_ma3_tf'] = ['sma', [ma3], CandleType.DAYS_TF, [QItem.close]]
                        #             for ma4 in ma_period_4:
                        #                 strategy_param['tai_ma4_tf'] = ['sma', [ma4], CandleType.DAYS_TF, [QItem.close]]

                        # for ma3 in ma_period_3:
                        #     for ma4 in ma_period_4:
                        #         for macd_criti in macd_list:
                        #             strategy_param['tai_macd_tf'] = ['macd', [ma3, ma4, 9], CandleType.DAYS_TF, [QItem.close], macd_criti]
                        #
                        # for bb in bb_list:
                        #     strategy_param['tai_bb_close_tf'] = ['bbands', [20, bb, bb, 0], CandleType.DAYS_TF, [QItem.close]]

                            for timeframes in timeframes_list:
                                if ntask % max_task != 0:
                                    params_tobe_updated[r.AM.AM_TIMEFRAMES] = timeframes
                                    strategy_param['timeframes'] = params_tobe_updated[r.AM.AM_TIMEFRAMES]
                                    strategy_param['timegap'] = timegap

                                    comm_channel_dic[f'params_tobe_updated_{simul_num}'] = params_tobe_updated

                                    q_t_val_processor = Process(target=startSimulation, args=(comm_channel_dic,simul_num))
                                    print(f'############### start process for simulating strategy #{simul_num}: {conf}-{params_tobe_updated}')
                                    simul_num = simul_num + 1
                                    q_t_val_processor.start()
                                    procs.append(q_t_val_processor)

                                else:
                                    for p in procs:
                                        print(f'{p.name} am waiting for termination of another process... Try to JOIN. ')
                                        p.join()
                                        print(f'{p.name} am waiting for termination of another process... Done to JOIN')

                                    for key in comm_channel_dic:
                                        if key.startswith('dic_'):
                                            result_dic = comm_channel_dic[key]
                                            df_strategy = pd.DataFrame(result_dic, index=['1'])
                                            dataframe = pd.concat([dataframe, df_strategy], ignore_index=True)
                                    time.sleep(3)
                                    print(f'STOP and SLEEP 3 SEC...')
                                ntask += 1

                                dataframe = dataframe.drop_duplicates(['conf', 'simul_start', 'simul_end', 'markets', 'vol_target', 'timeframes', 'timegap',  'params'])
                                dataframe.to_csv(csv_file_name)


        end = time.time()
        elapsed_time = end - start
        print(f'Elapsed Time: {elapsed_time}')


if __name__ == '__main__':
    unittest.main()

