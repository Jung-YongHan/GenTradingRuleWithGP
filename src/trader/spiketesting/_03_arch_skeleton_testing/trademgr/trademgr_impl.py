from spiketesting._03_arch_skeleton_testing.trademgr.itrademgr import ITradeMgr


class MockTradeMgr(ITradeMgr):

    def __init__(self):
        pass

    def execute_trade(self, strategy_name, dfs) -> bool:
        print(f'[{self.__class__.__name__}] execute_trade: {strategy_name}')
        return True



class LocalTradeMgr(ITradeMgr):
    def __init__(self):
        pass

    def execute_trade(self, strategy_name, dfs) -> bool:
        print(f'[{self.__class__.__name__}] execute_trade: {strategy_name}')
        pass

class RemoteTradeMgrProxy(ITradeMgr):
    def __init__(self):
        pass

    def execute_trade(self, strategy_name, dfs) -> bool:
        print(f'[{self.__class__.__name__}] execute_trade: send {strategy_name} and dfs to kafka server')
        pass


