
from spiketesting._03_arch_skeleton_testing.strategy.istrategy import IStrategy
from spiketesting._03_arch_skeleton_testing.trademgr.trademgr_impl import MockTradeMgr


class AbstractStrategy(IStrategy):
    def __init__(self):
        self.trade_mgr = MockTradeMgr()

    def perform(self, dfs):
        pass