import unittest

from bt4.model.storage_mgr import StrategyStorage
from bt4.utils.container_helper import ContainerHelper


class MyTestCase(unittest.TestCase):

    def setUp(self):
        """테스트 시작되기 전 파일 작성"""
        # self.init_default()
        # self.init_remote()

    def tearDown(self):
        """테스트 종료 후 파일 삭제 """


    # @unittest.skip("Tested")
    def test_execute_backtesting(self):
        target_id = "1"
        target_id = StrategyStorage.instance().get_trading_id_of_desc("ws_day_hdg_vol")
        status = ContainerHelper.instance().run_backtesting(target_id)
        print(status)
        pass



if __name__ == '__main__' :
    unittest.main()
