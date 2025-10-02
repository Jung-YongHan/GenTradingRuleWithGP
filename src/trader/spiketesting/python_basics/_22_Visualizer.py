import unittest
import talib
from bulltrader.ui.visualizer.plotting import plot
import pandas as pd
from datetime import datetime, timedelta
from bulltrader.ui.visualizer.util import _as_str, _Indicator, _Data, try_, _Array
import numpy as np
from math import copysign

from bokeh.io import output_notebook, output_file, show
from bokeh.layouts import gridplot

class MyTestCase(unittest.TestCase):
    def test_plot(self):

        plot_list = []
        market_list = ['KRW-BTC', 'KRW-ETH', 'KRW-XRP']
        # market_list = ['KRW-ETH']

        # equity 데이터(트레이딩 결과) 불러오기
        trade_result = pd.read_csv('../../report/SWKimStrategy1_BeforeRefactoring_26352.csv')
        # trade_result = pd.read_csv('data/SWKimStrategy1_4H_BeforeRefactoring_28684.csv')
        data_type = '1d'
        # data_type = '4h'

        strategy = 'dmi'
        file_name = f'{market_list}_{strategy}'

        for market in market_list:
            _indicators = []
            # 코인별 일봉/시간봉 데이터 - 그래프를 그리기 위해서는 데이터의 수, 포맷이 맞아야함
            if data_type == '1d':
                data = pd.read_csv(f'../../data/{market}_DAYS.csv')
            elif data_type == '1h':
                data = pd.read_csv(f'../../data/{market}_HOUR.csv')
            elif data_type == '4h':
                data = pd.read_csv(f'../../data/{market}_HOUR4.csv')

            # 그래프 사용을 위한 데이터 정제
            data.columns = ['Symbol', 'Date_ust', 'Date', 'Open', 'High', 'Low', 'Close', 'timestamp', 'candle', 'Volume', 'unit']

            # 인덱스 활용을 위한 복제
            temp_data = data.copy()
            temp_data['Date'] = temp_data['Date'].apply(lambda _: datetime.strptime(_, '%Y-%m-%dT%H:%M:%S'))

            data.index = data['Date'].apply(lambda _: datetime.strptime(_, '%Y-%m-%dT%H:%M:%S'))
            data = data[['Open', 'High', 'Low', 'Close', 'Volume']] # 불필요한 행 제거, Volume 선택

            #############################################
            # todo 사용한 지표가 들어가도록 변경
            data['ma5'] = talib.SMA(data['Close'], timeperiod=5)
            data['ma20'] = talib.SMA(data['Close'], timeperiod=20)

            # ta 값 활용을 위한 데이터 변환
            value = data['ma5']
            ma5 = _Indicator(value, name='ma5', plot=True, overlay=None,
                             color=None, scatter=False,
                             index=data.index)
            value = data['ma20']
            ma20 = _Indicator(value, name='ma20', plot=True, overlay=None,
                              color=None, scatter=False,
                              index=data.index)
            _indicators.append(ma5)
            _indicators.append(ma20)
            # todo 사용한 지표가 들어가도록 변경
            #############################################

            # 정산된 내용만 추리기
            trade_result_btc = trade_result.loc[trade_result['market'] == 'SETT']
            equity_result = trade_result_btc[['evaluated_balance', 'date', 'price']]
            equity_result.index = equity_result['date'].apply(lambda _: datetime.strptime(_, '%Y-%m-%dT%H:%M:%S'))
            equity_result.index = equity_result.index + timedelta(minutes=1) # 트레이딩 결과는 8:59과 같이 표기 -> 9:00으로 변경

            # 빈 날짜를 채우기 위한 병합 - 트레이딩 데이터 중 누락된 날짜 복원
            merged_df = pd.merge(data, equity_result, left_index=True, right_index=True, how='left')
            equity_curve = merged_df[['evaluated_balance', 'date', 'price']]
            equity_curve.columns = ['Equity', 'DrawdownDuration', 'DrawdownPct']

            # 빈 데이터 초기화
            equity_curve['Equity'] = equity_curve['Equity'].bfill().ffill()
            equity_curve['DrawdownDuration'] = 0
            equity_curve['DrawdownPct'] = 0
            equity_curve.fillna(0, inplace=True)

            # mdd 별 지속 날짜와 최대값 계산
            def compute_drawdown_duration_peaks(dd: pd.Series):
                iloc = np.unique(np.r_[(dd == 0).values.nonzero()[0], len(dd) - 1])
                iloc = pd.Series(iloc, index=dd.index[iloc])
                df = iloc.to_frame('iloc').assign(prev=iloc.shift())
                df = df[df['iloc'] > df['prev'] + 1].astype(int)

                # If no drawdown since no trade, avoid below for pandas sake and return nan series
                if not len(df):
                    return (dd.replace(0, np.nan),) * 2

                df['duration'] = df['iloc'].map(dd.index.__getitem__) - df['prev'].map(dd.index.__getitem__)
                df['peak_dd'] = df.apply(lambda row: dd.iloc[row['prev']:row['iloc'] + 1].max(), axis=1)
                df = df.reindex(dd.index)
                return df['duration'], df['peak_dd']

            # mdd 계산
            equity = equity_curve['Equity']
            index = data.index
            dd = 1 - equity / np.maximum.accumulate(equity)
            dd_dur, dd_peaks = compute_drawdown_duration_peaks(pd.Series(dd, index=index))

            equity_df = pd.DataFrame({
                'Equity': equity,
                'DrawdownPct': dd,
                'DrawdownDuration': dd_dur},
                index=index)

            print('=' * 10 + 'equity_df' + '=' * 10)
            print(equity_df)

            # trade 비트코인 매수/매도 지점 변환
            # 동일하게 트레이딩 결과 데이터를 활용함 - trade_result
            # market = 'KRW-BTC'
            trades = trade_result[trade_result['market'] == market][['vol', 'price', 'date', 'order']]
            trades['date'] = trades['date'].apply(lambda _: datetime.strptime(_, '%Y-%m-%dT%H:%M:%S'))
            trades['date'] = trades['date'] + timedelta(minutes=1)

            def find_bar_index(row):
                # print(row['order'])
                if row['order'] != 'SETT':
                    return temp_data[temp_data['Date'] == row['date']].index.values[0]
                else:
                    return 0
            trades['EntryBar'] = trades.apply(find_bar_index,  axis=1)
            trades['ExitBar'] = trades['EntryBar'].shift(-1)
            trades.fillna(len(temp_data), inplace=True) # 마지막 봉 채우기

            trades.columns = ['Size', 'EntryPrice', 'EntryTime', 'order', 'EntryBar', 'ExitBar']

            # 매수/매도 사이즈(볼륨) +/- 구분
            def check_size_sign(row):
                if row['order'] == 'SELL':
                    return copysign(row['Size'], -1)
                else:
                    return row['Size']
            trades['Size'] = trades.apply(check_size_sign,  axis=1)

            trades['ExitTime'] = trades['EntryTime'].shift(-1)
            trades.fillna(temp_data.iloc[-1]['Date'], inplace=True) # 마지막 날 채우기

            trades['ExitPrice'] = trades['EntryPrice'].shift(-1)
            trades.fillna(temp_data.iloc[-1]['Open'], inplace=True) # 마지막 날 가격 채우기

            def calc_ReturnPct(row): # 등락 퍼센트
                return row['Size'] * (row['ExitPrice'] - row['EntryPrice'])

            def calc_PnL(row): # 등락 절대값
                return copysign(1, row['Size']) * (row['ExitPrice'] / row['EntryPrice'] - 1)

            trades['PnL'] = trades.apply(calc_ReturnPct,  axis=1)
            trades['ReturnPct'] = trades.apply(calc_PnL,  axis=1)
            trades['Duration'] = trades['ExitTime'] - trades['EntryTime']

            results_dict = {'_strategy': file_name, '_equity_curve': equity_df, '_trades': trades}
            results = pd.Series(results_dict)
            fig, plots = plot(results=results, df=data, indicators=_indicators)
            plot_list.append(plots)

        final_plots = plot_list[0]
        for p in plot_list[1:]:
            final_plots = final_plots + p
        open_browser = True
        plot_width = None
        kwargs = {}
        if plot_width is None:
            kwargs['sizing_mode'] = 'stretch_width'

        fig = gridplot(
            final_plots,
            ncols=1,
            toolbar_location='right',
            toolbar_options=dict(logo=None),
            merge_tools=True,
            **kwargs
        )
        show(fig, browser=None if open_browser else 'none')
