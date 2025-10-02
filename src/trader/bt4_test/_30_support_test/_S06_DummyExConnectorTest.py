import unittest
from pprint import pprint

import ccxt
from ccxt.base.errors import ExchangeError

from bt4.Constants import ExType
from bt4.trade.DummyExConnector import DummyBinanceUSDMExConnector, DummyBinanceExConnector
from bt4_test._30_support_test._S03_ExchangeConnectorTest import fetch_current_market_price

api_key = "NjbQqYaSVwWSG0ZPfzKC5RwvNQutSVIYLJE10bYEG5vbRDbLpq4oupAK6xLpYLZg"
secret = "oIpo2OdG55I3iitaUCahwRO8pej532HgV0JY5IJHnaXSnpQTjhSVUpHsrn8tYBEh"

class MyTestCase(unittest.TestCase):
    """ Binance Dummy Test """

    # @unittest.skip('skip')
    def test_market_enter_long_exit_long_binance(self):
        """ Binance 현물 거래 테스트 """

        tgt_market = "XRP/USDT"
        min_usdt = 12.1
        fee_ratio = 0.001
        slippage = 0.0005

        ############ CCXT ############
        binance = ccxt.binance(config={
            'apiKey': api_key,
            'secret': secret,
        })
        balances = binance.fetch_balance()

        price = fetch_current_market_price(ExType.binance, tgt_market=tgt_market)
        # enter_long_volume = int(min_usdt * (1 - (fee_ratio + slippage)) / price)
        enter_long_volume = (min_usdt * (1 - (fee_ratio + slippage)) / price)
        print(f"{enter_long_volume=}")
        # print('\n@@@@@@@@@@@@@@@@@@ CCXT BUY @@@@@@@@@@@@@@@@@@')
        # buy_order = binance.create_order(
        #     symbol=tgt_market,
        #     type="market",
        #     side="buy",
        #     amount=enter_long_volume,
        # )
        # pprint(buy_order)

        print('\n@@@@@@@@@@@@@@@@@@ CCXT SELL @@@@@@@@@@@@@@@@@@')
        sell_order = binance.create_order(
            symbol=tgt_market,
            type="market",
            side="sell",
            amount=enter_long_volume,
        )
        pprint(sell_order)


        ############ DUMMY ############
        dummy_binance_ex = DummyBinanceExConnector()
        dummy_binance_ex.set_params(
            currency='USDT',
            balance=balances['USDT']['free'],
            fee_slippage=fee_ratio,
            slippage=slippage
        )

        # Fetch Price
        price = fetch_current_market_price(ExType.binance, tgt_market=tgt_market)
        enter_long_volume = int(min_usdt * (1 - (dummy_binance_ex.get_fee_ratio() + slippage)) / price)

        ############# BUY
        print('\n@@@@@@@@@@@@@@@@@@ DUMMY BUY @@@@@@@@@@@@@@@@@@')
        dummy_binance_ex_is_processed, dummy_binance_ex_avg_price, dummy_binance_ex_total_long_vol, dummy_binance_ex_paid_fee \
        = dummy_binance_ex.enter_long(tgt_market, price, enter_long_volume)
        pprint(f"{dummy_binance_ex_is_processed=}, {dummy_binance_ex_avg_price=}, {dummy_binance_ex_total_long_vol=}, {dummy_binance_ex_paid_fee=}")
        
        ############# SELL
        print('\n@@@@@@@@@@@@@@@@@@ DUMMY SELL @@@@@@@@@@@@@@@@@@')
        dummy_binance_ex_sell_is_processed, dummy_binance_ex_sell_avg_price, dummy_binance_ex_sell_total_vol, dummy_binance_ex_sell_paid_fee \
            = dummy_binance_ex.exit_long(tgt_market, dummy_binance_ex_total_long_vol, price)
        pprint(f"{dummy_binance_ex_sell_is_processed=}, {dummy_binance_ex_sell_avg_price=}, {dummy_binance_ex_sell_total_vol=}, {dummy_binance_ex_sell_paid_fee=}")

    # @unittest.skip('skip')
    def test_future_enter_long_exit_long_binance(self):
        """ Binance 선물 거래 롱 포지션 테스트 """

        tgt_market = "XRP/USDT"
        marginMode = "ISOLATED"
        min_usdt = 6.1
        fee_ratio = 0.04
        slippage = 0.0005

        ############ CCXT ############
        binance = ccxt.binance(config={
            'apiKey': api_key,
            'secret': secret,
            'options': {
                'defaultType': 'future'
            }
        })
        binance.set_leverage(leverage=1, symbol=tgt_market)
        binance.set_margin_mode(marginMode=marginMode, symbol=tgt_market)
        try:
            binance.set_position_mode(hedged=True)
        except ExchangeError as e:
            print("Already in hedge mode, ", e)

        balances = binance.fetch_balance()

        price = fetch_current_market_price(ExType.binance, tgt_market=tgt_market)
        enter_long_volume = int(min_usdt * (1 - (fee_ratio + slippage)) / price)

        print('\n@@@@@@@@@@@@@@@@@@ CCXT ENTER_LONG @@@@@@@@@@@@@@@@@@')
        buy_order = binance.create_order(
            symbol=tgt_market,
            type="market",
            side="buy",
            amount=enter_long_volume,
            params={
                'positionSide': 'LONG',
            }
        )
        pprint(buy_order)

        print('\n@@@@@@@@@@@@@@@@@@ CCXT EXIT_LONG @@@@@@@@@@@@@@@@@@')
        sell_order = binance.create_order(
            symbol=tgt_market,
            type="market",
            side="sell",
            amount=enter_long_volume,
            params={
                'positionSide': 'LONG',
            }
        )
        pprint(sell_order)


        ############ DUMMY ############
        dummy_binance_ex = DummyBinanceUSDMExConnector()
        dummy_binance_ex.set_params(
            currency='USDT',
            balance=balances['USDT']['free'],
            fee_ratio=fee_ratio,
            slippage=slippage
        )

        ## Fetch Price
        tgt_market = "XRP/USDT"
        price = fetch_current_market_price(ExType.binance, tgt_market=tgt_market)
        enter_long_volume = int(min_usdt * (1 - (fee_ratio + slippage)) / price)

        ############# BUY
        dummy_binance_ex_is_processed, dummy_binance_ex_avg_price, dummy_binance_ex_total_long_vol, dummy_binance_ex_paid_fee \
        = dummy_binance_ex.enter_long(tgt_market, price, enter_long_volume)
        pprint(f"{dummy_binance_ex_is_processed=}, {dummy_binance_ex_avg_price=}, {dummy_binance_ex_total_long_vol=}, {dummy_binance_ex_paid_fee=}")

        ############# SELL
        dummy_binance_ex_sell_is_processed, dummy_binance_ex_sell_avg_price, dummy_binance_ex_sell_total_vol, dummy_binance_ex_sell_paid_fee \
            = dummy_binance_ex.exit_long(tgt_market, dummy_binance_ex_total_long_vol, price)
        pprint(f"{dummy_binance_ex_sell_is_processed=}, {dummy_binance_ex_sell_avg_price=}, {dummy_binance_ex_sell_total_vol=}, {dummy_binance_ex_sell_paid_fee=}")


    @unittest.skip('skip')
    def test_future_enter_short_exit_short_binance(self):
        """ Binance 선물 거래 숏 포지션 테스트 """

        tgt_market = "XRP/USDT"
        marginMode = "ISOLATED"
        min_usdt = 6.1
        fee_ratio = 0.04
        slippage = 0.0005

        ############ CCXT ############
        binance = ccxt.binance(config={
            'apiKey': api_key,
            'secret': secret,
            'options': {
                'defaultType': 'future'
            }
        })
        binance.set_leverage(leverage=1, symbol=tgt_market)
        binance.set_margin_mode(marginMode=marginMode, symbol=tgt_market)
        try:
            binance.set_position_mode(hedged=True)
        except ExchangeError as e:
            print("Already in hedge mode, ", e)

        balances = binance.fetch_balance()

        price = fetch_current_market_price(ExType.binance, tgt_market=tgt_market)
        enter_short_volume = int(min_usdt * (1 - (fee_ratio + slippage)) / price)

        print('\n@@@@@@@@@@@@@@@@@@ CCXT ENTER_SHORT @@@@@@@@@@@@@@@@@@')
        buy_order = binance.create_order(
            symbol=tgt_market,
            type="market",
            side="sell",
            amount=enter_short_volume,
            params={
                'positionSide': 'SHORT',
            }
        )
        pprint(buy_order)

        print('\n@@@@@@@@@@@@@@@@@@ CCXT EXIT_SHORT @@@@@@@@@@@@@@@@@@')
        sell_order = binance.create_order(
            symbol=tgt_market,
            type="market",
            side="buy",
            amount=enter_short_volume,
            params={
                'positionSide': 'SHORT',
            }
        )
        pprint(sell_order)


        ############ DUMMY ############
        dummy_binance_ex = DummyBinanceUSDMExConnector()
        dummy_binance_ex.set_params(balances['USDT']['free'], fee_ratio)

        ## Fetch Price
        price = fetch_current_market_price(ExType.binance, tgt_market=tgt_market)
        enter_short_volume = int(min_usdt * (1 - (fee_ratio + slippage)) / price)


        ############# SELL
        dummy_binance_ex_is_processed, dummy_binance_ex_avg_price, dummy_binance_ex_total_long_vol, dummy_binance_ex_paid_fee \
        = dummy_binance_ex.enter_short(tgt_market, price, enter_short_volume)
        pprint(f"{dummy_binance_ex_is_processed=}, {dummy_binance_ex_avg_price=}, {dummy_binance_ex_total_long_vol=}, {dummy_binance_ex_paid_fee=}")


        ############# BUY
        dummy_binance_ex_sell_is_processed, dummy_binance_ex_sell_avg_price, dummy_binance_ex_sell_total_vol, dummy_binance_ex_sell_paid_fee \
            = dummy_binance_ex.exit_short(tgt_market, dummy_binance_ex_total_long_vol, price)
        print(f"{dummy_binance_ex_sell_is_processed=}, {dummy_binance_ex_sell_avg_price=}, {dummy_binance_ex_sell_total_vol=}, {dummy_binance_ex_sell_paid_fee=}")



if __name__ == '__main__':
    unittest.main()
