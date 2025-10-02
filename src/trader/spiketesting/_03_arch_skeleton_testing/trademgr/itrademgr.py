from abc import ABCMeta, abstractmethod


class ITradeMgr(metaclass=ABCMeta):
    def __init__(self):
        pass

    @abstractmethod
    def execute_trade(self, strategy_name, dfs) -> bool:
        pass

