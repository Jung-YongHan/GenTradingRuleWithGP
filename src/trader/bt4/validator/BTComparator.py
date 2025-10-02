import argparse
import sys

from bt4.Constants import R
from bt4.utils.python_utils import now_str, load_class_from_module
from difflib import unified_diff
from bt4.utils.mongodb import MongoDBHandler
from bt4.utils.python_utils import SingletonInstance
from bt4.utils.mylog import init_log
from os.path import dirname

log = init_log()

r = R()
def sort_lists_in_dict(datas, count=0):
    # todo list 안에 dict나 list가 들어간 경우 정렬 불가 => 해당 경우가 발생한다면 수정
    if type(datas) == list:
        datas.sort()
        # print(f'list type data = {datas}')
        return datas, count

    elif type(datas) == dict:
        for key in datas:
            if key == r.STGY.PARAMS:
                continue
            if type(datas[key]) == list or type(datas[key]) == dict:
                count += 1
                datas[key], count = sort_lists_in_dict(datas[key], count)
                # print(key, ': ', f'dict type data = {datas[key]}')
        if count > 0:
            count -= 1
            return datas, count
    else:
        return

def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(nargs='?', help='start_mode: simulator or real_trading)', dest='start_mode')
    parser.add_argument('-account', nargs='?', help='an alias name of account only for real_trading', default=None, dest='account')
    parser.add_argument('-conf', nargs='?', help='configuration module name (.py)', dest='config_module')
    return parser.parse_args().start_mode, parser.parse_args().account, parser.parse_args().config_module


class BTPersistenceMgr(SingletonInstance):

    def __init__(self):
        self.db_name = 'backtest'
        self.col_backtest_results = 'backtest_results'
        self.col_backtest_results_diff = 'backtest_results_diff'

        self.mongo = MongoDBHandler.instance(self.db_name)
        self.mongo.create_collection(self.col_backtest_results)
        self.mongo.create_collection(self.col_backtest_results_diff)

    def get_bt_col_name(self, search_base: bool = True) -> str:
        if search_base:
            return self.col_backtest_results
        else:
            return self.col_backtest_results_diff

    def search_bt_result_by_condition(self, condition: dict, search_base: bool = True):
        collection_name = self.get_bt_col_name(search_base)

        balance_states = []
        cursor = self.mongo.find_item(collection_name, condition)
        for data in cursor:
            balance_states.append(data)
        cursor.close()
        return balance_states

    def update_recent_test_time(self, entity: dict) -> None:
        newvalues = {"$set": {"recent_test_time": now_str()}}
        self.mongo.update_item_one(self.col_backtest_results, entity, newvalues)

    def update_base(self, entity: dict, new_entity: dict) -> None:
        newvalues = {"$set": new_entity}
        self.mongo.update_item_one(self.col_backtest_results, entity, newvalues)

    def check_bt_result_by_condition(self, condition: dict) -> None:
        return self.mongo.find_item_one(self.col_backtest_results, condition)

    def store_backtest_result(self, result_entity, search_base):
        collection_name = self.get_bt_col_name(search_base)

        count = self.mongo.count_documents(collection_name, {'strategy': result_entity['strategy']})
        result_entity['index'] = count

        obj_id = self.mongo.insert_item_one(collection_name, result_entity)
        if obj_id is not None:
            log.info(f'[ 저장 성공 ] 전략: {result_entity["strategy"]}, Index: {count}로 정상적으로 저장되었습니다.')
        else:
            log.warning(f'[ 저장 실패 ] 전략: {result_entity["strategy"]}, Index: {count}의 저장을 실패했습니다.')

    def get_all_backtest_result(self, strategy_name: str, search_base: bool):
        strategy_dict = {}
        collection_name = self.get_bt_col_name(search_base)

        if strategy_name == 'all':
            condition = {}
            print(f'모든 전략의 백테스트 결과 데이터를 불러옵니다. 출처: {collection_name}')
        else:
            print('Strategy :::::::::::', strategy_name)
            condition = {'strategy': strategy_name}
            print(f'{strategy_name}의 백테스트 결과 데이터를 불러옵니다. 출처: {collection_name}')

        balance_states = []
        cursor = self.mongo.find_item(collection_name, condition)
        for data in cursor:
            balance_states.append(data)
        cursor.close()

        if strategy_name == 'all':
            strategy_set = set()
            for idx, val in enumerate(balance_states):
                strategy_set.add(val['strategy'])

            for strategy in strategy_set:
                tmp_strategy_results = []
                cursor = self.mongo.find_item(collection_name, {'strategy': strategy})
                for data in cursor:
                    tmp_strategy_results.append(data)
                cursor.close()
                strategy_dict[strategy] = tmp_strategy_results

        else:
            strategy_dict[strategy_name] = balance_states
        return strategy_dict

    def get_backtest_results(self, condition_name: str, condition_val: dict) -> list: # 위 메서드와 동일하기 때문에 통합 가능
        condition = {condition_name: condition_val}

        balance_states = []
        cursor = self.mongo.find_item(self.col_backtest_results, condition)
        for data in cursor:
            balance_states.append(data['index'])
        cursor.close()
        return balance_states

    def get_results_comparing(self, base: dict, target: dict) -> (dict, dict):

        base_collection_name = self.get_bt_col_name(base['search_base'])
        target_collection_name = self.get_bt_col_name(target['search_base'])

        del base['search_base']
        del target['search_base']

        base_result = self.mongo.find_item_one(base_collection_name, base)
        target_result = self.mongo.find_item_one(target_collection_name, target)
        return base_result, target_result


