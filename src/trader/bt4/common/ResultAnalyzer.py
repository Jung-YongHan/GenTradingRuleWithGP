import math

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from bt4.Constants import R
from bt4.core.ReportSupport import FileReportStorage
from bt4.utils.mylog import init_log

pd.set_option("display.max_columns", None)
pd.set_option("display.expand_frame_repr", False)
pd.set_option("max_colwidth", None)


log = init_log()


def extract_year_month_balance(df_group, column_name):
    agg_df1 = pd.DataFrame()
    if column_name == "start_bal":
        agg_df1[column_name] = df_group.head(1)[column_name]
    elif column_name == "end_bal":
        agg_df1[column_name] = df_group.tail(1)[column_name]
    agg_df1["year"] = agg_df1.index.year
    agg_df1["month"] = agg_df1.index.month
    agg_df1["year-month"] = agg_df1["year"].map(str) + "-" + agg_df1["month"].map(str)
    agg_df1.set_index("year-month", inplace=True)
    agg_df1.drop(["year", "month"], axis=1, inplace=True)
    return agg_df1


def compute_monthly_profit_ratio_and_sharp_index(df):
    eval_columns = set(df.columns) - set(["evaluated_balance", "date"])
    df = df.drop(list(eval_columns), axis=1)
    df = df.rename(columns={"evaluated_balance": "end_bal"})
    df["start_bal"] = df["end_bal"].shift(1)
    df["start_bal"] = df["start_bal"].bfill()
    # df["start_bal"].iloc[0] = df["end_bal"].iloc[0]

    df.index = pd.to_datetime(df["date"], format="mixed")
    daily_shape_index = compute_shape_ratio_using_daily_profit(df)

    df_group = df.groupby(by=[df.index.year, df.index.month], as_index=False)
    agg_df1 = extract_year_month_balance(df_group, "start_bal")
    agg_df2 = extract_year_month_balance(df_group, "end_bal")
    # agg_df1 = extract_year_month_balance(pd.concat(map(lambda x: x[1], df_group)), 'start_bal')
    # agg_df2 = extract_year_month_balance(pd.concat(map(lambda x: x[1], df_group)), 'end_bal')

    agg_df = pd.concat([agg_df1, agg_df2], axis=1)
    agg_df["profit"] = agg_df["end_bal"] - agg_df["start_bal"]

    agg_df["profit_ratio_1"] = (agg_df["profit"] / agg_df["start_bal"]) + 1

    annualized_shape_index = compute_shape_ratio_using_monthly_profit(agg_df)
    # monthly_compound_interest = agg_df["profit_ratio_1"].prod() ** (1 / agg_df.shape[0]) - 1
    # profit_std_dev = agg_df["profit_ratio_1"].std()

    monthly_compound_interest = (agg_df["profit_ratio_1"].prod() ** (1 / agg_df.shape[0]) - 1)*12
    profit_std_dev = agg_df["profit_ratio_1"].std()*math.sqrt(12)

    # sharp_index = monthly_compound_interest / profit_std_dev
    # return monthly_compound_interest, profit_std_dev, annualized_shape_index
    return monthly_compound_interest, profit_std_dev, daily_shape_index

def compute_shape_ratio_using_monthly_profit(profit_df):
    sharpe_ratio_annualized = 0
    if len(profit_df) > 0:
        stdev = np.std(profit_df['profit'])
        if stdev != np.nan and stdev != 0.0:
            sharpe_ratio = np.mean(profit_df['profit']) / stdev
            annual_factor = np.sqrt(12)
            sharpe_ratio_annualized = sharpe_ratio * annual_factor
    return sharpe_ratio_annualized

def compute_shape_ratio_using_daily_profit(profit_df):
    profit_df['profit'] = (profit_df['end_bal'] - profit_df['start_bal']) / profit_df['start_bal']
    if np.std(profit_df['profit']) != 0:
        sharpe_ratio = np.mean(profit_df['profit']) / np.std(profit_df['profit'])
    else:
        sharpe_ratio = 0
    annual_factor = np.sqrt(365)
    sharpe_ratio_annualized = sharpe_ratio * annual_factor
    return sharpe_ratio_annualized


