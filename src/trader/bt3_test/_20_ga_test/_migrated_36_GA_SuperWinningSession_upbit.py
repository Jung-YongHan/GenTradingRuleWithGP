import unittest
from os.path import dirname, join

from bt4.utils.python_utils import dt2str_for_filename, now_dt
from bt4.optim.GASuperWinningSessionOptim import GASuperWinningSessionDayOptim, GASuperWinningSessionHdgOptim

import bt4.

class GA_SuperWinningSession_upbit(unittest.TestCase):


    def test_ga_binance_sws_day_hdg_vol(self):
        cfg_path = 'bt3_config.binance.sws_day_hdg_vol'
        root_dir = dirname(__file__)
        stgy_name = cfg_path.split('.')[2]
        ga_hist_output = join(root_dir, f'ga/ga_{stgy_name}_{dt2str_for_filename(now_dt())}.csv')
        ga_ws_optim = GASuperWinningSessionHdgOptim(cfg_path, ga_hist_output)

        tuner = ga_ws_optim.start_ga_optim()
        print(tuner.best_score)
        print(tuner.best_params)
        print(tuner.best_algorithm)
        print(tuner.best_algorithm.get_name())

    def test_ga_sws_day_hdg_vol(self):
        cfg_path = 'bt3_config.upbit.sws_day_hdg_vol'
        root_dir = dirname(__file__)
        stgy_name = cfg_path.split('.')[2]
        ga_hist_output = join(root_dir, f'ga/ga_{stgy_name}_{dt2str_for_filename(now_dt())}.csv')
        ga_ws_optim = GASuperWinningSessionHdgOptim(cfg_path, ga_hist_output)

        tuner = ga_ws_optim.start_ga_optim()
        print(tuner.best_score)
        print(tuner.best_params)
        print(tuner.best_algorithm)
        print(tuner.best_algorithm.get_name())


    def test_ga_sws_day_vol(self):
        cfg_path = 'bt3_config.upbit.sws_day_vol'
        root_dir = dirname(__file__)
        stgy_name = cfg_path.split('.')[2]
        ga_hist_output = join(root_dir, f'ga/ga_{stgy_name}_{dt2str_for_filename(now_dt())}.csv')
        ga_ws_optim = GASuperWinningSessionDayOptim(cfg_path, ga_hist_output)

        tuner = ga_ws_optim.start_ga_optim()
        print(tuner.best_score)
        print(tuner.best_params)
        print(tuner.best_algorithm)
        print(tuner.best_algorithm.get_name())


if __name__ == '__main__':
    unittest.main()
