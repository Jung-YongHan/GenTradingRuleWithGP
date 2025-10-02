import unittest
import sys
from bt4.utils.mylog import init_log
import bt4.utils.mylog as log_module
import bt4.exec.BullTraderMain as bm
from bt4.core.Interceptors import CompositeStgyInterceptor, HandleType
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
    si = CompositeStgyInterceptor(HandleType.Instant_Stream)
    si.update_params(params_tobe_updated)
    bm.main(sys.argv, si)
    stream_list, _result_dic = si.get_results()
    key = f'list_{simul_num}'
    result_dic[key] = stream_list
    key = f'dic_{simul_num}'
    result_dic[key] = _result_dic

class MultiProcessor_CompositeStgy(unittest.TestCase):

    # @unittest.skip("Tested")
    # Total Execution Times: 2x4x2x4 = 64 Times
    def test_bull_trader_multiple_strategies(self):

        # 전체: 2018 / 10 / 1(close: 737만)~2023 / 01 / 10(close: 2191만)
        # 상승장: 2020 / 10 / 1(close: 1244만)~2021 / 11 / 09(close: 8085만만)
        # 횡보장: 2018 / 10 / 1(close: 737만)~2020 / 10 / 31(close: 1560만)
        # 하락장: 2021 / 11 / 09(close: 8085만)~2023 / 01 / 10(close: 2091만)

        simul_starts = ['2018-10-01T08:59:00', '2020-10-01T08:59:00', '2018-10-01T08:59:00', '2021-11-09T08:59:00']
        simul_ends   = ['2023-01-10T08:59:00', '2021-11-09T08:59:00', '2020-10-31T08:59:00', '2023-01-10T08:59:00']

        # simul_starts = ['2018-10-01T08:59:00']
        # simul_ends   = ['2020-10-31T08:59:00']

        tgt_ex = 'upbit'
        cfg_prefix = f'bt3_config.{tgt_ex}.'
        confs = [f'{cfg_prefix}composite_bull_bear_market']

        marketss = [('KRW-BTC',),
                    ('KRW-ETH',),
                    ('KRW-BTC', 'KRW-ETH'),
                    ('KRW-BTC', 'KRW-ETH', 'KRW-XRP')]

        # marketss = [('KRW-BTC', 'KRW-ETH'),
        #             ('KRW-BTC', 'KRW-ETH', 'KRW-XRP')]

        # marketss = [('KRW-BCH',),
        #             ('KRW-ADA',),
        #             ('KRW-EOS',),
        #             ('KRW-QTUM', 'KRW-BCH'),
        #             ('KRW-EOS', 'KRW-ADA', 'KRW-BCH')
        #             ]

        # marketss = [('KRW-BTC', 'KRW-ETH', 'KRW-XRP')]

        vol_targets = [0.04, 0.03, 0.02]
        # vol_targets = [0.04]

        bull_strategy_confs = ['sws_day_vol', 'sws_ma_crossover_day_vol']
        bear_Strategy_confs = ['sws_day_vol', 'sws_4h_vol', 'sws_ma_crossover_day_vol']

        decisions = [
                     ['sma', [10], CandleType.DAYS, [QItem.close]],
                     ['sma', [20], CandleType.DAYS, [QItem.close]],
                     ['sma', [60], CandleType.DAYS, [QItem.close]],
                    ]

        ####################################################################
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
        self.file_name = join(root_dir, f'report/multi_exec_{nowDatetime}_composite_multi_processor.txt')
        csv_file_name = self.file_name + '.csv'

        with Manager() as manager:
            comm_channel_dic = manager.dict()

            for s_start, s_end in zip(simul_starts, simul_ends):
                params_tobe_updated[r.OP.BT.START] = s_start
                params_tobe_updated[r.OP.BT.END] = s_end

                for conf in confs:
                    sys.argv = ['BullTraderMain', 'backtestor', '-conf', conf]
                    params_tobe_updated['conf'] = conf

                    for markets in marketss:
                        params_tobe_updated[r.OP.MARKET] = markets

                        for vol in vol_targets:
                            params_tobe_updated[r.AM.AM_VOL_TARGET] = vol

                            strategy_param = {}

                            for bull_strategy_conf in bull_strategy_confs:
                                strategy_param['bull_mkt_conf'] = cfg_prefix + bull_strategy_conf
                                for bear_Strategy_conf in bear_Strategy_confs:
                                    strategy_param['bear_mkt_conf'] = cfg_prefix + bear_Strategy_conf

                                    for decision in decisions:
                                        strategy_param['tai_decision'] = decision
                                        params_tobe_updated[r.STGY.PARAMS] = strategy_param

                                        #################################################
                                        comm_channel_dic[f'params_tobe_updated_{simul_num}'] = params_tobe_updated

                                        q_t_val_processor = Process(target=startSimulation, args=(comm_channel_dic,simul_num))
                                        print(f'############### start process for simulating strategy #{simul_num}: {conf}')
                                        simul_num = simul_num + 1
                                        q_t_val_processor.start()
                                        procs.append(q_t_val_processor)

                                for p in procs:
                                    print(f'{p.name} am waiting for termination of another process... Try to JOIN. ')
                                    p.join()
                                    print(f'{p.name} am waiting for termination of another process... Done to JOIN')

                                for key in comm_channel_dic:
                                    if key.startswith('dic_'):
                                        result_dic = comm_channel_dic[key]
                                        df_strategy = pd.DataFrame(result_dic, index=['1'])
                                        dataframe = pd.concat([dataframe, df_strategy], ignore_index=True)

                            dataframe = dataframe.drop_duplicates(['conf', 'simul_start', 'simul_end', 'markets',
                                                                   'vol_target','bull_mkt_conf', 'bear_mkt_conf', 'tai_decision'])
                            dataframe.to_csv(csv_file_name)


        end = time.time()
        elapsed_time = end - start
        print(f'Elapsed Time: {elapsed_time}')


if __name__ == '__main__':
    unittest.main()

