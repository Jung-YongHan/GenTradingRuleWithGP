import json
import os
import random
import signal
import sys
import threading
import time
from multiprocessing import Lock, Process, Manager

from mealpy import Problem, BinaryVar

from bt4.Constants import R
from bt4.core.Interceptors import HandleType, TrendStgyInterceptor
from bt4.model.storage_mgr import StrategyStorage
from bt4.model.trade_request_support import rebuild_stgy_rules_from_ga_decoded
from bt4.utils.misc_utils import load_bt4_config
import pandas as pd
import bt4.exec.BullTraderMain as bm
import numpy as np

from abc import abstractmethod
from mealpy.evolutionary_based import GA


optim_pgm_grid = {
    "epoch"    : [10],
    "pop_size" : [10],
    # "pc"       : [0.85, 0.90, 0.95],
    # "pm"       : [0.015, 0.025, 0.035]
    "pc"       : [0.85, 0.95],
    "pm"       : [0.015, 0.035]
}

default_term_dict = {
    # "max_epoch": 10,
    # "max_time": 20,
    "max_fe": 500,
    # "max_fe": 10,
    # "max_early_stop": 5
}


class GAOptimizer:

    def __init__(self):
        pass

    @abstractmethod
    def create_problem(self) :
        pass

    @abstractmethod
    def setup_cfg_with_encoded_problem(self, r, encoded_pblm, stgy_cfg_param):
        pass

    @abstractmethod
    def validate_stgy_cfg_param(self, stgy_cfg_param):
        pass

    @abstractmethod
    def get_term_dict(self) :
        pass

    def start_ga_optim(self):
        # problem = self.create_problem()
        # model1 = GA.BaseGA()

        # tuner = Tuner(model1, optim_pgm_grid)
        # n_cpu = cpu_count()
        # tuner.execute(problem = problem_dict, termination = term, n_trials = 1, mode = "single")

        problem = self.create_problem()

        problem.registe_shutdown_hook()

        # model = GA.BaseGA(optim_pgm_grid)
        # model = GA.BaseGA(epoch=10000, pop_size=50, pc=0.85, pm=0.05)
        model = GA.BaseGA(epoch = 10000, pop_size = 50, pc = 0.85, pm = 0.001)
        # best_agent = model.solve(problem)
        ga_term_dict = self.get_term_dict()
        if ga_term_dict is None:
            ga_term_dict = default_term_dict
        best_agent = model.solve(problem, termination = ga_term_dict)

        print(best_agent.solution)
        print(problem.decode_solution(best_agent.solution))
        print(best_agent.target.fitness)
        print(model.get_parameters())
        print(model.get_name())
        print(model.problem.get_name())

        return best_agent


