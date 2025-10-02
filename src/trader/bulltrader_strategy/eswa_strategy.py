import argparse
import sys
from os.path import dirname
from pickle import load

import numpy as np
import pandas as pd
import torch

from bt4.Constants import CandleType
from bt4.utils.mylog import init_log
from bt4.utils.tai_utils import get_nary_tai, get_unary_tai
from bt4.strategy.Strategy import AbstractNettingStrategy
from stgy_lab._04_deeplearning.models.d_linear import DLinear
from stgy_lab._04_deeplearning.models.dilated_rnn import DilatedRNN
from stgy_lab._04_deeplearning.models.fed_former import FEDformer
from stgy_lab._04_deeplearning.models.light_ts import LightTS
from stgy_lab._04_deeplearning.models.lst_net import LSTNet
from stgy_lab._04_deeplearning.models.non_stationary_transformer import (
    NonStationaryTransformer,
)
from stgy_lab._04_deeplearning.models.sci_net import SCINet
from stgy_lab._04_deeplearning.models.times_net import TimesNet
from stgy_lab._04_deeplearning.utils.time_features import time_features

log = init_log()


class ESWAStrategyBase(AbstractNettingStrategy):
    def __init__(self):
        super(ESWAStrategyBase, self).__init__()
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        # self.device = torch.device('cpu')
        print(f"Use {self.device}")

        self.model_dict = {
            "DLinear": DLinear,
            "TimesNet": TimesNet,
            "Nonstationary_Transformer": NonStationaryTransformer,
            "LightTS": LightTS,
            "FEDformer": FEDformer,
            "SCINet": SCINet,
            "DilatedRNN": DilatedRNN,
            "LSTNet": LSTNet,
        }

    def setup(self, context):
        super(ESWAStrategyBase, self).setup(context)

    def __load_model__(self, model_class, model_path, args):
        model = model_class(args=args)
        state_dict = torch.load(model_path)
        model.load_state_dict(state_dict)
        model.to(self.device)
        model.eval()
        return model

    def __isBuySignal__(self, mkt_buy_tais, tmgr, market, price, time_dt):
        desc = "\r\n *[sws] = "
        buy_log = ""
        buy_log += desc + ",  "
        if self.is_use_tai:
            #################################################################
            if self.tai_macd_tf is None:
                macd_buy_signal = True
            else:
                macd = mkt_buy_tais[market][
                    "macd"
                ]  # [0]macd, [1] macd_signal, [2] macd_hist
                macd_buy_signal = False
                if macd[0] > macd[1]:
                    macd_buy_signal = True
                desc = f"\r\n *[macd] = {macd_buy_signal} :: macd({macd[0]}) > macd_sig({macd[1]})"
                # log.info(desc)
                buy_log += desc + ",  "
            #################################################################
            if self.tai_cci_tf is None:
                cci_buy_signal = True
            else:
                cci = mkt_buy_tais[market]["cci"]
                cci_buy_signal = False
                if cci > -100:
                    cci_buy_signal = True
                desc = f"\r\n *[cci] = {cci_buy_signal} :: cci({cci}) > 0"
                # log.info(desc)
                buy_log += desc + ",  "
            #################################################################
            if self.tai_bb_close_tf is None:
                bband_buy_signal = True
            else:
                bbands = mkt_buy_tais[market][
                    "bband"
                ]  # [0] upper, [1] middle, [2] lower
                bband_buy_signal = False
                if price > bbands[2]:
                    bband_buy_signal = True
                desc = f"\r\n *[bband] = {bband_buy_signal} :: price({price}) > bb_low({bbands[2]})"
                # log.info(desc)
                buy_log += desc + ",  "
            #################################################################
            if self.tai_rsi_tf is None:
                rsi_buy_signal = True
            else:
                rsi = mkt_buy_tais[market]["rsi"]
                rsi_buy_signal = False

                if rsi > 30:
                    rsi_buy_signal = True
                desc = f"\r\n *[rsi] = {rsi_buy_signal} :: rsi({rsi}) > 30"
                # log.info(desc)
                buy_log += desc + ",  "
            #################################################################
            if self.tai_golden_ma is None:
                golden_ma_buy_signal = True
            else:
                ma5 = mkt_buy_tais[market]["ma5"]
                ma20 = mkt_buy_tais[market]["ma20"]
                golden_ma_buy_signal = False

                if ma5 > ma20:
                    golden_ma_buy_signal = True
            #################################################################
            if self.tai_single_ma is None:
                single_ma_buy_signal = True
            else:
                single_ma = mkt_buy_tais[market]["single_ma"]
                single_ma_buy_signal = False

                if single_ma < price:
                    single_ma_buy_signal = True

            if (
                macd_buy_signal
                and cci_buy_signal
                and bband_buy_signal
                and rsi_buy_signal
                and golden_ma_buy_signal
                and single_ma_buy_signal
            ):
                if self.is_use_model:
                    forecast_sig = self.make_model_signal(tmgr, market)
                    return forecast_sig, ""
                else:
                    return True, ""

            else:
                return False, ""

        else:  # IS_USE_TAI = False
            forecast_sig = self.make_model_signal(tmgr, market)
            return forecast_sig, ""

    def __isSellSignal__(self, mkt_sell_tais, tmgr, market, price, time_dt):
        desc = "\r\n *[sws] = "
        sell_log = ""
        sell_log += desc + ",  "

        if self.is_use_tai:
            #################################################################
            if self.tai_macd_tf is None:
                macd_sell_signal = False
            else:
                macd = mkt_sell_tais[market][
                    "macd"
                ]  # [0]macd, [1] macd_signal, [2] macd_hist
                macd_sell_signal = False
                if macd[0] < macd[1]:
                    macd_sell_signal = True
                desc = f"\r\n *[macd] = {macd_sell_signal} :: macd({macd[0]}) < macd_sig({macd[1]})"
                # log.info(desc)
                sell_log += desc + ",  "
            #################################################################
            if self.tai_cci_tf is None:
                cci_sell_signal = False
            else:
                cci = mkt_sell_tais[market]["cci"]
                cci_sell_signal = False
                if cci < 100:
                    cci_sell_signal = True
                desc = f"\r\n *[cci] = {cci_sell_signal} :: cci({cci}) < 0"
                # log.info(desc)
                sell_log += desc + ",  "
            #################################################################
            if self.tai_bb_close_tf is None:
                bband_sell_signal = False
            else:
                bbands = mkt_sell_tais[market][
                    "bband"
                ]  # [0] upper, [1] middle, [2] lower
                bband_sell_signal = False
                if price > bbands[0]:
                    bband_sell_signal = True
                desc = f"\r\n *[bband] = {bband_sell_signal} :: price({price}) > bb_upper({bbands[0]})"
                # log.info(desc)
                sell_log += desc + ",  "
            #################################################################
            if self.tai_rsi_tf is None:
                rsi_sell_signal = False
            else:
                rsi = mkt_sell_tais[market]["rsi"]
                rsi_sell_signal = False
                if rsi > 70:
                    rsi_sell_signal = True
                desc = f"\r\n *[rsi] = {rsi_sell_signal} :: rsi({rsi}) > 70"
                # log.info(desc)
                sell_log += desc + ",  "
            #################################################################
            if self.tai_golden_ma is None:
                golden_ma_sell_signal = False
            else:
                ma5 = mkt_sell_tais[market]["ma5"]
                ma20 = mkt_sell_tais[market]["ma20"]
                golden_ma_sell_signal = False

                if ma5 < ma20:
                    golden_ma_sell_signal = True
            #################################################################
            if self.tai_single_ma is None:
                single_ma_sell_signal = False
            else:
                single_ma = mkt_sell_tais[market]["single_ma"]
                single_ma_sell_signal = False

                if single_ma > price:
                    single_ma_sell_signal = True
            #################################################################

            sell_sig = (
                macd_sell_signal
                or cci_sell_signal
                or bband_sell_signal
                or rsi_sell_signal
                or golden_ma_sell_signal
                or single_ma_sell_signal
            )

            forecast_sig = False
            if self.is_use_model:
                forecast_sig = not self.make_model_signal(tmgr, market)

            return sell_sig or forecast_sig, ""

        else:
            forecast_sig = not self.make_model_signal(tmgr, market)
            return forecast_sig, ""

    def make_model_signal(self, tmgr, market):
        quote = tmgr.get_quote()
        quote_h = quote.ex_quote[self.ex_type][self.candle_type]

        x = quote_h[market]["close"][-self.forecast_args.seq_len :].values.reshape(
            -1, 1
        )
        df_stamp = quote_h[market][-self.forecast_args.seq_len :]
        df_stamp["datetime"] = pd.to_datetime(df_stamp.index)

        future_hours = pd.date_range(
            df_stamp["datetime"].max(), periods=self.pred_len + 1, freq=self.get_freq()
        )[1:]
        df_future = pd.DataFrame({"datetime": future_hours})
        df_stamp = pd.concat([df_stamp, df_future]).reset_index(drop=True)

        data_stamp = time_features(
            pd.to_datetime(df_stamp["datetime"].values), freq=self.forecast_args.freq
        )
        data_stamp = data_stamp.transpose(1, 0)

        x = self.__predict__(x, data_stamp, market)

        forecast_buy_sig = self.__is_positive_slope__(x)
        return forecast_buy_sig

    def __predict__(self, x, data_stamp, market):
        x = self.scaler[market].transform(x)

        x_mark = data_stamp[: self.seq_len]
        x_mark = torch.Tensor(x_mark).to(self.device)
        x = torch.Tensor(x).to(self.device)
        x = x.unsqueeze(0)

        y = torch.zeros_like(x[:, -self.pred_len :, :]).float()
        y = torch.cat([x[:, -self.label_len :, :], y], dim=1).float().to(self.device)

        y_mark_begin = self.label_len + self.pred_len
        y_mark = data_stamp[-y_mark_begin:]
        y_mark = torch.Tensor(y_mark).to(self.device)

        predicted = self.model[market](x, x_mark, y, y_mark)
        predicted = predicted.reshape(-1)

        current_close = x[:, -1, :]
        current_close = current_close.reshape(-1)

        x = torch.cat([current_close, predicted], dim=0)
        x = x.detach().cpu().numpy().reshape(-1, 1)
        x = self.scaler[market].inverse_transform(x)
        return x

    def __is_positive_slope__(self, y_values):
        array = np.array(y_values)
        normalized_array = ((2 * array) - np.max(array) - np.min(array)) / (
            np.max(array) - np.min(array)
        )
        x_values = range(len(normalized_array))
        slope, _ = np.polyfit(x_values, normalized_array, 1)

        if slope >= 0:
            return True
        elif slope < 0:
            return False

    def load_tai_params(self, params):
        self.market = params["market"]
        self.candle_type = params["candle_type"]
        self.is_use_model = params["is_use_model"]
        self.is_use_tai = params["is_use_tai"]

        self.ma3 = params["ma3"]
        self.ma5 = params["ma5"]
        self.ma10 = params["ma10"]
        self.ma20 = params["ma20"]

        self.tai_single_ma = (
            params["tai_single_ma"] if "tai_single_ma" in params else None
        )
        self.tai_golden_ma = (
            params["tai_golden_ma"] if "tai_golden_ma" in params else None
        )
        self.tai_macd_tf = params["tai_macd_tf"] if "tai_macd_tf" in params else None
        self.tai_cci_tf = params["tai_ccl_tf"] if "tai_ccl_tf" in params else None
        self.tai_pdi_tf = params["tai_pdi_tf"] if "tai_pdi_tf" in params else None
        self.tai_mdi_tf = params["tai_mdi_tf"] if "tai_mdi_tf" in params else None
        self.tai_bb_close_tf = (
            params["tai_bb_close_tf"] if "tai_bb_close_tf" in params else None
        )
        self.tai_psar_tf = params["tai_psar_tf"] if "tai_psar_tf" in params else None
        self.tai_rsi_tf = params["tai_rsi_tf"] if "tai_rsi_tf" in params else None
        self.tai_vol_tf = params["tai_vol_tf"] if "tai_vol_tf" in params else None
        self.tai_vol_ma_tf = (
            params["tai_vol_ma_tf"] if "tai_vol_ma_tf" in params else None
        )

    def extract_tai(self, tmgr):
        market_tai = {f"KRW-{self.market}": {}}

        ma_key = self.candle_type.name
        if self.tai_macd_tf is not None:
            self.tai_macd_tf[2] = CandleType[ma_key]
            market_macd = get_nary_tai(tmgr, self.tai_macd_tf)

            for market in market_macd:
                market_tai[market]["macd"] = market_macd[market]

        if self.tai_cci_tf is not None:
            self.tai_cci_tf[2] = CandleType[ma_key]
            market_cci = get_unary_tai(tmgr, self.tai_cci_tf)
            for market in market_cci:
                market_tai[market]["cci"] = market_cci[market]

        if self.tai_pdi_tf is not None:
            self.tai_pdi_tf[2] = CandleType[ma_key]
            market_pdi = get_unary_tai(tmgr, self.tai_pdi_tf)
            for market in market_pdi:
                market_tai[market]["pdi"] = market_pdi[market]

        if self.tai_mdi_tf is not None:
            self.tai_mdi_tf[2] = CandleType[ma_key]
            market_mdi = get_unary_tai(tmgr, self.tai_mdi_tf)
            for market in market_mdi:
                market_tai[market]["mdi"] = market_mdi[market]

        if self.tai_bb_close_tf is not None:
            self.tai_bb_close_tf[2] = CandleType[ma_key]
            bbands = get_nary_tai(tmgr, self.tai_bb_close_tf)
            for market in bbands:
                market_tai[market]["bband"] = bbands[market]

        if self.tai_psar_tf is not None:
            self.tai_psar_tf[2] = CandleType[ma_key]
            psar = get_unary_tai(tmgr, self.tai_psar_tf)
            for market in psar:
                market_tai[market]["psar"] = psar[market]

        if self.tai_rsi_tf is not None:
            self.tai_rsi_tf[2] = CandleType[ma_key]
            rsi = get_unary_tai(tmgr, self.tai_rsi_tf)
            for market in rsi:
                market_tai[market]["rsi"] = rsi[market]

        if self.tai_vol_tf is not None:
            self.tai_vol_tf[2] = CandleType[ma_key]
            vol = get_unary_tai(tmgr, self.tai_vol_tf)
            for market in vol:
                market_tai[market]["vol"] = vol[market]

        if self.tai_vol_ma_tf is not None:
            self.tai_vol_ma_tf[2] = CandleType[ma_key]
            vol_ma = get_unary_tai(tmgr, self.tai_vol_ma_tf)
            for market in vol_ma:
                market_tai[market]["vol_ma"] = vol_ma[market]

        if self.tai_golden_ma is not None:
            tai_golden_ma = get_unary_tai(tmgr, self.tai_golden_ma)
            for market in tai_golden_ma:
                market_tai[market]["golden_ma"] = tai_golden_ma[market]

            ma5 = get_unary_tai(tmgr, self.ma5)
            for market in ma5:
                market_tai[market]["ma5"] = ma5[market]

            ma20 = get_unary_tai(tmgr, self.ma20)
            for market in ma20:
                market_tai[market]["ma20"] = ma20[market]

        if self.tai_single_ma is not None:
            tai_single_ma = get_unary_tai(tmgr, self.tai_single_ma)
            for market in tai_single_ma:
                market_tai[market]["single_ma"] = tai_single_ma[market]

        return market_tai

    def __is_rebalance_time__(self, time_dt):
        remainder = (
            time_dt.minute % self.candle_type.value
        )  # Rebalance every candle time
        if remainder == (self.candle_type.value - 1):
            return True
        return False

    def __is_settlement_time__(self, time_dt):
        return True if time_dt.hour == 8 and time_dt.minute == 59 else False

    def get_freq(self):
        freq_dict = {"day": "d", "hour4": "4h", "hour": "h", "min30": "30T"}
        return freq_dict[self.tick]


