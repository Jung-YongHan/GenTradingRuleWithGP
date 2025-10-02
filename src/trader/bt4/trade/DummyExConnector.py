import json
import os
from abc import abstractmethod
from os.path import dirname, join

from bt4 import GlobalProperties
from bt4.Constants import ExType
from bt4.model.state_mgr import StateStorage
from bt4.trade.ExchangeConnector import AbstractExConnector, FutureBalance, log
from bt4.utils.mylog import init_log
from bt4.utils.strings import split_source_target_markets

log = init_log()

class DummyDefaultExConnector(AbstractExConnector):
    def __init__(self):
        super(DummyDefaultExConnector, self).__init__()
        self.dummy_ex_bal_state_file = '__dummy_ex_balance_states.json'

    def fetch_balances(self):
        self.read_balance_states()

    def read_balance_states(self) :
        if GlobalProperties.is_live_trading :
            root_dir = dirname(__file__)
            self.storage_path = join(root_dir, self.dummy_ex_bal_state_file)
            if os.path.exists(self.storage_path) :
                f = open(self.storage_path, mode = 'r')
                self.market_balances = json.load(f)
                f.close()
            else:
                log.info(f"Dummy Balance States does not exist at '{self.storage_path}'. It will be created after the first trading...")

    def write_balance_states(self) :
        if GlobalProperties.is_live_trading :
            root_dir = dirname(__file__)
            self.storage_path = join(root_dir, self.dummy_ex_bal_state_file)
            if not os.path.exists(self.storage_path) :
                log.info(f"Dummy Balance States has been created at '{self.storage_path}'. It will be loaded when the strategy starts up later.")

            f = open(self.storage_path, mode = 'w')
            json.dump(self.market_balances, f)
            f.close()
            log.info(f"Dummy Balance States of '{self.storage_path}' has been updated.")



    @abstractmethod
    def get_base_currency(self):
        pass

    def set_params(self, cash_balance, fee_slippage):
        self.cash_balance = cash_balance
        base_currency = self.get_base_currency()
        self.market_balances = {base_currency: cash_balance}
        self.fee_calibration = 0.000000250125062606788
        self.fee_ratio = fee_slippage + self.fee_calibration

    def get_balance(self, currency):
        if currency in self.market_balances:
            return self.market_balances[currency]
        else:
            self.market_balances[currency] = 0
            return 0

    def get_fee_ratio(self):
        return self.fee_ratio

    @abstractmethod
    def get_post_market(self):
        pass


    @abstractmethod
    def get_post_amount(self):
        pass

    @abstractmethod
    def get_minimum_base_amount_for_rebalance(self):
        pass

    ## KRW-BTC, 5000, 0.001, return fee
    def enter_long(self, market, price, volume):
        src_cur, tgt_cur = split_source_target_markets(market)
        src_bal = self.market_balances[src_cur]

        should_be_payed = price * volume * (1+self.fee_ratio)

        if tgt_cur not in self.market_balances:
            self.market_balances[tgt_cur] = 0

        tgt_bal = self.market_balances[tgt_cur]
        log.info(f'DummyEx-BUY POS_1: ({market=}, {price=}, {volume=:.2f}, {src_cur=}, '
                 f'{src_bal=}, {tgt_cur=},{tgt_bal=}, {should_be_payed=}) ')

        if src_bal < should_be_payed:
            return False, -1, -1, -1

        fee = price * volume * self.fee_ratio
        self.market_balances[src_cur] = self.market_balances[src_cur] - should_be_payed
        self.market_balances[tgt_cur] += volume

        src_bal = self.market_balances[src_cur]
        tgt_bal = self.market_balances[tgt_cur]
        log.info(f'DummyEx-BUY POS_2: ({market=}, {price=}, {volume=:.2f}, {src_cur=}, '
                 f'{src_bal=}), {tgt_cur=}),{tgt_bal=}, {should_be_payed=}) ')
        self.write_balance_states()
        return True, price, volume, fee

    def exit_long(self, market, volume, price=0):
        src_cur, tgt_cur = split_source_target_markets(market)
        src_bal = self.market_balances[src_cur]
        tgt_bal = self.market_balances[tgt_cur]
        should_be_payed = volume * (1 + self.fee_ratio)
        log.info(f'DummyEx-SELL POS1: ({market=}, {volume=}, {src_cur=}, '
                 f'{src_bal=}, {tgt_cur=},{tgt_bal=}, {should_be_payed=}) ')

        if tgt_bal < should_be_payed:
            return False, -1, -1, -1

        if price != 0:
            fee = volume * price * self.fee_ratio
            source_add = volume * price - fee
            self.market_balances[src_cur] = src_bal + source_add
            self.market_balances[tgt_cur] = self.market_balances[tgt_cur] - should_be_payed

        else:
            fee = 0

        src_bal = self.market_balances[src_cur]
        tgt_bal = self.market_balances[tgt_cur]
        log.info(f'DummyEx-SELL POS2: ({market=}, {volume=}, {src_cur=}, '
                 f'{src_bal=}, {tgt_cur=},{tgt_bal=}, {should_be_payed=}) ')

        self.write_balance_states()
        return True, price, volume, fee

