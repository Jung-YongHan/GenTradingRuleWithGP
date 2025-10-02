import websockets
import asyncio
import json
import pybithumb
import pandas as pd
from pandas import DataFrame
from datetime import datetime

# 급상승/급하락 조건 변수
cycle_time = 120  # X초 동안
check_rate = 3  # 0.5% 상승하면


# 함수
# 이전가격 대비 상승률 함수
def diff(prev_price, current_price) :
    return round((float(current_price) - float(prev_price)) / float(prev_price) * 100, 3)


# X분 이전 가격
def prev_price(ticker) :
    return float(df.at[ticker, 'closing_price'])


# X분 이전 시간
def prev_time(ticker) :
    return df.at[ticker, 'time']


# 초기화
# DataFrame 초기화
df = DataFrame([(0, datetime.now(), 0)], columns = ['ticker_symbol', 'time', 'closing_price'])
df = df.drop(0)

# 전체 Symbol 초기데이터 획득
all = pybithumb.get_current_price("ALL")
ticker_symbol = []

# DataFrame 베이스 Data 취득
for ticker, data in all.items() :
    ticker_symbol.append(ticker + "_KRW")
    new_df = pd.DataFrame({'ticker_symbol' : [ticker + "_KRW"], 'time' : [datetime.now().strftime('%Y%m%d%H%M%S')],
                    'closing_price' : [data['closing_price']]})
    df = pd.concat([df, new_df])
df.set_index('ticker_symbol', inplace = True)


# 실시간 급등주 찾기 - 전체 Symbol 에서 WebSocket 이용한 실시간 시세 이용
async def bithumb_ws_client() :
    uri = "wss://pubwss.bithumb.com/pub/ws"

    async with websockets.connect(uri, ping_interval = None) as websocket :
        subscribe_fmt = {
            "type"      : "ticker",
            "symbols"   : ticker_symbol,
            "tickTypes" : ["1H"]
        }
        subscribe_data = json.dumps(subscribe_fmt)

        await websocket.send(subscribe_data)

        # 각 Ticker 에 대한 실시간 시세 변동 시 CallBack
        while True :
            data = await websocket.recv()
            data = json.loads(data)
            if 'content' in data :
                ticker_data = data['content']['symbol']  # 종목
                closePrice_data = data['content']['closePrice']  # 종목의 현재가
                time_data = data['content']['date'] + data['content']['time']  # 종목이 변화한 시간

                diff_rate = diff(prev_price(ticker_data), closePrice_data)  # 이전 가격과 현재 가격의 차이
                time_gap = int(time_data) - int(prev_time(ticker_data))  # 이전 시간과, 현재 시간의 간격

                # 급등주 출력 ( X 초 동안, Y % 상승한 경우 매수 체결 신호)
                if time_gap > cycle_time and diff_rate > check_rate :
                    print(ticker_data, closePrice_data, prev_price(ticker_data), diff_rate)

                # 시간 갱신 ( 이전 데이터에 현재 데이터로 업데이트 )
                if time_gap > cycle_time :
                    df.loc[ticker_data] = (time_data, closePrice_data)


async def main() :
    await bithumb_ws_client()


asyncio.run(main())