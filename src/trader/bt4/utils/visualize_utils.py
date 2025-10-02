import pandas
from plotly import graph_objects

from bt4.Constants import R, ExType, CandleType
from bt4.quote.QuoteMgr import QuoteStorageMgr
from bt4.utils.python_utils import load_class_from_module
from bt4.utils.bt4_cli_args import get_argument


def visualize_trades(result_file) :
    arg_map = get_argument()
    config_module = arg_map['config_module']

    from bt4.Constants import R
    r = R()
    params = {}

    config = load_class_from_module(config_module, 'Config')
    config.load_params(r, params)

    import plotly.graph_objects as go
    import pandas as pd

    markets = params[r.OP.MARKET]
    tgt_cdl = params[r.OP.BT.CANDLE_TYPE]
    cdl_types_needed = params[r.OP.BT.CDL_TYPES_NEEDED]

    try :
        cdl_types_needed.remove(CandleType.DAYS_TF)
    except ValueError :
        pass

    quote_storage = QuoteStorageMgr(markets, cdl_types_needed)
    quote_storage.initialize(ExType.upbit)
    simul_start = params[r.OP.BT.START]
    simul_end = params[r.OP.BT.END]
    start_pdt = pd.to_datetime(simul_start)
    fetch_start_pdt = start_pdt - pd.Timedelta(hours = 24 * 30)
    end_pdt = pd.to_datetime(simul_end)
    # df = pd.read_csv("../report/WSAlt_Price_Residual_Strategy_BeforeRefactoring_34252.csv", index_col = 0)
    trade_df = pd.read_csv(result_file, index_col = 0)
    # print(trade_df.head(10))

    markets = trade_df.loc[trade_df['market'] != "SETT"]["market"].unique()
    for market in markets :
        market_dfs = quote_storage.load_quote_in_range2(ExType.upbit, markets, fetch_start_pdt, end_pdt, tgt_cdl)[market]

        buy_date_str = trade_df.loc[(trade_df['order'] == "BUY") & (trade_df['market'] == market)]["date"]
        sell_date_str = trade_df.loc[(trade_df['order'] == "SELL") & (trade_df['market'] == market)]["date"]
        buy_date_ser = pd.to_datetime(buy_date_str)
        sell_date_ser = pd.to_datetime(sell_date_str)

        buy_date_ser = buy_date_ser - pd.Timedelta(minutes = tgt_cdl.value - 1)
        sell_date_ser = sell_date_ser - pd.Timedelta(minutes = tgt_cdl.value - 1)

        # print(buy_date_ser)
        # print(sell_date_ser)

        fig = go.Figure(data = [go.Candlestick(
            x = market_dfs.index,
            open = market_dfs['open'], high = market_dfs['high'],
            low = market_dfs['low'], close = market_dfs['close'],
            increasing_line_color = 'cyan', decreasing_line_color = 'gray')],
            layout = go.Layout(title = go.layout.Title(text = market))
        )

        fig.add_trace(go.Scatter(x = buy_date_ser, y = market_dfs.loc[buy_date_ser]['close'], mode = 'markers',
                                 marker = dict(size=15, color = "Red"), name = 'buy'))
        fig.add_trace(go.Scatter(x = sell_date_ser, y = market_dfs.loc[sell_date_ser]['close'], mode = 'markers',
                                 marker = dict(size=12,color = "Yellow"), name = 'sell'))

        fig.show()