def __store_rs(rs, key_results, key, text, value):
    if isinstance(rs, FileReportStorage):
        rs.store(text)
    key_results[key] = value


def perform_basic_stats(df, market=None):
    sell_df = df[df.order == "SELL"].copy(deep=True)
    num_of_trades = len(sell_df)
    market_stat_dic = {}
    market_stat_dic["market"] = [market]
    market_stat_dic["num_of_trades"] = [num_of_trades]

    if num_of_trades > 0:
        win_trade_df = sell_df.loc[sell_df.profit > 0]
        lose_trade_df = sell_df.loc[sell_df.profit <= 0]
        num_of_wins = len(win_trade_df)
        num_of_loses = len(lose_trade_df)
        win_rate = num_of_wins / num_of_trades

        # sell_df["invest_total"] = sell_df["emarket_bal"] - sell_df["profit"]
        sell_df["invest_total"] = sell_df["evaluated_market_balance"] - sell_df["profit"]
        sell_df["profit_ratio"] = sell_df["profit"] / sell_df["invest_total"]

        profit_sum = round(sell_df["profit"].sum(), 2)
        profit_std = round(sell_df["profit"].std(), 2)
        invest_sum = round(sell_df["invest_total"].sum(), 2)
        num_1_pcnt = round(len(sell_df.loc[sell_df["profit_ratio"] > 0.01]) / num_of_trades, 3)
        num_2_pcnt = round(len(sell_df.loc[sell_df["profit_ratio"] > 0.02]) / num_of_trades, 3)
        num_3_pcnt = round(len(sell_df.loc[sell_df["profit_ratio"] > 0.03]) / num_of_trades, 3)
        num_5_pcnt = round(len(sell_df.loc[sell_df["profit_ratio"] > 0.05]) / num_of_trades, 3)
        avg_profit_ratio = round(profit_sum / invest_sum, 3)

        market_stat_dic["profit_sum"] = [profit_sum]
        market_stat_dic["invest_sum"] = [invest_sum]
        market_stat_dic["avg_profit_ratio"] = [avg_profit_ratio]
        market_stat_dic["profit_std"] = [profit_std]
        market_stat_dic["num_1_pcnt"] = [num_1_pcnt]
        market_stat_dic["num_2_pcnt"] = [num_2_pcnt]
        market_stat_dic["num_3_pcnt"] = [num_3_pcnt]
        market_stat_dic["num_5_pcnt"] = [num_5_pcnt]
        market_stat_df = pd.DataFrame(market_stat_dic, index=[market])
    else:
        win_rate = 0.0
        num_of_wins = 0
        num_of_loses = 0
        profit_sum = 0
        invest_sum = 0
        profit_std = 0
        avg_profit_ratio = 0
        num_1_pcnt = 0
        num_2_pcnt = 0
        num_3_pcnt = 0
        num_5_pcnt = 0

        market_stat_dic["profit_sum"] = [0]
        market_stat_dic["invest_sum"] = [0]
        market_stat_dic["avg_profit_ratio"] = [0]
        market_stat_dic["profit_std"] = [0]
        market_stat_dic["num_1_pcnt"] = [0]
        market_stat_dic["num_2_pcnt"] = [0]
        market_stat_dic["num_3_pcnt"] = [0]
        market_stat_dic["num_5_pcnt"] = [0]
        market_stat_df = pd.DataFrame(market_stat_dic, index=[market])

    def compute_timeframe_profits(timeframe_sell_df):
        if len(timeframe_sell_df) == 0 and timeframe_sell_df.empty:
            return "", 0, 0, 0, 0.0, 0.0, 0, 0, 0.0

        hour = pd.to_datetime(timeframe_sell_df.head(1).date).dt.hour.values[0]
        minute = pd.to_datetime(timeframe_sell_df.head(1).date).dt.minute.values[0]
        tf_key = f"{hour}:{minute}"
        n_tf_trades = len(timeframe_sell_df)

        win_df = timeframe_sell_df[timeframe_sell_df.profit > 0]
        sum_of_win_profit = np.round(sum(win_df.profit), decimals=2)

        lose_df = timeframe_sell_df[timeframe_sell_df.profit <= 0]
        sum_of_lose_profit = np.round(sum(lose_df.profit), decimals=2)

        winning_rate = np.round(len(win_df) / n_tf_trades * 100, decimals=2)
        prop_of_trades_of_timeframe = np.round(n_tf_trades / num_of_trades * 100, decimals=2)

        if sum_of_lose_profit != 0:
            prop_of_win_lose_profits = np.round(sum_of_win_profit / abs(sum_of_lose_profit), decimals=2)
        else:
            prop_of_win_lose_profits = 0

        return (
            tf_key,
            n_tf_trades,
            len(win_df),
            len(lose_df),
            winning_rate,
            prop_of_trades_of_timeframe,
            sum_of_win_profit,
            sum_of_lose_profit,
            prop_of_win_lose_profits,
        )

    date_col = pd.to_datetime(sell_df.date)
    tf_perf_measure_df = pd.DataFrame()
    # TODO: measuring performance of each hourly-timeframe,
    #       There is an error when num of trades < 1, need to repair
    #       This is not generally used for measuring strategy's performance. Thus, it is postponded later.
    # tf_perf_measure_df['timeframe'], tf_perf_measure_df['trades'],tf_perf_measure_df['wins'],tf_perf_measure_df['loses'], \
    # tf_perf_measure_df['win_rate'],tf_perf_measure_df['tf/trades'],tf_perf_measure_df['win profit'],tf_perf_measure_df['lose profit'], \
    # tf_perf_measure_df['win/lose profits'] = zip(*sell_df.groupby([date_col.dt.hour, date_col.dt.minute]).apply(compute_timeframe_profits))
    # tf_perf_measure_df.set_index(['timeframe'])
    # # print(result_df.head(24))
    # tf_perf_measure_df['sum_profit'] = tf_perf_measure_df['win profit'] + tf_perf_measure_df['lose profit']
    # sum_profit = sum(tf_perf_measure_df['sum_profit'])
    # sort_df(tf_perf_measure_df, 'win/lose profits', ascending=False)

    return TradeStats(
        win_rate,
        num_of_trades,
        num_of_wins,
        num_of_loses,
        tf_perf_measure_df,
        profit_sum,
        invest_sum,
        profit_std,
        avg_profit_ratio,
        num_1_pcnt,
        num_2_pcnt,
        num_3_pcnt,
        num_5_pcnt,
        market_stat_df,
    )


