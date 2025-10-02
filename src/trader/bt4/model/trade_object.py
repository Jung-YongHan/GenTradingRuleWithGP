import json

from bt4.model.trade_model import TradeUnit


class Trade:
    def __init__(self, is_processed, order, date, market, evaluated_market_balance,
                 settled_price, settled_vol, fee, market_cash_bal, cash_bal, profit,
                 evaluated_balance, desc, tx_id, origin_tx_id):
        self.is_processed = is_processed
        self.order = order
        self.date = date
        self.market = market
        self.evaluated_market_balance = evaluated_market_balance
        self.settled_price = settled_price
        self.settled_vol = settled_vol
        self.fee = fee
        self.market_cash_bal = market_cash_bal
        self.cash_bal = cash_bal
        self.profit = profit
        self.evaluated_balance = evaluated_balance
        self.desc = desc
        self.id = tx_id
        self.origin_id = origin_tx_id

    @classmethod
    def columns(cls):
        return ['order','date','market','evaluated_market_balance','price','vol','fee',
                'market_cash_bal','cash_bal', 'profit', 'evaluated_balance', 'desc', 'id', 'origin_id']

    def __str__(self):
        p_string = f'({self.date}) {self.order} - {self.market} {self.evaluated_market_balance:3.1f}' \
                   f'({self.settled_price:3.1f}, {self.settled_vol:3.8f}, {self.fee:3.1f}) {self.desc}' \
                   f', market assigned cash: {self.market_cash_bal:3.2f}, Remained Cash:{self.cash_bal:3.2f},' \
                   f' profit:{self.profit}, Estimated Balance: {self.evaluated_balance:3.2f}'
        return p_string

    def toList(self):
        return [self.order, self.date, self.market, self.evaluated_market_balance, self.settled_price, self.settled_vol, self.fee,
                self.market_cash_bal, self.cash_bal, self.profit, self.evaluated_balance, self.desc, self.id, self.origin_id]

    def to_json(self):
        return f' "is_processed" : "{self.is_processed}", "order": "{self.order}", "date": "{self.date}", ' \
               f' "market": "{self.market}", "evaluated_market_balance" : "{self.evaluated_market_balance}", ' \
               f' "settled_price": "{self.settled_price}", "settled_vol" : "{self.settled_vol}", '\
               f' "fee" : "{self.fee}",  "market_cash_bal" : "{self.market_cash_bal}", "cash_bal" : "{self.cash_bal}", ' \
               f' "profit" : "{self.profit}", "evaluated_balance" : "{self.evaluated_balance}", "desc" : "{self.desc}" }}' \
               f' "id": {self.id}, "Origin" : "{self.origin_id}"'

    def from_json(json_string):
        json_obj = json.loads(json_string)
        if json_obj is not None:
            is_processed = True if json_obj['is_processed'] == 'True' else False
            order = json_obj['order']
            date = json_obj['date']
            market = json_obj['market']
            evaluated_market_balance = float(json_obj['evaluated_market_balance'])
            settled_price = float(json_obj['settled_price'])
            settled_vol = float(json_obj['settled_vol'])
            fee = float(json_obj['fee'])
            market_cash_bal = float(json_obj['market_cash_bal'])
            cash_bal = float(json_obj['cash_bal'])
            profit = float(json_obj['profit'])
            evaluated_balance = float(json_obj['evaluated_balance'])
            desc = json_obj['desc']
            id = json_obj['id'] if 'id' in json_obj else ""
            origin_id = json_obj['origin_id'] if 'origin_id' in json_obj else ""
            return Trade(is_processed, order, date, market, evaluated_market_balance, settled_price, settled_vol, fee,
                         market_cash_bal, cash_bal, profit,
                         evaluated_balance, desc, id, origin_id, tid)
        else:
            return None

    def to_trade_unit(self, tr_sum_id, tid) :
        attr_values = {
            "tr_sum_id"                : tr_sum_id,
            "is_processed"             : self.is_processed,
            "order"                    : self.order,
            "date"                     : self.date,
            "market"                   : self.market,
            "evaluated_market_balance" : self.evaluated_market_balance,
            "settled_price"            : self.settled_price,
            "settled_vol"              : self.settled_vol,
            "fee"                      : self.fee,
            "market_cash_bal"          : self.market_cash_bal,
            "cash_bal"                 : self.cash_bal,
            "profit"                   : self.profit,
            "evaluated_balance"        : self.evaluated_balance,
            "desc"                     : self.desc,
            "origin_id"                : self.origin_id,
            "tid" : tid,
        }
        return TradeUnit(**attr_values)

    def from_trade_unit(tu):
        trade = Trade.__new__(Trade)
        trade.__dict__.update(tu.__dict__)
        if trade.__dict__["cash_bal"] == None:
            trade.__dict__["cash_bal"] = 0
        return trade