import pyupbit
import unittest
import time

class MyTestCase(unittest.TestCase):

    @unittest.skip("Tested")
    def test_fetch_balance(self):
        # Access Key: AI9R8xhSWx4zpPgUUTLt3bMKoAoGx70DDps6bleP
        # Secret Key: BiZxxY4mBK5EbiCRiSgsWxYRbmDjYjxjkbxDdN0f

        access = "AI9R8xhSWx4zpPgUUTLt3bMKoAoGx70DDps6bleP"          # 본인 값으로 변경
        secret = "BiZxxY4mBK5EbiCRiSgsWxYRbmDjYjxjkbxDdN0f"          # 본인 값으로 변경
        upbit = pyupbit.Upbit(access, secret)

        print(upbit.get_balance("KRW-BTC"))     # KRW-BTC 조회
        print(upbit.get_balance("KRW-BTT"))     ## BTT 보유수량
        print(upbit.get_balance("KRW"))         # 보유 현금 조회

        print(upbit.get_amount("KRW"))

        print(upbit.get_amount("KRW"))
        print(upbit.get_amount("KRW-BTC"))      ## 매수 금액, 초기에 매입 금액.


        # [
        # 	{'currency': 'KRW', 'balance': '120855.27999632', 'locked': '15008.30735345', 'avg_buy_price': '0', 'avg_buy_price_modified': True, 'unit_currency': 'KRW'},
        # 	{'currency': 'BTC', 'balance': '0.00046942', 'locked': '0.0', 'avg_buy_price': '45269113.3332', 'avg_buy_price_modified': False, 'unit_currency': 'KRW'},
        # 	{'currency': 'BTT', 'balance': '11377.3665252', 'locked': '0.0', 'avg_buy_price': '4.3933', 'avg_buy_price_modified': False, 'unit_currency': 'KRW'},
        # 	{'currency': 'WIN', 'balance': '7324.56608147', 'locked': '0.0', 'avg_buy_price': '0', 'avg_buy_price_modified': False, 'unit_currency': 'KRW'},
        # 	{'currency': 'JUV', 'balance': '0.08355265', 'locked': '0.0', 'avg_buy_price': '16803.3428', 'avg_buy_price_modified': False, 'unit_currency': 'KRW'},
        # 	{'currency': 'APENFT', 'balance': '2471.00706221', 'locked': '0.0', 'avg_buy_price': '0', 'avg_buy_price_modified': False, 'unit_currency': 'KRW'}
        # ]
        balance = upbit.get_balances()
        for currency in balance:
            print('-------------------------------------')
            print('currency:', currency['currency'])
            print('balance:', currency['balance'])
            print('locked:', currency['locked'])
            print('avg_buy_price:', currency['avg_buy_price'])
            print('avg_buy_price_modified:', currency['avg_buy_price_modified'])
            print('unit_currency:', currency['unit_currency'])
            # if currency['currency'] != currency['unit_currency']:
            #     ticker = currency['unit_currency'] + '-' + currency['currency']
            #     # dc = DataCollector()
                # df = dc.fetchMarket(ticker, 1, None, DataType.MINUTES_1)
                # value = df['trade_price'].values
                # print(f'current_price: {ticker}: {value}')

    @unittest.skip("Tested")
    def test_fetch_markets(self):
        tickers = pyupbit.get_tickers(fiat="KRW")

        end = 10
        for i in range(end):
            for i, ticker in enumerate(tickers):
                try:
                    print(" ", i, ">>", ticker, "  -------------------------------------------------------------------")
                    df = pyupbit.get_ohlcv(ticker, count=1, interval="minute1")
                    print(df.columns)
                    time.sleep(0.1)
                except TypeError:
                    pass
            print('Sleep for 60 sec..')
            time.sleep(60)

    @unittest.skip("Tested")
    def test_fetch_current_markets(self):
        tickers = pyupbit.get_tickers(fiat="KRW")

        import requests
        url = "https://api.upbit.com/v1/ticker"
        querystring = {"count": 10, "markets": tickers}
        headers = {"Accept": "application/json"}
        response = requests.request("GET", url, headers=headers, params=querystring)
        print(response.text)


if __name__ == '__main__':
    unittest.main()
