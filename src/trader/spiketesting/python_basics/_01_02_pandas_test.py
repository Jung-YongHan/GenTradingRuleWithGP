import unittest
import json
import pandas as pd

class MyTestCase(unittest.TestCase):

    @unittest.skip("Tested")
    def test_dataframe(self):
        data = '''[{"market":"KRW-BTC","candle_date_time_utc":"2021-09-03T02:39:00","candle_date_time_kst":"2021-09-03T11:39:00","opening_price":56868000.00000000,"high_price":56903000.00000000,"low_price":56856000.00000000,"trade_price":56900000.00000000,"timestamp":1630636792784,"candle_acc_trade_price":420813429.35244000,"candle_acc_trade_volume":7.39886055,"unit":1},{"market":"KRW-ETH","candle_date_time_utc":"2021-09-03T02:39:00","candle_date_time_kst":"2021-09-03T11:39:00","opening_price":4385000.00000000,"high_price":4387000.00000000,"low_price":4384000.00000000,"trade_price":4386000.00000000,"timestamp":1630636790878,"candle_acc_trade_price":212466835.53544000,"candle_acc_trade_volume":48.44660426,"unit":1},{"market":"KRW-MTL","candle_date_time_utc":"2021-09-03T02:39:00","candle_date_time_kst":"2021-09-03T11:39:00","opening_price":4870.00000000,"high_price":4870.00000000,"low_price":4865.00000000,"trade_price":4870.00000000,"timestamp":1630636788825,"candle_acc_trade_price":13317607.88474075,"candle_acc_trade_volume":2734.90572272,"unit":1},{"market":"KRW-XRP","candle_date_time_utc":"2021-09-03T02:39:00","candle_date_time_kst":"2021-09-03T11:39:00","opening_price":1450.00000000,"high_price":1450.00000000,"low_price":1445.00000000,"trade_price":1450.00000000,"timestamp":1630636792901,"candle_acc_trade_price":140853703.38270410,"candle_acc_trade_volume":97251.58162835,"unit":1},{"market":"KRW-SRM","candle_date_time_utc":"2021-09-03T02:39:00","candle_date_time_kst":"2021-09-03T11:39:00","opening_price":10800.00000000,"high_price":10870.00000000,"low_price":10790.00000000,"trade_price":10860.00000000,"timestamp":1630636792936,"candle_acc_trade_price":324099221.94184700,"candle_acc_trade_volume":29948.43287833,"unit":1},{"market":"KRW-SAND","candle_date_time_utc":"2021-09-03T02:39:00","candle_date_time_kst":"2021-09-03T11:39:00","opening_price":1180.00000000,"high_price":1180.00000000,"low_price":1170.00000000,"trade_price":1170.00000000,"timestamp":1630636791211,"candle_acc_trade_price":78458247.66776655,"candle_acc_trade_volume":66803.40183736,"unit":1},{"market":"KRW-BCHA","candle_date_time_utc":"2021-09-03T02:39:00","candle_date_time_kst":"2021-09-03T11:39:00","opening_price":286000.00000000,"high_price":286000.00000000,"low_price":284650.00000000,"trade_price":285400.00000000,"timestamp":1630636793976,"candle_acc_trade_price":900872898.20828150,"candle_acc_trade_volume":3157.77585354,"unit":1},{"market":"KRW-DOT","candle_date_time_utc":"2021-09-03T02:39:00","candle_date_time_kst":"2021-09-03T11:39:00","opening_price":36980.00000000,"high_price":37050.00000000,"low_price":36950.00000000,"trade_price":36970.00000000,"timestamp":1630636786404,"candle_acc_trade_price":61955309.88984160,"candle_acc_trade_volume":1675.66388164,"unit":1},{"market":"KRW-ETC","candle_date_time_utc":"2021-09-03T02:39:00","candle_date_time_kst":"2021-09-03T11:39:00","opening_price":78300.00000000,"high_price":78400.00000000,"low_price":78290.00000000,"trade_price":78400.00000000,"timestamp":1630636793233,"candle_acc_trade_price":212307488.64400810,"candle_acc_trade_volume":2710.24655218,"unit":1},{"market":"KRW-PLA","candle_date_time_utc":"2021-09-03T02:39:00","candle_date_time_kst":"2021-09-03T11:39:00","opening_price":1425.00000000,"high_price":1425.00000000,"low_price":1420.00000000,"trade_price":1425.00000000,"timestamp":1630636770587,"candle_acc_trade_price":38494544.20596900,"candle_acc_trade_volume":27025.98366558,"unit":1},{"market":"KRW-DOGE","candle_date_time_utc":"2021-09-03T02:39:00","candle_date_time_kst":"2021-09-03T11:39:00","opening_price":341.00000000,"high_price":341.00000000,"low_price":340.00000000,"trade_price":341.00000000,"timestamp":1630636794364,"candle_acc_trade_price":35903460.00995037,"candle_acc_trade_volume":105448.43310572,"unit":1},{"market":"KRW-ADA","candle_date_time_utc":"2021-09-03T02:39:00","candle_date_time_kst":"2021-09-03T11:39:00","opening_price":3410.00000000,"high_price":3415.00000000,"low_price":3410.00000000,"trade_price":3410.00000000,"timestamp":1630636792266,"candle_acc_trade_price":131914034.54197855,"candle_acc_trade_volume":38635.35016174,"unit":1},{"market":"KRW-AHT","candle_date_time_utc":"2021-09-03T02:39:00","candle_date_time_kst":"2021-09-03T11:39:00","opening_price":16.70000000,"high_price":16.70000000,"low_price":16.70000000,"trade_price":16.70000000,"timestamp":1630636780004,"candle_acc_trade_price":192616.03943573,"candle_acc_trade_volume":11533.89457699,"unit":1},{"market":"KRW-KAVA","candle_date_time_utc":"2021-09-03T02:39:00","candle_date_time_kst":"2021-09-03T11:39:00","opening_price":9365.00000000,"high_price":9375.00000000,"low_price":9360.00000000,"trade_price":9375.00000000,"timestamp":1630636790730,"candle_acc_trade_price":30515056.10266660,"candle_acc_trade_volume":3257.61364123,"unit":1},{"market":"KRW-LSK","candle_date_time_utc":"2021-09-03T02:39:00","candle_date_time_kst":"2021-09-03T11:39:00","opening_price":5300.00000000,"high_price":5300.00000000,"low_price":5295.00000000,"trade_price":5295.00000000,"timestamp":1630636787635,"candle_acc_trade_price":4550211.94605505,"candle_acc_trade_volume":859.05074267,"unit":1},{"market":"KRW-QTUM","candle_date_time_utc":"2021-09-03T02:39:00","candle_date_time_kst":"2021-09-03T11:39:00","opening_price":15260.00000000,"high_price":15270.00000000,"low_price":15250.00000000,"trade_price":15270.00000000,"timestamp":1630636790166,"candle_acc_trade_price":6619088.36312000,"candle_acc_trade_volume":433.51912613,"unit":1},{"market":"KRW-BTG","candle_date_time_utc":"2021-09-03T02:39:00","candle_date_time_kst":"2021-09-03T11:39:00","opening_price":91960.00000000,"high_price":92140.00000000,"low_price":91960.00000000,"trade_price":92140.00000000,"timestamp":1630636793050,"candle_acc_trade_price":46783668.99027940,"candle_acc_trade_volume":507.96926910,"unit":1},{"market":"KRW-EOS","candle_date_time_utc":"2021-09-03T02:39:00","candle_date_time_kst":"2021-09-03T11:39:00","opening_price":6050.00000000,"high_price":6055.00000000,"low_price":6045.00000000,"trade_price":6055.00000000,"timestamp":1630636769805,"candle_acc_trade_price":8116700.96637900,"candle_acc_trade_volume":1341.70026614,"unit":1},{"market":"KRW-TRX","candle_date_time_utc":"2021-09-03T02:39:00","candle_date_time_kst":"2021-09-03T11:39:00","opening_price":116.00000000,"high_price":116.00000000,"low_price":115.00000000,"trade_price":116.00000000,"timestamp":1630636793999,"candle_acc_trade_price":99762047.07970805,"candle_acc_trade_volume":860291.46542879,"unit":1},{"market":"KRW-XTZ","candle_date_time_utc":"2021-09-03T02:39:00","candle_date_time_kst":"2021-09-03T11:39:00","opening_price":6070.00000000,"high_price":6070.00000000,"low_price":6065.00000000,"trade_price":6065.00000000,"timestamp":1630636766825,"candle_acc_trade_price":22214093.22499545,"candle_acc_trade_volume":3659.85799238,"unit":1},{"market":"KRW-BCH","candle_date_time_utc":"2021-09-03T02:39:00","candle_date_time_kst":"2021-09-03T11:39:00","opening_price":764300.00000000,"high_price":764900.00000000,"low_price":764300.00000000,"trade_price":764900.00000000,"timestamp":1630636793740,"candle_acc_trade_price":10217857.14928400,"candle_acc_trade_volume":13.36805519,"unit":1}]'''
        a_json = json.loads(data)
        quote_df = pd.DataFrame.from_records(a_json)
        # selected_quotes = quote_df[quote_df['market'] == ['KRW-BTC', 'KRW-ETH']] ## It does not work.
        selected_quotes = quote_df[quote_df['market'].isin(['KRW-BTC','KRW-ETH'])]

        print(selected_quotes.head())
        # market = ['KRW-ETH', 'KRW-BTC']
        # market = ['KRW-BTC', 'KRW-ETH']
        market = ['KRW-BTC', 'KRW-ETH', 'KRW-XRP']
        print(sorted(selected_quotes['market'].unique()) == sorted(market))


    def test_dataframe_join(self):
        df_left = pd.DataFrame({'A': ['A0', 'A1', 'A2', 'A3'],'B': ['B0', 'B1', 'B2', 'B3']},
                               index=['K0', 'K1', 'K2', 'K3'])
        df_right = pd.DataFrame({'C': ['C2', 'C3', 'C4', 'C5'],'D': ['D2', 'D3', 'D4', 'D5']},
                                index=['K2', 'K3', 'K4', 'K5'])

        df_joined = df_left.join(df_right, how='outer')
        print(df_joined)
        print(df_joined.index.to_numpy())

    def test_shift(self):
        df = pd.DataFrame({'X': [1, 2, 3, ],
                           'Y': [4, 1, 8]})
        print("Original DataFrame:")
        print(df)

        df['Y'] = df['Y'].shift(1)
        print("Shifted DataFrame")
        print(df)


if __name__ == '__main__':
    unittest.main()