class BTComparator:
    def __init__(self):
        self.btpm = BTPersistenceMgr.instance()
        self.config_v2_keys = 'bt_start_date bt_end_date market data_type_DAY_HOUR_MINUTE bt_ta_indicators am_type am_vol_target_volatility_ratio am_vol_volatility_tai am_vol_timeframes strategy bt_time ex_dummy_initial_ratio'.split()
        self.except_keys = 'summary trade_dataframe index test_time recent_test_time bt_cdl_type_needed rs_visualize operation params'.split()

    def __check_txt_diff(self, base_file: str, target_file: str, subject_name: str) -> bool:
        is_diff = False
        root_dir = dirname(dirname(dirname(__file__)))  ## parent of parent of directory of simulator.py
        target_file = f'{root_dir}/{target_file}'
        base_file = f'{root_dir}/{base_file}'

        with open(base_file) as base_tmp:
            with open(target_file) as target_tmp:
                diff = unified_diff(base_tmp.readlines(), target_tmp.readlines(), fromfile='base', tofile='target',  n=0)
                for line in diff:
                    print(line)
                    is_diff = True
                if not is_diff:
                    print(subject_name, '::::::::::::: 결과 CSV 파일 간 차이가 없습니다. :::::::::::::')
        return is_diff

    def compare(self, base: dict, target: dict, only_for_the_same_cfg: bool = False, show_trading_details: bool = True) -> bool:
        if self.validate_data(base, target):
            log.error('[ 실패 ] 잘못된 입력 값입니다. strategy_name에는 문자열을 base과 target에는 int를 넣어주세요')
            return False

        base_result, target_result = self.btpm.get_results_comparing(base, target)

        if not base_result:
            log.error('[ 실패 ] 지정하신 base 데이터가 없습니다. 다른 전략 이름 또는 인덱스를 지정해주세요')
            return False
        else:
            log.info(f'[ 성공 ] base 결과를 정상적으로 읽었습니다.')

        if not target_result:
            log.error('[ 실패 ] 지정하신 target 데이터가 없습니다. 다른 전략 이름 또는 인덱스를 지정해주세요')
            return False
        else:
            log.info(f'[ 성공 ] target 결과를 정상적으로 읽었습니다.')

        return self.__compare_detail(base_result, target_result, only_for_the_same_cfg, show_trading_details)

    def compare_on_the_fly(self, base_result: dict, target_result: dict, only_for_the_same_cfg: bool = False, show_trading_details: bool = True) -> bool:
        return self.__compare_detail(base_result, target_result, only_for_the_same_cfg, show_trading_details)

    def __compare_dict_by_key(self, x: dict, y: dict, subject_name: str) -> bool:
        num_key = 0
        num_diff = 0

        x_keys = x.keys()
        y_keys = y.keys()

        is_same_dict = True
        all_keys = set().union(x_keys, y_keys)
        except_key_list = set(self.except_keys)
        key_union = list(all_keys.difference(except_key_list))
        key_union.sort()

        for key in key_union:
            if key not in x:
                x[key] = 'empty'
                is_same_dict = False

            if key not in y:
                y[key] = 'empty'
                is_same_dict = False

            x_val = x[key]
            y_val = y[key]

            if type(x_val) == tuple:
                x_val = list(x_val)
            if type(y_val) == tuple:
                y_val = list(y_val)

            if type(x_val) == list:
                x_val.sort()
            if type(y_val) == list:
                y_val.sort()

            if x_val == y_val:
                print(subject_name, num_key, 'Ok ', key, x[key])
            else:
                print(subject_name, num_key, 'Not', key)
                print(' '*len(subject_name), '|---- base   ', x[key])
                print(' '*len(subject_name), '|---- target ', y[key])
                is_same_dict = False
                num_diff += 1
            num_key += 1

        print(subject_name, '|', '-' * 100)
        print(subject_name, '|', '[ 동일 ]' if num_diff == 0 else '[ 상이 ]', f'   차이: {num_diff}개, 비교: {num_key + 1}개')
        print(subject_name, '|', '-' * 100, '\n\n')
        return is_same_dict

    def validate_data(self, base: dict, target: dict) -> bool:
        if type(base) is not dict and type(target) is not dict:
            return True
        if "search_base" in base and "search_base" in target:
            print(f'base 데이터 출처: {self.btpm.get_bt_col_name(base["search_base"])}', '----', f'target 데이터 출처: {self.btpm.get_bt_col_name(target["search_base"])}')
        elif "search_base" in base and "search_base" not in target:
            print(f'base 데이터 출처: {self.btpm.get_bt_col_name(base["search_base"])}', '----', f'target 데이터 출처: 현재 실행한 백테스트 결과')

        for key in base:
            log.info(f'[ base 정보 ] - {key}: {base[key]}')
        for key in target:
            log.info(f'[ target 정보 ] - {key}: {target[key]}')

        return False

    def search_list_by_config(self, config: dict) -> list:
        strategy_list = []
        bt_result_list = self.btpm.get_backtest_results('config', config)
        for result in bt_result_list:
            print(result)
        return strategy_list

    def search_same_stgy_name_cfg(self, strategy_name: str, search_base) -> None:
        backtest_results = self.btpm.get_all_backtest_result(strategy_name, search_base)
        for idx, key in enumerate(backtest_results):
            print('\nStrategy ' f'[{idx}]', ':::::::::::',  key)
            self.__show_bt_results(backtest_results[key])

    def search_same_cfg(self, args=None, search_base=True):
        from bt4.Constants import R
        from bt3_config.bt_common_conf import BtCommonConfig

        start_mode, account, config_module = get_arguments()
        r = R()
        parameters = {}

        config = load_class_from_module(config_module, 'Config')
        config.load_params(r, parameters)

        common_config = BtCommonConfig()
        common_config.load_params(r, parameters)
        sort_lists_in_dict(parameters)

        self.remove_unwanted_keys(parameters)

        print('Strategy     :::::::::::', parameters['strategy'], f"출처: {self.btpm.get_bt_col_name(search_base)}")
        backtest_results = self.btpm.search_bt_result_by_condition(parameters, search_base)
        self.__show_bt_results(backtest_results)

    def __show_bt_results(self, backtest_results):
        if backtest_results is None:
            log.info('검색 결과 없음')
            return

        print('*', 'test_date', ' ' * (len(now_str()) - len('test_date')-1), 'recent_test_date', ' ' * (len(now_str()) - len('recent_test_date')-1), 'index', 'config')
        for idx, val in enumerate(backtest_results):
            default_start = '2018-10-01T08:59:00'
            default_end = '2022-11-24T08:59:00'
            markets = None
            ex_dummy_fee_ratio = None
            am_vol_target_volatility_ratio = None
            bt_ta_indicators = None

            if 'bt_start_date' in val:
                default_start = val["bt_start_date"]
            if 'bt_end_date' in val:
                default_end = val["bt_end_date"]
            if 'market' in val:
                markets = val["market"]
            if 'ex_dummy_fee_ratio' in val:
                ex_dummy_fee_ratio = val["ex_dummy_fee_ratio"]
            if 'am_vol_target_volatility_ratio' in val:
                am_vol_target_volatility_ratio = val["am_vol_target_volatility_ratio"]
            if 'bt_ta_indicators' in val:
                bt_ta_indicators = val["bt_ta_indicators"]

            print(idx, val['test_time'], val['recent_test_time'], str(val['index']).rjust(5),
                  f'period: {default_start}~{default_end},',
                  f'market: {markets},',
                  f'slippage: {ex_dummy_fee_ratio},',
                  f'target_volatility_ratio: {am_vol_target_volatility_ratio}',
                  f'tais: {bt_ta_indicators},',)

    def __compare_detail(self, base_result, target_result, only_for_the_same_cfg, show_trading_details) -> bool:
        subject_name = 'config'
        print(subject_name, '=' * 100)

        is_same_dict = self.__compare_dict_by_key(base_result, target_result, subject_name)
        if only_for_the_same_cfg and not is_same_dict:
            print(f'[ 실패 ] -------- 백테스트 환경 설정이 다릅니다. 회귀 테스트를 진행할 수 없습니다.')
            return is_same_dict

        subject_name = 'summary'
        print(subject_name, '=' * 100)
        is_same_dict = self.__compare_dict_by_key(base_result[subject_name], target_result[subject_name], subject_name)

        subject_name = 'trade_dataframe'
        if show_trading_details:
            print(subject_name, '=' * 100)
            self.__check_txt_diff(base_result[subject_name], target_result[subject_name], subject_name)

        return is_same_dict

    def remove_unwanted_keys(self, parameters):
        unwanted = set(parameters) - set(self.config_v2_keys)
        for unwanted_key in unwanted: del parameters[unwanted_key]


if __name__ == '__main__':
    br_compartor = BTComparator()

    # 전략 환경 파일을 입력 받아 동작하도록
    sys.argv = ['BullTraderMain', 'simulator', '-conf', 'bulltrader_conf.sws_day_hdg_vol']
    search_base = False
    br_compartor.search_same_cfg(sys.argv, search_base)
    print()

    # 전략별 조회 - all or strategy_name
    br_compartor.search_same_stgy_name_cfg('all', search_base)  # 성능 비교를 위한 검색
    print()

    base = {'strategy': 'SuperWinningSession_Hedge', 'index': 0, 'search_base': True}
    target = {'strategy': 'SuperWinningSession_Hedge', 'index': 0, 'search_base': False}
    # target = {'strategy': 'WinningSession_Day', 'index': 0, 'search_base': False}
    only_for_the_same_cfg = False
    show_trading_details = True
    br_compartor.compare(base, target, only_for_the_same_cfg, show_trading_details)
