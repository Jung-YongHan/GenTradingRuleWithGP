import pickle
from abc import ABC, abstractmethod

import pandas as pd
import torch
import torch.nn as nn

from bt4.ai.args.base_args import BaseArgs
from bt4.ai.utils.time_features import time_features
from bt4.ai.utils.tool import calculate_slope
from bt4.model.storage_mgr import StrategyStorage
from bt4.model.trade_model import AIModel


class TaskStrategy(ABC):
    def __init__(self, args: BaseArgs) -> None:
        self.args = args
        self.model = self._build_model().to(args.device)
        self.scaler = self._load_scaler()

    @abstractmethod
    def _build_model(self):
        pass

    def _load_scaler(self):
        return None

    @abstractmethod
    def perform_task(self, **kwargs):
        pass


class ForecastingTask(TaskStrategy):
    def __init__(self, ex_type: str, market: str, model_class: nn.Module, args: BaseArgs, **kwargs):
        self.ex_type = ex_type
        self.market = market
        self.model_class = model_class
        self.args = args

        self.candle_type = self.args.candle_type
        self.seq_len = self.args.seq_len
        self.pred_len = self.args.pred_len
        self.label_len = self.args.label_len
        self.task_name = self.args.task_name
        self.freq = self.args.freq

        super().__init__(args)

    def _build_model(self):
        model: nn.Module = self.model_class(self.args)

        self.ai_model: AIModel = StrategyStorage.instance().load_ai_model(
            ex_type=self.ex_type,
            market=self.market,
            category=self.task_name,
            candle_type=self.candle_type,
            model=model.__class__.__name__,
            pred_len=self.pred_len,
        )

        state_dict = {k: torch.tensor(v) for k, v in pickle.loads(self.ai_model.saved_model).items()}
        model.load_state_dict(state_dict)
        model.eval()

        return model

    def _load_scaler(self):
        return self.ai_model.saved_scaler

    def _prepare_data(self, market_data: pd.DataFrame):
        """
        Prepare the input data and corresponding time features for the forecasting model.

        Args:
            market_data (pd.DataFrame): The raw market data.

        Returns:
            Tuple[pd.DataFrame, torch.Tensor]: The prepared data and time features.
        """
        # Select the necessary sequence length from the market data
        df_seq = market_data.iloc[-self.seq_len :].copy()
        df_seq["datetime"] = pd.to_datetime(df_seq.index)

        # Generate future timestamps for the prediction horizon
        future_dates = pd.date_range(df_seq["datetime"].max(), periods=self.pred_len + 1, freq=self.freq)[1:]
        df_future = pd.DataFrame({"datetime": future_dates})

        # Combine historical data with future dates
        df_combined = pd.concat([df_seq, df_future]).reset_index(drop=True)

        # Generate time features
        time_stamps = time_features(pd.to_datetime(df_combined["datetime"].values), freq=self.freq)
        time_stamps = torch.tensor(time_stamps.transpose(1, 0), dtype=torch.float32).to(self.args.device)

        return df_combined, time_stamps

    def perform_task(self, market_data: pd.DataFrame):
        """
        Perform the forecasting task on the provided market data.

        Args:
            market_data (pd.DataFrame): The market data on which to perform the forecasting task.

        Returns:
            np.ndarray: The model's predictions on the original scale.
        """
        prepared_data, time_stamps = self._prepare_data(market_data)

        # Apply scaler to the input data
        encoded_input = self.scaler.transform(prepared_data["close"][: self.seq_len].values.reshape(-1, 1))

        # Convert to torch tensors
        encoded_input = torch.tensor(encoded_input, dtype=torch.float32).unsqueeze(0).to(self.args.device)

        # Perform forecasting using the model
        predictions = self.model_forward(encoded_input, time_stamps)

        # Inverse transform to get the original scale
        predictions_original_scale = self.scaler.inverse_transform(predictions.cpu().numpy().reshape(-1, 1)).flatten()

        slope = self.calculate_trend(predictions_original_scale)

        return predictions_original_scale, slope

    def model_forward(self, x_enc: torch.Tensor, x_enc_mark: torch.Tensor):
        """
        Forward pass through the model with the encoded inputs and time features.

        Args:
            x_enc (torch.Tensor): Encoded input data.
            x_enc_mark (torch.Tensor): Time features for the input data.

        Returns:
            torch.Tensor: The model's output predictions.
        """
        with torch.no_grad():
            predictions = self.model(x_enc=x_enc, x_mark_enc=x_enc_mark, x_dec=None, x_mark_dec=None)

        return predictions

    def calculate_trend(self, predictions):
        slope = calculate_slope(predictions=predictions)

        return slope
