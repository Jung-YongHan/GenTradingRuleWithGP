from abc import ABCMeta, abstractmethod
from enum import Enum

from spiketesting._03_arch_skeleton_testing.quote.iquote_dispatcher import IQuoteDispacher
from spiketesting._03_arch_skeleton_testing.quote.quote_dispatcher import LocalQuoteJobDistributor, ExchangeQuoteDispatcher, \
    MockQuoteDispatcher
from spiketesting._03_arch_skeleton_testing.trademgr.itrademgr import ITradeMgr
from spiketesting._03_arch_skeleton_testing.trademgr.remote_trademgr import RemoteTradeMgr
from spiketesting._03_arch_skeleton_testing.trademgr.trademgr_impl import LocalTradeMgr, MockTradeMgr


class ExecutionMode(str, Enum):
    Live_Mode = 'Live_Mode'
    BackTesting_Mode = 'BackTesting_Mode'
    MockTest_Mode = 'MockTest_Mode'

class AbstractFactory(metaclass=ABCMeta):
    @classmethod
    def getFactory(cls, exec_mode):
        if exec_mode == ExecutionMode.BackTesting_Mode:
            return BackTestorFactory()
        elif exec_mode == ExecutionMode.Live_Mode:
            return LiveTradingFactory()
        elif exec_mode == ExecutionMode.MockTest_Mode:
            return MockTestFactory()
        else:
            return None

    @abstractmethod
    def getQuoteDispatcher(self) -> IQuoteDispacher:
        pass

    @abstractmethod
    def getTradeMgr(self) -> ITradeMgr:
        pass

class BackTestorFactory(AbstractFactory):

    def __init__(self):
        pass

    def getQuoteDispatcher(self) -> IQuoteDispacher:
        return LocalQuoteJobDistributor()

    def getTradeMgr(self) -> ITradeMgr:
        return LocalTradeMgr()

class LiveTradingFactory(AbstractFactory):

    def __init__(self):
        pass

    def getQuoteDispatcher(self) -> IQuoteDispacher:
        return ExchangeQuoteDispatcher()

    def getTradeMgr(self) -> ITradeMgr:
        return RemoteTradeMgr()

class MockTestFactory(AbstractFactory):

    def __init__(self):
        pass

    def getQuoteDispatcher(self) -> IQuoteDispacher:
        return MockQuoteDispatcher()

    def getTradeMgr(self) -> ITradeMgr:
        return MockTradeMgr()