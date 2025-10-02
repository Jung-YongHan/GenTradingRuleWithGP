import signal
import time

from bt4 import GlobalProperties
from bt4.Constants import R, ExType, Operation_Type
from bt4.core.CfgStgyRuleGenerator import CfgStgyRuleGenerator
from bt4.core.TradingCtxBuilder import TradingContextBuilder
from bt4.model.storage_mgr import StrategyStorage
from bt4.resource_path_mgr import RPath
from bt4.utils.python_utils import load_class_from_module, dt2str_for_filename, now_dt
from os.path import dirname, join
import os
import bt4.GlobalProperties as global_prop
from bt4.utils.bt4_cli_args import get_argument
from bt4.validator.json_schema_validator import JSonSchemaValidator
from bt4_cfg.binance.bt_binance_common_conf import Bt_binance_CommonConfig
from bt4_cfg.bithumb.bt_bithumb_common_conf import Bt_bithumb_CommonConfig
from bt4_cfg.upbit.bt_upbit_common_conf import Bt_upbit_CommonConfig
import warnings
from bt4.common.ResultAnalyzer import analyze_result

warnings.filterwarnings("ignore", category = DeprecationWarning)

r = R()
class BullTrader:
    def __init__(self):
        GlobalProperties.bt_emergency_stop = False

    def prepare(self, params):
        '''
          Build All System Configuration including
            - Trading System (Backtestor, StrategyLiveTrader)
            - Exchange (Upbit, Binance, BinanceUSDM)
            - Assetmgmt (Fixed/Volatility, Netting / Heding)
            - Report Storage (File, Mongo)
            - Strategy
        :param params:
        :return:
        '''
        self.trading_builder = TradingContextBuilder(params)
        self.trading_builder.build_trading_system()
        self.trading_builder.build_exchange()
        self.trading_builder.build_asset_mgmt()
        self.trading_builder.build_report_storage()
        self.trading_builder.build_strategy()
        return self.trading_builder.get_context()

    def setup(self, context):
        context.strategy.setup(context)

    def register(self):
        signal.signal(signal.SIGTERM, self.handle_exit)
        signal.signal(signal.SIGINT, self.handle_exit)

    def handle_exit(self, *args):
        try :
            GlobalProperties.bt_emergency_stop = True
        except BaseException as exception :
            log.error(f"exception : {exception}")

    def start(self):
        '''
          System Start after setting up the system according to the configuration.
        :return:
        '''
        file_name = ''
        op_type = self.trading_builder.get_op_type()
        ctx = self.trading_builder.get_context()
        stgy_name = ctx.ctx_params[r.STGY.NAME]
        try:
            from bt4.Constants import Operation_Type
            if op_type == Operation_Type.BACK_TESTOR:
                ctx.backtestor.start_backtesting(ctx.strategy)
            elif op_type == Operation_Type.LIVE_TRADING or op_type == Operation_Type.FORWARD_TESTING:
                ctx.stgy_live_trader.start_auto_trading(ctx.strategy)

            df = ctx.strategy.report.toDataFrame()
            if len(df) > 0 :
                # if isinstance(ctx.report_storage, FileReportStorage):
                root_dir = dirname(dirname(dirname(__file__)))
                file_name = join(root_dir, f'report/{dt2str_for_filename(now_dt())}_{stgy_name}({os.getpid()}).csv')
                df.to_csv(file_name)
                analyze_result(df, stgy_name, ctx, ctx.report_storage)
            self.result_df = df
        finally:
            ctx.strategy.finish()

        return file_name



def generate_config_strategy(bt_request) :

    if bt_request is not None:
        print(bt_request.cfg_stgy_rules_json)
        ex_type = ExType(bt_request.ex_type)
        cfg_stgy_rules_json = bt_request.cfg_stgy_rules_json
        cfg_stgy_rules_json["stgy_name"] = "dummy"
        cfg_stgy_rules_json["module_name"] = f"{bt_request.tid}_module"

        csr = CfgStgyRuleGenerator()
        if cfg_stgy_rules_json is not None :
            print("###### Load Cfg_Stgy_Rules_JSON.json from database")
            cfg_py, stgy_py, cfg_module = csr.generate_cfg_stgy_rule(bt_request.tid, ex_type, cfg_stgy_rules_json)
        return cfg_module

    return None