class DummyUpbitExConnector(DummyDefaultExConnector):
    def __init__(self):
        super(DummyUpbitExConnector, self).__init__()

    def fetch_balances(self) :
        if GlobalProperties.is_live_trading :
            usr_uuid = GlobalProperties.usr_uuid
            tid = GlobalProperties.tid
            base_cur = self.get_base_currency()
            bal_states, _ = StateStorage.instance().get_balance_states(usr_uuid, ExType.upbit, tid, base_cur)

            for bs in bal_states:
                # if bs == base_cur and base_cur not in self.market_balances:
                #     self.market_balances[base_cur] = bal_states[bs]
                if bs == base_cur:
                    self.market_balances[base_cur] = bal_states[bs]

                if bs.endswith("_price"):
                    market = bs.replace("_price", "")
                    self.market_balances[market] = bal_states[market]

    def write_balance_states(self):
        pass


    def get_base_currency(self):
        return 'KRW'

    def get_minimum_base_amount_for_rebalance(self):
        return 50000

    def get_post_market(self) :
        return "KRW-BTC"

    def get_post_amount(self):
        return 5100


class DummyBithumbExConnector(DummyDefaultExConnector):
    def __init__(self):
        super(DummyBithumbExConnector, self).__init__()

    def fetch_balances(self) :
        if GlobalProperties.is_live_trading :
            usr_uuid = GlobalProperties.usr_uuid
            tid = GlobalProperties.tid
            base_cur = self.get_base_currency()
            bal_states, _ = StateStorage.instance().get_balance_states(usr_uuid, ExType.bithumb, tid, base_cur)

            for bs in bal_states:
                # if bs == base_cur and base_cur not in self.market_balances:
                #     self.market_balances[base_cur] = bal_states[bs]
                if bs == base_cur:
                    self.market_balances[base_cur] = bal_states[bs]

                if bs.endswith("_price"):
                    market = bs.replace("_price", "")
                    self.market_balances[market] = bal_states[market]

    def write_balance_states(self):
        pass


    def get_base_currency(self):
        return 'KRW'

    def get_minimum_base_amount_for_rebalance(self):
        return 50000

    def get_post_market(self) :
        return "KRW-ETH"

    def get_post_amount(self):
        return 5100



class DummyBinanceExConnector(DummyUpbitExConnector):
    def __init__(self):
        super(DummyBinanceExConnector, self).__init__()

    def get_base_currency(self):
        return 'USDT'

    def get_minimum_base_amount_for_rebalance(self):
        return 10

    def get_post_market(self) :
        return "USDT-BTC"

    def get_post_amount(self):
        return 11   #USDT



