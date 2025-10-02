import unittest

from sqlalchemy import select, update
from sqlalchemy.ext.serializer import loads

from bt4.Constants import ExType, Operation_Type
from bt4.model.storage_mgr import StrategyStorage
from bt4.model.trade_model import TradeUnit, TRSummary
from bt4.model.postgresql_mgr import PostgreSQLMgr
import pandas as pd

from bt4.model.trade_object import Trade

pd.set_option("display.max_columns", None)
pd.set_option("display.expand_frame_repr", False)
pd.set_option("max_colwidth", None)

class MyTestCase(unittest.TestCase) :

    def setUp(self) -> None :
        pass
        # with PostgreSQLMgr.instance().session() as session :
        #     Base.metadata.drop_all(PostgreSQLMgr.instance().__sync_engine__)
        #     Base.metadata.create_all(PostgreSQLMgr.instance().__sync_engine__)

    def test_get_trade_units(self):
        tus = StrategyStorage.instance().get_trade_units(122, 863)
        for tu in tus:
            tr = Trade.from_trade_unit(tu)
            print(f"{tu} => {tr}")


    def test_get_tr_summary_id(self):
        tr_sum_id = StrategyStorage.instance().get_tr_summary_id(122, Operation_Type.LIVE_TRADING)
        print(tr_sum_id)

    def test_postgre_bt_summary_load(self):

        with PostgreSQLMgr.instance().session() as session :
            bts = session.execute(select(TRSummary).where(TRSummary.id == "dc3f6d4a-dc11-4e90-8a3a-a90a71c3ce5b")).scalar()
            print(bts)
            if bts is not None:
                df = loads(bts.result_df)
                print(df.head(10))



    def test_postgre_bt_add(self) :
        attr_values2 = {
            "stgy_id"             : "aaaaaaaa",
            "bt_start"           : "2023-01-24 08:59:00",
            "bt_end" : "2023-01-24 08:59:00",
            "last_balance"        : "0",
            "num_of_trades" : "0",
            "num_of_wins"   : "0",
            "num_of_loses"  : "0",
            "mdd"           : "0",
        }
        bt_summary = TRSummary(**attr_values2)

        with PostgreSQLMgr.instance().session() as session :
            print(f"after commit: {bt_summary.id}")
            session.add(bt_summary)
            session.commit()
            bt_sum_id = bt_summary.id
            print(f"after commit: {bt_summary.id}")


        for idx in range(10):
            attr_values = {
                "bt_sum_id" : bt_sum_id,
                "is_processed" : True,
                "order"  : "BUY",
                "date" : "2023-01-24 08:59:00",
                "market" : "KRW-BTC",
                "evaluated_market_balance" : "1318943.6698349174",
                "settled_price" : "28609000.0",
                "settled_vol" : "0.04610240378324714",
                "fee" : "1055.4848367359264",
                "market_cash_bal" : "8680000.845328346",
                "profit" : "0.0",
                "evaluated_balance" : "9998944.515163263",
                "desc" : """,
                    *[time] = True::time(2023-01-24 08:59:00) == base_time(08:59)
                    *[ma] = True::price(28609000.0) > ma(27912600.0),""",
                "origin_id" : "60989e17-b633-4895-8237-e267bc2725be"
            }
            bttrade_unit = TradeUnit(**attr_values)

            with PostgreSQLMgr.instance().session() as session :
                session.add(bttrade_unit)
                session.commit()

        attr_values2 = {
            "stgy_id"             : "aaaaaaaa",
            "bt_start"           : "2023-01-24 08:59:00",
            "last_balance"        : "8680000.845328346",
            "num_of_trades" : "1111",
            "num_of_wins"   : "2222",
            "num_of_loses"  : "3333",
            "mdd"           : "-50",
            # "balance_chart" : "cd:\asdf\asdf",
        }
        bt_summary2 = TRSummary(**attr_values2)

        with PostgreSQLMgr.instance().session() as session :
            session.execute(update(TradeUnit).where(TradeUnit.tr_sum_id == bt_summary.id).values(bt_sum_id = bt_sum_id))

            session.execute(
                update(TRSummary).where(TRSummary.id == bt_summary.id).values(last_balance = attr_values2["last_balance"],
                                                                              num_of_trades = attr_values2["num_of_trades"],
                                                                              num_of_wins = attr_values2["num_of_wins"],
                                                                              num_of_loses = attr_values2["num_of_loses"],
                                                                              mdd = attr_values2["mdd"],
                                                                              ))
            # session.execute(
            #     update(BTSummary).where(BTSummary.id == bt_summary.id).values(last_balance = bt_summary2.last_balance,
            #                                                                   num_of_trades = bt_summary2.num_of_trades,
            #                                                                   num_of_wins = bt_summary2.num_of_wins,
            #                                                                   num_of_loses = bt_summary2.num_of_loses,
            #                                                                   mdd = bt_summary2.mdd,
            #                                                                   ))
            session.commit()




    def test_postgre_bt_add_trading_summary(self) :
        attr_values2 = {
            "stgy_id"                       : "aaaaaaaa",
            "bt_period"                     : "2023-01-24 08:59:00",
            "last_balance"                  : "8680000.845328346",
            "num_of_trades"                 : "1111",
            "num_of_wins"                   : "2222",
            "num_of_loses"                  : "3333",
            "mdd"                           : "-50",
            "yearly_profit_ratio"           : "10.5",
            "worst_num_of_continuous_loses" : "57",
            "worst_lost_profit"             : "9998944.65",
            "best_num_of_continuous_loses"  : "11",
            "best_lost_profit"              : "4234.44",
            "buy_n_hold_profit"             : "645",
            "balance_chart"                 : "cd:\asdf\asdf",
        }
        bt_summary = TRSummary(**attr_values2)

        with PostgreSQLMgr.instance().session() as session :
            session.add(bt_summary)
            print(f"id-before: {bt_summary.id}")
            session.add(bt_summary)
            session.commit()
            print(f"id-after: {bt_summary.id}")

    def test_postgre_bt_add_trading_unit(self) :
        # trade_unit_list  = []
        # for idx in range(10):
        attr_values = {
            "is_processed" : True,
            "order"  : "BUY",
            "date" : "2023-01-24 08:59:00",
            "market" : "KRW-BTC",
            "evaluated_market_balance" : "1318943.6698349174",
            "settled_price" : "28609000.0",
            "settled_vol" : "0.04610240378324714",
            "fee" : "1055.4848367359264",
            "market_cash_bal" : "8680000.845328346",
            "profit" : "0.0",
            "evaluated_balance" : "9998944.515163263",
            "desc" : """,
                *[time] = True::time(2023-01-24 08:59:00) == base_time(08:59)
                *[ma] = True::price(28609000.0) > ma(27912600.0),""",
            "origin_id" : "60989e17-b633-4895-8237-e267bc2725be"
        }
        bttrade_unit = TradeUnit(**attr_values)


        with PostgreSQLMgr.instance().session() as session :
            session.add(bttrade_unit)
            session.commit()

    def test_postgre_bt_add_trading_unit(self) :
        # trade_unit_list  = []
        # for idx in range(10):
        attr_values = {
            "is_processed" : True,
            "order"  : "BUY",
            "date" : "2023-01-24 08:59:00",
            "market" : "KRW-BTC",
            "evaluated_market_balance" : "1318943.6698349174",
            "settled_price" : "28609000.0",
            "settled_vol" : "0.04610240378324714",
            "fee" : "1055.4848367359264",
            "market_cash_bal" : "8680000.845328346",
            "profit" : "0.0",
            "evaluated_balance" : "9998944.515163263",
            "desc" : """,
                *[time] = True::time(2023-01-24 08:59:00) == base_time(08:59)
                *[ma] = True::price(28609000.0) > ma(27912600.0),""",
            "origin_id" : "60989e17-b633-4895-8237-e267bc2725be"
        }
        bttrade_unit = TradeUnit(**attr_values)


        with PostgreSQLMgr.instance().session() as session :
            session.add(bttrade_unit)
            session.commit()

    def test_postgre_migrate_user_account(self) :

        StrategyStorage.instance().add_usr_account("08be8af3-d45a-4aa6-8e73-523283831a5a", ExType.upbit, "123aaaaaa", "123aaaaaasss", "2024-07-15 23:00:00")

        am = StrategyStorage.instance().load_usr_api_key("08be8af3-d45a-4aa6-8e73-523283831a5a", "upbit")
        print(f"{am.id=}, {am.user_id=}, {am.ex_type=}, {am.access_key=}, {am.secret_key=}, {am.exp_date=}")


if __name__ == '__main__' :
    unittest.main()
