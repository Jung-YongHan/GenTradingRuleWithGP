from bt4.model.storage_mgr import StrategyStorage
from bt4.utils.mylog import init_log
from bt4.utils.stopwatch import StopWatch

log = init_log()

class ProgressMgr:
    def __init__(self, tr_sum_id, mkt_total_row, markets):
        self.tr_sum_id = tr_sum_id

        self.markets = markets
        self.mkt_total_row = mkt_total_row
        self.total_row = self.mkt_total_row * len(self.markets)
        self.progress_percentage = 0

        self.mkt_processed_row = 0
        self.total_processed_row = 0

        self.current_market = None
        self.__PROGRESS_INIT__ = 1
        self.__PROGRESS_SETTLE__ = 2
        self.__PROGRESS_CALC_TAI__ = 100 - (self.__PROGRESS_INIT__ + self.__PROGRESS_SETTLE__)

        pu = round(self.total_row / self.__PROGRESS_CALC_TAI__)
        self.progress_unit = pu if pu != 0 else 1
        self.estimated_remaining_time_sec = int(self.total_row * 0.01)
        self.sw = StopWatch()
        self.sw.start()

    def update_preparation_progress(self, elapsed_time):
        e_remaining_time_msg = self.__build_estimated_time_msg__(self.estimated_remaining_time_sec)
        log.info(f"Progress {self.progress_percentage}% $ 수행시간: {elapsed_time:.2f} $ 예상 남은수행시간 {e_remaining_time_msg}$데이터 로딩 중... ")

        msg = f"{self.progress_percentage}%${elapsed_time:.2f}${e_remaining_time_msg}$데이터 로딩 중..."
        StrategyStorage.instance().update_backtesting_progress(self.tr_sum_id, msg)
        self.progress_percentage = 1


    def update_tai_calculation_progress(self, market, elapsed_time, elapsed_time_from_beginning):
        if self.current_market is None:
            self.current_market = market

        if self.current_market != market:
            self.current_market = market
            self.mkt_processed_row = 0

        self.mkt_processed_row = self.mkt_processed_row + 1
        self.total_processed_row = self.total_processed_row + 1

        if (self.total_processed_row % self.progress_unit == 0) or (self.total_processed_row == self.total_row) :
            self.e_time_of_one = self.sw.stop()
            self.estimated_remaining_time_sec = (100 - self.progress_percentage ) * self.e_time_of_one
            e_remaining_time_msg = self.__build_estimated_time_msg__(self.estimated_remaining_time_sec)
            msg_for_log = f"Progress {self.progress_percentage}% $ 수행시간: {elapsed_time:.2f}초 $ 예상 남은수행시간 {e_remaining_time_msg} $ {market} 변수 전처리 중... {self.mkt_processed_row}/{self.mkt_total_row}"
            log.info(msg_for_log)

            msg_for_db = f"{self.progress_percentage}%${elapsed_time_from_beginning:.2f}초${e_remaining_time_msg}${market} 변수 전처리 중... {self.mkt_processed_row}/{self.mkt_total_row}"
            StrategyStorage.instance().update_backtesting_progress(self.tr_sum_id, msg_for_db)

            self.progress_percentage = self.progress_percentage + 1
            self.sw.start()

    def update_before_settle_progress(self, elapsed_time, elapsed_time_from_beginning):
        self.estimated_remaining_time_sec = (100 - self.progress_percentage) * self.e_time_of_one
        e_remaining_time_msg = self.__build_estimated_time_msg__(self.estimated_remaining_time_sec)
        msg_for_log = f"Progress {self.progress_percentage}% $ 수행시간: {elapsed_time:.2f} $ 예상 남은수행시간 {e_remaining_time_msg} $ 백테스팅 결과 취합 중... "
        log.info(msg_for_log)
        msg_for_db = f"{self.progress_percentage}%${elapsed_time_from_beginning:.2f}${e_remaining_time_msg}$백테스팅 결과 취합 중..."
        StrategyStorage.instance().update_backtesting_progress(self.tr_sum_id,msg_for_db)

        self.progress_percentage = self.progress_percentage + 1

    def update_after_settle_progress(self, elapsed_time, elapsed_time_from_beginning) :
        msg_for_log = f"Progress {self.progress_percentage}% $ 수행시간: {elapsed_time:.2f} $ 백테스팅 결과 취합 완료"
        log.info(msg_for_log)
        msg_for_db = f"{self.progress_percentage}%${elapsed_time_from_beginning:.2f}$0초$백테스팅 결과 취합 완료"
        StrategyStorage.instance().update_backtesting_progress(self.tr_sum_id,msg_for_db)


    def __build_estimated_time_msg__(self, estimated_remaining_time):
        e_remaining_time_msg = ""
        e_hour, e_min, e_sec = convert_hour_min_from_sec(self.estimated_remaining_time_sec)
        if e_hour < 0:
            e_remaining_time_msg = f"0초"
        elif e_hour == 0:
            if e_min == 0:
                e_remaining_time_msg = f"{e_sec:.1f}초"
            else:
                e_remaining_time_msg = f"{e_min}분 {int(e_sec)}초"
        else:
                e_remaining_time_msg = f"{e_hour}시 {e_min}분 {int(e_sec)}초"
        return e_remaining_time_msg


def convert_hour_min_from_sec(total_in_sec):
    second = total_in_sec % 60
    minute = int((total_in_sec // 60) % 60)  # 초를 분으로 환산하여 60으로 나눈 나머지
    hour = int(total_in_sec // 60 // 60)  # 초를 분으로 환산하고, 그 분을 시간으로 환산한 몫
    return hour, minute, second


def build_desc(row, market, order) :
    if order == "BUY" :
        buy_system_key = f"{market}_buy_system"
        desc = ""
        for idx in range(1, 100) :
            if f"{buy_system_key}{idx}" in row :
                # if row[f"{buy_system_key}{idx}"] == True :
                if idx == 1:
                    desc = f"*[{buy_system_key}{idx}] = {row[f'{buy_system_key}{idx}']} :: {row[f'{buy_system_key}{idx}_desc']}"
                else:
                    desc = f"{desc} \n*[{buy_system_key}{idx}] = {row[f'{buy_system_key}{idx}']} :: {row[f'{buy_system_key}{idx}_desc']}"

            else :
                break
        return desc
    elif order == "SELL" :
        sell_system_key = f"{market}_sell_system"
        desc = ""
        for idx in range(1, 100) :
            if f"{sell_system_key}{idx}" in row :
                # if row[f"{sell_system_key}{idx}"] == True :
                if idx == 1:
                    desc = f"*[{sell_system_key}{idx}] = {row[f'{sell_system_key}{idx}']} :: {row[f'{sell_system_key}{idx}_desc']}"
                else:
                    desc = f"{desc} \n*[{sell_system_key}{idx}] = {row[f'{sell_system_key}{idx}']} :: {row[f'{sell_system_key}{idx}_desc']}"
            else :
                break
        return desc
    else :
        print("It should never gonna happen!")
        return ""