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

        simul_starts = ['2018-10-01T08:59:00', '2020-10-01T08:59:00', '2018-10-01T08:59:00', '2021-11-09T08:59:00']
        simul_ends   = ['2023-01-10T08:59:00', '2021-11-09T08:59:00', '2020-10-31T08:59:00', '2023-01-10T08:59:00']

        tgt_ex = 'upbit'
        cfg_prefix = f'bt3_config.{tgt_ex}.'

        conf = 'ws_day_hdg_vol_mma'
        markets =  ('KRW-BTC', 'KRW-ETH', 'KRW-XRP')

        vol_targets = [0.04]

        timeframes = ['08:59', '17:59']
        timegap = 1

        ma_period_1 = [x for x in range(2, 10)]
        ma_period_2 = [x for x in range(5, 20)]

        params_tobe_updated = {}
        r = R()

        mp.set_start_method('spawn')

        procs = []
        simul_num = 0
        start = time.time()

        dataframe = pd.DataFrame()

        now = datetime.now()
        nowDatetime = now.strftime('%Y-%m-%dT%H_%M_%S')
        root_dir = dirname(dirname(__file__))
        self.file_name = join(root_dir, f'report/multi_exec_{nowDatetime}_ws_2ma_optim.txt')
        csv_file_name = self.file_name + '.csv'

        max_task = mp.cpu_count() - 3
        ntask = 1
        with Manager() as manager:
            comm_channel_dic = manager.dict()

            for s_start, s_end in zip(simul_starts, simul_ends):
                params_tobe_updated[r.OP.BT.START] = s_start
                params_tobe_updated[r.OP.BT.END] = s_end

                #############################
                conf_path = cfg_prefix + conf
                sys.argv = ['BullTraderMain', 'backtestor', '-conf', conf_path]
                params_tobe_updated['conf'] = conf

                #############################
                params_tobe_updated[r.OP.MARKET] = markets

                for vol in vol_targets:
                    params_tobe_updated[r.AM.AM_VOL_TARGET] = vol
                    params_tobe_updated[r.AM.AM_TIMEFRAMES] = timeframes
                    strategy_param = {}
                    params_tobe_updated[r.STGY.PARAMS] = strategy_param

                    for ma1 in ma_period_1:
                        strategy_param['tai_ma_tf1'] = ['sma', [ma1], CandleType.DAYS_TF, [QItem.close]]
                        for ma2 in ma_period_2:
                            strategy_param['tai_ma_tf2'] = ['sma', [ma2], CandleType.DAYS_TF, [QItem.close]]

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

                                dataframe = dataframe.drop_duplicates(
                                    ['conf', 'simul_start', 'simul_end', 'markets', 'vol_target', 'timeframes',
                                     'timegap', 'params'])
                                dataframe.to_csv(csv_file_name)
                                print(f'STOP and SLEEP 3 SEC...')
                            ntask += 1




        end = time.time()
        elapsed_time = end - start
        print(f'Elapsed Time: {elapsed_time}')


if __name__ == '__main__':
    unittest.main()

