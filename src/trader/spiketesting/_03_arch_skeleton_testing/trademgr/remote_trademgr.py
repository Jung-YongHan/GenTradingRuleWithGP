
from spiketesting._03_arch_skeleton_testing.trademgr.itrademgr import ITradeMgr

class RemoteTradeMgr(ITradeMgr):
    def __init__(self):
        pass

    def start_trading(self):
        self.kafka_trade_mgr = KafkaTradeReceiver(self)

    def execute_trade(self, strategy_name, dfs) -> bool:
        print(f'[{self.__class__.__name__}] execute_trade: send {strategy_name} and dfs to server')
        pass


class KafkaTradeReceiver:
    def __init__(self, i_trade_mgr):
        self.receiver = i_trade_mgr

        ## when received
        strategy_name = '...'
        dfs = '...'
        i_trade_mgr.execute_trade(strategy_name, dfs)

