from abc import ABCMeta, abstractmethod

from bt4.Constants import CandleType


class IQuoteDispacher(metaclass=ABCMeta):
    @abstractmethod
    def initialize(self):
        pass

    @abstractmethod
    def process_quote(self):
        pass

    @abstractmethod
    def process_local_quote(self, markets, simul_start_dt, simul_end_dt, simul_times, simul_tais,
                            simul_data_type=CandleType.MINUTES_1):
        pass