class MAStrategy(AbstractNettingStrategy):
    def __init__(self):
        super(MAStrategy, self).__init__()

    def __isBuySignal__(self, mkt_buy_tais, tmgr, market, price, time_dt):
        ma = mkt_buy_tais[market]

        if ma < price:
            return True, f"ma({ma})"
        else:
            return False, f"ma({ma})"

    def __isSellSignal__(self, mkt_sell_tais, tmgr, market, price, time_dt):
        ma = mkt_sell_tais[market]

        if ma > price:
            return True, f"ma({ma})"
        else:
            return False, f"ma({ma})"

    def load_tai_params(self, params):
        self.candle_type = params["candle_type"]
        self.tai_ma = params["tai_ma"]

    def extract_tai(self, tmgr):
        market_ma = get_unary_tai(tmgr, self.tai_ma)

        return market_ma

    def __is_rebalance_time__(self, time_dt):
        remainder = (
            time_dt.minute % self.candle_type.value
        )  # Rebalance every candle time
        if remainder == (self.candle_type.value - 1):
            return True
        return False

    def __is_settlement_time__(self, time_dt):
        return True if time_dt.hour == 8 and time_dt.minute == 59 else False


class ESWATimesNetStrategy(ESWAStrategyBase):
    def setup(self, context):
        super(ESWATimesNetStrategy, self).setup(context)
        root_dir = dirname(dirname(__file__))

        # forecast model
        market = self.context.ctx_params["params"]["market"]
        model = self.context.ctx_params["params"]["model"]
        model_class = self.model_dict[model]
        checkpoint_path = f"models/eswa/{model}"
        self.tick = self.context.ctx_params["params"]["tick"]
        self.pred_len = self.context.ctx_params["params"]["pred_len"]
        self.seq_len = 36 if self.tick == "day" else 96
        self.label_len = int(self.seq_len / 2)

        dir_path = (
            f"{root_dir}/{checkpoint_path}/{market}/{self.tick}_pred{self.pred_len}"
        )
        model_path = f"{dir_path}/checkpoint.pth"
        scaler_path = f"{dir_path}/scaler.pkl"

        sys.argv = ["BullTraderMain"]
        parser = argparse.ArgumentParser(description="Strategy")
        parser.add_argument("--seq_len", type=int, default=self.seq_len)
        parser.add_argument("--label_len", type=int, default=self.label_len)
        parser.add_argument("--pred_len", type=int, default=self.pred_len)
        parser.add_argument("--c_in", type=int, default=1)
        parser.add_argument("--c_out", type=int, default=1)
        parser.add_argument("--e_layers", type=int, default=2)
        parser.add_argument("--d_model", type=int, default=32)
        parser.add_argument("--d_ff", type=int, default=32)
        parser.add_argument("--top_k", type=int, default=4)
        parser.add_argument("--num_kernels", type=int, default=6)
        parser.add_argument("--embed", type=str, default="timeF")
        parser.add_argument("--dropout", type=float, default=0.1)
        parser.add_argument("--freq", type=str, default="h")
        parser.add_argument("--task_name", type=str, default="forecast")
        self.forecast_args = parser.parse_args()

        self.model = {
            f"KRW-{market}": self.__load_model__(
                model_class, model_path, self.forecast_args
            ),
        }

        with open(scaler_path, "rb") as scaler_file:
            scaler = load(scaler_file)
        self.scaler = {
            f"KRW-{market}": scaler,
        }


