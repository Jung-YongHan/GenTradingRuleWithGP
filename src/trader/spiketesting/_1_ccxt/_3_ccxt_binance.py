import unittest

import ccxt


class MyTestCase(unittest.TestCase) :

    def test_create_buy_order(self):
        api_key = "NjbQqYaSVwWSG0ZPfzKC5RwvNQutSVIYLJE10bYEG5vbRDbLpq4oupAK6xLpYLZg"
        secret = "oIpo2OdG55I3iitaUCahwRO8pej532HgV0JY5IJHnaXSnpQTjhSVUpHsrn8tYBEh"

        # binance 객체 생성
        binance = ccxt.binance(config = {
            'apiKey'          : api_key,
            'secret'          : secret,
        })
        amount = 0.00060000
        buy_order = binance.create_order(
            symbol='BTC/USDT',
            type="market",
            side="sell",
            amount=amount
        )
        print(buy_order)


if __name__ == '__main__' :
    unittest.main()
