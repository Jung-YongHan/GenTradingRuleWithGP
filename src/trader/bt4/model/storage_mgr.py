from sqlalchemy import select, desc, update, delete, text
from sqlalchemy.ext.serializer import dumps

from bt4.model.postgresql_mgr import PostgreSQLMgr
from bt4.model.trade_model import TradingRequestTbl, TRSummary, TradeUnit, UserExchangeApiKeyModel, AIModel
from bt4.utils.python_utils import SingletonInstance
import inspect

class StrategyStorage(SingletonInstance) :
    def __init__(self) :
        self.support_db_access_count = False
        self.db_access_method_cnt = 0
        self.db_access_req = {}

    """
    Use only for storing strategy config rules (for storing strategy for backtesting) 
    """
    def store_trading_request(self, stgy_json_name, ex_type, op_type, cfg_stgy_rules_json) -> str :
        if self.support_db_access_count:
            self.__inc_db_access_cnt__(inspect.currentframe().f_code.co_name)
        attr_values = {
            "cfg_stgy_rules_json" : cfg_stgy_rules_json,
            "sid"                 : "cbf03663-ba81-4a2d-b257-46ce9131b4ab",
            "user_id"             : "844164d3-207f-4fdf-8464-01a7bf20e663",
            "user_id_first_char"  : "b",
            "period_type"         : "custom",
            "bt_start"            : cfg_stgy_rules_json["bt_start"],
            "bt_end"              : cfg_stgy_rules_json["bt_end"],
            "op_type"             :  op_type,
            "stgy_name"           : stgy_json_name,
            "ex_type"             : ex_type,
        }

        stgy = TradingRequestTbl(**attr_values)

        sid = None
        with PostgreSQLMgr.instance().session() as session :
            session.add(stgy)
            sid = session.commit()
        return sid

    def load_strategy_using_tid(self, tid) :
        if self.support_db_access_count :
            self.__inc_db_access_cnt__(inspect.currentframe().f_code.co_name)

        stbl = None
        with PostgreSQLMgr.instance().session() as session :
            stbl = session.execute(select(TradingRequestTbl).where(TradingRequestTbl.tid == tid)).scalar()
        return stbl

    def load_strategy_using_desc(self, op_type, desc2) :
        self.__inc_db_access_cnt__(inspect.currentframe().f_code.co_name)
        stbl = None
        with PostgreSQLMgr.instance().session() as session :
            stbl = session.execute(select(TradingRequestTbl).where(TradingRequestTbl.op_type == op_type).where(TradingRequestTbl.desc == desc2).
                                   order_by(desc(TradingRequestTbl.tid))).scalars().first()
        return stbl

    def load_strategy_using_stgyname(self, op_type, stgy_name) :
        if self.support_db_access_count :
            self.__inc_db_access_cnt__(inspect.currentframe().f_code.co_name)

        stbl = None
        with PostgreSQLMgr.instance().session() as session :
            stbl = session.execute(select(TradingRequestTbl).where(TradingRequestTbl.op_type == op_type).where(TradingRequestTbl.stgy_name == stgy_name).
                                   order_by(desc(TradingRequestTbl.tid))).scalars().first()
        return stbl

    def get_trading_id_of_desc(self, op_type, desc) :
        if self.support_db_access_count :
            self.__inc_db_access_cnt__(inspect.currentframe().f_code.co_name)

        stbl = self.load_strategy_using_desc(op_type, desc)
        if stbl is not None:
            return stbl.tid
        return None

    def get_trading_id_of_stgyname(self, op_type, stgy_name) :
        if self.support_db_access_count :
            self.__inc_db_access_cnt__(inspect.currentframe().f_code.co_name)

        stbl = self.load_strategy_using_stgyname(op_type, stgy_name)
        if stbl is not None:
            return stbl.tid
        return None

    def load_backtesting_request(self, tid):
        if self.support_db_access_count :
            self.__inc_db_access_cnt__(inspect.currentframe().f_code.co_name)

        btrt = None
        with PostgreSQLMgr.instance().session() as session :
            btrt = session.execute(select(TradingRequestTbl).where(TradingRequestTbl.tid == tid)).scalar()
        return btrt

    def get_tr_summary_id(self, tid, op_type):
        if self.support_db_access_count :
            self.__inc_db_access_cnt__(inspect.currentframe().f_code.co_name)

        tr_summary_id = None
        with PostgreSQLMgr.instance().session() as session :
            tr_summary = session.execute(select(TRSummary).where(TRSummary.tid == tid).where(TRSummary.op_type == op_type)).scalar()
            if tr_summary is not None:
                tr_summary_id = tr_summary.id
        return tr_summary_id

    def add_initial_tr_summary(self, tid, bt_start, bt_end, op_type, markets) -> str:
        if self.support_db_access_count :
            self.__inc_db_access_cnt__(inspect.currentframe().f_code.co_name)

        tr_sum_id = None
        attr_values2 = {
            "tid"      : tid,
            "bt_start" : bt_start,
            "bt_end"   : bt_end,
            "op_type"  : op_type,
            "markets"  : str(markets)[1 :-1],
        }
        bts = TRSummary(**attr_values2)
        with PostgreSQLMgr.instance().session() as session :
            session.add(bts)
            session.commit()
            tr_sum_id = bts.id
        return tr_sum_id

    def update_trade_summary(self, tr_sum_id, result_dic, result_df):
        if self.support_db_access_count :
            self.__inc_db_access_cnt__(inspect.currentframe().f_code.co_name)

        with PostgreSQLMgr.instance().session() as session :
            session.execute(update(TRSummary).where(TRSummary.id == tr_sum_id).values(
                bt_end = result_dic["bt_end"],
                markets = result_dic["markets"],
                last_balance = result_dic["last_bal"],
                max_bal = result_dic["max_bal"],
                init_bal = result_dic["init_bal"],
                trade_win_rate = result_dic["trade_win_rate"],
                num_of_trades = result_dic["num_of_trades"],
                num_of_wins = result_dic["num_of_wins"],
                num_of_loses = result_dic["num_of_loses"],
                profit_sum = result_dic["profit_sum"],
                invest_sum = result_dic["invest_sum"],
                avg_profit_ratio = result_dic["avg_profit_ratio"],
                num_1_pcnt = result_dic["num_1_pcnt"],
                num_2_pcnt = result_dic["num_2_pcnt"],
                num_3_pcnt = result_dic["num_3_pcnt"],
                num_5_pcnt = result_dic["num_5_pcnt"],
                settle_winning_rate = result_dic["settle_winning_rate"],
                settle_total_trade = result_dic["settle_total_trade"],
                settle_winning = result_dic["settle_winning"],
                settle_lose = result_dic["settle_lose"],
                mdd = result_dic["mdd"] if "mdd" in result_dic else "0",
                mdd_10 = result_dic["mdd_10"] if "mdd_10" in result_dic else "0",
                mdd_20 = result_dic["mdd_20"] if "mdd_20" in result_dic else "0",
                twoXdur = result_dic["2xdur"],
                mpr = result_dic["mpr"] if "mpr" in result_dic else "0",
                profit_std = result_dic["profit_std"] if "profit_std" in result_dic else "0",
                sharp_index = result_dic["sharp_index"] if "sharp_index" in result_dic else "0",
                result_df = dumps(result_df))
            )
            session.commit()

    def update_ga_params(self, tr_sum_id, stgy_json, ga_params):
        if self.support_db_access_count :
            self.__inc_db_access_cnt__(inspect.currentframe().f_code.co_name)

        with PostgreSQLMgr.instance().session() as session :
            session.execute(update(TRSummary).where(TRSummary.id == tr_sum_id).values(
                tr_req_json = stgy_json ,
                ga_params_json = ga_params
                )
            )
            session.commit()

    def delete_trade_unit(self, tr_sum_id) :
        if self.support_db_access_count :
            self.__inc_db_access_cnt__(inspect.currentframe().f_code.co_name)

        with PostgreSQLMgr.instance().session() as session:
            session.execute(delete(TradeUnit).where(TradeUnit.tr_sum_id == tr_sum_id))
            session.commit()

    def add_trade_unit(self, trade_unit_obj):
        if self.support_db_access_count :
            self.__inc_db_access_cnt__(inspect.currentframe().f_code.co_name)

        with PostgreSQLMgr.instance().session() as session :
            session.add(trade_unit_obj)
            session.commit()

    def get_trade_units(self, tid, tr_sum_id):
        if self.support_db_access_count :
            self.__inc_db_access_cnt__(inspect.currentframe().f_code.co_name)

        trade_units = []
        with PostgreSQLMgr.instance().session() as session :
            trade_units = session.execute(select(TradeUnit).where(TradeUnit.tid == tid).where(TradeUnit.tr_sum_id == tr_sum_id).order_by(TradeUnit.date.asc())).scalars().all()
        return trade_units

    def add_usr_account(self, uid, ex_type, access_key, secret_key, exp_date):
        if self.support_db_access_count :
            self.__inc_db_access_cnt__(inspect.currentframe().f_code.co_name)

        id = None
        attr_values2 = {
            "user_id"      : "08be8af3-d45a-4aa6-8e73-523283831a5a",
            "ex_type" : ex_type,
            "access_key"   : access_key,
            "secret_key"  : secret_key,
            "exp_date"  : exp_date,
            "executable_ip_addresses" : ["123.123.123.123","123.123.123.124","123.123.123.124"]
        }
        am = UserExchangeApiKeyModel(**attr_values2)
        with PostgreSQLMgr.instance().session() as session :
            session.add(am)
            session.commit()
            id = am.id
        return id

    def load_usr_api_key(self, user_id, ex_type):
        if self.support_db_access_count :
            self.__inc_db_access_cnt__(inspect.currentframe().f_code.co_name)

        am = None
        with PostgreSQLMgr.instance().session() as session :
            am = session.execute(select(UserExchangeApiKeyModel).where(UserExchangeApiKeyModel.user_id == user_id).where(
                UserExchangeApiKeyModel.ex_type == ex_type
            )).scalar()
        return am

    def load_ai_model(self, ex_type: str, pred_len: int, model: str, category: str, market: str, candle_type: str):
        if self.support_db_access_count :
            self.__inc_db_access_cnt__(inspect.currentframe().f_code.co_name)

        with PostgreSQLMgr.instance().session() as session:
            result = session.execute(
                select(AIModel)
                .where(AIModel.ex_type == ex_type)
                .where(AIModel.pred_len == pred_len)
                .where(AIModel.model == model)
                .where(AIModel.category == category)
                .where(AIModel.market == market)
                .where(AIModel.candle_type == candle_type)
            ).scalar()
        return result

    def update_backtesting_progress(self, tr_sum_id, progress_desc):
        if self.support_db_access_count :
            self.__inc_db_access_cnt__(inspect.currentframe().f_code.co_name)

        with PostgreSQLMgr.instance().session() as session :
            session.execute(update(TRSummary).where(TRSummary.id == tr_sum_id).values(
                progress = progress_desc)
            )
            session.commit()

    def __inc_db_access_cnt__(self, method_name):
        self.db_access_method_cnt += 1
        if method_name not in self.db_access_req:
            self.db_access_req[method_name] = 0
        self.db_access_req[method_name] += 1

        tgt_mth_db_access_cnt = self.db_access_req[method_name]
        print(f"@@@@ database access total: {self.db_access_method_cnt}, {method_name} - {tgt_mth_db_access_cnt}({tgt_mth_db_access_cnt/self.db_access_method_cnt * 100}%)")
