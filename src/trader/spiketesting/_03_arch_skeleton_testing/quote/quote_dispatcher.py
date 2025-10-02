import random
import time
from multiprocessing import cpu_count, Manager, Process

from bt4.Constants import CandleType
from bt4.quote.QuoteMgr import QuoteStorageMgr
from bt4.quote.TAIndicatorMgr import TAIndicatorMgr
from spiketesting._03_arch_skeleton_testing.quote.iquote_dispatcher import IQuoteDispacher
import bulltrader_conf.quote.quote_config as QC
import pandas as pd
import multiprocessing as mp
from spiketesting._03_arch_skeleton_testing.utils import divide_period

from bt4.utils.mylog import init_log

log = init_log()

class LocalQuoteJobDistributor(IQuoteDispacher):
    def __init__(self):
        qd_params = QC.QUOTE_DISPATCHER_PARAMS
        self.q_connector_name = qd_params[QC.PARAM_QUOTE_CONNECTOR]
        self.markets = qd_params[QC.PARAM_MARKET]
        self.tai_mgr = TAIndicatorMgr(qd_params, True)
        self.timeframe_hours = qd_params[QC.PARAM_TIMEFRAME_HOURS]
        self.simul_storage = QuoteStorageMgr.instance()

    def initialize(self):
        print(f'[{self.__class__.__name__}] initialize')

    def process_quote(self):
        print(f'[{self.__class__.__name__}] process_quote')

    def process_local_quote(self, markets, simul_start_dt, simul_end_dt, simul_times, simul_tais,
                            simul_data_type=CandleType.MINUTES_1):
        print(f'[{self.__class__.__name__}] process_local_quote'
              f'{markets=}, {simul_start_dt=}, {simul_end_dt=}, {simul_times=}, '
              f'{simul_tais=}, {simul_data_type=}')

        start_pdt = pd.to_datetime(simul_start_dt)
        end_pdt = pd.to_datetime(simul_end_dt)

        cpus = cpu_count()
        # cpus = 3
        quote_ranges = divide_period(start_pdt, end_pdt, cpus-2)
        process_list = []
        mp.set_start_method('spawn')
        start = time.time()
        with Manager() as manager:
            comm_channel_dic = manager.dict()
            for proc_idx, quote_range in enumerate(quote_ranges):
                print(f'backtesting range {quote_range.left}~{quote_range.right}')

                start_pdt= quote_range.left
                end_pdt = quote_range.right
                _1m_simul_dfs = self.simul_storage.load_quote_in_range2(markets,
                                                                        start_pdt, end_pdt, CandleType.MINUTES_1)
                bt_unit_process = Process(target=start_back_testing_unit,
                                            args=(comm_channel_dic, proc_idx, _1m_simul_dfs,
                                                  start_pdt, end_pdt))

                print(f'############### start process for simulating strategy #{proc_idx}')
                bt_unit_process.start()
                process_list.append(bt_unit_process)

            for proc in process_list:
                print(f'{proc.name} am waiting for termination of another process... Try to JOIN. ')
                proc.join()
                print(f'{proc.name} am waiting for termination of another process... Done to JOIN')

            for key in comm_channel_dic:
                print(f'result from each process : {key} - {comm_channel_dic[key]}')

        end = time.time()
        elapsed_time = end - start
        log.debug(f'Simulation Elapsed time:{elapsed_time} sec!')

def start_back_testing_unit(result_dic, proc_idx, _1m_simul_dfs, start_pdt, end_pdt):

    print(f'[[{proc_idx}]] starting... : {start_pdt}~{end_pdt} ')

    time.sleep(random.uniform(1, 10))

    for market in _1m_simul_dfs:
        market_df = _1m_simul_dfs[market]
        market_df.index = pd.to_datetime(market_df.index)
        ranged_mdf = market_df[start_pdt:end_pdt]
        print(f'[[{proc_idx}]] processing... {market} - range {start_pdt}~{end_pdt} : {len(ranged_mdf)}')
        num = 0
        for index, row in ranged_mdf.iterrows():
            if num % 100000 == 0:
                print(f'[[{proc_idx}]] {market} ==> {index}')
            num = num + 1

    result_dic[f'result_{proc_idx}'] = f'result_of_{proc_idx}_backtesting_period:{start_pdt}~{end_pdt}'



class ExchangeQuoteDispatcher(IQuoteDispacher):
    def __init__(self):
        pass

    def initialize(self):
        print(f'[{self.__class__.__name__}] initialize')

    def process_quote(self):
        print(f'[{self.__class__.__name__}] process_quote')

    def process_local_quote(self, markets, simul_start_dt, simul_end_dt, simul_times, simul_tais,
                            simul_data_type=CandleType.MINUTES_1):
        print(f'[{self.__class__.__name__}] process_local_quote')

class MockQuoteDispatcher(IQuoteDispacher):
    def __init__(self):
        pass

    def initialize(self):
        print(f'[{self.__class__.__name__}] initialize')

    def process_quote(self):
        print(f'[{self.__class__.__name__}] process_quote')

    def process_local_quote(self, markets, simul_start_dt, simul_end_dt, simul_times, simul_tais,
                            simul_data_type=CandleType.MINUTES_1):
        print(f'[{self.__class__.__name__}] process_local_quote')