class ESWAFEDformerStrategy(ESWAStrategyBase):
    def setup(self, context):
        super(ESWAFEDformerStrategy, self).setup(context)
        root_dir = dirname(dirname(__file__))

        # forecast model
        market = self.context.ctx_params["params"]["market"]
        model = self.context.ctx_params["params"]["model"]
        model_class = self.model_dict[model]
        checkpoint_path = f"models/eswa/{model}"
        self.tick = self.context.ctx_params["params"]["tick"]
        self.pred_len = self.context.ctx_params["params"]["pred_len"]
        self.seq_len = 36 if self.tick == "day" else 96
        self.label_len = int(self.seq_len / 2)

        dir_path = (
            f"{root_dir}/{checkpoint_path}/{market}/{self.tick}_pred{self.pred_len}"
        )
        model_path = f"{dir_path}/checkpoint.pth"
        scaler_path = f"{dir_path}/scaler.pkl"

        sys.argv = ["BullTraderMain"]
        parser = argparse.ArgumentParser(description="Strategy")
        parser.add_argument("--seq_len", type=int, default=self.seq_len)
        parser.add_argument("--label_len", type=int, default=self.label_len)
        parser.add_argument("--pred_len", type=int, default=self.pred_len)
        parser.add_argument(
            "--version",
            type=str,
            default="Fourier",
            help="for FEDformer, there are two versions to choose, options: [Fourier, Wavelets]",
        )
        parser.add_argument(
            "--mode_select",
            type=str,
            default="random",
            help="for FEDformer, there are two mode selection method, options: [random, low]",
        )
        parser.add_argument(
            "--modes", type=int, default=64, help="modes to be selected random 64"
        )
        parser.add_argument("--L", type=int, default=3, help="ignore level")
        parser.add_argument("--base", type=str, default="legendre", help="mwt base")
        parser.add_argument(
            "--cross_activation",
            type=str,
            default="tanh",
            help="mwt cross atention activation function tanh or softmax",
        )
        parser.add_argument("--c_in", type=int, default=1)
        parser.add_argument("--c_out", type=int, default=1)
        parser.add_argument("--e_layers", type=int, default=2)
        parser.add_argument(
            "--d_layers", type=int, default=1, help="num of decoder layers"
        )
        parser.add_argument("--d_model", type=int, default=512)
        parser.add_argument("--d_ff", type=int, default=2048, help="dimension of fcn")
        parser.add_argument("--embed", type=str, default="timeF")
        parser.add_argument("--dropout", type=float, default=0.1)
        parser.add_argument("--freq", type=str, default="h")
        parser.add_argument("--task_name", type=str, default="forecast")
        parser.add_argument("--n_heads", type=int, default=8, help="num of heads")
        parser.add_argument("--activation", type=str, default="gelu", help="activation")
        parser.add_argument(
            "--output_attention",
            action="store_true",
            help="whether to output attention is in encoder",
        )
        parser.add_argument(
            "--moving_avg", type=int, default=25, help="window size of moving average"
        )
        self.forecast_args = parser.parse_args()

        self.model = {
            f"KRW-{market}": self.__load_model__(
                model_class, model_path, self.forecast_args
            ),
        }

        with open(scaler_path, "rb") as scaler_file:
            scaler = load(scaler_file)
        self.scaler = {
            f"KRW-{market}": scaler,
        }


