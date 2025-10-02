
from binance import Client

client = Client(api_key="your_api_key", api_secret="your_api_secret")

symbol = "BTCUSDT"
interval = "1m"

# Get the last 10 minutes of data

end_time = int(time.time() * 1000)  # Current timestamp in milliseconds

start_time = end_time - (10 * 60 * 1000)  # 10 minutes ago



klines = client.get_historical_klines(symbol, interval, start_time, end_time)



# Process the klines data (e.g., extract open, high, low, close prices)

for kline in klines:

    print(kline)