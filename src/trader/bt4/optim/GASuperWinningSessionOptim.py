from mealpy import FloatVar

from bt4.Constants import R
from bt4.core.ga_optim import GAParamOptimizer
import numpy as np

from bt4.utils.misc_utils import calibrate_simul_env2
from bt4.utils.python_utils import dt2str_for_filename, now_dt


class GASuperWinningSessionDayOptim(GAParamOptimizer):
    def __init__(self, tid, stgy_name, cfg_module, ga_hist_output):
        super(GASuperWinningSessionDayOptim, self).__init__(tid, stgy_name, cfg_module, ga_hist_output)

    def create_problem(self):
        TGT_VOL_LB = [2.00]         # 0.2~0.4
        TGT_VOL_UB = [4.99]
        MA_PERIODS_LB = [3.00,  5.00, 10.00, 20.00]
        MA_PERIODS_UB = [4.99,  9.99, 19.99, 29.99]
        BUY_HOUR_LB = [0.0]         # 0~23
        BUY_HOUR_UB = [23.99]
        SELL_HOUR_LB = [0.0]        # 0~23
        SELL_HOUR_UB = [23.99]

        LBS = []
        LBS.extend(TGT_VOL_LB)
        LBS.extend(MA_PERIODS_LB)
        LBS.extend(BUY_HOUR_LB)
        LBS.extend(SELL_HOUR_LB)

        UBS = []
        UBS.extend(TGT_VOL_UB)
        UBS.extend(MA_PERIODS_UB)
        UBS.extend(BUY_HOUR_UB)
        UBS.extend(SELL_HOUR_UB)

        problem = {
            "obj_func": self.fitness_function,
            "bounds" : FloatVar(lb = LBS, ub = UBS),
            "minmax": "max",
            "obj_weights": [0.4, 0.4, 0.2],
            "save_population": True,
            "name" : self.stgy_name,
            "log_to"   : "file",
            "log_file" : f"ga_{self.stgy_name}_{dt2str_for_filename(now_dt())}.log",  # Default value = "mealpy.log"
        }
        return problem

    def encode_problem(self, problem):
        tgt_vol   = int(problem[0]) / 100 ## range 0.02~0.04
        ma_periods_int = problem[1:5].astype(int)
        _ma_periods_idx_wo0 = np.where(ma_periods_int != 0)[0]
        ma_periods = ma_periods_int[_ma_periods_idx_wo0].tolist()
        buy_hour  = int(problem[5])       ## range 0~23
        zero_padding_buy_hour = f"0{buy_hour}" if buy_hour < 10 else buy_hour
        sell_hour = int(problem[6])       ## range 0~23

        e_problems = {
            "tgt_vol"   : tgt_vol,
            "buy_hour"  : f'{zero_padding_buy_hour}:59',
            "sell_hour" : f'{sell_hour}:59',
            "ma1_period" : ma_periods[0],
            "ma2_period" : ma_periods[1],
            "ma3_period" : ma_periods[2],
            "ma4_period" : ma_periods[3],
        }
        return e_problems

    def decode_solution(self, sol):
        tgt_vol  = int(sol[0]) / 100 ## range 0.01~0.04
        ma1_period = int(sol[1])
        ma2_period = int(sol[2])
        ma3_period = int(sol[3])
        ma4_period = int(sol[4])
        buy_hour = int(sol[5])
        zero_padding_buy_hour  = f"0{buy_hour}" if buy_hour < 10 else buy_hour
        sell_hour = int(sol[6])

        d_sol = {
            "tgt_vol": tgt_vol,
            "buy_hour": zero_padding_buy_hour,
            "sell_hour": sell_hour,
            "ma1_period":  ma1_period,
            "ma2_period" : ma2_period,
            "ma3_period" : ma3_period,
            "ma4_period" : ma4_period
        }
        return d_sol

    def setup_cfg_with_encoded_problem(self, r, encoded_pblm, stgy_cfg_param):
        self.stgy_cfg_param[r.AM.AM_VOL_TARGET] = encoded_pblm['tgt_vol']
        bt_time = [encoded_pblm['buy_hour'], encoded_pblm['sell_hour']]
        self.stgy_cfg_param[r.OP.BT.TIME] = bt_time
        self.stgy_cfg_param[r.STGY.PARAMS]['base_time'] = encoded_pblm['buy_hour']
        self.stgy_cfg_param[r.STGY.PARAMS]['sell_time'] = encoded_pblm['sell_hour']
        ma1_params = self.stgy_cfg_param[r.STGY.PARAMS]["ma1"]
        ma1_params[1] = [encoded_pblm['ma1_period']]
        ma2_params = self.stgy_cfg_param[r.STGY.PARAMS]["ma2"]
        ma2_params[1] = [encoded_pblm['ma2_period']]
        ma3_params = self.stgy_cfg_param[r.STGY.PARAMS]["ma3"]
        ma3_params[1] = [encoded_pblm['ma3_period']]
        ma4_params = self.stgy_cfg_param[r.STGY.PARAMS]["ma4"]
        ma4_params[1] = [encoded_pblm['ma4_period']]

        return self.stgy_cfg_param


