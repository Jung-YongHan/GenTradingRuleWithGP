from mealpy import FloatVar, IntegerVar

from bt4.core.ga_optim import GAOptimizer, GAProblem
from bt4.utils.python_utils import dt2str_for_filename, now_dt


class GAWinningSessionDayOptim(GAOptimizer):

    def __init__(self, tid, stgy_name, cfg_module, ga_hist_output):
        self.tid = tid
        self.stgy_name = stgy_name
        self.cfg_module = cfg_module
        self.ga_hist_output = ga_hist_output


    def create_problem(self) :
        my_bounds = [
            FloatVar(lb = 0.2, ub = 0.4, name = "tgt_vol"),
            IntegerVar(lb = 3, ub = 20, name = "ma_period"),
            IntegerVar(lb = 0, ub = 23, name = "buy_hour"),
            IntegerVar(lb = 0, ub = 23, name = "sell_hour"),
            # StringVar(valid_sets = ('linear', 'poly', 'rbf', 'sigmoid'), name = "kernel_paras")
        ]

        problem_dic = {
            "obj_weights"     : [0.4, 0.4, 0.2],
            "save_population" : True,
            "name"            : self.stgy_name,
            "log_to"          : "file",
            "log_file"        : f"ga_{self.stgy_name}_{dt2str_for_filename(now_dt())}.log",
            # Default value = "mealpy.log"
        }

        problem = GAProblem(self, self.tid, self.stgy_name, self.cfg_module,
                            self.ga_hist_output, my_bounds, "max",
                            **problem_dic)
        return problem

    def setup_cfg_with_encoded_problem(self, r, encoded_pblm, stgy_cfg_param):
        stgy_cfg_param[r.AM.AM_VOL_TARGET] = encoded_pblm['tgt_vol']
        bt_time = [encoded_pblm['buy_hour'], encoded_pblm['sell_hour']]
        stgy_cfg_param[r.OP.BT.TIME] = bt_time
        stgy_cfg_param[r.STGY.PARAMS]['base_time'] = f"{encoded_pblm['buy_hour']}:59"
        stgy_cfg_param[r.STGY.PARAMS]['sell_time'] = f"{encoded_pblm['sell_hour']}:59"
        ma_params = stgy_cfg_param[r.STGY.PARAMS]['ma']
        ma_params[1] = [encoded_pblm['ma_period']]

        return stgy_cfg_param


    def validate_stgy_cfg_param(self, r, stgy_cfg_param):
        return True