def store_rs_of_trade_stats(report_storage, key_results, ts, market=None):
    def __key(key, market=None):
        return key if market == None else f"{market}-{key}"

    idnt = "  " if market == None else "    "
    key_twr = __key("trade_win_rate", market)
    if market == None:
        __store_rs(
            report_storage,
            key_results,
            key_twr,
            f"## Winning rate of trades : {ts.win_rate:.2f}",
            f"{ts.win_rate:.2f}",
        )
    else:
        __store_rs(
            report_storage,
            key_results,
            key_twr,
            f"#### {key_twr} : {ts.win_rate:.4f}",
            f"{ts.win_rate}",
        )

    key_not = __key("num_of_trades", market)
    __store_rs(
        report_storage,
        key_results,
        key_not,
        f"{idnt}{key_not}: {ts.num_of_trades}",
        f"{ts.num_of_trades}",
    )

    key_now = __key("num_of_wins", market)
    __store_rs(
        report_storage,
        key_results,
        key_now,
        f"{idnt}{key_now}: {ts.num_of_wins}",
        f"{ts.num_of_wins}",
    )

    key_nol = __key("num_of_loses", market)
    __store_rs(
        report_storage,
        key_results,
        key_nol,
        f"{idnt}{key_nol}: {ts.num_of_loses}",
        f"{ts.num_of_loses}",
    )

    key_pfs = __key("profit_sum", market)
    __store_rs(
        report_storage,
        key_results,
        key_pfs,
        f"{idnt}{key_pfs}: {ts.profit_sum}",
        f"{ts.profit_sum}",
    )

    key_ivs = __key("invest_sum", market)
    __store_rs(
        report_storage,
        key_results,
        key_ivs,
        f"{idnt}{key_ivs}: {ts.invest_sum}",
        f"{ts.invest_sum}",
    )

    key_apr = __key("avg_profit_ratio", market)
    __store_rs(
        report_storage,
        key_results,
        key_apr,
        f"{idnt}{key_apr} : {ts.avg_profit_ratio}",
        f"{ts.avg_profit_ratio}",
    )

    key_n1p = __key("num_1_pcnt", market)
    __store_rs(
        report_storage,
        key_results,
        key_n1p,
        f"{idnt}{key_n1p} : {ts.num_1_pcnt}",
        f"{ts.num_1_pcnt}",
    )

    key_n2p = __key("num_2_pcnt", market)
    __store_rs(
        report_storage,
        key_results,
        key_n2p,
        f"{idnt}{key_n2p} : {ts.num_2_pcnt}",
        f"{ts.num_2_pcnt}",
    )

    key_n3p = __key("num_3_pcnt", market)
    __store_rs(
        report_storage,
        key_results,
        key_n3p,
        f"{idnt}{key_n3p} : {ts.num_3_pcnt}",
        f"{ts.num_3_pcnt}",
    )

    key_n5p = __key("num_5_pcnt", market)
    __store_rs(
        report_storage,
        key_results,
        key_n5p,
        f"{idnt}{key_n5p} : {ts.num_5_pcnt}",
        f"{ts.num_5_pcnt}",
    )