class GASuperWinningSessionHdgOptim(GAParamOptimizer):
    def __init__(self, tid, stgy_name, cfg_module, ga_hist_output):
        super(GASuperWinningSessionHdgOptim, self).__init__(tid, stgy_name, cfg_module, ga_hist_output)

    def create_problem(self):
        TGT_VOL_LB = [2.00]  # 0.2~0.4
        TGT_VOL_UB = [4.99]
        MA_PERIODS_LB = [3.00, 5.00, 10.00, 20.00]
        MA_PERIODS_UB = [4.99, 9.99, 19.99, 29.99]

        TF_HOURS_LB = [0] * 4
        TF_HOURS_UB = [6.99] * 4
        TF_H_GAP_LB = [0.0]
        TF_H_GAP_UB = [4.99]

        LBS = []
        LBS.extend(TGT_VOL_LB)
        LBS.extend(MA_PERIODS_LB)
        LBS.extend(TF_HOURS_LB)
        LBS.extend(TF_H_GAP_LB)

        UBS = []
        UBS.extend(TGT_VOL_UB)
        UBS.extend(MA_PERIODS_UB)
        UBS.extend(TF_HOURS_UB)
        UBS.extend(TF_H_GAP_UB)

        problem = {
            "obj_func"        : self.fitness_function,
            "bounds"          : FloatVar(lb = LBS, ub = UBS),
            "minmax"          : "max",
            "obj_weights"     : [0.4, 0.4, 0.2],
            "save_population" : True,
            "name"            : self.stgy_name,
            "log_to"          : "file",
            "log_file"        : f"ga_{self.stgy_name}_{dt2str_for_filename(now_dt())}.log",
            # Default value = "mealpy.log"
        }

        return problem

    def encode_problem(self, problem):
        tgt_vol   = int(problem[0]) / 100 ## range 0.02~0.04
        ma_periods_int = problem[1:5].astype(int)
        _ma_periods_idx_wo0 = np.where(ma_periods_int != 0)[0]
        ma_periods = ma_periods_int[_ma_periods_idx_wo0].tolist()

        tf_hours_idx = problem[5 :5 + 4].astype(int)
        timegap = int(problem[5+4])

        list_of_buy_hour = []
        for idx, tf_hour in enumerate(tf_hours_idx):
            if tf_hour != 0:
                buy_hour = 6 * idx + tf_hour
                buy_hour = 0 if buy_hour >= 24 else buy_hour
                zero_padding_buy_hour = f"0{buy_hour}" if buy_hour < 10 else buy_hour
                list_of_buy_hour.append(f'{zero_padding_buy_hour}:59')

        e_problems = {
            "tgt_vol"    : tgt_vol,
            "ma1_period" : ma_periods[0],
            "ma2_period" : ma_periods[1],
            "ma3_period" : ma_periods[2],
            "ma4_period" : ma_periods[3],
            "buy_hours" : list_of_buy_hour,
            "timegap" : timegap,
        }
        return e_problems

    def decode_solution(self, sol):
        tgt_vol = int(sol[0]) / 100  ## range 0.01~0.04
        ma1_period = int(sol[1])
        ma2_period = int(sol[2])
        ma3_period = int(sol[3])
        ma4_period = int(sol[4])

        tf_hours_idx = sol[5 :5 + 4].astype(int)
        timegap = int(sol[5+4])
        list_of_buy_hour = []
        for idx, tf_hour in enumerate(tf_hours_idx) :
            if tf_hour != 0 :
                buy_hour = 6 * idx + tf_hour
                buy_hour = 0 if buy_hour >= 24 else buy_hour
                zero_padding_buy_hour = f"0{buy_hour}" if buy_hour < 10 else buy_hour
                list_of_buy_hour.append(f'{zero_padding_buy_hour}:59')

        d_sol = {
            "tgt_vol"    : tgt_vol,
            "ma1_period" : ma1_period,
            "ma2_period" : ma2_period,
            "ma3_period" : ma3_period,
            "ma4_period" : ma4_period,
            "buy_hours"  : list_of_buy_hour,
            "timegap" : timegap
        }

        return d_sol

    def setup_cfg_with_encoded_problem(self, r, encoded_pblm, stgy_cfg_param):
        self.stgy_cfg_param[r.AM.AM_VOL_TARGET] = encoded_pblm['tgt_vol']
        self.stgy_cfg_param[r.AM.AM_TIMEFRAMES] = encoded_pblm['buy_hours']
        self.stgy_cfg_param[r.STGY.PARAMS]['timeframes'] = encoded_pblm['buy_hours']
        self.stgy_cfg_param[r.STGY.PARAMS]['timegap'] = encoded_pblm['timegap']

        ma1_params = self.stgy_cfg_param[r.STGY.PARAMS]['ma1']
        ma1_params[1] = [encoded_pblm['ma1_period']]
        ma2_params = self.stgy_cfg_param[r.STGY.PARAMS]['ma2']
        ma2_params[1] = [encoded_pblm['ma2_period']]
        ma3_params = self.stgy_cfg_param[r.STGY.PARAMS]['ma3']
        ma3_params[1] = [encoded_pblm['ma3_period']]
        ma4_params = self.stgy_cfg_param[r.STGY.PARAMS]['ma4']
        ma4_params[1] = [encoded_pblm['ma4_period']]

        r = R()
        calibrate_simul_env2(r, self.stgy_cfg_param)  ## set r.OP.BT.TIME for boosting backtesting
        return self.stgy_cfg_param