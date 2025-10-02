import unittest
import sys

from bt4.model.storage_mgr import StrategyStorage
from bt4.utils.mylog import init_log
import bt4.utils.mylog as log_module
import bt4.exec.BullTraderMain as bm
from bt4.core.Interceptors import TrendStgyInterceptor, HandleType
from bt4.Constants import R, CandleType, QItem
from os.path import dirname, join
from datetime import datetime
import multiprocessing as mp
from multiprocessing import Process, Manager
import time

from bt4.utils.python_utils import load_class_from_module

log_module.log_mode = 'simulator'
log = init_log()
import pandas as pd

def startSimulation(result_dic, simul_num):
    params_tobe_updated = result_dic[f'params_tobe_updated_{simul_num}']
    si = TrendStgyInterceptor(HandleType.Instant_Stream)
    si.update_params(params_tobe_updated)
    bm.main(sys.argv, si)
    stream_list, _result_dic = si.get_results()
    key = f'list_{simul_num}'
    result_dic[key] = stream_list
    key = f'dic_{simul_num}'
    result_dic[key] = _result_dic

class MultiProcessor_MultiStgy(unittest.TestCase):

    # @unittest.skip("Tested")
    # Total Execution Times: 2x4x2x4 = 64 Times
    def test_bull_trader_multiple_strategies(self):

        # 전체: 2019 / 01 / 01(close: 737만)~2023 / 01 / 10(close: 2191만)
        # 상승장: 2020 / 10 / 1(close: 1244만)~2021 / 11 / 09(close: 8085만만)
        # 횡보장: 2018 / 10 / 1(close: 737만)~2020 / 10 / 31(close: 1560만)
        # 하락장: 2021 / 11 / 09(close: 8085만)~2023 / 01 / 10(close: 2091만)

        simul_starts = ['2020-10-01T08:59:00', '2019-01-01T08:59:00', '2021-11-09T08:59:00', '2019-01-01T08:59:00']
        simul_ends   = ['2021-11-09T08:59:00', '2020-10-01T08:59:00', '2023-01-10T08:59:00', '2023-01-10T08:59:00']

        # simul_starts = ['2022-12-25T08:59:00']
        # simul_ends =   ['2023-01-10T08:59:00']

        tid = StrategyStorage.instance().get_trading_id_of_stgyname("bt", "ws_day_vol")

        marketss = [('KRW-BTC',),
                    ('KRW-ETH',),
                    ('KRW-XRP',),
                    ('KRW-BCH',),
                    ]

        ma_periods = [5,10,20]

        # cdls = [CandleType.HOUR]

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
        self.file_name = join(root_dir, f'report/multi_exec_{nowDatetime}_multi_processor.txt')
        csv_file_name = self.file_name + '.csv'

        max_task = mp.cpu_count() / 2
        # max_task = 4
        # max_task = 1
        ntask = 1

        with Manager() as manager:
            comm_channel_dic = manager.dict()

            for s_start, s_end in zip(simul_starts, simul_ends):
                params_tobe_updated[r.OP.BT.START] = s_start
                params_tobe_updated[r.OP.BT.END] = s_end

                sys.argv = ['BullTraderMain', 'bt', '-tid', f"{tid}"]

                for markets in marketss:
                    params_tobe_updated[r.OP.MARKET] = markets

                    for ma_period in ma_periods:
                        strategy_param = {}
                        strategy_param["ma"] = ["sma", [ma_period,],CandleType(1440), [QItem("close"),]]
                        params_tobe_updated[r.STGY.PARAMS] = strategy_param

                        comm_channel_dic[f'params_tobe_updated_{simul_num}'] = params_tobe_updated

                        q_t_val_processor = Process(target=startSimulation, args=(comm_channel_dic,simul_num))
                        print(f'############### start process for simulating strategy #{simul_num}({s_start}~{s_end}) -{markets}')
                        simul_num = simul_num + 1
                        q_t_val_processor.start()
                        procs.append(q_t_val_processor)
                        time.sleep(1)
                        if ntask % max_task == 0 :
                            for p in procs:
                                print(f'{p.name} am waiting for termination of another process... Try to JOIN. ')
                                p.join()
                                print(f'{p.name} am waiting for termination of another process... Done to JOIN')

                            for key in comm_channel_dic:
                                if key.startswith('dic_'):
                                    result_dic = comm_channel_dic[key]
                                    self.post_process_results(result_dic)
                                    df_strategy = pd.DataFrame(result_dic, index=['1'])
                                    dataframe = pd.concat([dataframe, df_strategy], ignore_index=True)
                            comm_channel_dic.clear()

                            # dataframe = dataframe.drop_duplicates(['conf', 'simul_start', 'simul_end', 'markets', 'params', 'cdl_type'])
                            dataframe.to_csv(csv_file_name)

                        ntask += 1




        end = time.time()
        elapsed_time = end - start
        print(f'Elapsed Time: {elapsed_time}')

    def load_rules(self, cfg) :
        params = {}
        r = R()
        config = load_class_from_module(cfg, 'Config')
        config.load_params(r, params)
        stgy_params = params[r.STGY.PARAMS]
        stgy_params.pop("rebalance")
        ## Disable All Rules
        for rule in stgy_params:
            stgy_params[rule]["enable"] = False
        return stgy_params

    def post_process_results(self, result_dic) :
        param_dict = result_dic["params_dict"]
        target_rule = ""
        for param in param_dict:
            if param.endswith("_rule"):
                if param_dict[param]["enable"] == True:
                    target_rule = param
        result_dic["params"] = target_rule
        result_dic.pop("params_dict")



if __name__ == '__main__':
    unittest.main()

