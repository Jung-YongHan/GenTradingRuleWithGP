import argparse

from bt4.Constants import QUOTE_MODE, Operation_Type, ExType
import bt4.GlobalProperties as global_prop


def add_common_arguments(parser, use_kafka=True, use_postgre_sql = True):
    parser.add_argument("-redis", type=str, help=f"ip:port of the redis, default is {global_prop.redis_svr}",
                        required = False, dest='redis_svr', default = global_prop.redis_svr)

    if use_kafka:
        parser.add_argument("-kafka", type = str, help = f"ip:port of the kafka bootstrap server, default is {global_prop.kafka_bootstrap_svr}",
                            required = False, dest = 'kafka_bootstrap_svr', default = global_prop.kafka_bootstrap_svr)

    if use_postgre_sql:
        parser.add_argument("-postgre", type = str, help = f"ip:port of the postgre sql server, default is {global_prop.postgre_sql_svr}",
                            required = False, dest='postgre_sql_svr', default = global_prop.postgre_sql_svr)
        parser.add_argument("-postgre_db", type = str, help = f"database name of the postgre sql server, default is {global_prop.postgre_sql_db}",
                            required = False, dest = 'postgre_sql_db', default = global_prop.postgre_sql_db)

def str2bool(value):
    if isinstance(value, bool):
        return value
    if value.lower() in ('true', 't', 'yes', '1'):
        return True
    elif value.lower() in ('false', 'f', 'no', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

def handle_common_arguments(args, use_kafka=True, use_postgre_sql = True):
    # print(f"{global_prop.redis_svr=}")
    # print(f"{global_prop.REDIS_HOST=}")
    # print(f"{global_prop.REDIS_PORT=}")
    #
    # print(f"{args.redis_svr=}")
    # print(f"{args.postgre_sql_svr=}")
    # print(f"{args.postgre_sql_db=}")
    global_prop.redis_svr = args.redis_svr
    global_prop.REDIS_HOST = global_prop.redis_svr.split(":")[0]
    global_prop.REDIS_PORT = int(global_prop.redis_svr.split(":")[1])

    if use_kafka:
        global_prop.kafka_bootstrap_svr = args.kafka_bootstrap_svr

    if use_postgre_sql:
        global_prop.postgre_sql_svr = args.postgre_sql_svr
        global_prop.postgre_sql_db = args.postgre_sql_db
        global_prop.DATABASE_URI = global_prop.postgre_sql_svr.split(":")[0]
        global_prop.DATABASE_PORT = global_prop.postgre_sql_svr.split(":")[1]
        global_prop.DATABASE_NAME = global_prop.postgre_sql_db

    # print(f"{global_prop.postgre_sql_db=}")
    # print(f"{global_prop.DATABASE_URI=}")
    # print(f"{global_prop.DATABASE_PORT=}")

    # print(f"{global_prop.redis_svr=}")
    # print(f"{global_prop.REDIS_HOST=}")
    # print(f"{global_prop.REDIS_PORT=}")

def get_argument():
    arg_map = {}
    parser = argparse.ArgumentParser(description = 'bt4 CLI tool')
    subparsers = parser.add_subparsers(title = 'Commands', dest = 'command')

    bt_parser = subparsers.add_parser('bt',  help = 'start mode for backtesting')
    bt_parser.add_argument('-conf', nargs='?', help='configuration module name (.py), do not use this when -tid is used(for bt3)',
                           required = False, dest='config_module')
    bt_parser.add_argument("-tid", nargs = "?", help = "backtesting request id stored in PostgreSQL",
                           required = True, dest = "tid")
    bt_parser.add_argument("-enable_bulk", nargs = "?", type = str2bool, help = f"default: {global_prop.enable_bulk}, True to enable bulk for fast backtesting, set false for visualizing backtesting steps with slow backtesting.",
                           default = global_prop.enable_bulk,
                           required = False, dest = "enable_bulk")
    add_common_arguments(bt_parser, False, True)

    ft_parser = subparsers.add_parser('ft', help = 'start mode for forward testing')
    ft_parser.add_argument('-usr_uuid', nargs = '?', help = "user's uuid for live trading",
                           required = True, default = None, dest = 'usr_uuid')
    ft_parser.add_argument('-usr_name', nargs = '?', help = "user's name only for forward testing",
                           required = True, default = None, dest = 'usr_name')
    ft_parser.add_argument('-exec_mode', nargs = '?', help = 'set \'redis_kafka\' for storing quote in redis and pull it by kafka-message(default, bt4)'
                                                             'set \'kafka\' for receiving quote by kafka(bt2)'
                                                             'set \'self\' for self-mode quote and local trading(bt1)',
                           required = False, default = 'redis_kafka', dest = 'exec_mode')
    ft_parser.add_argument('-conf', nargs = '?', help = 'configuration module name (.py), do not use this when -tid is used(for bt3)', dest = 'config_module')
    ft_parser.add_argument("-tid", nargs = "?", help = "trading request id stored in PostgreSQL",
                           required = False, dest = "tid")
    add_common_arguments(ft_parser, True, True)

    lt_parser = subparsers.add_parser('lt', help = 'start mode for live trading')
    lt_parser.add_argument('-usr_uuid', nargs = '?', help = "user's uuid for live_trading",
                           required = True, default = None, dest = 'usr_uuid')
    lt_parser.add_argument('-usr_name', nargs = '?', help = "user's name for live_trading",
                           required = True, default = None, dest = 'usr_name')
    lt_parser.add_argument('-exec_mode', nargs = '?', help = 'Set \'self\' for self-mode trading with '
                                                             'embedded ExchangeQuoteDispatcher. '
                                                             'Default is \'kafka\'. ',
                           required = False, default = 'kafka', dest = 'exec_mode')
    lt_parser.add_argument('-reset_trades', action='store_true', help='If set, resets trades.', dest='reset_trades')
    lt_parser.add_argument('-conf', nargs='?', help='configuration module name (.py), do not use this when -tid is used(for bt3)', dest='config_module')
    lt_parser.add_argument("-tid", nargs = "?", help = "trading request id stored in PostgreSQL",
                           required = False, dest = "tid")
    add_common_arguments(lt_parser, True, True)

    args = parser.parse_args()

    if args.command == Operation_Type.BACK_TESTOR.value:
        print(f"## Backtesting Mode with tid={args.tid}")
        arg_map["start_mode"] = args.command
        arg_map["config_module"] = args.config_module
        arg_map["tid"] = args.tid
        global_prop.enable_bulk = args.enable_bulk
        handle_common_arguments(args, False, True)
    elif args.command == Operation_Type.FORWARD_TESTING.value:
        print(f"## Forward Testing Mode with usr_uuid={args.usr_uuid}, usr_name={args.usr_name}, exec_mode={args.exec_mode},tid={args.tid}")
        arg_map['start_mode'] = args.command
        arg_map['usr_uuid'] = args.usr_uuid
        arg_map['usr_name'] = args.usr_name
        arg_map['exec_mode'] = QUOTE_MODE(args.exec_mode)
        arg_map['config_module'] = args.config_module
        arg_map['tid'] = args.tid
        handle_common_arguments(args, True, True)
    elif args.command == Operation_Type.LIVE_TRADING.value:
        print(f"## Live Trading Mode with usr_uuid={args.usr_uuid}, usr_name={args.usr_name}, exec_mode={args.exec_mode},tid={args.tid}")
        arg_map['start_mode'] = args.command
        arg_map['usr_uuid'] = args.usr_uuid
        arg_map['usr_name'] = args.usr_name
        arg_map['exec_mode'] = QUOTE_MODE(args.exec_mode)
        arg_map['reset_trades'] = args.reset_trades
        arg_map['config_module'] = args.config_module
        arg_map['tid'] = args.tid
        handle_common_arguments(args, True, True)

    return arg_map

def get_ga_argument():
    arg_map = {}
    parser = argparse.ArgumentParser(description = 'bt4 Genetic Algorithm CLI tool')
    subparsers = parser.add_subparsers(title = 'Commands', dest = 'command')

    ga_parser = subparsers.add_parser("ga", help = "start mode for genetic algorithm")
    ga_parser.add_argument("-tid", nargs = "?", help = "genetic algorithm based backtesting request id stored in PostgreSQL",
                           required = True, dest = "tid")
    add_common_arguments(ga_parser, False, True)

    args = parser.parse_args()

    if args.command == "ga":
        print(f"## Genetic Algorithm based Backtesting Mode with tid={args.tid}")
        arg_map["start_mode"] = args.command
        arg_map["tid"] = args.tid
        handle_common_arguments(args, False, True)
    else:
        print(f"## GAExecMain should be started with 'ga'.")

    return arg_map

def get_eqd_argument():
    arg_map = {}
    parser = argparse.ArgumentParser(description = 'bt4 exchange quote dispatcher cli tool')

    parser.add_argument('-quote_mode', nargs = '?',
                           help = 'set \'redis_kafka\' for storing quote in redis and send quote pull requests by kafka-message(default, bt4), '
                                  'set \'kafka\' for sending quote by kafka(bt2), '
                                  'set \'self\' for self-mode quote and local trading(bt1)',
                           required = True, default = 'redis_kafka', dest = 'quote_mode')

    add_common_arguments(parser, True, False)

    args = parser.parse_args()
    print(f"## Starting Exchange Quote Dispatcher with quote_mode=\"{args.quote_mode}\"")

    arg_map['quote_mode'] = QUOTE_MODE(args.quote_mode)
    handle_common_arguments(args, True, False)

    return arg_map

def get_websocket_eqd_argument():
    arg_map = {}
    parser = argparse.ArgumentParser(description = 'bt4 websocket exchange quote dispatcher cli tool')

    parser.add_argument('-ex_type', nargs = '?',
                           help = 'set \'upbit\' for getting quote from upbit websocket'
                                  'set \'bithumb\' for getting quote from bithumb websocket'
                                  'set \'binance\' for getting quote from binance websocket',
                           required = True, default = 'upbit', dest = 'ex_type')

    add_common_arguments(parser, True, False)

    args = parser.parse_args()
    print(f"## Starting Websocket Exchange Quote Dispatcher for Exchange =\"{args.ex_type}\"")

    arg_map["ex_type"] = ExType(args.ex_type)
    handle_common_arguments(args, True, False)

    return arg_map