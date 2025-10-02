import time
from pprint import pprint
import ccxt
from ccxt.base.errors import InvalidOrder, OrderNotFound, ExchangeError
import unittest


api_key = "NjbQqYaSVwWSG0ZPfzKC5RwvNQutSVIYLJE10bYEG5vbRDbLpq4oupAK6xLpYLZg"
secret = "oIpo2OdG55I3iitaUCahwRO8pej532HgV0JY5IJHnaXSnpQTjhSVUpHsrn8tYBEh"

symbol = "XRP/USDT"
marginMode = "ISOLATED"
# binance 객체 생성
binance = ccxt.binance(config={
    'apiKey': api_key,
    'secret': secret,
    # Post-Only
    'enableRateLimit': True,
    # future
    'options': {
        'defaultType': 'future'
    }
})
try:
    binance.set_position_mode(hedged=True)
except ExchangeError as e:
    print("Already in hedge mode, ", e)
binance.set_leverage(leverage=1, symbol=symbol)
binance.set_margin_mode(marginMode=marginMode, symbol=symbol)


class MyTestCase(unittest.TestCase):
    def test_create_buy_order(self):
        buy_order = binance.create_order(
            symbol=symbol,
            type="market",
            side="sell",
            amount=15,
            params={
                # 'positionSide': 'LONG',
                'positionSide': 'SHORT',
            }
        )
        pprint(buy_order)

    def test_check_order(self):
        # 최신 주문 ID 조회
        latest_order_id = binance.fetch_orders(
            symbol=symbol,
            limit=1
        )[0]['info']['orderId']

        # 주문 확인
        order = binance.fetch_order(id=latest_order_id, symbol=symbol)
        pprint(order)

    def test_get_open_orders(self):
        # 미체결 주문 조회
        open_orders = binance.fetch_open_orders(symbol=symbol)
        print(open_orders)

    def test_edit_order(self):
        # 최신 주문 ID 조회
        latest_order_id = binance.fetch_orders(
            symbol=symbol,
            limit=1
        )[0]['info']['orderId']
        
        # 미체결 주문 수정, 체결 되었다면 에러
        order = binance.edit_order(
            id=latest_order_id,
            symbol=symbol,
            type=type,
            side="buy",
            amount=14,
        )
        pprint(order)

    def test_fetch_orders(self):
        # 최신 부터 limit 갯수 만큼 주문 조회
        orders = binance.fetch_orders(
            symbol=symbol,
            limit=1
        )
        pprint(orders)
        print(len(orders))

    def test_cancel_order(self):
        try:
            # 가장 최신 주문 ID
            latest_order_id = binance.fetch_orders(
                symbol=symbol,
                limit=1
            )[0]['info']['orderId']

            order = binance.cancel_order(
                id=latest_order_id,
                symbol=symbol
            )
            print(order)
        except OrderNotFound as e:
            print("Unknown order ", e)
        except InvalidOrder as e:
            print("Cancelled or fully filled. ", e)

    def test_load_position(self):
        balance = binance.fetch_balance()
        print(balance['USDT'])
        for position in balance['info']['positions']:
            if position['symbol'] == symbol.replace('/', ""):
                pprint(position)


if __name__ == "__main__":
    # https://www.binance.com/en/futures/XRPUSDT
    unittest.main()