def compute_2x_duration(stat_df):
    e_bal_df = stat_df[["date", "evaluated_balance"]]
    e_bal_df = e_bal_df.set_index(["date"], drop=True)
    e_bal_df.index = pd.to_datetime(e_bal_df.index, format="mixed")
    e_bal_df["next0"] = e_bal_df.index
    e_bal_df["next"] = e_bal_df["next0"].shift(-1)
    e_bal_df = e_bal_df.bfill()

    try:
        init_balance = int(e_bal_df.head(1)["evaluated_balance"].iloc[0].item())
    except ValueError:
        init_balance = 0

    try:
        last_balance = int(e_bal_df.tail(1)["evaluated_balance"].iloc[0].item())
    except ValueError:
        last_balance = 0

    durations = []
    interval_start = e_bal_df.head(1)["evaluated_balance"].index.strftime("%Y-%m-%d").values[0]
    interval_end = None
    next_range_end = init_balance

    def compute_2x0(row):
        nonlocal durations
        nonlocal interval_start
        nonlocal interval_end
        nonlocal next_range_end

        if row["evaluated_balance"] >= next_range_end * 2:
            interval_end = row["next0"].strftime("%Y-%m-%d")
            interval_end_bal = row["evaluated_balance"]

            period = len(pd.date_range(interval_start, interval_end, freq="1D"))
            if period > 0:
                pft_times = round(interval_end_bal / init_balance, 2)

                if len(durations) == 0:
                    period_str = f"{period}[x{pft_times}]({interval_start}~{interval_end})"
                else:
                    period_str = f"{period}[x{pft_times}](~{interval_end})"
                durations.append(period_str)

            interval_start = row["next"]
            next_range_end = next_range_end * 2
        else:
            try:
                e_balance = int(row["evaluated_balance"])
            except ValueError:
                e_balance = 0
            if e_balance == last_balance:
                interval_end = row["next0"].strftime("%Y-%m-%d")
                period = len(pd.date_range(interval_start, interval_end, freq="1D"))
                interval_end_bal = last_balance
                pft_times = round(interval_end_bal / init_balance, 2)
                period_str = f"{period}[x{pft_times}](~{interval_end})"
                durations.append(period_str)

    if init_balance == last_balance:
        interval_end = e_bal_df.tail(1)["evaluated_balance"].index.strftime("%Y-%m-%d").values[0]
        period = len(pd.date_range(interval_start, interval_end, freq = "1D"))
        pft_times = 1
        period_str= f"{period}[x{pft_times}]({interval_start}~{interval_end})"
        durations.append(period_str)
    else:
        e_bal_df.apply(compute_2x0, axis=1, args=())

    return durations


