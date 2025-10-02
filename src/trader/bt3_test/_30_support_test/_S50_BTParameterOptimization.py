import unittest

from bt4.core.Interceptors import TrendStgyHdgeInterceptor, HandleType
import bt4.exec.BullTraderMain as bm
import sys
from bt4.Constants import R, CandleType, QItem
from os.path import dirname, join
from datetime import datetime
import multiprocessing as mp
from multiprocessing import Process, Manager
import time
from bt4.utils.mylog import init_log
import bt4.utils.mylog as log_module
import pandas as pd

from bt4.optim.AdaptiveWSParamOptim import AdaptiveWSParamOptim

log_module.log_mode = 'simulator'
log = init_log()


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

class MyTestCase(unittest.TestCase) :
    def test_parameter_optimization(self) :
        import warnings
        warnings.filterwarnings("ignore", category = DeprecationWarning)

        # simul_start = '2021-10-01T08:59:00'
        # simul_end  = '2021-11-01T08:59:00'
        simul_start = '2018-11-01T08:59:00'
        simul_end = '2018-12-01T08:59:00'

        malist = [3,5,10,20]

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
        self.file_name = join(root_dir, f'report/multi_exec_{nowDatetime}_multi_processor.txt')
        csv_file_name = self.file_name + '.csv'

        market = ('KRW-BTC', )

        # timeframes_list = [
        #     ['07:59', '17:59'],
        #     ['07:59', '18:59'],
        #     ['07:59', '19:59'],
        #     ['07:59', '20:59'],
        #     ['07:59', '21:59'],
        #     ['07:59', '22:59'],
        #     ['08:59', '17:59'],
        #     ['08:59', '18:59'],
        #     ['08:59', '19:59'],
        #     ['08:59', '20:59'],
        #     ['08:59', '21:59'],
        #     ['08:59', '22:59'],
        # ]
        # timegaps_list = [0, 1, 2, ]

        with Manager() as manager:
            comm_channel_dic = manager.dict()

            params_tobe_updated[r.OP.BT.START] = simul_start
            params_tobe_updated[r.OP.BT.END] = simul_end

            conf_path = "bt3_config.upbit.ws_day_hdg_volume_vol"
            sys.argv = ['BullTraderMain', 'backtestor', '-conf', conf_path]
            params_tobe_updated['conf'] = conf_path

            params_tobe_updated[r.OP.MARKET] = market

            # for timegap in timegaps_list :

            strategy_param = {}
            params_tobe_updated[r.STGY.PARAMS] = strategy_param
                # for timeframes in timeframes_list :
                #     params_tobe_updated[r.AM.AM_TIMEFRAMES] = timeframes
                #     strategy_param['timeframes'] = params_tobe_updated[r.AM.AM_TIMEFRAMES]
                #     strategy_param['timegap'] = timegap

            for price_ma_period in malist:
                for volume_ma_period in malist:
                    strategy_param['tai_ma_tf'] = ['sma', [price_ma_period], CandleType.DAYS_TF, [QItem.close]]
                    strategy_param['tai_vol_ma_tf'] = ['sma', [volume_ma_period], CandleType.DAYS_TF, [QItem.vol]]

                    comm_channel_dic[f'params_tobe_updated_{simul_num}'] = params_tobe_updated

                    q_t_val_processor = Process(target=startSimulation, args=(comm_channel_dic,simul_num))
                    print(f'############### start process for simulating strategy #{simul_num}: {conf_path}')
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

            dataframe = dataframe.drop_duplicates(['conf', 'simul_start', 'simul_end', 'markets', 'timeframes', 'timegap', 'tai_ma_tf', 'tai_vol_ma_tf'])
            dataframe.to_csv(csv_file_name)

        end = time.time()
        elapsed_time = end - start
        optimal_params= {}
        dataframe["sharp_index"] = dataframe["sharp_index"].astype("float")
        optimal_params["sharp_index"] = dataframe["sharp_index"].max()
        optimal_params["tai_ma_tf"] = dataframe.loc[dataframe["sharp_index"] == dataframe["sharp_index"].max()]["tai_ma_tf"].item()
        optimal_params["tai_vol_ma_tf"] = dataframe.loc[dataframe["sharp_index"] == dataframe["sharp_index"].max()]["tai_vol_ma_tf"].item()
        print(f'Elapsed Time: {elapsed_time}')
        print(f"{optimal_params=}")
        print(f'Elapsed Time: {elapsed_time}')

    def test_parameter_optimization2(self) :
        awso = AdaptiveWSParamOptim()

        # simul_start = '2018-11-01T08:59:00'
        # simul_end = '2018-12-01T08:59:00'
        simul_start = '2020-10-01T08:59:00'
        simul_end = '2021-04-25T08:59:00'
        market = ("KRW-BTC",)
        malist = [3, 5, 10, 20]

        optimal_params = awso.getOptimalParameters(simul_start, simul_end, market, malist)
        print(optimal_params)


if __name__ == '__main__' :
    unittest.main()
