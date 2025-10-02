from bt4.utils.misc_utils import calibrate_simul_env2
from bt4.utils.python_utils import dt2str_for_filename
from datetime import datetime
from os.path import dirname, join
import pandas as pd
from bt4.Constants import R, AssetMgrType
from abc import *
from enum import Enum

class HandleType(Enum):
    Cumulated_File = 'Cumulated_File'
    Instant_Stream = 'Instant_Stream'

def write_print(file, text):
    print(text)
    file.write(text+'\r')

def print_n_append(_list, text):
    print(text)
    _list.append(text)


class AbstractBTInterceptor(metaclass=ABCMeta):

    @abstractmethod
    def __init__(self, handle_type, out_file=''):
        self.handle_type = handle_type
        if handle_type == HandleType.Cumulated_File:       ## For Iterative Processing with Single Thread
            now = datetime.now()
            root_dir = dirname(dirname(dirname(__file__)))
            self.file_name = join(root_dir, f'report/multi_exec_{dt2str_for_filename(now)}_{out_file}.txt')
            self.result_output = open(self.file_name, 'a')
        elif handle_type == HandleType.Instant_Stream:      ## For Multiprocessing
            self.result_list = []

        self.result_dic = {}
        self.dataframe = pd.DataFrame()

    def update_params(self, params_tobe_updated):
        self.params_tobe_updated = params_tobe_updated

    def intercept_before(self, bt_params):
        r = R()
        self.handle("#############################################################")
        self.handle("Simulation Params ======================================")
        conf = self.params_tobe_updated['conf'] if 'conf' in self.params_tobe_updated else None
        self.handle(f' Strategy: {conf}')
        if conf is not None:
            self.result_dic['conf'] = conf

        if r.STGY.NAME in self.params_tobe_updated and r.STGY.NAME in self.params_tobe_updated :
            bt_params[r.STGY.NAME] = self.params_tobe_updated[r.STGY.NAME]

        if r.OP.BT.START in self.params_tobe_updated and r.OP.BT.END in self.params_tobe_updated :
            bt_params[r.OP.BT.START] = self.params_tobe_updated[r.OP.BT.START]
            bt_params[r.OP.BT.END] = self.params_tobe_updated[r.OP.BT.END]

        self.handle(f' Period: {bt_params[r.OP.BT.START]} ~ {bt_params[r.OP.BT.END]}')
        self.result_dic['simul_start'] = bt_params[r.OP.BT.START]
        self.result_dic['simul_end'] = bt_params[r.OP.BT.END]

        if r.OP.MARKET in self.params_tobe_updated:
            bt_params[r.OP.MARKET] = self.params_tobe_updated[r.OP.MARKET]

        self.handle(f' Markets: {bt_params[r.OP.MARKET]}')
        self.result_dic['markets'] = f'{",".join(bt_params[r.OP.MARKET])}'

        if r.AM.AM_FIXED_TRADE_RATIO in self.params_tobe_updated:
            bt_params[r.AM.AM_FIXED_TRADE_RATIO] = self.params_tobe_updated[r.AM.AM_FIXED_TRADE_RATIO]
            self.handle(f' Fixed Ratio: {bt_params[r.AM.AM_FIXED_TRADE_RATIO]}')
            self.result_dic['fixed_ratio'] = bt_params[r.AM.AM_FIXED_TRADE_RATIO]
        elif r.AM.AM_VOL_TARGET in self.params_tobe_updated:
            bt_params[r.AM.AM_VOL_TARGET] = self.params_tobe_updated[r.AM.AM_VOL_TARGET]
            self.handle(f' Volatility Target: {bt_params[r.AM.AM_VOL_TARGET]}')
            self.result_dic['vol_target'] = bt_params[r.AM.AM_VOL_TARGET]

        if r.AM.AM_TIMEFRAMES in self.params_tobe_updated:
            bt_params[r.AM.AM_TIMEFRAMES] = self.params_tobe_updated[r.AM.AM_TIMEFRAMES]

        if r.OP.BT.TIME in self.params_tobe_updated:
            bt_params[r.OP.BT.TIME] = self.params_tobe_updated[r.OP.BT.TIME]

        if r.STGY.PARAMS in self.params_tobe_updated:
            bt_params[r.STGY.PARAMS].update(self.params_tobe_updated[r.STGY.PARAMS])
            # bt_params[r.STGY.PARAMS] = self.params_tobe_updated[r.STGY.PARAMS]
            self.handle(f' Strategy Params: {bt_params[r.STGY.PARAMS]}')
            self.result_dic[r.STGY.PARAMS] = bt_params[r.STGY.PARAMS]

        if r.OP.BT.CANDLE_TYPE in self.params_tobe_updated :
            bt_params[r.OP.BT.CANDLE_TYPE] = self.params_tobe_updated[r.OP.BT.CANDLE_TYPE]
            self.handle(f' Candle Type: {bt_params[r.OP.BT.CANDLE_TYPE]}')
            self.result_dic['cdl_type'] = bt_params[r.OP.BT.CANDLE_TYPE]

        if r.STGY.STOP_LOSS in self.params_tobe_updated :
            bt_params[r.STGY.STOP_LOSS] = self.params_tobe_updated[r.STGY.STOP_LOSS]
            self.handle(f' Stop Loss: {bt_params[r.STGY.STOP_LOSS]}')
            self.result_dic['stop_loss'] = bt_params[r.STGY.STOP_LOSS]

    def intercept_after(self, context):
        key_results = context.report_storage.get_key_results()
        self.result_dic.update(key_results)

        self.handle("Simulation result ======================================")
        self.handle(key_results['last_bal'])
        self.handle(key_results['max_bal'])
        self.handle(key_results['init_bal'])

        self.handle(key_results['trade_win_rate'])
        self.handle(key_results['num_of_trades'])
        self.handle(key_results['num_of_wins'])
        self.handle(key_results['num_of_loses'])

        self.handle(key_results['settle_winning_rate'])
        self.handle(key_results['settle_total_trade'])
        self.handle(key_results['settle_winning'])
        self.handle(key_results['settle_lose'])

        self.handle(key_results['mdd'])
        self.handle(key_results['mdd_10'])
        self.handle(key_results['mdd_20'])

        self.handle(key_results['mpr'])
        self.handle(key_results['profit_std'])
        self.handle(key_results['sharp_index'])

        if 'tai_decision' in self.result_dic:
            l = self.result_dic['tai_decision']
            self.result_dic['tai_decision'] = f'{l}'
        self.result_dic['params_dict'] = self.result_dic['params']
        self.result_dic['params'] = self.result_dic['params'].__str__()

        self.result_dic['stgy_params'] = self.result_dic['stgy_params'].__str__()

        print(f"dic size: {len(self.result_dic)}==> {self.result_dic}")
        print(f"1)dataframe size: {len(self.dataframe.columns)}")
        df_strategy = pd.DataFrame(self.result_dic, index=['1'])
        if len(self.dataframe) == 0:
            self.dataframe = df_strategy
        else:
            self.dataframe = pd.concat([self.dataframe, df_strategy], ignore_index=True)
        print(f"2)dataframe size: {len(self.dataframe.columns)}")

    def handle(self, text):
        print(text)
        if self.handle_type == HandleType.Cumulated_File:
            self.handle_in_file(text)
        elif self.handle_type == HandleType.Instant_Stream:
            self.handle_in_stream(text)

    def handle_in_file(self, text):
        self.result_output.write(text+'\r')

    def handle_in_stream(self, text):
        self.result_list.append(text)

    def get_results(self):
        if self.handle_type == HandleType.Cumulated_File:
            if self.result_output is not None:
                self.result_output.close()
            return self.file_name
        elif self.handle_type == HandleType.Instant_Stream:
            return self.result_list, self.result_dic


