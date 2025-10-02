from datetime import datetime

import ccxt

binance = ccxt.binance()
markets = binance.fetch_tickers()
print(markets.keys())

ticker = binance.fetch_ticker('ETH/BTC')
print(ticker['open'], ticker['high'], ticker['low'], ticker['close'])

ohlcvs = binance.fetch_ohlcv('ETH/BTC')
print(ohlcvs)

for ohlc in ohlcvs:
    print(datetime.fromtimestamp(ohlc[0]/1000).strftime('%Y-%m-%d %H:%M:%S'))

#######################################################################
upbit = ccxt.upbit()
markets = upbit.fetch_tickers()
print(markets.keys())

ticker = upbit.fetch_ticker('ETH/BTC')
print(ticker['open'], ticker['high'], ticker['low'], ticker['close'])
ohlcvs = upbit.fetch_ohlcv('ETH/BTC')
print(ohlcvs)