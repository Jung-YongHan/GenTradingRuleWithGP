import datetime
import logging

from bt4.Constants import CandleType, ExType
from bt4.quote.QuoteMgr import QuoteStorageMgr
import requests

from bt4.utils.exchange_filter import ExFilterFactory


def get_upbit_markets() -> str or None:
    url: str = "https://api.upbit.com/v1/market/all"
    response: requests.Response = requests.get(url)

    if response.status_code == 200:
        markets_resp: str = response.json()
        return markets_resp
    else:
        print(f"Error: {response.status_code}")
        return None


if __name__ == '__main__':
    ex_type: ExType = ExType.binance
    # markets = 'KRW-BTC KRW-ETH KRW-XRP KRW-SOL KRW-DOGE KRW-ADA KRW-SHIB KRW-AVAX KRW-TRX KRW-DOT KRW-BCH KRW-LINK KRW-NEAR KRW-MATIC KRW-ETC KRW-HBAR KRW-APT KRW-ATOM KRW-MNT KRW-CRO'.split() #정보를 읽어와 진행 필요
    # markets = 'KRW-BTC KRW-ETH KRW-XRP KRW-SOL KRW-DOGE'.split() #정보를 읽어와 진행 필요
    # markets = 'KRW-BTC KRW-ETH'.split() #정보를 읽어와 진행 필요

    # markets = "USDT-BTC USDT-ETH USDT-XRP USDT-SOL USDT-DOGE USDT-SUI USDT-ADA USDT-TRX USDT-ENA USDT-PNUT".split()
    markets = "USDT-BTC USDT-ETH USDT-XRP USDT-SOL USDT-DOGE USDT-SUI USDT-ADA USDT-TRX USDT-ENA USDT-PNUT".split()

    # markets: list = [market['market'] for market in get_upbit_markets() if 'KRW' in market['market']]

    # markets = []
    # if markets_temp:
    #     for market in markets_temp:
    #         print(
    #             f"Market: {market['market']}, Korean Name: {market['korean_name']}, English Name: {market['english_name']}")
    #         markets.append(market['market'])

    needed_cdl_type: list = [
                             CandleType.DAYS,
                             CandleType.HOUR4,
                             CandleType.HOUR,
                             CandleType.MINUTES_30,
                             CandleType.MINUTES_15,
                             CandleType.MINUTES_5,
                             CandleType.MINUTES_3,
                             CandleType.MINUTES_1,
                             ]

    # 데이터가 아무것도 없을 때 설정하는 끝 지점
    from_to: datetime.datetime = datetime.datetime(2017, 1, 1, 9, 0, 0)

    # 데이터가 존재하면 해당 데이터의 가장 최근 날짜까지 수집 진행
    start_to: datetime.datetime = datetime.datetime.now() - datetime.timedelta(days=1)  # 확정된 데이터 수집을 위해
    do_update: bool = True
    # root_dir: str = '/app'

    # 10개씩 10번에 나눠서 처리
    batch_size = 1
    num_batches = (len(markets) + batch_size - 1) // batch_size

    for i in range(num_batches):
        batch = markets[i * batch_size: (i + 1) * batch_size]
        logging.info(f'{i}번째 배치 - {batch}')
        # 여기서 batch에 대한 처리 수행
        QuoteStorageMgr(batch, needed_cdl_type).load_stored_quote(ex_type,
                                                                batch,
                                                                needed_cdl_type,
                                                                start_to,
                                                                from_to,
                                                                do_update,
                                                                # root_dir
                                                                )
