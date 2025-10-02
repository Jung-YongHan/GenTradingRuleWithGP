import os
from datetime import datetime
from os.path import dirname, join

import pandas as pd

from bt4.Constants import Operation_Type
from bt4.model.trade_object import Trade
from bt4.model.storage_mgr import StrategyStorage
from bt4.utils.mongodb import MongoDBHandler
from bt4.utils.mylog import init_log
from bt4.utils.python_utils import dt2str_for_filename
import bt4.GlobalProperties as global_prop

log = init_log()


class AbstractReportStorage:
    def __init__(self):
        pass

    def restore(self):
        pass

    def store(self, trade_result):
        pass

    def update_intermediate(self, result_df):
        pass

    def close(self):
        pass

    def set_key_results(self, results):
        self.results = results

    def get_key_results(self):
        return self.results

    def is_visualize_support(self):
        return False


class FileReportStorage(AbstractReportStorage):
    def __int__(self):
        pass

    def set_params(self, file_name, visualize_support):
        super(FileReportStorage, self).__init__()

        nowDatetime = dt2str_for_filename(datetime.now())
        root_dir = dirname(dirname(dirname(__file__)))  ## parent of parent of directory of simulator.py
        file_name = join(root_dir, f"report{os.sep}{nowDatetime}_{file_name}.txt")

        self.file = open(file_name, "w", encoding = 'UTF-8')
        self.visualize_support = visualize_support

    def store(self, trade_result) -> None:
        log.debug(trade_result.__str__())
        self.file.write(trade_result.__str__() + "\n")

    def is_visualize_support(self):
        return self.visualize_support

    def close(self, result_df):
        self.file.close()


class MongoDBReportStorage(AbstractReportStorage):
    def __init__(self):
        super(MongoDBReportStorage, self).__init__()
        self.collection_name = "TRADE_LOG"
        self.mongo = MongoDBHandler().instance()

    def store(self, trade_result) -> None:
        print(trade_result.__str__())
        now = datetime.now()
        time = now.strftime("%d/%m/%Y %H:%M:%S")
        data = {"time": time, "msg": trade_result.__str__()}
        self.mongo.insert_item_one(self.collection_name, data)

    def close(self, result_df):
        self.mongo.close()

class PostgreSQLReportStorage(AbstractReportStorage):
    def __init__(self):
        super(PostgreSQLReportStorage, self).__init__()


    def set_params(self, tid, bt_start, bt_end, op_type, markets):
        super(PostgreSQLReportStorage, self).__init__()
        self.tid = tid
        self.tr_sum_id = None
        if op_type == Operation_Type.FORWARD_TESTING or op_type == Operation_Type.LIVE_TRADING:
            self.tr_sum_id = StrategyStorage.instance().get_tr_summary_id(tid, op_type)

        if self.tr_sum_id is None:
            self.tr_sum_id = StrategyStorage.instance().add_initial_tr_summary(tid, bt_start, bt_end, op_type, markets)
        else:
            log.info(f"trade summary({self.tr_sum_id}) is recovered.")

        if self.tr_sum_id is None:
            log.error(f"Storing Initial TRSummary ({tid}, {bt_start},{bt_end}, {op_type}, {markets}) Error!")
            return

        ## Thread Version
        # self.queue = queue.Queue()
        # self.event = None

    def restore(self) :
        tus = StrategyStorage.instance().get_trade_units(self.tid, self.tr_sum_id)
        trade_list = []
        for tu in tus:
            tu_obj = Trade.from_trade_unit(tu)
            trade_list.append(tu_obj)
            log.info(f"recover trade unit: {tu_obj}")
        return trade_list


    def store(self, trade_result) -> None:
        ## Thread Version
        # self.queue.put(trade_result)
        #
        # if self.event is None:
        #     self.event = threading.Event()
        #     threading.Thread(target = self.__consumer__, daemon = True).start()

        ## Non Thread Version
        if global_prop.is_live_trading:     ## Store Trade Unit only for Forward Testing and Live Trading
            sa_obj = trade_result.to_trade_unit(self.tr_sum_id, self.tid)
            StrategyStorage.instance().add_trade_unit(sa_obj)

    def __consumer__(self) :
        while not self.event.is_set():
            trade_result = self.queue.get()
            if global_prop.is_live_trading :  ## Store Trade Unit only for Forward Testing and Live Trading
                sa_obj = trade_result.to_trade_unit(self.tr_sum_id, self.tid)
                StrategyStorage.instance().add_trade_unit(sa_obj)
            self.queue.task_done()

    def update_intermediate(self, result_df):
        log.info(f"update_intermediate result: {self.results}")
        if self.results is not None and len(self.results) >= 26 :
            StrategyStorage.instance().update_trade_summary(self.tr_sum_id, self.results, result_df)
        else :
            log.error(f"Something is missing in {self.results}")

    def close(self, result_df):
        ## Thread Version
        # Finish Thread
        # if self.event is not None:
        #     self.event.set()

        if hasattr(self, "results"):
            log.info(f"Result: {self.results}")
            if self.results is not None and len(self.results) >= 26:
                StrategyStorage.instance().update_trade_summary(self.tr_sum_id, self.results, result_df)
                StrategyStorage.instance().delete_trade_unit(self.tr_sum_id)
            else:
                log.error(f"Somethig is missing in {self.results}")

    def update_ga_params(self, stgy_json, ga_params):
        StrategyStorage.instance().update_ga_params(self.tr_sum_id, stgy_json, ga_params)



class Report:
    def __init__(self, result_storage: AbstractReportStorage):
        self.trading_list = []
        self.result_storage = result_storage
        self.trading_list = self.result_storage.restore()

    def append(self, trade) -> None:
        self.trading_list.append(trade)
        self.result_storage.store(trade)

    def close(self):
        self.result_storage.close(self.toDataFrame())

    def get_trading_list(self):
        return self.trading_list

    def set_trading_list(self, trading_list):
        self.trading_list = trading_list

    def toDataFrame(self):
        data = []
        for trade in self.trading_list:
            data.append(trade.toList())
        df = pd.DataFrame(data, columns=Trade.columns())
        # df.sort_values(by="date", ascending=True, inplace=True)
        # df.set_index(keys=['date'], drop=False, inplace=True)
        # df.index = pd.to_datetime(df.index)
        # df.sort_index(inplace=True, ascending=True)
        return df