class ESWANonStationaryTransformerStrategy(ESWAStrategyBase):
    def setup(self, context):
        super(ESWANonStationaryTransformerStrategy, self).setup(context)
        root_dir = dirname(dirname(__file__))

        # forecast model
        market = self.context.ctx_params["params"]["market"]
        model = self.context.ctx_params["params"]["model"]
        model_class = self.model_dict[model]
        checkpoint_path = f"models/eswa/{model}"
        self.tick = self.context.ctx_params["params"]["tick"]
        self.pred_len = self.context.ctx_params["params"]["pred_len"]
        self.seq_len = 36 if self.tick == "day" else 96
        self.label_len = int(self.seq_len / 2)

        dir_path = (
            f"{root_dir}/{checkpoint_path}/{market}/{self.tick}_pred{self.pred_len}"
        )
        model_path = f"{dir_path}/checkpoint.pth"
        scaler_path = f"{dir_path}/scaler.pkl"

        sys.argv = ["BullTraderMain"]
        parser = argparse.ArgumentParser(description="Strategy")
        parser.add_argument("--seq_len", type=int, default=self.seq_len)
        parser.add_argument("--label_len", type=int, default=self.label_len)
        parser.add_argument("--pred_len", type=int, default=self.pred_len)
        parser.add_argument(
            "--version",
            type=str,
            default="Fourier",
            help="for FEDformer, there are two versions to choose, options: [Fourier, Wavelets]",
        )
        parser.add_argument(
            "--mode_select",
            type=str,
            default="random",
            help="for FEDformer, there are two mode selection method, options: [random, low]",
        )
        parser.add_argument(
            "--modes", type=int, default=64, help="modes to be selected random 64"
        )
        parser.add_argument("--L", type=int, default=3, help="ignore level")
        parser.add_argument("--base", type=str, default="legendre", help="mwt base")
        parser.add_argument(
            "--cross_activation",
            type=str,
            default="tanh",
            help="mwt cross atention activation function tanh or softmax",
        )
        parser.add_argument("--c_in", type=int, default=1)
        parser.add_argument("--c_out", type=int, default=1)
        parser.add_argument("--e_layers", type=int, default=2)
        parser.add_argument(
            "--d_layers", type=int, default=1, help="num of decoder layers"
        )
        parser.add_argument("--d_model", type=int, default=512)
        parser.add_argument("--d_ff", type=int, default=2048, help="dimension of fcn")
        parser.add_argument("--embed", type=str, default="timeF")
        parser.add_argument("--dropout", type=float, default=0.1)
        parser.add_argument("--freq", type=str, default="h")
        parser.add_argument("--task_name", type=str, default="forecast")
        parser.add_argument("--n_heads", type=int, default=8, help="num of heads")
        parser.add_argument("--activation", type=str, default="gelu", help="activation")
        parser.add_argument(
            "--output_attention",
            action="store_true",
            help="whether to output attention is in encoder",
        )
        parser.add_argument(
            "--moving_avg", type=int, default=25, help="window size of moving average"
        )
        parser.add_argument("--factor", type=int, default=1, help="attn factor")
        parser.add_argument(
            "--p_hidden_dims",
            type=int,
            nargs="+",
            default=[128, 128],
            help="hidden layer dimensions of projector (List)",
        )
        parser.add_argument(
            "--p_hidden_layers",
            type=int,
            default=2,
            help="number of hidden layers in projector",
        )
        self.forecast_args = parser.parse_args()

        self.model = {
            f"KRW-{market}": self.__load_model__(
                model_class, model_path, self.forecast_args
            ),
        }

        with open(scaler_path, "rb") as scaler_file:
            scaler = load(scaler_file)
        self.scaler = {
            f"KRW-{market}": scaler,
        }