def main(args, interceptor = None):
    arg_map = get_argument()
    start_mode = arg_map["start_mode"]
    config_module = arg_map["config_module"]
    tid = arg_map["tid"]
    GlobalProperties.tid = tid

    from bt4.Constants import R
    r = R()
    parameters = {}

    bt_request = None
    if tid is not None:
        bt_request = StrategyStorage.instance().load_backtesting_request(tid)
    if bt_request is None:
        print(f"[ERROR] Backtesting Request \"{tid}\" does not exist in {global_prop.postgre_sql_db} database of {global_prop.postgre_sql_svr}.")
        import sys
        sys.exit(0)

    if global_prop.json_schema_validation_support:
        jsv = JSonSchemaValidator()
        if not jsv.validate(bt_request.cfg_stgy_rules_json):
            print(f"JSon Schema Validation Error!")
            import sys
            sys.exit(0)

    config_module = generate_config_strategy(bt_request)

    from bt4.Constants import Operation_Type
    parameters[r.OP.tid] = tid
    parameters[r.OP.OP] = Operation_Type(start_mode)
    parameters[r.OP.cfg_module] = config_module

    import bt4.utils.mylog as log_module

    exchange = config_module.split('.')[1]
    ex_type = ExType(exchange)
    arg_map['exchange'] = ex_type
    if start_mode == Operation_Type.BACK_TESTOR.value:
        print("########################### Backtesting Mode ######################")
        cfg_root = RPath.instance().bt_cfg_root_module()
        comm_cfg_module = f'{cfg_root}.{exchange}.bt_{exchange}_common_conf'
        comm_cls = f'Bt_{exchange}_CommonConfig'
        common_config = load_class_from_module(comm_cfg_module, comm_cls)
        log_module.log_mode = Operation_Type.BACK_TESTOR.value

    elif start_mode == Operation_Type.FORWARD_TESTING.value:
        print("########################### Forward Testing Mode ######################")
        usr_uuid = arg_map['usr_uuid']
        usr_name = arg_map['usr_name']
        print(f"### usr_uuid: {usr_uuid}, name : {usr_name}")
        global_prop.usr_uuid = usr_uuid
        log_module.log_mnemonic = f"{usr_name}@dummy{exchange}"
        comm_cfg_module = f"{RPath.instance().bt_cfg_root_module()}.{exchange}.ft_{exchange}_common_conf"
        comm_cls = f'Ft_{exchange}_CommonConfig'
        common_config = load_class_from_module(comm_cfg_module, comm_cls)
        common_config.set_account(usr_uuid, ex_type)
        log_module.log_mode = Operation_Type.FORWARD_TESTING.value
        GlobalProperties.is_live_trading = True

    elif start_mode == Operation_Type.LIVE_TRADING.value:
        print("########################### Live Trading Mode ######################")
        usr_uuid = arg_map['usr_uuid']
        usr_name = arg_map['usr_name']
        log_module.log_mnemonic = f"{usr_name}@{exchange}"
        comm_cfg_module = f"{RPath.instance().bt_cfg_root_module()}.{exchange}.lt_{exchange}_common_conf"
        comm_cls = f'Lt_{exchange}_CommonConfig'
        common_config = load_class_from_module(comm_cfg_module, comm_cls)
        common_config.set_account(usr_uuid, ex_type)
        log_module.log_mode = Operation_Type.LIVE_TRADING.value
        GlobalProperties.is_live_trading = True
        GlobalProperties.reset_trades = arg_map['reset_trades']

    common_config.load_params(r, parameters)
    # log_module.log_strategy = parameters[r.STGY.NAME]

    from bt4.utils.mylog import init_log
    log = init_log()

    handle_args(arg_map, parameters)

    ############################################################
    config = load_class_from_module(config_module, 'Config')
    config.load_params(r, parameters)
    log_module.log_strategy = parameters[r.STGY.NAME]

    if interceptor is not None:
        interceptor.intercept_before(parameters)

    bullTrader = BullTrader()
    context = bullTrader.prepare(parameters)
    bullTrader.setup(context)
    bullTrader.register()
    result_file_path = bullTrader.start()

    if interceptor is not None:
        interceptor.intercept_after(context)

    return context, result_file_path




def handle_args(arg_map, params) :
    start_mode = arg_map['start_mode']
    r = R()
    if start_mode == Operation_Type.FORWARD_TESTING.value:
        ex_params = {}
        ex_common_cfg_obj = None

        if arg_map['exchange'] == ExType.upbit:
            params[r.EX.EX_TYPE] = ExType.dummy_upbit
            ex_common_cfg_obj = Bt_upbit_CommonConfig()
        if arg_map['exchange'] == ExType.bithumb:
            params[r.EX.EX_TYPE] = ExType.dummy_bithumb
            ex_common_cfg_obj = Bt_bithumb_CommonConfig()
        elif arg_map['exchange'] == ExType.binance:
            params[r.EX.EX_TYPE] = ExType.dummy_binance
            ex_common_cfg_obj = Bt_binance_CommonConfig()
        elif arg_map['exchange'] == ExType.binanceusdm:
            params[r.EX.EX_TYPE] = ExType.dummy_binanceusdm
            ex_common_cfg_obj = Bt_binanceusdm_CommonConfig()

        ex_common_cfg_obj.load_params(r, ex_params)
        params[r.EX.EX_DUMMY_INITIAL_RATIO] = ex_params[r.EX.EX_DUMMY_INITIAL_RATIO]
        params[r.EX.EX_DUMMY_FEE_SLIPPAGE] = ex_params[r.EX.EX_DUMMY_FEE_SLIPPAGE]

    if 'exec_mode' in arg_map:
        exec_mode = arg_map['exec_mode']
        params[r.OP.live.QUOTE_MODE] = exec_mode


if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
