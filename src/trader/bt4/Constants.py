from enum import Enum, IntEnum


class R:
    def __init__(self):
        self.OP = self.Op()
        self.EX = self.Ex()
        self.AM = self.Am()
        self.Tm = self.Tm()
        self.RS = self.Rs()
        self.STGY = self.Stgy()


    class Op:
        '''
        Operation Type - Simulation / AutoTrader
        '''
        def __init__(self):
            self.OP = 'operation'
            self.QUOTE_PROVIDERS = 'quote_providers'
            self.MARKET = 'market'
            self.BT = self.Bt()
            self.live = self.Real()
            self.EXTYPE = 'extype'
            self.tid = "tid"
            self.cfg_module = "cfg_module"

        class Bt:
            '''
            Simulation Parameters
            '''
            def __init__(self):
                self.CANDLE_TYPE = "data_type_DAY_HOUR_MINUTE"
                self.START = "bt_start_date"
                self.END   = "bt_end_date"
                self.TIME = "bt_time"
                self.TA_INDICATORS = "bt_ta_indicators"
                self.CDL_TYPES_NEEDED = "bt_cdl_type_needed"

            def params(self):
                return [self.MARKET, self.CANDLE_TYPE, self.START, self.END, self.TIME, self.TA_INDICATORS]

        class Real:
            def __init__(self):
                self.QUOTE_MODE = "real_trading_quote_model"

            def params(self):
                return [self.QUOTE_MODE]

    class Ex:
        '''
        Exchange Parameters
        '''
        def __init__(self):
            self.EX_TYPE = "ex_type_DUMMY"
            self.EX_DUMMY_INITIAL_RATIO = "ex_dummy_initial_ratio"
            self.EX_DUMMY_FEE_SLIPPAGE = "ex_dummy_fee_slippage"
            self.EX_USR_ID = 'usr_id'
            self.EX_ACCOUNT = 'account'
            self.EX_ACCESS_KEY = 'ex_access_key'
            self.EX_SECRET_KEY = 'ex_secret_key'

        def params(self, ex_type):
            if ex_type == ExType.dummy_upbit:
                return [self.EX_DUMMY_INITIAL_RATIO, self.EX_DUMMY_FEE_SLIPPAGE]
            elif ex_type == ExType.upbit:
                return [self.EX_ACCESS_KEY, self.EX_SECRET_KEY]

    class Tm:
        '''
        TradeMgr Parameters
        '''
        def __init__(self):
            self.TM_TACTIC = 'tm_tactic'

    class Am:
        '''
        Asset Management Parameters
        '''
        def __init__(self):
            self.AM_TYPE = 'am_type'
            self.AM_WGHT_TOP_N = "am_weight_top_n"
            self.AM_FIXED_TRADE_RATIO = 'am_fixed_fixed_trade_ratio'
            self.AM_VOL_TARGET = 'am_vol_target_volatility_ratio'
            self.AM_VOL_PERIOD = 'am_vol_volatility_period'  ## TO BE REMOVED after archiecture refactoring
            self.AM_VOL_TAI = 'am_vol_volatility_tai'
            self.AM_TIMEFRAMES = 'am_vol_timeframes'
            self.REBAL_TIMES = 'am_rebalance'

        def params(self, am_type):
            if am_type == AssetMgrType.FIXED:
                return [self.AM_FIXED_TRADE_RATIO]
            elif am_type == AssetMgrType.VOLATILITY:
                return [self.AM_VOL_TARGET, self.AM_VOL_PERIOD]

    class Rs:
        '''
        Report Storage Parameters
        '''
        def __init__(self):
            self.RS_TYPE = 'rs'
            self.RS_FILE_NAME = 'rs_file_name'
            self.RS_VISUALIZE = 'rs_visualize'

        def params(self, rs_type):
            if rs_type == TradeResultStorageType.FILE:
                return [self.RS_FILE_NAME]
            elif rs_type == AssetMgrType.VOLATILITY:
                return []

    class Stgy:
        '''
        Strategy Parameters
        '''
        def __init__(self):
            self.NAME = 'strategy'
            self.MODULE = 'module'
            self.STOP_LOSS = "stop_loss"
            self.TRAILING_STOP = "trailing_stop"
            self.PARAMS = "params"
            self.TAKE_PROFIT = "take_profit"

        def params(self, strategy):
            return strategy.get_parameters()