def analyze_result(df: pd.DataFrame, desc: str, context, report_storage, save_plot=False):

    r = R()
    config_params = None
    if context is not None:
        config_params = context.ctx_params

    key_results = {}
    # TODO: SETT 없을 시 처리

    stat_df = df.loc[(df.order == "SETT")].copy()
    stat_df_len = len(stat_df)

    #####################################################################
    ## MDD
    if stat_df_len != 0:
        stat_df["date2"] = stat_df["date"]
        def rowIndex(row):
            return row.name

        stat_df["rowIndex"] = stat_df.apply(rowIndex, axis=1)
        stat_df["mdd"] = -1

        def compute_mdd(row):
            if row.rowIndex <= 0:
                return
            previous_high = stat_df.loc[0: row.rowIndex].evaluated_balance.max()
            current = stat_df.loc[row.rowIndex].evaluated_balance
            # dd = ((current - previous_high) / previous_high ) * 100
            dd = (current / previous_high - 1) * 100
            return dd

        stat_df["mdd"] = stat_df.apply(compute_mdd, axis="columns")
        mdd = stat_df.mdd.min()
    else:
        mdd = 0
    ####################################################################################################
    ## s_period setting
    s_period = None
    if config_params is not None:
        s_period = f"{config_params[r.OP.BT.START]} ~ {config_params[r.OP.BT.END]}"
        bt_end = config_params[r.OP.BT.END]
        __store_rs(
            report_storage,
            key_results,
            "bt_end",
            f"## bt_end: {bt_end}", bt_end,
        )
    else:
        if stat_df_len != 0:
            s_period = f"{stat_df.date2.iloc[0]} ~ {stat_df.date2.iloc[-1]}"
        else:
            if len(df) != 0:
                s_period = f"{df['date'].iloc[0]} ~ {df['date'].iloc[-1]}"
            else:
                s_period = ""

    __store_rs(
        report_storage,
        key_results,
        "s_period",
        f"## Simulation period: {s_period}",s_period,
    )

    ####################################################################################################
    ## market setting
    market = None
    if config_params is not None:
        markets = list(config_params[r.OP.MARKET])
    else:
        markets = [item for item in df["market"].unique().tolist() if item not in ["SETT"]]

    if len(markets) > 0:
        markets_str = ",".join(markets)
        if isinstance(report_storage, FileReportStorage):
            report_storage.store(f"  markets:{markets_str}")

        __store_rs(
            report_storage,
            key_results,
            "markets",
            f"  markets:{markets_str}", markets_str)

    ####################################################################################################
    ## init_bal,last_bal,max_val  setting
    if stat_df_len != 0:
        init_bal = stat_df.evaluated_balance.iloc[0]
        last_bal = stat_df.evaluated_balance.iloc[-1]
        max_val = stat_df.evaluated_balance.max()
    else:
        if len(df) != 0:
            init_bal = df.head(1)["evaluated_balance"].item()
            last_bal = df.tail(1)["evaluated_balance"].item()
            max_val = df["evaluated_balance"].max()
        else:
            init_bal = 0
            last_bal = 0
            max_val = 0

    __store_rs(
        report_storage,
        key_results,
        "last_bal",
        f"## Last Balance: {last_bal:.2f} ({last_bal/init_bal:.2f} Times)",
        f"{last_bal:.2f}",
    )
    __store_rs(
        report_storage,
        key_results,
        "max_bal",
        f"  max: {max_val:.2f} ({max_val/init_bal:.2f} Times)",
        f"{max_val:.2f}",
    )
    __store_rs(
        report_storage,
        key_results,
        "init_bal",
        f"  init Balance: {init_bal}",
        f"{init_bal}",
    )

    ####################################################################################################
    ## Strategy Statistics (TODO: Remove Selection Index)
    selection_index = math.log(last_bal, 10) * (((100 + mdd) ** 3) / 100**3)
    __store_rs(
        report_storage,
        key_results,
        "selection_index",
        f"  selection index: {selection_index}",
        f"{selection_index}",
    )

    #####################################################################
    ## trade_win_rate
    ts = perform_basic_stats(df)
    store_rs_of_trade_stats(report_storage, key_results, ts)

    #####################################################################
    ## Market trade_win_rate
    df_group = df.groupby(by=["market"], as_index=False)
    for market in df_group.groups:
        if market != "SETT":
            idx = df_group.groups[market]
            market_df = df.iloc[idx, :]
            ts = perform_basic_stats(market_df, market)
            store_rs_of_trade_stats(report_storage, key_results, ts, market)

    #####################################################################
    ## Win/Lose Rate of Settles
    winning_df = stat_df.loc[stat_df["profit"] > 0]
    lose_df = stat_df.loc[stat_df["profit"] < 0]
    len_win = len(winning_df)
    len_lose = len(lose_df)
    winning_rate = 0 if len_win == 0 and len_lose == 0 else len_win/(len_win + len_lose)
    __store_rs(
        report_storage,
        key_results,
        "settle_winning_rate",
        f"## Winning rate of settles: {winning_rate:.2f}",
        f"{winning_rate:.2f}",
    )
    __store_rs(
        report_storage,
        key_results,
        "settle_total_trade",
        f"  Settle Total Trade: {len_win + len_lose}",
        f"{len_win + len_lose}",
    )
    __store_rs(
        report_storage,
        key_results,
        "settle_winning",
        f"  winning: {len_win}",
        f"{len_win}",
    )
    __store_rs(
        report_storage,
        key_results,
        "settle_lose",
        f"  lose: {len_lose}",
        f"{len_lose}")

    __store_rs(
        report_storage,
        key_results,
        "mdd",
        f"## MDD: {mdd:.2f} %",
        f"{mdd:.2f}",
    )
    try:
        if stat_df_len != 0:
            _mdd_10 = stat_df.mdd.map(lambda mdd_: mdd_ < -10).sum()
            _mdd_20 = stat_df.mdd.map(lambda mdd_ : mdd_ < -20).sum()
        else:
            _mdd_10 = 0
            _mdd_20 = 0

        __store_rs(report_storage, key_results, "mdd_10", f"  under 10%: {_mdd_10}", f"{_mdd_10}")
        __store_rs(report_storage, key_results, "mdd_20", f"  under 20%: {_mdd_20}", f"{_mdd_20}")
    except TypeError:
        _mdd_10 = None
        _mdd_20 = None

    _2x_duration = ""
    if stat_df_len != 0:
        _2x_duration = compute_2x_duration(stat_df)

    __store_rs(
        report_storage,
        key_results,
        "2xdur",
        f"## 2x durations: {_2x_duration}",
        f"{_2x_duration}",
    )

    #####################################################################
    ## compute MPR and Shape Index
    if stat_df_len != 0:
        (
            monthly_profit_ratio,
            profit_std,
            sharp_index,
        ) = compute_monthly_profit_ratio_and_sharp_index(stat_df)
    else:
        monthly_profit_ratio = 0
        profit_std = 0
        sharp_index = 0

    __store_rs(
        report_storage,
        key_results,
        "mpr",
        f" monthly_profit_ratio: {monthly_profit_ratio*100:3.3f}%",
        f"{monthly_profit_ratio*100:3.3f}",
    )
    __store_rs(
        report_storage,
        key_results,
        "profit_std",
        f" profit_std: {profit_std * 100:3.3f}%",
        f"{profit_std * 100:3.3f}",
    )
    __store_rs(
        report_storage,
        key_results,
        "sharp_index",
        f" sharp_index: {sharp_index:.4f}",
        f"{sharp_index:.4f}",
    )


    report_storage.set_key_results(key_results)

    def plot_seaborn(desc, stat_df):
        fig = plt.figure()
        fig.suptitle("Trade Summary", fontsize=12)
        ax1 = fig.add_subplot(2, 1, 1)
        stat_df["date2"] = pd.to_datetime(stat_df["date2"], format="mixed").dt.strftime("%Y-%m-%d")
        # stat_df['date2'] = stat_df['date2'].dt.strftime('%Y-%m-%d')
        ax1.plot(stat_df.date2, stat_df.evaluated_balance, marker=".")
        ax1.set_title("Balance")

        # ax1.get_title().set_visible(False) ##

        y_base = stat_df.head(1)["evaluated_balance"].item()

        ax1.set_xlabel("Date")
        ax1.xaxis.set_major_locator(mdates.DayLocator(interval=5))
        ax1.tick_params(labelrotation=45)
        ax1.set_ylim(
            [
                stat_df.evaluated_balance.min() * 0.9,
                stat_df.evaluated_balance.max() * 1.2,
            ]
        )
        # ax1.set_xticks(rotation=90)
        ax1.axhline(y=3 * y_base, color="gray", linestyle="--")
        ax1.axhline(y=2 * y_base, color="gray", linestyle="--")
        ax1.axhline(y=y_base, color="black", linestyle="-")
        ax1.axhline(y=-1 * y_base, color="red", linestyle="--")
        ax1.set_ylabel("Balance")
        ax1.get_xaxis().set_visible(False)

        if stat_df["mdd"].isnull().values.any():
            ax2 = fig.add_subplot(2, 1, 2)
            # ax2.plot(stat_df.date2, stat_df['mdd'], marker="o")
            ax2.bar(
                stat_df.date2,
                stat_df["mdd"],
                0.5,
                alpha=0.4,
                color="b",
                error_kw={"ecolor": "0.3"},
            )
            ax2.set_title("MDD")
            ax2.set_xlabel("Date")
            ax2.xaxis.set_major_locator(mdates.DayLocator(interval=5))
            ax2.tick_params(labelrotation=45)
            # ax2.set_xticks(rotation=90)
            ax2.set_ylabel("MDD(%)")
            ax2.axhline(y=0, color="black", linestyle="-")
            ax2.axhline(y=-10, color="red", linestyle="--")
            ax2.axhline(y=-20, color="red", linestyle="--")

        # fig.tight_layout()

        if report_storage.is_visualize_support():
            plt.show()

        # if save_plot:
        #     plt.savefig("static/__profit_mdd_graph.jpg", bbox_inches="tight")
        #     plt.close("all")

    if report_storage.is_visualize_support() or save_plot:
        plot_seaborn(desc, stat_df)
        # Visualizer(df, desc).visualize()

    # report_storage.close()


