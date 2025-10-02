import sys
from logging import handlers
import logging
import os
from logging import StreamHandler
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from datetime import datetime
from os.path import dirname, join

from bt4.Constants import Operation_Type

## TODO: Implement Memory Log
## TODO: Refactoring firebase log to support separated processors (e.g., ExchangeQuoteDispatcher, TradeMgr, Stragegy)
# global log_mode
log_mode = Operation_Type.BACK_TESTOR.value
# log_mode = 'live_trading'
# log_mode = 'quote'

log_mnemonic = 'stkim'
log_strategy = ''

def init_log():
    '''
    name = 'simulator' for simulation
    name = 'real_trading' for real_trading
    name = 'quote' for quote dispatcher

    :param name:
    :return:
    '''
    trader_logger = logging.getLogger(log_mode)
    if len(trader_logger.handlers) <= 0:
        pid = os.getpid()
        #log settings

        if log_mode == Operation_Type.LIVE_TRADING.value:
            log_level = logging.INFO
        else:
            log_level = logging.DEBUG
        # log_level = logging.CRITICAL
        trader_logger.setLevel(log_level)

        #handler settings
        root_dir = dirname(dirname(dirname(__file__)))
        log_file_name = f'log/{log_mode}@{log_mnemonic}_{log_strategy}_{str(pid)}.log'
        file_name = join(root_dir, log_file_name)

        log_formatter = SpecialFormatter(log_mnemonic)
        file_handler = handlers.TimedRotatingFileHandler(filename=file_name, when='midnight', interval=1, encoding='utf-8')
        # file_handler.setFormatter(trader_log_formatter)
        file_handler.setFormatter(log_formatter)
        file_handler.suffix = "%Y%m%d"
        trader_logger.addHandler(file_handler)

        console_handler = logging.StreamHandler(stream=sys.__stderr__)
        # console_handler.setFormatter(fmt=trader_log_formatter)
        console_handler.setFormatter(log_formatter)

        trader_logger.addHandler(console_handler)

        ## Firebase Logger
        ## Add This logger only for realtime operation
        if log_mode == Operation_Type.LIVE_TRADING.value:
            root_dir = dirname(dirname(__file__))
            firebase_auth_json_path = join(root_dir, f"exec{os.sep}auto-trader-95285-firebase-adminsdk-gftpc-4b1f1b8c6d.json")

            firebase_handle = FirebaseLogHandler(firebase_auth_json_path)
            # firebase_handle.setFormatter(fmt=trader_log_formatter)
            firebase_handle.setFormatter(log_formatter)
            trader_logger.addHandler(firebase_handle)

    return trader_logger

class SpecialFormatter(logging.Formatter):
    """Logging Formatter to add colors and count warning / errors"""
    grey = "\x1b[38;21m"
    yellow = "\x1b[33;21m"
    red = "\x1b[31;21m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    # debug_format = "[%(levelname)s:%(asctime)s] %(message)s (%(filename)s:%(lineno)d)"
    # debug_format = "[%(levelname)s:%(asctime)s] %(message)s"
    # info_format = f'@{log_account}[%(levelname)s] %(message)s'

    def __init__(self, my_log_account):
        super(SpecialFormatter, self).__init__()

        debug_format = "[%(levelname)s:%(asctime)s] %(message)s"
        info_format = f'@{my_log_account}[%(levelname)s] %(message)s'

        self.FORMATS = {
        # logging.DEBUG: grey + debug_format + reset,
        # logging.INFO: grey + info_format + reset,
        # logging.WARNING: yellow + debug_format + reset,
        # logging.ERROR: red + debug_format + reset,
        # logging.CRITICAL: bold_red + debug_format + reset
        logging.DEBUG: debug_format,
        logging.INFO: info_format,
        logging.WARNING: debug_format,
        logging.ERROR: debug_format,
        logging.CRITICAL: debug_format
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


class FirebaseLogHandler(StreamHandler):

    def __init__(self, path):
        StreamHandler.__init__(self)

        # cred = credentials.Certificate("auto-trader-95285-firebase-adminsdk-gftpc-4b1f1b8c6d.json")
        cred = credentials.Certificate(path)
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://auto-trader-95285-default-rtdb.asia-southeast1.firebasedatabase.app/'})

    def emit(self, record):
        try:
            msg = self.format(record)

            now = datetime.now()
            ref = db.reference(log_mnemonic)

            # dir = now.strftime('%Y-%m-%d')
            # ref = db.reference(dir)
            key = now.strftime('%Y-%m-%d %H:%M:%S')
            ref.update({'time': key, 'message': msg})
        except firebase_admin.exceptions.UnavailableError as err:
            print(f"Firebase error {err=}, {type(err)=}")
        except Exception as err:
            print(f"Firebase - General error {err=}, {type(err)=}")


