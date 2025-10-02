import time
import unittest

from bt4.core.TradingCtxBuilder import TradingContextBuilder
from bt4.trade.TradeMgr import NettingTradeMgr, HedgingTradeMgr
from bt4.Constants import Operation_Type, R, ExType, AssetMgrType, CandleType
from bt4.model.trade_object import Trade
from bt4.utils.python_utils import str2dt
from bt4_test._30_support_test._S03_ExchangeConnectorTest import fetch_current_market_price, mingu_upbit_access_key, \
    mingu_upbit_secret_key, stkim_bithumb_access_key, stkim_bithumb_secrete_key


class MyTestCase(unittest.TestCase):

    def test_am_enter_long_bithumb(self):
        r = R()
        params = {}
        params[r.OP.OP] = Operation_Type.LIVE_TRADING
        ## Dummy Upbit
        # params[r.EX.EX_TYPE] = ExType.dummy_upbit
        # params[r.EX.EX_DUMMY_INITIAL_RATIO] = 10000000
        # params[r.EX.EX_DUMMY_FEE_RATIO] = 0.0008
        params[r.EX.EX_ACCOUNT] = "simulator"

        params[r.EX.EX_TYPE] = ExType.bithumb
        params[r.EX.EX_ACCOUNT]  = "stkim"
        params[r.EX.EX_ACCESS_KEY] = stkim_bithumb_access_key
        params[r.EX.EX_SECRET_KEY] = stkim_bithumb_secrete_key

        params[r.OP.MARKET] = ('KRW-BTC', 'KRW-ETH', 'KRW-XRP')
        params[r.OP.BT.CANDLE_TYPE] = CandleType.HOUR
        params[r.AM.AM_TYPE] = AssetMgrType.FIXED
        params[r.AM.AM_FIXED_TRADE_RATIO] = 0.4  #### Changed

        trading_builder = TradingContextBuilder(params)
        trading_builder.build_exchange()
        am = trading_builder.build_asset_mgmt()

        # trading_builder.context.exchange.is_live_trading = False

        #######################################
        ## Fetching Quote
        quote_ex_type = ExType.bithumb
        tgt_market = 'KRW-BTC'
        tick = fetch_current_market_price(quote_ex_type, tgt_market, return_tick=True)
        price = tick.close

        am.refresh_balance()
        am.rebalance(tick)
        buy_trade_result = am.enter_long(tgt_market, price, tick, '08:59')

        print(f'[{tick.datetime}] BUY ORDER:: {tick.market} price:{buy_trade_result.settled_price}, '
             f'vol:{buy_trade_result.settled_vol}, market evaluated market bal: {buy_trade_result.evaluated_market_balance}')

        print("wait for 10 sec...")
        time.sleep(10)

        sell_trade_result = am.exit_long(buy_trade_result, tgt_market, price, tick, '08:59')
        print(f'[{tick.datetime}] SELL ORDER:: {sell_trade_result.market} price:{sell_trade_result.settled_price}, '
            f'vol:{sell_trade_result.settled_vol}, market cash bal:{sell_trade_result.market_cash_bal}')


    def test_am_enter_long_upbit(self):
        r = R()
        params = {}
        params[r.OP.OP] = Operation_Type.LIVE_TRADING
        ## Dummy Upbit
        # params[r.EX.EX_TYPE] = ExType.dummy_upbit
        # params[r.EX.EX_DUMMY_INITIAL_RATIO] = 10000000
        # params[r.EX.EX_DUMMY_FEE_RATIO] = 0.0008
        params[r.EX.EX_ACCOUNT] = 'simulator'

        params[r.EX.EX_TYPE] = ExType.upbit
        params[r.EX.EX_ACCOUNT]  = 'mingu'
        params[r.EX.EX_ACCESS_KEY] = mingu_upbit_access_key
        params[r.EX.EX_SECRET_KEY] = mingu_upbit_secret_key

        params[r.OP.MARKET] = ('KRW-BTC', 'KRW-ETH', 'KRW-XRP')
        params[r.OP.BT.CANDLE_TYPE] = CandleType.HOUR
        params[r.AM.AM_TYPE] = AssetMgrType.FIXED
        params[r.AM.AM_FIXED_TRADE_RATIO] = 0.4  #### Changed

        trading_builder = TradingContextBuilder(params)
        trading_builder.build_exchange()
        am = trading_builder.build_asset_mgmt()

        #######################################
        ## Fetching Quote
        quote_ex_type = ExType.upbit
        tgt_market = 'KRW-BTC'
        tick = fetch_current_market_price(quote_ex_type, tgt_market, return_tick=True)
        price = tick.close

        am.refresh_balance()
        am.rebalance(tick)
        buy_trade_result = am.enter_long(tgt_market, price, tick, '08:59')

        print(f'[{tick.datetime}] BUY ORDER:: {tick.market} price:{buy_trade_result.settled_price}, '
             f'vol:{buy_trade_result.settled_vol}, market evaluated market bal: {buy_trade_result.evaluated_market_balance}')

        sell_trade_result = am.exit_long(buy_trade_result, tgt_market, price, tick, '08:59')
        print(f'[{tick.datetime}] SELL ORDER:: {sell_trade_result.market} price:{sell_trade_result.settled_price}, '
            f'vol:{sell_trade_result.settled_vol}, market cash bal:{sell_trade_result.market_cash_bal}')


    # @unittest.skip("Tested")
    def test_trade_states_for_netting(self):
        buy_trade_result_btc = Trade(True, 'BUY', '2018-10-03T07:59:00', 'KRW-BTC', 1549612.4031007756, 7410000.0, 0.2091244808503071, 774.8062015503878, 1550387.9844961243, 8449612.790697673, 0.0, 9999225.193798449,"prop: 0.310,vola: 0.0215, price(7410000.0) > mas([7390000.0,7386200.0,7392600.0,7371600.0])")
        sell_trade_result_btc = Trade(True, 'SELL', '2018-10-04T05:59:00', 'KRW-BTC', 1535110.4227644398, 7348000.0, 0.20901991860988195, 767.9391809727063, 3085498.407260564, 9984723.213462112, -14501.98033633572, 9973289.925757775,", price(7348000.0) < mas([7361000.0,7358600.0,7378800.0,7361700.0]")

        buy_trade_result_eth = Trade(True, 'BUY', '2018-10-03T07:59:00', 'KRW-ETH', 1549612.4031007756, 7410000.0,
                                     0.2091244808503071, 774.8062015503878, 1550387.9844961243, 8449612.790697673, 0.0,
                                     9999225.193798449,
                                     "prop: 0.310,vola: 0.0215, price(7410000.0) > mas([7390000.0,7386200.0,7392600.0,7371600.0])")
        sell_trade_result_eth = Trade(True, 'SELL', '2018-10-04T05:59:00', 'KRW-ETH', 1535110.4227644398, 7348000.0,
                                      0.20901991860988195, 767.9391809727063, 3085498.407260564, 9984723.213462112,
                                      -14501.98033633572, 9973289.925757775,
                                      ", price(7348000.0) < mas([7361000.0,7358600.0,7378800.0,7361700.0]")

        tm = NettingTradeMgr(Operation_Type.LIVE_TRADING)
        tm.initialize(['KRW-BTC','KRW-ETH'])
        tm.handle_buy_position(buy_trade_result_btc)
        tm.handle_sell_position(sell_trade_result_btc)
        tm.handle_buy_position(buy_trade_result_eth)
        # tm.handle_sell_position(sell_trade_result_eth)


    def test_trade_states_for_hedging(self):
        t1 = Trade(True, 'BUY', '2018-10-03T07:59:00', 'KRW-BTC', 1549612.4031007756, 7410000.0, 0.2091244808503071, 774.8062015503878, 1550387.9844961243, 8449612.790697673, 0.0, 9999225.193798449,"prop: 0.310,vola: 0.0215, price(7410000.0) > mas([7390000.0,7386200.0,7392600.0,7371600.0])")
        t2 = Trade(True, 'SELL', '2018-10-04T07:59:00', 'KRW-BTC', 1535110.4227644398, 7348000.0, 0.20901991860988195, 767.9391809727063, 3085498.407260564, 9984723.213462112, -14501.98033633572, 9973289.925757775,", price(7348000.0) < mas([7361000.0,7358600.0,7378800.0,7361700.0]")
        t3 = Trade(True, 'BUY', '2018-10-05T08:59:00', 'KRW-BTC', 1663288.5396351102, 7459000.0, 0.22299082177706264,831.6442698175551, 1664121.0159652275, 8320603.029557185, 0.0, 9983891.958529796,"prop: 0.362,vola: 0.0184, price(7459000.0) > mas([7394666.7,7382200.0,7364900.0,7354000.0])")
        t4 = Trade(True, 'BUY', '2018-10-05T07:59:00', 'KRW-BTC', 1663288.5396351102, 7464000.0, 0.2228414442169226,831.6442698175551, 0.8320602998137474, 6656482.845652258, 0.0, 9985513.214501994,"prop: 0.362,vola: 0.0184, price(7464000.0) > mas([7407333.3,7396400.0,7376600.0,7375750.0])")
        t5 = Trade(True, 'BUY', '2018-10-06T23:59:00', 'KRW-ETH', 649722.0481040198, 257500.0, 2.523192419821436,324.86102405200995, 650047.2341516075, 6006435.936524186, 0.0, 9980729.582005668,"prop: 0.130,vola: 0.0512, price(257500.0) > mas([252700.0,254500.0,253690.0,253062.5])")
        t6 = Trade(True, 'BUY', '2018-10-07T08:59:00', 'KRW-ETH', 649722.2105345317, 255350.0, 2.5444378716840874,324.8611052672659, 0.16251180844847113, 5356388.864884388, 0.0, 9979076.796096789,"prop: 0.176,vola: 0.0378, price(255350.0) > mas([254166.7,253760.0,253600.0,251710.0])")
        t7 = Trade(True, 'SELL', '2018-10-07T23:59:00', 'KRW-BTC', 1655165.3982032235, 7430000.0, 0.22287932636617414,827.9966974503369, 1655166.2302635233, 7011554.263087612, -8123.141431886703, 9979778.931553029,", price(7430000.0) < mas([7460333.3,7423400.0,7393200.0,7370000.0]")
        t8 = Trade(True, 'SELL', '2018-10-07T23:59:00', 'KRW-ETH', 642590.8208762491, 252800.0, 2.5431656527482454,321.4561385073782, 642590.9833880576, 7654145.083963861, -7131.389658282627, 9972326.085756239,", price(252800.0) < mas([254350.0,254150.0,254300.0,252315.0]")

        timeframes = ['07:59','05:59', '01:59', '08:59', '23:59']
        tm = HedgingTradeMgr(Operation_Type.LIVE_TRADING)
        tm.initialize(['KRW-BTC','KRW-ETH'], timeframes)
        trades = [t1, t2, t3, t4,t5,t6,t7,t8]
        for trade in trades:
            exp_timeframe_dt = str2dt(trade.date)
            prefix = '0' if exp_timeframe_dt.hour < 10 else ''
            exp_timeframe = f'{prefix}{exp_timeframe_dt.hour}:59'
            if trade.order == 'BUY':
                tm.handle_buy_position(trade, exp_timeframe)
            else:
                tm.handle_sell_position(trade, exp_timeframe)


if __name__ == '__main__':
    unittest.main()

