from abc import ABCMeta, abstractmethod


class QuoteListener(metaclass=ABCMeta):

    @abstractmethod
    def quote_received(self, quote):
        pass

class QuotePullRequestListener(metaclass=ABCMeta):
    @abstractmethod
    def do_pull_quote(self, ex_type, time_str) :
        pass