class TrendStgyInterceptor(AbstractBTInterceptor):
    def __init__(self, handle_type, out_file=''):
        super(TrendStgyInterceptor, self).__init__(handle_type, out_file)

    def intercept_before(self, bt_params):
        super(TrendStgyInterceptor, self).intercept_before(bt_params)
        r = R()

        strategy_params = self.params_tobe_updated[r.STGY.PARAMS]
        origin_strategy_params = bt_params[r.STGY.PARAMS]
        origin_strategy_params.update(strategy_params)

        self.handle(f' stgy_params: {strategy_params}')
        self.result_dic['stgy_params'] = strategy_params


        bt_params[r.RS.RS_VISUALIZE] = False

class TrendStgyHdgeInterceptor(AbstractBTInterceptor):
    def __init__(self, handle_type, out_file=''):
        super(TrendStgyHdgeInterceptor, self).__init__(handle_type, out_file)

    def intercept_before(self, bt_params):
        super(TrendStgyHdgeInterceptor, self).intercept_before(bt_params)
        r = R()

        to_be_updated_strategy_params = self.params_tobe_updated[r.STGY.PARAMS]
        strategy_params = bt_params[r.STGY.PARAMS]

        if 'timeframes' in strategy_params:
            updated_tf = strategy_params['timeframes']
            self.handle(f' timeframes: {updated_tf}')
            self.result_dic['timeframes'] = ','.join(strategy_params['timeframes'])

        if 'timegap' in strategy_params:
            updated_timegap = strategy_params['timegap']
            self.handle(f' timegap: {updated_timegap}')
            self.result_dic['timegap'] = updated_timegap

        bt_params = calibrate_simul_env2(r, bt_params)
        bt_params[r.RS.RS_VISUALIZE] = False


