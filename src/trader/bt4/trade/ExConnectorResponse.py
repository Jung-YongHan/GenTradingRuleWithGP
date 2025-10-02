from bt4.utils.python_utils import SingletonInstance, load_class_from_module, from_utc_int_timestamp, TIME_FORMAT


class ExResponseHandlerFactory(SingletonInstance):
    def __init__(self):
        pass

    def get(self, ex_type):
        handler_cls = ex_type.value + '_ExResponseHandler'
        return load_class_from_module(self.__module__, handler_cls)


class GeneralExResponseHandler:
    def __init__(self):
        self.extracted_vars = {}

    def handle(self, resp_dict):
        print(f'GeneralExResponseHandler : {resp_dict}')
        self.extracted_vars = {}

        if 'fee' in resp_dict and resp_dict['fee'] is not None:
            paid_fee = resp_dict['fee']['cost']
            resp_dict['paid_fee'] = float(paid_fee) if isinstance(paid_fee, str) else paid_fee
            resp_dict['paid_fee_currency'] = resp_dict['fee']['currency']
        else:
            resp_dict['paid_fee'] = 0
            resp_dict['paid_fee_currency'] = 'BASE_CURRENCY'

        resp_dict['trades'] = self.__handle_trades__(resp_dict['trades'])
        resp_dict['trades_count'] = len(resp_dict['trades'])

        ex_resp = ExResponse()
        for var in ex_resp.__dict__:
            self.extracted_vars[var] = resp_dict[var] if var in resp_dict else None

    def __handle_trades__(self, trades_dict):
        trade_list = []
        for trade_dict in trades_dict:
            ex_resp_trade = ExResp_Trade.__new__(ExResp_Trade)
            ex_resp_trade.__dict__.update(trade_dict)
            trade_list.append(ex_resp_trade)
        return trade_list



    def update_n_create_ExResponse(self):
        ex_resp = ExResponse.__new__(ExResponse)
        ex_resp.__dict__.update(self.extracted_vars)
        return ex_resp


class upbit_ExResponseHandler(GeneralExResponseHandler):
    def __init__(self):
        super(upbit_ExResponseHandler, self).__init__()

    def handle(self, resp_dict):
        super(upbit_ExResponseHandler, self).handle(resp_dict)
        info = resp_dict['info']
        self.extracted_vars['price'] = info['price'] if 'price' in info else None   ## For the sell in upbit, it does not exist price

        return super(upbit_ExResponseHandler, self).update_n_create_ExResponse()

class bithumb_ExResponseHandler(GeneralExResponseHandler):
    def __init__(self):
        super(bithumb_ExResponseHandler, self).__init__()

    def handle(self, resp_dict):
        super(bithumb_ExResponseHandler, self).handle(resp_dict)
        info = resp_dict['info']
        if "status" in info:
            self.extracted_vars['status'] = "open" if info["status"] == "0000" else "Error"
        elif "order_status" in info:
            self.extracted_vars['status'] = "closed" if info["order_status"] == "Completed" else "Error"

        self.extracted_vars['price'] = resp_dict['price'] if 'price' in resp_dict else None

        return super(bithumb_ExResponseHandler, self).update_n_create_ExResponse()

class binance_ExResponseHandler(GeneralExResponseHandler):
    def __init__(self):
        super(binance_ExResponseHandler, self).__init__()

    def handle(self, resp_dict):
        super(binance_ExResponseHandler, self).handle(resp_dict)
        info = resp_dict['info']
        if self.extracted_vars['status'] == 'closed':
            self.extracted_vars['status'] = 'open'

        return super(binance_ExResponseHandler, self).update_n_create_ExResponse()


class binanceusdm_ExResponseHandler(GeneralExResponseHandler):
    def __init__(self):
        super(binanceusdm_ExResponseHandler, self).__init__()

    def handle(self, resp_dict):
        super(binanceusdm_ExResponseHandler, self).handle(resp_dict)
        info = resp_dict['info']
        timestamp = info['updateTime']
        self.extracted_vars['timestamp'] = timestamp
        # timestamp_dt = datetime.fromtimestamp(int(timestamp))
        timestamp_dt = from_utc_int_timestamp(timestamp, to_kor_timezone=True)
        self.extracted_vars['datetime'] = timestamp_dt.strftime(TIME_FORMAT)

        return super(binanceusdm_ExResponseHandler, self).update_n_create_ExResponse()


class ExResponse:
    def __init__(self):
        self.id = None          # '57af968a-ce17-4a60-b92f-e7bd7b217c99',
        self.clientOrderId = None
        self.timestamp = None   #1673620275704
        self.datetime = None    #'2023-01-13T14:31:15.704Z'
        self.lastTradeTimestamp = None # None
        self.symbol = None      # 'BTC/KRW'
        self.type = None        # 'market'
        self.timeInForce = None # None
        self.postOnly = None    # None
        self.side = None        # 'buy'
        self.price = None       # None
        self.stopPrice = None   # None
        self.cost = None        # 5094.9
        self.average = None     # None
        self.amount = None      # None
        self.filled = None      # 0.0
        self.remaining = None   # None
        self.status = None      # 'open'
        self.fee = None         # {'currency = None # 'KRW', 'cost = None # 0.0},
        self.paid_fee = None    # NEW (Not in ccxt) => fee['cost']
        self.paid_fee_currency = None  # NEW (Not in ccxt)  => fee['currency']
        self.trades = None      # []
        self.trades_count = None # NEW (Not in ccxt) => len(trades)

    def get(self, key):
        return self.resp_dict[key]

class ExResp_Trade:
    def __init__(self):
        self.timestamp = None  # None,
        self.datetime = None  # None,
        self.symbol = None  # 'BTC/USDT'
        self.id = None  # '2472442211',
        self.order = None  # '17273552707'
        self.type = None  # 'market'
        self.side = None  # 'sell'
        self.takerOrMaker = None  # None,
        self.price = None  # 18817.11
        self.amount = None  # 0.00058
        self.cost = None  # 10.9139238,
        self.fee = None  # {'cost': 0.0, 'currency': 'BNB'},
        self.fees = None  # [{'cost': 0.0, 'currency': 'BNB'}]