class DummyBinanceUSDMExConnector(AbstractExConnector):
    def __init__(self):
        super(DummyBinanceUSDMExConnector, self).__init__()

    # def set_params(self, future_balance, fee_ratio):
    #     self.future_balance = future_balance
    #     self.market_balances = {
    #         'USDT': FutureBalance(
    #             balance=future_balance, long=0.0, short=0.0
    #         )
    #     }
    #     self.fee_calibration = 0.000000250125062606788
    #     self.fee_ratio = fee_ratio + self.fee_calibration

    def set_params(self, balance, fee_slippage) :
        currency = self.get_base_currency()

        self.future_balances = {
            currency : FutureBalance(
                balance = balance, long = 0.0, short = 0.0
            )
        }
        self.fee_calibration = 0.000000250125062606788
        self.fee_ratio = fee_slippage + self.fee_calibration

    def get_base_currency(self):
        return 'USDT'

    def fetch_balances(self):
        pass

    def get_balance(self, currency):
        ## Temporally, it returns long position.
        if currency in self.future_balances:
            if self.future_balances[currency].balance == 0:
                return self.future_balances[currency].long
            else:
                return self.future_balances[currency].balance
        else:
            self.future_balances[currency] = FutureBalance(long=0.0, short=0.0, balance=0.0)
            return 0

    def get_fee_ratio(self):
        return self.fee_ratio

    def get_minimum_base_amount_for_rebalance(self):
        return 10

    def get_post_market(self) :
        return "BTC/USDT"

    def get_post_amount(self):
        return 11   #USDT

    def enter_long(self, market, price, volume):
        src_cur, tgt_cur = split_source_target_markets(market)

        src_bal = self.future_balances[src_cur].balance

        if tgt_cur not in self.future_balances:
            self.future_balances[tgt_cur] = FutureBalance(short=0.0, long=0.0, balance=0.0)
        tgt_long = self.future_balances[tgt_cur].long
        tgt_short = self.future_balances[tgt_cur].short

        should_be_payed = price * volume * (1 + self.fee_ratio)

        log.info(f'DummyEx-BUY POS_1: ({market=}, {price=}, {volume=:.2f}, {src_cur=}, '
                 f'{src_bal=}, {tgt_long=}, {tgt_short=}, {should_be_payed=}) ')

        if src_bal < should_be_payed:
            return False, -1, -1, -1

        fee = volume * self.fee_ratio
        self.future_balances[src_cur].balance -= should_be_payed
        self.future_balances[tgt_cur].long += volume

        src_bal = self.future_balances[src_cur].balance
        tgt_long = self.future_balances[tgt_cur].long
        tgt_short = self.future_balances[tgt_cur].short

        log.info(f'DummyEx-BUY POS_2: ({market=}, {price=}, {volume=:.2f}, {src_cur=}, '
                 f'{src_bal=}, {tgt_cur=}, {tgt_long=}, {tgt_short=}, {should_be_payed=}) ')
        super(DummyBinanceUSDMExConnector, self).__write_market_bal_into_file()
        return True, price, volume, fee

    def exit_long(self, market, volume, price=0):
        src_cur, tgt_cur = split_source_target_markets(market)

        src_bal = self.future_balances[src_cur].balance
        tgt_long = self.future_balances[tgt_cur].long
        tgt_short = self.future_balances[tgt_cur].short

        should_be_payed = volume * (1 + self.fee_ratio)

        log.info(f'DummyEx-SELL POS_1: ({market=}, {volume=}, {src_cur=}, '
                 f'{src_bal=}, {tgt_cur=}, {tgt_long=}, {tgt_short=}, {should_be_payed=}) ')

        if tgt_long  < should_be_payed:
            return False, -1, -1, -1

        fee = price * volume * self.fee_ratio
        self.future_balances[src_cur].balance += volume * price - fee
        self.future_balances[tgt_cur].long -= should_be_payed

        src_bal = self.future_balances[src_cur].balance
        tgt_long = self.future_balances[tgt_cur].long
        tgt_short = self.future_balances[tgt_cur].short

        log.info(f'DummyEx-SELL POS_2: ({market=}, {volume=}, {src_cur=}, '
                 f'{src_bal=}, {tgt_cur=},{tgt_long=}, {tgt_short=}, {should_be_payed=}) ')
        super(DummyBinanceUSDMExConnector, self).__write_market_bal_into_file()
        return True, price, volume, fee

    def enter_short(self, market, price, volume):
        src_cur, tgt_cur = split_source_target_markets(market)
        src_bal = self.future_balances[src_cur].balance

        if tgt_cur not in self.future_balances:
            self.future_balances[tgt_cur] = FutureBalance(short=0.0, long=0.0, balance=0.0)
        tgt_long = self.future_balances[tgt_cur].long
        tgt_short = self.future_balances[tgt_cur].short

        should_be_payed = price * volume * (1 + self.fee_ratio)

        log.info(f'DummyEx-SELL POS_1: ({market=}, {price=}, {volume=:.2f}, {src_cur=}, '
                 f'{src_bal=}, {tgt_long=}, {tgt_short=}, {should_be_payed=}) ')

        if src_bal < should_be_payed:
            return False, -1, -1, -1

        fee = price * volume * self.fee_ratio
        self.future_balances[src_cur].balance -= should_be_payed
        self.future_balances[tgt_cur].short += volume

        src_bal = self.future_balances[src_cur].balance
        tgt_long = self.future_balances[tgt_cur].long
        tgt_short = self.future_balances[tgt_cur].short

        log.info(f'DummyEx-SELL POS_2: ({market=}, {price=}, {volume=:.2f}, {src_cur=}, '
                 f'{src_bal=}, {tgt_cur=}, {tgt_long=}, {tgt_short=}, {should_be_payed=}) ')

        super(DummyBinanceUSDMExConnector, self).__write_market_bal_into_file()
        return True, price, volume, fee

    def exit_short(self, market, volume, price=0):
        src_cur, tgt_cur = split_source_target_markets(market)

        src_bal = self.market_balances[src_cur].balance
        tgt_long = self.market_balances[tgt_cur].long
        tgt_short = self.market_balances[tgt_cur].short

        should_be_payed = volume * (1 + self.fee_ratio)

        log.info(f'DummyEx-BUY POS_1: ({market=}, {volume=}, {src_cur=}, '
                 f'{src_bal=}, {tgt_cur=}, {tgt_long=}, {tgt_short=}, {should_be_payed=}) ')

        if tgt_short < should_be_payed:
            return False, -1, -1, -1

        if price != 0:
            fee = volume * price * self.fee_ratio
            self.market_balances[src_cur].balance += volume * price - fee
            self.market_balances[tgt_cur].short -= should_be_payed
        else:
            fee = 0

        src_bal = self.market_balances[src_cur].balance
        tgt_long = self.market_balances[tgt_cur].long
        tgt_short = self.market_balances[tgt_cur].short

        log.info(f'DummyEx-BUY POS_2: ({market=}, {volume=}, {src_cur=}, '
                 f'{src_bal=}, {tgt_cur=},{tgt_long=}, {tgt_short=}, {should_be_payed=}) ')

        super(DummyBinanceUSDMExConnector, self).__write_market_bal_into_file()
        return True, price, volume, fee