class CompositeStgyInterceptor(AbstractBTInterceptor):
    def __init__(self, handle_type, out_file=''):
        super(CompositeStgyInterceptor, self).__init__(handle_type, out_file)

    def intercept_before(self, bt_params):
        super(CompositeStgyInterceptor, self).intercept_before(bt_params)
        r = R()

        strategy_params = self.params_tobe_updated[r.STGY.PARAMS]
        origin_strategy_params = bt_params[r.STGY.PARAMS]
        origin_strategy_params.update(strategy_params)

        updated_bull_strategy_conf = origin_strategy_params['bull_mkt_conf']
        self.handle(f' Bull Strategy : {updated_bull_strategy_conf}')
        self.result_dic['bull_mkt_conf'] = updated_bull_strategy_conf

        updated_bear_strategy_conf = origin_strategy_params['bear_mkt_conf']
        self.handle(f' Bear Strategy : {updated_bear_strategy_conf}')
        self.result_dic['bear_mkt_conf'] = updated_bear_strategy_conf

        updated_decisions = strategy_params['tai_decision']
        self.handle(f' tai_decision : {updated_decisions}')
        self.result_dic['tai_decision'] = updated_decisions

        bt_params[r.RS.RS_VISUALIZE] = False


class CompositeStgyHdgeInterceptor(AbstractBTInterceptor):
    def __init__(self, handle_type, out_file=''):
        super(CompositeStgyHdgeInterceptor, self).__init__(handle_type, out_file)

    def intercept_before(self, bt_params):
        super(CompositeStgyHdgeInterceptor, self).intercept_before(bt_params)
        r = R()

        bt_params[r.AM.AM_TIMEFRAMES] = self.params_tobe_updated[r.AM.AM_TIMEFRAMES]

        strategy_params = self.params_tobe_updated[r.STGY.PARAMS]
        origin_strategy_params = bt_params[r.STGY.PARAMS]
        origin_strategy_params.update(strategy_params)

        updated_bull_strategy_conf = origin_strategy_params['bull_mkt_conf']
        self.handle(f' Bull Strategy : {updated_bull_strategy_conf}')
        self.result_dic['bull_mkt_conf'] = updated_bull_strategy_conf

        updated_bear_strategy_conf = origin_strategy_params['bear_mkt_conf']
        self.handle(f' Bear Strategy : {updated_bear_strategy_conf}')
        self.result_dic['bear_mkt_conf'] = updated_bear_strategy_conf

        updated_decision = origin_strategy_params['tai_decision']
        self.handle(f' decisions : {updated_decision}')
        self.result_dic['tai_decision'] = updated_decision

        updated_tf = origin_strategy_params['timeframes']
        self.handle(f' timeframes: {updated_tf}')
        self.result_dic['timeframes'] = ','.join(strategy_params['timeframes'])

        updated_timegap = origin_strategy_params['timegap']
        self.handle(f' timegap: {updated_timegap}')
        self.result_dic['timegap'] = updated_timegap

        bt_params = calibrate_simul_env2(r, bt_params)
        bt_params[r.RS.RS_VISUALIZE] = False