import websockets
import asyncio
import json

"""
https://apidocs.bithumb.com/v1.2.0/reference/%EB%B9%97%EC%8D%B8-%EA%B1%B0%EB%9E%98%EC%86%8C-%EC%A0%95%EB%B3%B4-%EC%88%98%EC%8B%A0
"""
async def hello():
    uri = "wss://pubwss.bithumb.com/pub/ws"

    async with websockets.connect(uri, ping_interval=None) as websocket:
        greeting = await websocket.recv()
        print(greeting)
        """
            {"type":"transaction",
             "content":{
                "list":[
                    {"updn":"dn",                               ## 직전 시세와 비교(up-상승, down-하락)
                      "contDtm":"2025-01-01 12:15:47.153513",   ## 2.3. Trading date and time
                      "contAmt":"140365.000",                   ## 체결 금액
                      "contQty":"0.001",                        ## 5. 체결 수량(trading volume) 
                      "contPrice":"140365000",                  ## 4. trading price (tp)   
                      "buySellGb":"1",                          ## 6. 체결 종류(1-매도체결(bid), 2-매수체결(ask))
                      "symbol":"BTC_KRW"}           ## 1. market (upbit: cd)
                      ]
                  }
              }
        """

        # 구독 요청
        # data = '{"type":"ticker", "symbols": ["BTC_KRW"], "tickTypes": ["1M"]}'
        # data = '{"type":"transaction", "symbols": ["BTC_KRW", "ETH_KRW" ]}'
        # await websocket.send(data)

        subscribe_msg = {
            "type" : "transaction",
            "symbols" : ["BTC_KRW", "ETH_KRW", "XRP_KRW"]
        }
        data = json.dumps(subscribe_msg)
        print(data)
        await websocket.send(data)

        print("after send data")

        while True:
            recv_data = await websocket.recv()
            print(recv_data)

asyncio.get_event_loop().run_until_complete(hello())