class ESWADLinearStrategy(ESWAStrategyBase):
    def setup(self, context):
        super(ESWADLinearStrategy, self).setup(context)
        root_dir = dirname(dirname(__file__))

        # forecast model
        market = self.context.ctx_params["params"]["market"]
        model = self.context.ctx_params["params"]["model"]
        model_class = self.model_dict[model]
        checkpoint_path = f"models/eswa/{model}"
        self.tick = self.context.ctx_params["params"]["tick"]
        self.pred_len = self.context.ctx_params["params"]["pred_len"]
        self.seq_len = 36 if self.tick == "day" else 96
        self.label_len = int(self.seq_len / 2)

        dir_path = (
            f"{root_dir}/{checkpoint_path}/{market}/{self.tick}_pred{self.pred_len}"
        )
        model_path = f"{dir_path}/checkpoint.pth"
        scaler_path = f"{dir_path}/scaler.pkl"

        sys.argv = ["BullTraderMain"]
        parser = argparse.ArgumentParser(description="Strategy")
        parser.add_argument("--seq_len", type=int, default=self.seq_len)
        parser.add_argument("--label_len", type=int, default=self.label_len)
        parser.add_argument("--pred_len", type=int, default=self.pred_len)
        parser.add_argument("--c_in", type=int, default=1)
        parser.add_argument("--c_out", type=int, default=1)
        parser.add_argument("--embed", type=str, default="timeF")
        parser.add_argument("--freq", type=str, default="h")
        parser.add_argument("--task_name", type=str, default="forecast")
        parser.add_argument(
            "--moving_avg", type=int, default=25, help="window size of moving average"
        )
        self.forecast_args = parser.parse_args()

        self.model = {
            f"KRW-{market}": self.__load_model__(
                model_class, model_path, self.forecast_args
            ),
        }

        with open(scaler_path, "rb") as scaler_file:
            scaler = load(scaler_file)
        self.scaler = {
            f"KRW-{market}": scaler,
        }