class ExType(str, Enum):
    upbit = 'upbit'
    bithumb = 'bithumb'
    binance = 'binance'
    binanceusdm = 'binanceusdm'
    dummy_upbit = 'DummyUpbit'
    dummy_bithumb = 'DummyBithumb'
    dummy_binance = 'DummyBinance'
    dummy_binanceusdm = 'DummyBinanceUSDM'



class AssetMgrType(str, Enum):
    # FIXED = 1
    # VOLATILITY = 2
    # FIXED_HDGE = 3
    # VOLATILITY_HDGE = 4
    FIXED = 'FixedRatioAssetMgr'
    WEIGHTED = 'WeightedRatioAssetMgr'
    VOLATILITY = 'VolatilityAssetMgr'
    FIXED_HDGE = 'FixedHdgeAssetMgr'
    VOLATILITY_HDGE = 'VolatilityHdgeAssetMgr'

class TradeResultStorageType(str, Enum):
    FILE = 'FileReportStorage'
    MONGO = 'MongoDBReportStorage'
    PSQL = 'PostgreSQLReportStorage'


class QUOTE_MODE(str, Enum):
    SELF = 'self'
    KAFKA = 'kafka'
    REDIS_KAFKA = 'redis_kafka'


class Operation_Type(str, Enum):
    BACK_TESTOR  = 'bt'
    FORWARD_TESTING = 'ft'
    LIVE_TRADING = 'lt'

class QItem(str, Enum):
    time = 'datetime'
    market = 'market'
    open = 'open'
    high = 'high'
    low  = 'low'
    close= 'close'
    vol  = 'vol'

class Ary(str, Enum):
    Unary = 'unary'
    Nary = 'nary'


class CandleType(IntEnum):
    DAYS = 1440
    HOUR4 = 240
    HOUR = 60
    MINUTES_30 = 30
    MINUTES_15 = 15
    MINUTES_10 = 10
    MINUTES_5 = 5
    MINUTES_3 = 3
    MINUTES_1 = 1
    DAYS_0  = 1450
    DAYS_1  = 1451
    DAYS_2  = 1452
    DAYS_3  = 1453
    DAYS_4  = 1454
    DAYS_5  = 1455
    DAYS_6  = 1456
    DAYS_7  = 1457
    DAYS_8  = 1458
    DAYS_9  = 1459
    DAYS_10 = 1460
    DAYS_11 = 1461
    DAYS_12 = 1462
    DAYS_13 = 1463
    DAYS_14 = 1464
    DAYS_15 = 1465
    DAYS_16 = 1466
    DAYS_17 = 1467
    DAYS_18 = 1468
    DAYS_19 = 1469
    DAYS_20 = 1470
    DAYS_21 = 1471
    DAYS_22 = 1472
    DAYS_23 = 1473
    DAYS_TF = 1474

    def to_ccxt(self):
        if self.name == CandleType.DAYS.name:
            return '1d'
        elif self.name == CandleType.HOUR4.name:
            return '4h'
        elif self.name == CandleType.HOUR.name:
            return '1h'
        elif self.name == CandleType.MINUTES_30.name:
            return '30m'
        elif self.name == CandleType.MINUTES_15.name:
            return '15m'
        elif self.name == CandleType.MINUTES_10.name:
            return '10m'
        elif self.name == CandleType.MINUTES_5.name:
            return '5m'
        elif self.name == CandleType.MINUTES_3.name:
            return '3m'
        elif self.name == CandleType.MINUTES_1.name:
            return '1m'
        else:
            return None

@classmethod
def from_ccxt(cls, ccxt_str):
    if ccxt_str == '1d':
        return CandleType.DAYS
    elif ccxt_str == '4h':
        return CandleType.HOUR4
    elif ccxt_str == '1h':
        return CandleType.HOUR
    elif ccxt_str == '30m':
        return CandleType.MINUTES_30
    elif ccxt_str == '15m':
        return CandleType.MINUTES_15
    elif ccxt_str == '5m':
        return CandleType.MINUTES_5
    elif ccxt_str == '3m':
        return CandleType.MINUTES_3
    elif ccxt_str == '1m':
        return CandleType.MINUTES_1
    else:
        return None
