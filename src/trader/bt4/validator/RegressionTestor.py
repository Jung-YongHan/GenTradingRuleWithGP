from datetime import datetime

from bt4.validator.BTComparator import BTComparator
from bt4.validator.BTComparator import BTPersistenceMgr, sort_lists_in_dict
from bt4.utils.mylog import init_log
log = init_log()


class RegressionTestor:

    def __init__(self):
        self.btpm = BTPersistenceMgr.instance()
        self.bt_compartor = BTComparator()

    def test_on_the_fly(self, src_ctx, src_r_file: str,
                        only_for_the_same_cfg: bool=True,
                        show_trading_details: bool=True,
                        store_when_diff: bool=True,
                        bt_version: str='v3',
                        is_base: bool=False):
        bt_entity = src_ctx.ctx_params
        sort_lists_in_dict(bt_entity)
        tmp_dict = bt_entity.copy()
        self.bt_compartor.remove_unwanted_keys(tmp_dict)
        base_result = self.btpm.check_bt_result_by_condition(tmp_dict)

        # report 경로 저장
        idx = src_r_file.find('report')
        bt_entity['trade_dataframe'] = src_r_file[idx:]

        ####################### Test
        # src_ctx.report_storage.results['2xdur'] = 1 # 테스트를 위한 임시 데이터 삽입
        ####################### Test

        if not hasattr(src_ctx.report_storage, "results"):
            return

        bt_entity['summary'] = src_ctx.report_storage.results
        bt_entity['bt_version'] = bt_version
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        bt_entity['test_time'] = now
        bt_entity['recent_test_time'] = now

        ####################### Test
        # print('bt_entity summary', bt_entity['summary'])
        # print('result summary', result['summary'])
        ####################### Test

        sty_name = bt_entity['strategy']
        is_same = False
        if base_result is not None:
            log.info(f'전략: {sty_name} :::::::::::::::: Base와 현재 백테스트 결과의 회귀 테스트를 진행합니다.')
            is_same = self.bt_compartor.compare_on_the_fly(base_result, bt_entity, only_for_the_same_cfg, show_trading_details)

        if base_result is None:
            if is_base:
                log.info(f'전략: {sty_name}을/를 Base로 백테스트 결과를 저장합니다.')
                self.btpm.store_backtest_result(bt_entity, True)
            else:
                log.info(f'전략: {sty_name}을/를 설정에 따라 Base로 저정하지 않습니다.')
        elif is_base:
            log.info(f'전략: {sty_name}이/가 Base로 최신화합니다.')
            self.btpm.update_base(tmp_dict, bt_entity)
        elif base_result['summary'] == bt_entity['summary']:
            log.info(f'전략: {sty_name}이/가 Base 백테스트 결과와 [ 동일 ] 합니다.')
            self.btpm.update_recent_test_time(base_result)
        else:
            log.info(f'전략: {sty_name}이/가 Base 백테스트 결과와 [ 상이 ] 합니다.')
            if store_when_diff:
                log.info(f'전략: {sty_name}을/를 상이한 백테스트 결과로 저장합니다.')
                self.btpm.store_backtest_result(bt_entity, False)
        return is_same

    def test_stgy_in_storage(self, stgy_name, src_idx, tgt_idx, only_for_the_same_cfg=True, show_trading_details=True):
        base = {'strategy': stgy_name, 'index': src_idx, 'search_base': True}
        target = {'strategy': stgy_name, 'index': tgt_idx, 'search_base': False}

        self.bt_compartor.compare(base, target, only_for_the_same_cfg, show_trading_details)