class ESWALightTSStrategy(ESWAStrategyBase):
    def setup(self, context):
        super(ESWALightTSStrategy, self).setup(context)
        root_dir = dirname(dirname(__file__))

        # forecast model
        market = self.context.ctx_params["params"]["market"]
        model = self.context.ctx_params["params"]["model"]
        model_class = self.model_dict[model]
        checkpoint_path = f"models/eswa/{model}"
        self.tick = self.context.ctx_params["params"]["tick"]
        self.pred_len = self.context.ctx_params["params"]["pred_len"]
        self.seq_len = 36 if self.tick == "day" else 96
        self.label_len = int(self.seq_len / 2)

        dir_path = (
            f"{root_dir}/{checkpoint_path}/{market}/{self.tick}_pred{self.pred_len}"
        )
        model_path = f"{dir_path}/checkpoint.pth"
        scaler_path = f"{dir_path}/scaler.pkl"

        sys.argv = ["BullTraderMain"]
        parser = argparse.ArgumentParser(description="Strategy")
        parser.add_argument("--seq_len", type=int, default=self.seq_len)
        parser.add_argument("--label_len", type=int, default=self.label_len)
        parser.add_argument("--pred_len", type=int, default=self.pred_len)
        parser.add_argument("--c_in", type=int, default=1)
        parser.add_argument("--c_out", type=int, default=1)
        parser.add_argument(
            "--d_model", type=int, default=512, help="dimension of model"
        )
        parser.add_argument("--embed", type=str, default="timeF")
        parser.add_argument("--dropout", type=float, default=0.1, help="dropout")
        parser.add_argument("--freq", type=str, default="h")
        parser.add_argument("--task_name", type=str, default="forecast")
        self.forecast_args = parser.parse_args()

        self.model = {
            f"KRW-{market}": self.__load_model__(
                model_class, model_path, self.forecast_args
            ),
        }

        with open(scaler_path, "rb") as scaler_file:
            scaler = load(scaler_file)
        self.scaler = {
            f"KRW-{market}": scaler,
        }


