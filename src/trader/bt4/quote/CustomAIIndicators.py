import pandas as pd
import torch

from bt4.ai.tasks.task_context import AITaskContextCache
from bt4.ai.utils.tool import calculate_slope, select_prediction_length
from bt4.Constants import CandleType
from bt4.utils.mylog import init_log

log = init_log()


def __ai__forecasting_dlinear(*args, **kwargs):
    close = args[0]

    user_selected_length = args[1]
    pred_len = select_prediction_length(user_selected_length)

    candle_type = args[-2]
    dfs = args[-1]

    market_df = dfs[candle_type]
    market = market_df["market"].iloc[0]

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    forecasting_context = AITaskContextCache.get_or_create_context(
        ex_type="upbit",
        market=market,
        model_name="DLinear",
        task_type="forecasting",
        candle_type=CandleType(candle_type).name,
        pred_len=pred_len,
        device=device,
    )

    if len(close) < forecasting_context.args.seq_len:
        return [pd.Series(0), pd.Series(0)]

    predictions, slope = forecasting_context.execute(market_df)

    if 1 < user_selected_length < pred_len:
        predictions = predictions[:user_selected_length]
        slope = calculate_slope(predictions=predictions)

    return [pd.Series(predictions[-1]), pd.Series(slope)]
