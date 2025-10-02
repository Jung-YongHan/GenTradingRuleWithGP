from abc import ABCMeta, abstractmethod

import pandas as pd

class IStrategy(metaclass=ABCMeta):
    def __init__(self):
        pass

    @abstractmethod
    def perform(self, dfs) -> None:
        pass