class ESWALSTNetStrategy(ESWAStrategyBase):
    def setup(self, context):
        super(ESWALSTNetStrategy, self).setup(context)
        root_dir = dirname(dirname(__file__))

        # forecast model
        market = self.context.ctx_params["params"]["market"]
        model = self.context.ctx_params["params"]["model"]
        model_class = self.model_dict[model]
        checkpoint_path = f"models/eswa/{model}"
        self.tick = self.context.ctx_params["params"]["tick"]
        self.pred_len = self.context.ctx_params["params"]["pred_len"]
        self.seq_len = 36 if self.tick == "day" else 96
        self.label_len = int(self.seq_len / 2)

        dir_path = (
            f"{root_dir}/{checkpoint_path}/{market}/{self.tick}_pred{self.pred_len}"
        )
        model_path = f"{dir_path}/checkpoint.pth"
        scaler_path = f"{dir_path}/scaler.pkl"

        sys.argv = ["BullTraderMain"]
        parser = argparse.ArgumentParser(description="Strategy")
        parser.add_argument("--seq_len", type=int, default=self.seq_len)
        parser.add_argument("--label_len", type=int, default=self.label_len)
        parser.add_argument("--pred_len", type=int, default=self.pred_len)
        parser.add_argument("--c_in", type=int, default=1)
        parser.add_argument("--c_out", type=int, default=1)
        parser.add_argument(
            "--d_model", type=int, default=100, help="dimension of model"
        )
        parser.add_argument("--embed", type=str, default="timeF")
        parser.add_argument("--dropout", type=float, default=0.2, help="dropout")
        parser.add_argument("--freq", type=str, default="h")
        parser.add_argument("--task_name", type=str, default="forecast")
        parser.add_argument("--num_kernels", type=int, default=6, help="for Inception")
        parser.add_argument(
            "--rnn_hidden", type=int, default=100, help="rnn hidden size"
        )
        parser.add_argument(
            "--cnn_hidden", type=int, default=100, help="cnn hidden size"
        )
        parser.add_argument("--skip_hidden", type=int, default=5)
        parser.add_argument("--skip", type=float, default=24)
        parser.add_argument(
            "--highway_window",
            type=int,
            default=24,
            help="The window size of the highway component",
        )
        self.forecast_args = parser.parse_args()

        self.model = {
            f"KRW-{market}": self.__load_model__(
                model_class, model_path, self.forecast_args
            ),
        }

        with open(scaler_path, "rb") as scaler_file:
            scaler = load(scaler_file)
        self.scaler = {
            f"KRW-{market}": scaler,
        }


