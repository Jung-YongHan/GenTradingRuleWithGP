import time
import unittest
import uuid

from bt4.Constants import ExType
from bt4.model.trade_object import Trade
from bt4.model.state_mgr import StateStorage
from bt4.model.state_model import BalanceState
from bt4.utils.python_utils import now_dt, now_str


class MyTestCase(unittest.TestCase) :


    def test_get_netting_brought_trade_states(self):
        import uuid
        account = str(uuid.uuid4())
        ex_type = ExType.upbit
        tid = 384
        trade_list = []
        import uuid
        uuid = str(uuid.uuid4())
        time_str = now_str()
        trade_list.append(Trade(False, 'BUY', time_str, 'KRW-BTC', 123, 0, 0, 0, 123, 111, 0, 222, f'', uuid, uuid))
        trade_list.append(Trade(False, 'SELL', time_str, 'KRW-BTC', 123, 0.222, 0, 12, 123, 123, 0, 0, f'', uuid,uuid))
        trade_list.append(Trade(True, 'BUY', time_str, 'KRW-ETH', 123, 0.222, 0, 12, 123, 123, 0, 0, f'', uuid,uuid))
        trade_list.append(Trade(True, 'SELL', time_str, 'KRW-ETH', 123, 0.222, 0, 12, 123, 123, 0, 0, f'', uuid,uuid))

        tsid_list = StateStorage.instance().upsert_trade_states(account, ex_type, tid, trade_list)

        tss = StateStorage.instance().get_bought_trade_states(account, ex_type, tid)
        for ts in tss:
            ts_obj = tss[ts]
            print(f"{ts_obj}")

    def test_get_hding_brought_trade_states(self):
        import uuid
        account = str(uuid.uuid4())
        ex_type = ExType.upbit
        tid = 384
        trade_list = []
        import uuid
        uuid = str(uuid.uuid4())
        time_str = now_str()
        trade_list.append(Trade(False, 'BUY', time_str, 'KRW-BTC', 123, 0, 0, 0, 123, 111, 0, 222, f'(B)07:59/(S)07:79', uuid, uuid))
        trade_list.append(Trade(False, 'SELL', time_str, 'KRW-BTC', 123, 0.222, 0, 12, 123, 123, 0, 0, f'(S)17:59/(B)17:79', uuid,uuid))
        trade_list.append(Trade(True, 'BUY', time_str, 'KRW-ETH', 123, 0.222, 0, 12, 123, 123, 0, 0, f'(B)07:59/(S)07:79', uuid,uuid))
        trade_list.append(Trade(True, 'BUY', time_str, 'KRW-ETH', 123, 0.222, 0, 12, 123, 123, 0, 0, f'(S)17:59/(B)17:79', uuid,uuid))

        tsid_list = StateStorage.instance().upsert_trade_states(account, ex_type, tid, trade_list)

        tss = StateStorage.instance().get_bought_trade_states(account, ex_type, tid)
        print(f"{tss=}")

    def test_store_netting_trade_states(self):
        import uuid
        account = str(uuid.uuid4())
        ex_type = ExType.upbit
        tid = 384
        trade_list = []
        import uuid
        uuid = str(uuid.uuid4())
        time_str = now_str()
        trade_list.append(Trade(False, 'BUY', time_str, 'KRW-BTC', 123, 0, 0, 0, 123, 111, 0, 222, f'', uuid, uuid))
        trade_list.append(Trade(False, 'SELL', time_str, 'KRW-BTC', 123, 0.222, 0, 12, 123, 123, 0, 0, f'', uuid, uuid))
        trade_list.append(Trade(True, 'BUY', time_str, 'KRW-ETH', 123, 0.222, 0, 12, 123, 123, 0, 0, f'', uuid, uuid))
        trade_list.append(Trade(True, 'BUY', time_str, 'KRW-ETH', 123, 0.222, 0, 12, 123, 123, 0, 0, f'', uuid, uuid))

        tsid_list = StateStorage.instance().upsert_trade_states(account, ex_type, tid, trade_list)

        while (True) :
            print("waiting for 10 sec.")
            time.sleep(10)
            StateStorage.instance().upsert_trade_states(account, ex_type, tid, trade_list, tsid_list)


    def test_store_hdging_trade_states(self):
        import uuid
        account = str(uuid.uuid4())
        ex_type = ExType.upbit
        tid = 384
        trade_list = []
        import uuid
        uuid = str(uuid.uuid4())
        time_str = now_str()
        trade_list.append(Trade(False, 'BUY', time_str, 'KRW-BTC', 123, 0, 0, 0, 123, 111, 0, 222, f'(B)07:59/(S)07:79', uuid, uuid))
        trade_list.append(Trade(False, 'SELL', time_str, 'KRW-BTC', 123, 0.222, 0, 12, 123, 123, 0, 0, f'(S)17:59/(B)17:79', uuid, uuid))
        trade_list.append(Trade(True, 'BUY', time_str, 'KRW-ETH', 123, 0.222, 0, 12, 123, 123, 0, 0, f'(B)07:59/(S)07:79', uuid, uuid))
        trade_list.append(Trade(True, 'BUY', time_str, 'KRW-ETH', 123, 0.222, 0, 12, 123, 123, 0, 0, f'(S)17:59/(B)17:79', uuid, uuid))

        tsid_list = StateStorage.instance().upsert_trade_states(account, ex_type, tid, trade_list)

        while (True) :
            print("waiting for 10 sec.")
            time.sleep(10)
            StateStorage.instance().upsert_trade_states(account, ex_type, tid, trade_list, tsid_list)


    def test_balance_state(self) :
        account = str(uuid.uuid4())
        ex_type = ExType.upbit
        tid = 384

        attr_values = {
            "user_id" : account,
            "ex_type" : ex_type.value,
            "tid"     : tid,
            "ex_type" : ex_type.value,
            "datetime": now_dt(),
            "total"   : 2865.731716902534,
            "base_cur": 1508.9928244694129,
            "market"  : "KRW-BTC",
            "market_vol" : 1508.9928244694129,
            "market_price": 1508.9928244694129
        }

        bs =  BalanceState(**attr_values)

        merged_bs_obj = StateStorage.instance().__upsert_balance_state__(bs)
        print(f"{merged_bs_obj.id=}")

        print("waiting for 10 sec.")
        time.sleep(10)

        merged_bs_obj.total = 1111111.11111
        merged_ts_obj = StateStorage.instance().__upsert_balance_state__(merged_bs_obj)
        print(f"{merged_ts_obj.id=}")
        print(f"{merged_ts_obj.total=}")

    def test_balance_state2(self) :
        account = "721b98e3-23c0-4545-875c-31d63f7ec7c9"
        ex_type = ExType.upbit
        tid = 384
        now = now_dt()

        id = 9
        if now.hour >= 9 and now.minute >= 0:
            id = None

        attr_values = {
            "id"      : id,
            "user_id" : account,
            "ex_type" : ex_type.value,
            "tid"     : tid,
            "datetime": now_dt(),
            "total"   : 2865.731716902534,
            "base_cur": 1508.9928244694129,
            "market"  : "KRW-BTC",
            "market_vol" : 1508.9928244694129,
            "market_price" :1508.9928244694129
        }

        bs = BalanceState(**attr_values)

        merged_bs_obj = StateStorage.instance().__upsert_balance_state__(bs)
        print(f"{merged_bs_obj.id=}")

        print("waiting for 10 sec.")
        time.sleep(10)

        merged_ts_obj = StateStorage.instance().get_todays_balance_state(merged_bs_obj)
        print(f"{merged_ts_obj.id=}")

    def test_get_balance_state(self) :
        account = "721b98e3-23c0-4545-875c-31d63f7ec7c9"
        ex_type = ExType.upbit
        tid = 384

        attr_values = {
            "id"      : id,
            "user_id" : account,
            "ex_type" : ex_type.value,
            "tid"     : tid,
            "datetime": now_dt(),
            "total"   : 2865.731716902534,
            "base_cur": 1508.9928244694129,
            "market"  : "KRW-BTC",
            "market_vol" : 1508.9928244694129,
            "market_price" :1508.9928244694129
        }

        bs = BalanceState(**attr_values)

        merged_ts_obj = StateStorage.instance().get_todays_balance_state(bs)
        if merged_ts_obj is None:
            print("there is no today's balance state")
        else:
            print(f"{merged_ts_obj.id=}")

    def test_upsert_balance_states(self):
        account = "721b98e3-23c0-4545-875c-31d63f7ec7c9"
        ex_type = ExType.upbit
        tid = 384

        balance_state = {}
        balance_state['Total'] = 10000000
        balance_state['KRW'] = 10000
        balance_state['BTC'] = 0.2222
        balance_state['BTC_price'] = 25000
        balance_state['ETH'] = 0.2345
        balance_state['ETH_price'] = 14530
        balance_state['XRP'] = 15.24
        balance_state['XRP_price'] = 1234

        while(True):
            now = now_dt()
            StateStorage.instance().upsert_balance_states(account, ex_type, tid, now, "KRW", balance_state)
            time.sleep(20)
            balance_states, datetime = StateStorage.instance().get_balance_states(account, ex_type, tid, "KRW")
            print(f"{datetime=} => {balance_states}")



if __name__ == '__main__' :
    unittest.main()
