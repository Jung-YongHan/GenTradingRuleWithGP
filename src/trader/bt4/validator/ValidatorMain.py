from bt4.Constants import TradeResultStorageType
from bt4.validator.QuoteTAIValidator import QuoteTAIValidator
from bt4.utils.python_utils import str2dt
from multiprocessing import Process, Manager
import time
import multiprocessing as mp
from bt4.validator.StrategyValidator import StrategyValidator
from bt4.utils.python_utils import load_class_from_module

def startQuoteTAIValidator(result_dic):
    ################### load quote tai configs
    q_t_val_markets = ('KRW-BTC', 'KRW-ETH', 'KRW-XRP')
    # start_dt = str2dt('2018-10-01T09:00:00')
    q_t_val_start_dt = str2dt('2021-12-20T09:00:00')
    q_t_val_end_dt = str2dt('2021-12-27T08:59:00')
    q_t_val_simul_hours = []
    q_t_val_simul_tais = ['vol', 'vol5', 'ma3', 'ma5', 'ma10', 'ma20']

    qtv = QuoteTAIValidator(q_t_val_markets)
    qtv.start_simulator_quote_tai_validator(q_t_val_markets, q_t_val_start_dt,
                                                 q_t_val_end_dt, q_t_val_simul_hours,
                                                 q_t_val_simul_tais)
    result_dfs_file_names = qtv.validate_quote_and_tai()
    result_dic['quote_tai_results'] = result_dfs_file_names

    # report_storage.store(str(result_dfs_file_names))



def startStrategyValidator(stgy_conf, result_dic):

    s_validator = StrategyValidator(stgy_conf)
    simul_result_loc = s_validator.start_validation()
    log_list = s_validator.validate_result(simul_result_loc)

    key = f'strategy_validator_{stgy_conf}'
    result_dic[key] = log_list

class RegressionTestMain:
    def __init__(self):
        core_package_name = "bt4.common."
        self.rs = load_class_from_module(core_package_name + "ReportSupport", TradeResultStorageType.FILE.value)
        file_name = "Regression_Test"
        visualize_support = False
        self.rs.set_params_0(file_name, visualize_support)

        # self.stgy_conf_list_4_reg_test = ['ws_day_vol', 'sws_day_vol']
        self.stgy_conf_list_4_reg_test = ['ws_day_vol']

    def startRegressionTest(self):
        start = time.time()
        mp.set_start_method('spawn')

        procs = []
        with Manager() as manager:
            result_dic = manager.dict()

            ##########################################################
            ### Start Quote TAI Validation
            q_t_val_processor = Process(target=startQuoteTAIValidator, args=(result_dic,))
            self.rs.store('############### start process for validating quote and ta indicators')
            ## TODO: How can we get the result from the startQuoteTAIValidator processor?
            q_t_val_processor.start()
            procs.append(q_t_val_processor)

            ##########################################################
            ### Start Strategy Validation
            for stgy_conf in self.stgy_conf_list_4_reg_test:
                stgy_val_processor = Process(target=startStrategyValidator, args=(stgy_conf, result_dic))
                print(f'############### start process for validating strategy : {stgy_conf}')
                stgy_val_processor.start()
                procs.append(stgy_val_processor)

            for p in procs:
                self.rs.store(f'{p.name} am waiting for termination of another process... Try to JOIN. ')
                p.join()
                self.rs.store(f'{p.name} am waiting for termination of another process... Done to JOIN')

            self.rs.store(str(result_dic))

        end = time.time()
        elapsed_time = end - start
        self.rs.store(f'Elapsed Time: {elapsed_time}')

    def report(self):
        self.rs.close()


if __name__ == '__main__':
    rtm = RegressionTestMain()
    rtm.startRegressionTest()
    rtm.report()