class ESWADilatedRNNStrategy(ESWAStrategyBase):
    def setup(self, context):
        super(ESWADilatedRNNStrategy, self).setup(context)
        root_dir = dirname(dirname(__file__))

        # forecast model
        market = self.context.ctx_params["params"]["market"]
        model = self.context.ctx_params["params"]["model"]
        model_class = self.model_dict[model]
        checkpoint_path = f"models/eswa/{model}"
        self.tick = self.context.ctx_params["params"]["tick"]
        self.pred_len = self.context.ctx_params["params"]["pred_len"]
        self.seq_len = 36 if self.tick == "day" else 96
        self.label_len = int(self.seq_len / 2)

        dir_path = (
            f"{root_dir}/{checkpoint_path}/{market}/{self.tick}_pred{self.pred_len}"
        )
        model_path = f"{dir_path}/checkpoint.pth"
        scaler_path = f"{dir_path}/scaler.pkl"

        sys.argv = ["BullTraderMain"]
        parser = argparse.ArgumentParser(description="Strategy")
        parser.add_argument("--seq_len", type=int, default=self.seq_len)
        parser.add_argument("--label_len", type=int, default=self.label_len)
        parser.add_argument("--pred_len", type=int, default=self.pred_len)
        parser.add_argument("--c_in", type=int, default=1)
        parser.add_argument("--c_out", type=int, default=1)
        parser.add_argument(
            "--e_layers", type=int, default=5, help="num of encoder layers"
        )
        parser.add_argument(
            "--d_model", type=int, default=256, help="dimension of model"
        )
        parser.add_argument("--hidden_size", type=int, default=256, help="hidden size")
        parser.add_argument("--embed", type=str, default="timeF")
        parser.add_argument("--dropout", type=float, default=0.2, help="dropout")
        parser.add_argument("--freq", type=str, default="h")
        parser.add_argument("--task_name", type=str, default="forecast")
        self.forecast_args = parser.parse_args()

        self.model = {
            f"KRW-{market}": self.__load_model__(
                model_class, model_path, self.forecast_args
            ),
        }

        with open(scaler_path, "rb") as scaler_file:
            scaler = load(scaler_file)
        self.scaler = {
            f"KRW-{market}": scaler,
        }


class ESWASCINetStrategy(ESWAStrategyBase):
    def setup(self, context):
        super(ESWASCINetStrategy, self).setup(context)
        root_dir = dirname(dirname(__file__))

        # forecast model
        market = self.context.ctx_params["params"]["market"]
        model = self.context.ctx_params["params"]["model"]
        model_class = self.model_dict[model]
        checkpoint_path = f"models/eswa/{model}"
        self.tick = self.context.ctx_params["params"]["tick"]
        self.pred_len = self.context.ctx_params["params"]["pred_len"]
        self.seq_len = 36 if self.tick == "day" else 96
        self.label_len = int(self.seq_len / 2)
        self.num_levels = 2 if self.tick == "day" else 5

        dir_path = (
            f"{root_dir}/{checkpoint_path}/{market}/{self.tick}_pred{self.pred_len}"
        )
        model_path = f"{dir_path}/checkpoint.pth"
        scaler_path = f"{dir_path}/scaler.pkl"

        sys.argv = ["BullTraderMain"]
        parser = argparse.ArgumentParser(description="Strategy")
        parser.add_argument("--seq_len", type=int, default=self.seq_len)
        parser.add_argument("--label_len", type=int, default=self.label_len)
        parser.add_argument("--pred_len", type=int, default=self.pred_len)
        parser.add_argument("--c_in", type=int, default=1)
        parser.add_argument("--c_out", type=int, default=1)
        parser.add_argument("--embed", type=str, default="timeF")
        parser.add_argument("--freq", type=str, default="h")
        parser.add_argument("--task_name", type=str, default="forecast")
        parser.add_argument("--dropout", type=float, default=0.25, help="dropout")
        parser.add_argument(
            "--d_layers", type=int, default=1, help="num of decoder layers"
        )
        parser.add_argument("--hidden_size", type=int, default=4, help="hidden size")
        parser.add_argument("--num_stacks", type=int, default=1, help="number of stack")
        parser.add_argument(
            "--num_levels", type=int, default=self.num_levels, help="number of level"
        )
        parser.add_argument("--num_kernels", type=int, default=5, help="for Inception")
        # parser.add_argument('--num_kernels', type=int, default=6, help='for Inception')
        self.forecast_args = parser.parse_args()

        self.model = {
            f"KRW-{market}": self.__load_model__(
                model_class, model_path, self.forecast_args
            ),
        }

        with open(scaler_path, "rb") as scaler_file:
            scaler = load(scaler_file)
        self.scaler = {
            f"KRW-{market}": scaler,
        }
