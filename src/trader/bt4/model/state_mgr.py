import datetime

from sqlalchemy import select, delete

from bt4.model.trade_object import Trade
from bt4.model.postgresql_mgr import PostgreSQLMgr
from bt4.model.state_model import BalanceState, TradeState

from bt4.utils.python_utils import SingletonInstance, now_dt, create_dt_at


class StateStorage(SingletonInstance) :
    def __init__(self) :
        self.balance_state_ids = {}
        self.last_bal_state_update_time = None
        self.is_bal_state_newly_updated = False

    def get_trade_states(self, account, ex_type, tid):
        tss = None
        with PostgreSQLMgr.instance().session() as session:
            tss = session.execute(select(TradeState).where(TradeState.user_id == account).
                                 where(TradeState.ex_type == ex_type.value).
                                 where(TradeState.tid == tid)).scalars().all()
            session.expunge_all()
        return tss

    def remove_trade_states(self, account, ex_type, tid) :
        with PostgreSQLMgr.instance().session() as session :
            session.execute(delete(TradeState).where(TradeState.user_id == account).
                             where(TradeState.ex_type == ex_type.value).
                             where(TradeState.tid == tid))
            session.commit()
            session.expunge_all()

    def get_trade_states_ids(self, account, ex_type, tid):
        tss = self.get_trade_states(account, ex_type, tid)
        ts_ids = []
        for ts in tss:
            ts_ids.append(ts.id)
        return None if len(ts_ids) == 0 else ts_ids

    def get_bought_trade_states(self, account, ex_type, tid):
        tss = self.get_trade_states(account, ex_type, tid)
        bought_trade_states = {}
        for ts in tss:
            flag_stmt = ts.flag_stmt
            if ts.is_processed == True:
                if ts.order == "BUY":
                    if flag_stmt.startswith("(B)"):  ## Hedging with Timeframe
                        buy_timeframe = flag_stmt.replace("(B)", "")
                        buy_timeframe = buy_timeframe[:buy_timeframe.find("/")]
                        bought_trade_states[f"{ts.market}_{buy_timeframe}"] = self.__build_trade_from_trade_states__(ts)
                    else:                            ## Netting with Timeframe
                        bought_trade_states[f"{ts.market}"] = self.__build_trade_from_trade_states__(ts)
        return bought_trade_states

    def __build_trade_from_trade_states__(self, ts):
        attr_values = {
            "is_processed"             : ts.is_processed,
            "order"                    : ts.order,
            "date"                     : ts.date,
            "market"                   : ts.market,
            "evaluated_market_balance" : ts.evaluated_market_balance,
            "settled_price"            : ts.settled_price,
            "settled_vol"              : ts.settled_vol,
            "fee"                      : ts.fee,
            "market_cash_bal"          : ts.market_cash_bal,
            "cash_bal"                 : ts.cash_bal,
            "profit"                   : ts.profit,
            "evaluated_balance"        : ts.evaluated_balance,
            "desc"                     : ts.desc,
            "tx_id"                    :ts.txid,
            "origin_tx_id"             : ts.origin_id
        }

        return Trade(**attr_values)

    def upsert_trade_states(self, account, ex_type, tid, trades, tsid_list=None):
        updated_tsid_list = []
        with PostgreSQLMgr.instance().session() as session:
            for idx, trade in enumerate(trades):
                ts_id = None
                if tsid_list is not None:
                    if idx < len(tsid_list):
                        ts_id = tsid_list[idx]

                flag_stmt = ""                                              # netting
                if trade.desc is not None and trade.desc.startswith("(B)"): # hdeging
                    flag_stmt = trade.desc
                attr_values = {
                    "id"      : ts_id,
                    "tid"     : tid,
                    "user_id" : account,
                    "ex_type" : ex_type.value,
                    "datetime": now_dt(),
                    "flag_stmt": flag_stmt,
                    "is_processed": trade.is_processed,
                    "order" : trade.order,
                    "date" : trade.date,
                    "market" : trade.market,
                    "evaluated_market_balance" : trade.evaluated_market_balance,
                    "settled_price" : trade.settled_price,
                    "settled_vol" : trade.settled_vol,
                    "fee" : trade.fee,
                    "market_cash_bal" : trade.market_cash_bal,
                    "cash_bal" : trade.cash_bal,
                    "profit" : trade.profit,
                    "evaluated_balance" : trade.evaluated_balance,
                    "desc" : trade.desc,
                    "txid" : trade.id,
                    "origin_id" : trade.origin_id
                }

                merged_obj = session.merge(TradeState(**attr_values))
                session.flush()
                updated_tsid_list.append(merged_obj.id)
                session.commit()
                session.expunge_all()

        # remove remainders (because sell trade state exists temporarily)
        if tsid_list is not None:
            remainders = list(set(tsid_list) - set(updated_tsid_list))
            with PostgreSQLMgr.instance().session() as session:
                for processed_sell_id in remainders:
                    print(f"remove TradeState : {processed_sell_id=}")
                    session.execute(delete(TradeState).where(TradeState.id == processed_sell_id))
                    session.commit()
                    session.expunge_all()
        return updated_tsid_list


    '''
        balance_state = {}
        balance_state['Total'] = 10000000
        balance_state['KRW'] = 10000
        balance_state['BTC'] = 0.2222
        balance_state['BTC_price'] = 25000
        balance_state['ETH'] = 0.2345
        balance_state['ETH_price'] = 14530
        balance_state['XRP'] = 15.24
        balance_state['XRP_price'] = 1234
    '''
    def upsert_balance_states(self, account, ex_type, tid, time_dt, base_cur, balance_states):

        total = balance_states["Total"]
        base_cur_amount = balance_states[base_cur]

        for mkt_key in balance_states:
            if mkt_key == "Total" or mkt_key == base_cur:
                continue
            if mkt_key.endswith("_price"):
                market = mkt_key.replace("_price", "")
                attr_values = {
                    "user_id"      : account,
                    "ex_type"      : ex_type.value,
                    "tid"          : tid,
                    "datetime"     : time_dt,
                    "total"        : total,
                    "base_cur"     : base_cur_amount,
                    "market"       : market,
                    "market_vol"   : balance_states[market],
                    "market_price" : balance_states[mkt_key]
                }

                bs = BalanceState(**attr_values)
                todays_bs = self.get_todays_balance_state(bs)
                if todays_bs is not None:
                    bs.id = todays_bs.id
                else:
                    bs.id = None

                StateStorage.instance().__upsert_balance_state__(bs)

    def get_balance_states(self, usr_uuid, ex_type, tid, base_cur):
        balance_states = {}
        _datetime = None

        with PostgreSQLMgr.instance().session() as session:
            bss = session.execute(select(BalanceState).where(BalanceState.user_id == usr_uuid).
                                 where(BalanceState.ex_type == ex_type.value).
                                 where(BalanceState.tid == tid).
                                 order_by(BalanceState.datetime.desc())).scalars().all()

            for bs in bss:
                if bs.market not in balance_states:
                    balance_states["Total"] = int(bs.total) if "Total" not in balance_states else balance_states["Total"]
                    balance_states[base_cur] = int(bs.base_cur) if base_cur not in balance_states else balance_states[base_cur]

                    balance_states[bs.market] = bs.market_vol
                    balance_states[f"{bs.market}_price"] = bs.market_price
                    _datetime = bs.datetime

            session.expunge_all()
        return balance_states, _datetime

    def __upsert_balance_state__(self, balance_state) -> BalanceState :

        with PostgreSQLMgr.instance().session() as session:
            merged_obj = session.merge(balance_state)
            session.flush()
            session.commit()
            balance_state.id = merged_obj.id
            session.expunge_all()

        return balance_state

    def get_todays_balance_state(self, b_state) -> BalanceState:
        bs = None
        base_hour = 9
        base_min = 0
        now = datetime.datetime.now()
        if now.hour >= base_hour and (now.minute -1) >= base_min:
            start_dt = create_dt_at(now.year, now.month, now.day, base_hour, base_min, 0)
        else:
            yesterday_dt = now-datetime.timedelta(days = 1)
            start_dt = create_dt_at(yesterday_dt.year, yesterday_dt.month, yesterday_dt.day, base_hour, base_min, 0)

        with PostgreSQLMgr.instance().session() as session:
            bs = session.execute(select(BalanceState).where(BalanceState.user_id == b_state.user_id).
                                 where(BalanceState.ex_type == b_state.ex_type).
                                 where(BalanceState.tid == b_state.tid).
                                 where(BalanceState.market == b_state.market).
                                 where(BalanceState.datetime >= start_dt).
                                 where(BalanceState.datetime <= now).
                                 order_by(BalanceState.datetime.desc())).scalar()
            session.expunge_all()
        return bs


