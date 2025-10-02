import ccxt

import unittest
import pandas as pd
from os.path import dirname, join
import re
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('max_colwidth', None)

def _excel_sheet_name_for_market(source):
    pattern_text = '[A-Z]+[A-Z]+[A-Z]+-[A-Z]*'
    pattern = re.compile(pattern_text)
    m = pattern.match(source)
    return bool(m)

## Issue1 : Setting TimeZone?
## Issue2 : binance support sendbox model, how about upbit?

class MyTestCase(unittest.TestCase):

    @unittest.skip("Tested")
    def test_binance_load_markets(self):
        exchange = ccxt.binance()

        # Load Markets
        print("############################################")
        print('MARKETS')
        ## Print All Markets
        print(exchange.load_markets())

        ## Print Only BTC/USDT Market
        markets = exchange.load_markets()
        print(markets['BTC/USDT'])

    @unittest.skip("Tested")
    def test_binance_fetch_ticker(self):
        exchange = ccxt.binance()
        print("############################################")
        print('fetch_ticker')
        print(exchange.fetch_ticker('BTC/USDT'))


    @unittest.skip("Tested")
    def test_binance_fetch_trades(self):
        exchange = ccxt.binance()
        print("############################################")
        print('fetch_trades')
        print(exchange.fetch_trades('BTC/USDT'))

    # @unittest.skip("Tested")
    def test_binance_fetch_ohlcv(self):
        exchange = ccxt.binance()
        # btc = exchange.fetch_ohlcv('USDT-BTC', timeframe='1m', since=None,limit=10)  ## Does not work
        btc = exchange.fetch_ohlcv('BTC/USDT', timeframe='1m', since=None, limit=10)   ## Works
        import pandas as pd
        df = pd.DataFrame(btc, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
        df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')
        df['datetime'] = df['datetime'] + pd.Timedelta(hours=9)
        df.set_index('datetime', inplace=True)
        print(df)

    def test_upbit_fetch_ohlcv(self):
        exchange = ccxt.upbit()
        btc = exchange.fetch_ohlcv('KRW-BTC', timeframe='1d', since=None,limit=180)    ## Works
        # btc = exchange.fetch_ohlcv('BTC/KRW', timeframe='1m', since=None, limit=10)     ## Works
        import pandas as pd
        df = pd.DataFrame(btc, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
        df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')
        df.set_index('datetime', inplace=True)
        print(df)

    # @unittest.skip("Tested")
    def test_binance_fetch_future_ohlcv(self):
        exchange = ccxt.binanceusdm()
        exchange.load_markets()
        btc = exchange.fetch_ohlcv('ETH/USDT', timeframe='1m', since=None, limit=10)
        import pandas as pd
        df = pd.DataFrame(btc, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
        df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')
        df.set_index('datetime', inplace=True)
        print(df)

    def test_upbit_fetch_fees(self):
        upbit    = ccxt.upbit({
            'apiKey': 'hiVhxgDTuwVrV6KSMQYUEaxSf7qecjox949x229a',
            'secret': 'aanuPVEFBN0vfttfzass4muGiWn17Ja1u6a2KP2v'
        })
        # btc = exchange.fetch_ohlcv('USDT-BTC', timeframe='1m', since=None,limit=10)  ## Does not work
        fees = upbit.fetch_fees()
        for fee_key in fees:
            print(f'{fee_key} - {fees[fee_key]}')

    def test_binance_adjust_time_diff(self):
        exchange = ccxt.binance({
            'options' : {
                'adjustForTimeDifference' : False       ## Does Not Work
            }
        })

        btc = exchange.fetch_ohlcv('BTC/USDT', timeframe='1m', since=None, limit=10)   ## Works
        import pandas as pd
        df = pd.DataFrame(btc, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
        df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')
        df.set_index('datetime', inplace=True)
        print(df)

    def test_binance_upbit_desc(self):
        def describe_ex(ex_name, desc):
            print(f'{ex_name} =============================================')
            print(desc)
            print('support_spot:', desc['has']['spot'])
            print('support_futures:', desc['has']['future'])
            print('support_ohldv:', desc['has']['fetchOHLCV'])
            print('support_timeframes:',desc['timeframes'])

        binance = ccxt.binance()
        binance.fetch_markets()
        binance_des_dict = binance.describe()
        describe_ex('binance', binance_des_dict)

        upbit    = ccxt.upbit({
            'apiKey': 'hiVhxgDTuwVrV6KSMQYUEaxSf7qecjox949x229a',
            'secret': 'aanuPVEFBN0vfttfzass4muGiWn17Ja1u6a2KP2v'
        })
        upbit_dict = upbit.describe()
        upbit.fetch_markets()
        describe_ex('upbit', upbit_dict)

    def test_binance_upbit_precision(self):
        binance = ccxt.binance()
        binance.load_markets()
        symbol = 'BTC/USDT'
        amount = 1.2345678  # amount in base currency BTC
        price = 87654.321  # price in quote currency USDT
        formatted_amount = binance.amount_to_precision(symbol, amount)
        formatted_price = binance.price_to_precision(symbol, price)
        print(formatted_amount, formatted_price)

    def test_time(self):
        binance = ccxt.binance()
        binance_desc = binance.describe()
        if binance_desc['has']['fetchTime']:
            svr_time = binance.fetch_time()
            print(f'binance time: {svr_time}')

        upbit = ccxt.upbit()
        upbit_desc = binance.describe()
        if upbit_desc['has']['fetchTime']:
            pass
            # svr_time = upbit.fetch_t.fetch_time()
            # print(f'upbit time: {svr_time}')


if __name__ == '__main__':
    unittest.main()


#################################
### Binance


#################################


# hitbtc   = ccxt.hitbtc({'verbose': True})
# hitbtc_markets = hitbtc.load_markets()
# print(hitbtc.id, hitbtc_markets)
#
# bitmex   = ccxt.bitmex()
# huobipro = ccxt.huobipro()
# upbit    = ccxt.upbit({
#     'apiKey': 'hiVhxgDTuwVrV6KSMQYUEaxSf7qecjox949x229a',
#     'secret': 'aanuPVEFBN0vfttfzass4muGiWn17Ja1u6a2KP2v'
# })
#
# exmo     = ccxt.exmo({
#     'apiKey': 'YOUR_PUBLIC_API_KEY',
#     'secret': 'YOUR_SECRET_PRIVATE_KEY',
# })
#
# kraken = ccxt.kraken({
#     'apiKey': 'YOUR_PUBLIC_API_KEY',
#     'secret': 'YOUR_SECRET_PRIVATE_KEY',
# })

######################################################
exchange_id = 'binance'
# exchange_class = getattr(ccxt, exchange_id)
# exchange = exchange_class({
#     'apiKey': 'hiVhxgDTuwVrV6KSMQYUEaxSf7qecjox949x229a',
#     'secret': 'aanuPVEFBN0vfttfzass4muGiWn17Ja1u6a2KP2v'
#     # 'options' : {'defaultType': 'future',},
# })