class GAProblem(Problem):

    def __init__(self, stgy_optim, tid, stgy_name, cfg_module, ga_hist_output, ga_markets,
                 bounds, minmax = "min",
                 **kwargs) :
        self.stgy_optim = stgy_optim
        r = R()
        self.tid = tid
        self.stgy_name = stgy_name
        self.cfg_module = cfg_module
        self.stgy_cfg_param = load_bt4_config(cfg_module)
        self.stgy_cfg_param[r.STGY.NAME] = stgy_name
        self.stgy_name = stgy_name
        self.ga_history_df = pd.DataFrame()
        self.idx = 0
        self.ga_hist_output = ga_hist_output
        self.ga_markets = ga_markets

        stgy_model = StrategyStorage.instance().load_strategy_using_tid(self.tid)
        self.stgy_json = stgy_model.cfg_stgy_rules_json
        self.exec_count = 0
        self.emergency_stop = False

        super().__init__(bounds, minmax, **kwargs)

    """
    overriding of Problem for handling "markets" and "timeframes" not to be selected anything. 
    """
    def generate_solution(self, encoded: bool = True):
        flag = False
        generated_solution = None
        while not flag:
            generated_solution = self.generate_solution_with_bounds(self.bounds, encoded)
            gen_decoded_sol = self.decode_solution(generated_solution)
            print(f"{threading.current_thread().ident}::{gen_decoded_sol=}")
            is_markets_okay = False

            if "markets" in gen_decoded_sol:
                selected_any_markets = False
                for mkt_bool in gen_decoded_sol["markets"]:
                    if mkt_bool == 1:
                        selected_any_markets = True
                        break

                if not selected_any_markets:
                    print(f"not selected any markets: {gen_decoded_sol['markets']}")
                    continue
                else:
                    is_markets_okay = True
            else:
                is_markets_okay = True

            is_timeframes_okay = False
            if "timeframes" in gen_decoded_sol:
                selected_any_timeframes = False
                for tf_bool in gen_decoded_sol["timeframes"]:
                    if tf_bool == 1:
                        selected_any_timeframes = True
                        break

                if not selected_any_timeframes:
                    print(f"not selected any timeframes: {gen_decoded_sol['timeframes']}")
                    continue
                else:
                    is_timeframes_okay = True
            else:
                is_timeframes_okay = True

            if is_markets_okay and is_timeframes_okay:
                flag = True
            else:
                continue

        gen_decoded_sol = self.decode_solution(generated_solution)
        print(f"before return {threading.current_thread().ident}::{gen_decoded_sol=}")
        return generated_solution

    """
        overriding of Problem for handling "markets" and "timeframes" not to be selected anything. 
    """
    def correct_solution(self, x: np.ndarray) -> np.ndarray:
        x_new, n_vars = [], 0
        for idx, var in enumerate(self.bounds):
            if isinstance(var, BinaryVar) :
                tgt = x[n_vars :n_vars + var.n_vars]
                if not any(tgt): # when all tgt values ==0, return False
                    while True:
                        gen_tgt = var.generate()
                        if not any(gen_tgt):
                            continue
                        else:
                            x_new += list(gen_tgt)
                            n_vars += var.n_vars
                            break
                else:
                    x_new += list(var.correct(x[n_vars :n_vars + var.n_vars]))
                    n_vars += var.n_vars
            else:
                x_new += list(var.correct(x[n_vars :n_vars + var.n_vars]))
                n_vars += var.n_vars
        return np.array(x_new)


    def registe_shutdown_hook(self):
        """
        handling stopping GA
        :return:
        """
        signal.signal(signal.SIGTERM, self.handle_exit)
        signal.signal(signal.SIGINT, self.handle_exit)
        print("registrating shutdown hook!!")

    def handle_exit(self, *args):
        print("handling exit!!")
        self.emergency_stop = True

    def obj_func(self, sol):
        if self.emergency_stop:
            print("Emergency stop of GA has been enabled!")
            print("GA Termination has been successfully done.")
            sys.exit(1)
            return [0, 0]

        # ga_params = self.encode_problem(sol)
        self.exec_count += 1
        x_decoded = self.decode_solution(sol)
        print(f"## #{self.exec_count} times execution of obj_func with {x_decoded}")

        ## Config Setting
        r = R()
        self.stgy_cfg_param = self.stgy_optim.setup_cfg_with_encoded_problem(r, x_decoded, self.stgy_cfg_param)

        ## loading trade_request and update the decoded_solution from GA
        updated_stgy_json, updated_ga_decoded = rebuild_stgy_rules_from_ga_decoded(self.stgy_json, x_decoded)
        ##########################################################################
        if os.path.exists(self.ga_hist_output):
            lock = Lock()
            while True :
                with lock :
                    try :
                        self.ga_history_df = pd.read_csv(self.ga_hist_output, index_col = 'idx')
                        break
                    except IOError :
                        time.sleep(1)
                    except pd.errors.EmptyDataError:
                        time.sleep(1)

            if self.ga_history_df.empty == False :
                cached_result_df = self.ga_history_df.loc[self.ga_history_df['params'] == f'{x_decoded}']

                if cached_result_df.empty == False:
                    cached_result_df = cached_result_df.tail(1)
                    print(f'## The same parameter exists in the result cache of GA : parameter - {x_decoded.items()} ')
                    print(f"{cached_result_df['mpr']=}")
                    mpr = float(cached_result_df['mpr'].iloc[0])
                    mdd = float(cached_result_df['mdd'].iloc[0])
                    return [mpr, mdd]
                else:
                    print(f'## Not exist in the result cache of GA : parameter - {x_decoded.items()} ')

        ##########################################################################
        ## Execute Backtestor

        with Manager() as manager :
            comm_channel_dic = manager.dict()
            p = Process(target = startSimulation, args = (self.stgy_cfg_param, self.tid, updated_ga_decoded, updated_stgy_json, comm_channel_dic))
            p.start()

            print("waiting for join...")

            while p.is_alive() :
                p.join(timeout = 1)  # Check every second if the process is still running

            _result_dic = comm_channel_dic["result_dic"]

        # si = TrendStgyInterceptor(HandleType.Instant_Stream)
        # si.update_params(self.stgy_cfg_param)
        # sys.argv = ["BullTraderMain", "bt", "-tid", f"{self.tid}"]
        # ctx, _ = bm.main(sys.argv, si)
        #
        # ga_decoded_json = json.dumps(updated_ga_decoded)
        # ctx.report_storage.update_ga_params(updated_stgy_json, ga_decoded_json)
        # _, _result_dic = si.get_results()

        # print("sleeping for three seconds for terminating...")
        # time.sleep(10)
        #
        # ## for Testing
        # _result_dic = {"mpr":0, "mdd":0, "selection_index":0,
        #                "num_of_trades":0, "trade_win_rate":0, }


        ##########################################################################
        mpr = float(_result_dic['mpr'])
        mdd = float(_result_dic['mdd'])
        sel_index = float(_result_dic['selection_index'])
        num_of_trades = _result_dic['num_of_trades']
        winning_rate  = _result_dic['trade_win_rate']
        print(f'#### {self.stgy_name} with {updated_ga_decoded} execution result ==>'
              f' selection idx: {sel_index} '
              f' mdd: {mdd} monthly profit ratio: {mpr} trades : {num_of_trades}'
              f' winning rate : {winning_rate}')
        _result_dic['params'] = f'{updated_ga_decoded}'
        result_df = pd.DataFrame(_result_dic, index=[self.idx])

        lock = Lock()
        while True :
            with lock :
                try :
                    if os.path.exists(self.ga_hist_output) :
                        self.ga_history_df = pd.read_csv(self.ga_hist_output, index_col = 'idx')
                        self.ga_history_df = pd.concat([self.ga_history_df, result_df], axis = 0)
                    else :
                        self.ga_history_df = result_df

                    self.ga_history_df.index.name = 'idx'
                    self.ga_history_df.to_csv(self.ga_hist_output)
                    self.idx = self.idx + 1
                    break
                except IOError :
                    # If the file is not accessible, wait for 1 second and try again
                    time.sleep(1)

        ###########################################################################
        cache_result = [mpr, (100+mdd)]
        # self.result_cache[cache_key] = cache_result
        return cache_result

def startSimulation(stgy_cfg_param, tid, updated_ga_decoded, updated_stgy_json, comm_channel_dic):
    si = TrendStgyInterceptor(HandleType.Instant_Stream)
    si.update_params(stgy_cfg_param)
    sys.argv = ["BullTraderMain", "bt", "-tid", f"{tid}"]
    ctx, _ = bm.main(sys.argv, si)

    ga_decoded_json = json.dumps(updated_ga_decoded)
    ctx.report_storage.update_ga_params(updated_stgy_json, ga_decoded_json)
    _, _result_dic = si.get_results()
    comm_channel_dic["result_dic"] = _result_dic