class TradeStats:
    def __init__(
        self,
        win_rate,
        num_of_trades,
        num_of_wins,
        num_of_loses,
        tf_perf_measure_df,
        profit_sum,
        invest_sum,
        profit_std,
        avg_profit_ratio,
        num_1_pcnt,
        num_2_pcnt,
        num_3_pcnt,
        num_5_pcnt,
        market_stat_df,
    ):
        self.__win_rate = win_rate
        self.__num_of_trades = num_of_trades
        self.__num_of_wins = num_of_wins
        self.__num_of_loses = num_of_loses
        self.__tf_perf_measure_df = tf_perf_measure_df
        self.__profit_sum = profit_sum
        self.__invest_sum = invest_sum
        self.__profit_std = profit_std
        self.__avg_profit_ratio = avg_profit_ratio
        self.__num_1_pcnt = num_1_pcnt
        self.__num_2_pcnt = num_2_pcnt
        self.__num_3_pcnt = num_3_pcnt
        self.__num_5_pcnt = num_5_pcnt
        self.__market_stat_df = market_stat_df

    @property
    def win_rate(self):
        return self.__win_rate

    @property
    def num_of_trades(self):
        return self.__num_of_trades

    @property
    def num_of_wins(self):
        return self.__num_of_wins

    @property
    def num_of_loses(self):
        return self.__num_of_loses

    @property
    def tf_perf_measure_df(self):
        return self.__tf_perf_measure_df

    @property
    def profit_sum(self):
        return self.__profit_sum

    @property
    def invest_sum(self):
        return self.__invest_sum

    @property
    def profit_std(self):
        return self.__profit_std

    @property
    def avg_profit_ratio(self):
        return self.__avg_profit_ratio

    @property
    def num_1_pcnt(self):
        return self.__num_1_pcnt

    @property
    def num_2_pcnt(self):
        return self.__num_2_pcnt

    @property
    def num_3_pcnt(self):
        return self.__num_3_pcnt

    @property
    def num_5_pcnt(self):
        return self.__num_5_pcnt

    @property
    def market_stat_df(self):
        return self.__market_stat_df
