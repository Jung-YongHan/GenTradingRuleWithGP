import argparse
import sys
from os.path import dirname
from pickle import load

import numpy as np
import pandas as pd
import torch

from bt4.Constants import CandleType, QItem
from bt4.utils.market_utils import pick_market_unary_tais
from bt4.utils.mylog import init_log
from bt4.utils.python_utils import to_curr_unit_str2
from bt4.utils.tai_utils import get_unary_tai
from bt4.strategy.Strategy import (
    AbstractHedgingStrategy,
    AbstractNettingStrategy,
)
from stgy_lab._04_deeplearning.models.times_net import TimesNet
from stgy_lab._04_deeplearning.utils.time_features import time_features

log = init_log()


######################################################
## Common functions in SWS
def signal_buy_pos(mas_list, price):
    buySignal = True
    for ma in mas_list:
        if price <= ma:
            buySignal = False
            break
    return buySignal


def signal_sell_pos(mas_list, price):
    sellSignal = False
    for ma in mas_list:
        if price <= ma:
            sellSignal = True
            break
    return sellSignal


def get_mas_str2(ma_prefix_list, tf_hour, mas_list):
    mas_str = '{'
    for i, ma_prefix in enumerate(ma_prefix_list):
        mas_str = mas_str + f'{ma_prefix}{tf_hour}({to_curr_unit_str2(mas_list[i], None)}),'
    return mas_str[0:-1] + '}'


def get_mas_str(mas_list):
    mas_str = '['
    for i, ma in enumerate(mas_list):
        mas_str = mas_str + f'{ma:3.1f}'
        if i < len(mas_list) - 1:
            mas_str = mas_str + ','
    mas_str = mas_str + ']'
    return mas_str


@DeprecationWarning
def pick_up_mas_from_ta_indicators(ta_indicators, ma_name_list):
    market_mas = {}

    market_ma_list = []
    for ma_name in ma_name_list:
        market_ma = pick_market_unary_tais(ta_indicators, ma_name)
        market_ma_list.append(market_ma)

    for market in ta_indicators:
        market_mas[market] = []
        for market_ma in market_ma_list:
            market_mas[market].append(market_ma[market])
    return market_mas


def pick_up_mas_from_ta_indicators3(tmgr, tai_ma_list):
    market_mas = {}

    market_ma_list = []
    for tai_ma in tai_ma_list:
        market_ma = get_unary_tai(tmgr, tai_ma)
        market_ma_list.append(market_ma)

    quote = tmgr.get_quote()
    market_ticks = quote.get_market_ticks(tmgr.ex_type)
    for market in market_ticks:
        market_mas[market] = []
        for market_ma in market_ma_list:
            market_mas[market].append(market_ma[market])
    return market_mas


@DeprecationWarning
def pick_up_mas_from_ta_indicators2(tmgr, market_ticks, candle_type, ma_period_list):
    market_mas = {}

    market_ma_list = []
    for ma_period in ma_period_list:
        market_ma = tmgr.get_unary('sma', [ma_period], candle_type, [QItem.close])
        market_ma_list.append(market_ma)

    for market in market_ticks:
        market_mas[market] = []
        for market_ma in market_ma_list:
            market_mas[market].append(market_ma[market])
    return market_mas


class TimesNetStrategy(AbstractHedgingStrategy):
    def __init__(self):
        super(TimesNetStrategy, self).__init__()
        root_dir = dirname(dirname(__file__))
        checkpoint_path = "models/TimesNet"

        btc_path = "/BTC"
        btc_dir_path = f'{root_dir}/{checkpoint_path}/{btc_path}'
        btc_model_path = f'{btc_dir_path}/checkpoint.pth'

        eth_path = "/ETH"
        eth_dir_path = f'{root_dir}/{checkpoint_path}/{eth_path}'
        eth_model_path = f'{eth_dir_path}/checkpoint.pth'

        xrp_path = "/XRP"
        xrp_dir_path = f'{root_dir}/{checkpoint_path}/{xrp_path}'
        xrp_model_path = f'{xrp_dir_path}/checkpoint.pth'

        # all_path = "/ALL"
        # all_dir_path = f'{root_dir}/{checkpoint_path}/{all_path}'
        # all_model_path = f'{all_dir_path}/checkpoint.pth'

        sys.argv = ['BullTraderMain']
        parser = argparse.ArgumentParser(description='TimesNet Strategy')
        parser.add_argument('--seq_len', type=int, default=104)
        parser.add_argument('--pred_len', type=int, default=24)
        parser.add_argument('--c_in', type=int, default=1)
        parser.add_argument('--c_out', type=int, default=1)
        parser.add_argument('--e_layers', type=int, default=4)
        parser.add_argument('--d_model', type=int, default=16)
        parser.add_argument('--d_ff', type=int, default=32)
        parser.add_argument('--top_k', type=int, default=3)
        parser.add_argument('--num_kernels', type=int, default=6)
        parser.add_argument('--embed', type=str, default='timeF')
        parser.add_argument('--dropout', type=float, default=0.1)
        parser.add_argument('--freq', type=str, default='h')

        self.args = parser.parse_args()

        self.device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

        self.model = {
            'KRW-BTC': self.__load_model__(btc_model_path),
            # 'KRW-ETH': self.__load_model__(eth_model_path),
            # 'KRW-XRP': self.__load_model__(xrp_model_path),
        }

        self.scaler = {
            'KRW-BTC': load(open(f'{btc_dir_path}/scaler.pkl', 'rb')),
            # 'KRW-ETH': load(open(f'{eth_dir_path}/scaler.pkl', 'rb')),
            # 'KRW-XRP': load(open(f'{xrp_dir_path}/scaler.pkl', 'rb')),
        }

    def __load_model__(self, model_path):
        model = TimesNet(args=self.args)
        state_dict = torch.load(model_path)
        model.load_state_dict(state_dict)
        model.to(self.device)
        model.eval()
        return model

    def load_tai_params(self, params):
        self.tai_ma1_tf = params['tai_ma1_tf']
        self.tai_ma2_tf = params['tai_ma2_tf']
        self.tai_ma3_tf = params['tai_ma3_tf']
        self.tai_ma4_tf = params['tai_ma4_tf']

    def __isBuySignal__(self, mkt_buy_tais, tmgr, market, price, time_dt, tf_hour):
        quote = tmgr.get_quote()
        quote_h = quote.ex_quote[self.ex_type][CandleType.HOUR]

        ma1 = mkt_buy_tais[market]['ma0']
        ma2 = mkt_buy_tais[market]['ma1']

        df_stamp = quote_h[market][-self.args.seq_len :]
        df_stamp['datetime'] = pd.to_datetime(df_stamp.index)
        data_stamp = time_features(pd.to_datetime(df_stamp['datetime'].values), freq=self.args.freq)
        data_stamp = data_stamp.transpose(1, 0)

        x = quote_h[market]['close'][-self.args.seq_len :].values.reshape(-1, 1)
        x = self.__predict__(x, data_stamp, market)

        is_positive = self.__is_positive_slope__(x)
        return is_positive, f"positive({is_positive}) and (ma1({ma1}) < price({price}) and ma2({ma2}) < price({price})))"

    def __isSellSignal__(self, mkt_sell_tais, tmgr, market, price, time_dt, tf_hour):
        quote = tmgr.get_quote()
        quote_h = quote.ex_quote[self.ex_type][CandleType.HOUR]

        df_stamp = quote_h[market][-self.args.seq_len :]
        df_stamp['datetime'] = pd.to_datetime(df_stamp.index)
        data_stamp = time_features(pd.to_datetime(df_stamp['datetime'].values), freq=self.args.freq)
        data_stamp = data_stamp.transpose(1, 0)

        x = quote_h[market]['close'][-self.args.seq_len :].values.reshape(-1, 1)
        x = self.__predict__(x, data_stamp, market)
        timesnet_sell_sig = not self.__is_positive_slope__(x)
        timesnet_sell_log = f"timesnet_sell_sig({timesnet_sell_sig})"

        return timesnet_sell_sig, f"{timesnet_sell_log}"

    def __predict__(self, x, x_mark, market):
        x = self.scaler[market].transform(x)

        x_mark = torch.Tensor(x_mark).to(self.device)
        x = torch.Tensor(x).to(self.device)
        x = x.unsqueeze(0)

        predicted = self.model[market](x, x_mark)
        predicted = predicted.reshape(-1)

        current_close = x[:, -1, :]
        current_close = current_close.reshape(-1)

        x = torch.cat([current_close, predicted], dim=0)
        x = x.detach().cpu().numpy().reshape(-1, 1)
        x = self.scaler[market].inverse_transform(x)
        return x

    def __is_positive_slope__(self, y_values):
        array = np.array(y_values)
        normalized_array = ((2 * array) - np.max(array) - np.min(array)) / (np.max(array) - np.min(array))
        x_values = range(len(normalized_array))
        slope, _ = np.polyfit(x_values, normalized_array, 1)

        if slope >= 0:
            return True
        elif slope < 0:
            return False

    def extract_tai(self, tmgr, timeframe_hour):
        tai_ma_list = [self.tai_ma1_tf, self.tai_ma2_tf, self.tai_ma3_tf, self.tai_ma4_tf]
        market_mas_list = []
        for tai_ma in tai_ma_list:
            ma_key = f'DAYS_{timeframe_hour}'  # it should be matched with that of euote dispatcher
            cdl_type = CandleType[ma_key]
            tai_ma[2] = cdl_type
            market_ma = get_unary_tai(tmgr, tai_ma)
            market_mas_list.append(market_ma)

        quote = tmgr.get_quote()
        market_ticks = quote.get_market_ticks(tmgr.ex_type)

        market_mas = {}
        for market in market_ticks:
            market_mas[market] = {}
            for idx, mas in enumerate(market_mas_list):
                market_mas[market][f"ma{idx}"] = mas[market]

        return market_mas


class SuperTimesNetStrategy(AbstractHedgingStrategy):
    def __init__(self):
        super(SuperTimesNetStrategy, self).__init__()
        root_dir = dirname(dirname(__file__))
        checkpoint_path = "models/forecast/TimesNet"

        btc_path = "BTC"
        btc_dir_path = f'{root_dir}/{checkpoint_path}/{btc_path}'
        btc_model_path = f'{btc_dir_path}/checkpoint.pth'

        # eth_path = "ETH"
        # eth_dir_path = f'{root_dir}/{checkpoint_path}/{eth_path}'
        # eth_model_path = f'{eth_dir_path}/checkpoint.pth'

        # xrp_path = "XRP"
        # xrp_dir_path = f'{root_dir}/{checkpoint_path}/{xrp_path}'
        # xrp_model_path = f'{xrp_dir_path}/checkpoint.pth'

        # all_path = "/ALL"
        # all_dir_path = f'{root_dir}/{checkpoint_path}/{all_path}'
        # all_model_path = f'{all_dir_path}/checkpoint.pth'

        sys.argv = ['BullTraderMain']
        parser = argparse.ArgumentParser(description='TimesNet Strategy')
        parser.add_argument('--seq_len', type=int, default=104)
        parser.add_argument('--pred_len', type=int, default=24)
        parser.add_argument('--c_in', type=int, default=1)
        parser.add_argument('--c_out', type=int, default=1)
        parser.add_argument('--e_layers', type=int, default=4)
        parser.add_argument('--d_model', type=int, default=16)
        parser.add_argument('--d_ff', type=int, default=32)
        parser.add_argument('--top_k', type=int, default=3)
        parser.add_argument('--num_kernels', type=int, default=6)
        parser.add_argument('--embed', type=str, default='timeF')
        parser.add_argument('--dropout', type=float, default=0.1)
        parser.add_argument('--freq', type=str, default='h')

        self.args = parser.parse_args()

        self.device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

        self.model = {
            'KRW-BTC': self.__load_model__(btc_model_path),
            # 'KRW-ETH': self.__load_model__(eth_model_path),
            # 'KRW-XRP': self.__load_model__(xrp_model_path),
        }

        # self.scaler = load(open(f'{dir_path}/KRW-BTC_HOUR_scaler.pkl', 'rb'))
        self.scaler = {
            'KRW-BTC': load(open(f'{btc_dir_path}/scaler.pkl', 'rb')),
            # 'KRW-ETH': load(open(f'{eth_dir_path}/scaler.pkl', 'rb')),
            # 'KRW-XRP': load(open(f'{xrp_dir_path}/scaler.pkl', 'rb')),
        }

    def __load_model__(self, model_path):
        model = TimesNet(args=self.args)
        state_dict = torch.load(model_path)
        model.load_state_dict(state_dict)
        model.to(self.device)
        model.eval()
        return model

    def load_tai_params(self, params):
        self.tai_ma1_tf = params['tai_ma1_tf']
        self.tai_ma2_tf = params['tai_ma2_tf']
        self.tai_ma3_tf = params['tai_ma3_tf']
        self.tai_ma4_tf = params['tai_ma4_tf']

    def __isBuySignal__(self, mkt_buy_tais, tmgr, market, price, time_dt, tf_hour):
        quote = tmgr.get_quote()
        quote_h = quote.ex_quote[self.ex_type][CandleType.HOUR]

        ma1 = mkt_buy_tais[market]['ma0']
        ma2 = mkt_buy_tais[market]['ma1']

        if ma1 < price and ma2 < price:
            df_stamp = quote_h[market][-self.args.seq_len :]
            df_stamp['datetime'] = pd.to_datetime(df_stamp.index)
            data_stamp = time_features(pd.to_datetime(df_stamp['datetime'].values), freq=self.args.freq)
            data_stamp = data_stamp.transpose(1, 0)

            x = quote_h[market]['close'][-self.args.seq_len :].values.reshape(-1, 1)
            x = self.__predict__(x, data_stamp, market)

            is_positive = self.__is_positive_slope__(x)
            return is_positive, f"positive({is_positive}) and (ma1({ma1}) < price({price}) and ma2({ma2}) < price({price})))"
        else:
            return False, f"ma1({ma1}) < price({price}) and ma2({ma2}) < price({price})"

    def __isSellSignal__(self, mkt_sell_tais, tmgr, market, price, time_dt, tf_hour):
        quote = tmgr.get_quote()
        quote_h = quote.ex_quote[self.ex_type][CandleType.HOUR]

        ma1 = mkt_sell_tais[market]['ma0']
        ma2 = mkt_sell_tais[market]['ma1']

        sws_sell_sig = ma1 > price or ma2 > price
        sws_sell_log = f"sws_sell_sig({sws_sell_sig})= ma1({ma1}) > price({price}) or ma2({ma2}) > price({price})"

        df_stamp = quote_h[market][-self.args.seq_len :]
        df_stamp['datetime'] = pd.to_datetime(df_stamp.index)
        data_stamp = time_features(pd.to_datetime(df_stamp['datetime'].values), freq=self.args.freq)
        data_stamp = data_stamp.transpose(1, 0)

        x = quote_h[market]['close'][-self.args.seq_len :].values.reshape(-1, 1)
        x = self.__predict__(x, data_stamp, market)
        timesnet_sell_sig = not self.__is_positive_slope__(x)
        dlinear_sell_log = f"timesnet_sell_sig({timesnet_sell_sig})"

        return sws_sell_sig or timesnet_sell_sig, f"{sws_sell_log} / {dlinear_sell_log}"

    def __predict__(self, x, x_mark, market):
        x = self.scaler[market].transform(x)

        x_mark = torch.Tensor(x_mark).to(self.device)
        x = torch.Tensor(x).to(self.device)
        x = x.unsqueeze(0)

        predicted = self.model[market](x, x_mark)
        predicted = predicted.reshape(-1)

        current_close = x[:, -1, :]
        current_close = current_close.reshape(-1)

        x = torch.cat([current_close, predicted], dim=0)
        x = x.detach().cpu().numpy().reshape(-1, 1)
        x = self.scaler[market].inverse_transform(x)
        return x

    def __is_positive_slope__(self, y_values):
        array = np.array(y_values)
        normalized_array = ((2 * array) - np.max(array) - np.min(array)) / (np.max(array) - np.min(array))
        x_values = range(len(normalized_array))
        slope, _ = np.polyfit(x_values, normalized_array, 1)

        if slope >= 0:
            return True
        elif slope < 0:
            return False

    def extract_tai(self, tmgr, timeframe_hour):
        tai_ma_list = [self.tai_ma1_tf, self.tai_ma2_tf, self.tai_ma3_tf, self.tai_ma4_tf]
        market_mas_list = []
        for tai_ma in tai_ma_list:
            ma_key = f'DAYS_{timeframe_hour}'  # it should be matched with that of euote dispatcher
            cdl_type = CandleType[ma_key]
            tai_ma[2] = cdl_type
            market_ma = get_unary_tai(tmgr, tai_ma)
            market_mas_list.append(market_ma)

        quote = tmgr.get_quote()
        market_ticks = quote.get_market_ticks(tmgr.ex_type)

        market_mas = {}
        for market in market_ticks:
            market_mas[market] = {}
            for idx, mas in enumerate(market_mas_list):
                market_mas[market][f"ma{idx}"] = mas[market]

        return market_mas


class AnomalyTimesNetStrategy(AbstractNettingStrategy):
    def __init__(self):
        super(AnomalyTimesNetStrategy, self).__init__()
        root_dir = dirname(dirname(__file__))
        self.device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

        # forecast model
        forecast_checkpoint_path = "models/forecast/TimesNet"

        poly_forecast_path = "POLYX"
        poly_forecast_dir_path = f'{root_dir}/{forecast_checkpoint_path}/{poly_forecast_path}'
        poly_forecast_model_path = f'{poly_forecast_dir_path}/checkpoint.pth'

        sys.argv = ['BullTraderMain']
        parser = argparse.ArgumentParser(description='TimesNet Strategy')
        parser.add_argument('--seq_len', type=int, default=100)
        parser.add_argument('--pred_len', type=int, default=8)
        parser.add_argument('--c_in', type=int, default=1)
        parser.add_argument('--c_out', type=int, default=1)
        parser.add_argument('--e_layers', type=int, default=4)
        parser.add_argument('--d_model', type=int, default=16)
        parser.add_argument('--d_ff', type=int, default=32)
        parser.add_argument('--top_k', type=int, default=3)
        parser.add_argument('--num_kernels', type=int, default=6)
        parser.add_argument('--embed', type=str, default='timeF')
        parser.add_argument('--dropout', type=float, default=0.1)
        parser.add_argument('--freq', type=str, default='h')
        parser.add_argument('--task_name', type=str, default='forecast')
        self.forecast_args = parser.parse_args()

        self.forecast_model = {
            'KRW-POLYX': self.__load_model__(poly_forecast_model_path, self.forecast_args),
        }

        # anomaly model
        anomaly_checkpoint_path = "models/anomaly/TimesNet"

        poly_anomaly_path = "POLYX"
        poly_anomaly_dir_path = f'{root_dir}/{anomaly_checkpoint_path}/{poly_anomaly_path}'
        poly_anomaly_model_path = f'{poly_anomaly_dir_path}/checkpoint.pth'

        sys.argv = ['BullTraderMain']
        parser = argparse.ArgumentParser(description='TimesNet Strategy')
        parser.add_argument('--seq_len', type=int, default=100)
        parser.add_argument('--pred_len', type=int, default=0)
        parser.add_argument('--c_in', type=int, default=1)
        parser.add_argument('--c_out', type=int, default=1)
        parser.add_argument('--e_layers', type=int, default=4)
        parser.add_argument('--d_model', type=int, default=32)
        parser.add_argument('--d_ff', type=int, default=32)
        parser.add_argument('--top_k', type=int, default=3)
        parser.add_argument('--num_kernels', type=int, default=6)
        parser.add_argument('--embed', type=str, default='timeF')
        parser.add_argument('--dropout', type=float, default=0.1)
        parser.add_argument('--freq', type=str, default='h')
        parser.add_argument('--task_name', type=str, default='anomaly_detection')
        self.anomaly_args = parser.parse_args()

        self.anomaly_model = {
            'KRW-POLYX': self.__load_model__(poly_anomaly_model_path, self.anomaly_args),
        }

        self.scaler = {
            'KRW-POLYX': load(open(f'{poly_forecast_dir_path}/scaler.pkl', 'rb')),
        }

        # 25% : 7.370059001551068e-05
        # 10% : 3.1069678379937575e-05
        self.threshold = 3.1069678379937575e-05

    def __load_model__(self, model_path, args):
        model = TimesNet(args=args)
        state_dict = torch.load(model_path)
        model.load_state_dict(state_dict)
        model.to(self.device)
        model.eval()
        return model

    def __isBuySignal__(self, mkt_buy_tais, tmgr, market, price, time_dt):
        quote = tmgr.get_quote()
        quote_h = quote.ex_quote[self.ex_type][CandleType.MINUTES_15]

        x = quote_h[market]['close'][-self.forecast_args.seq_len :].values.reshape(-1, 1)

        ma1 = mkt_buy_tais[0][market]
        ma2 = mkt_buy_tais[1][market]

        if self.__is_detected__(x, market) and (ma1 > ma2):
            df_stamp = quote_h[market][-self.forecast_args.seq_len :]
            df_stamp['datetime'] = pd.to_datetime(df_stamp.index)
            data_stamp = time_features(pd.to_datetime(df_stamp['datetime'].values), freq=self.forecast_args.freq)
            data_stamp = data_stamp.transpose(1, 0)

            x = self.__predict__(x, data_stamp, market)

            forecast_buy_sig = self.__is_positive_slope__(x)
            anomaly_sig = True

            return forecast_buy_sig and anomaly_sig, f"anomaly sig({anomaly_sig}) and forecast sig({forecast_buy_sig})"
            # return True, " ma1({ma1}) > ma2({ma2}) "
        else:
            return False, "anomaly sig(False)"

    def __isSellSignal__(self, mkt_sell_tais, tmgr, market, price, time_dt):
        quote = tmgr.get_quote()
        quote_h = quote.ex_quote[self.ex_type][CandleType.MINUTES_15]

        x = quote_h[market]['close'][-self.forecast_args.seq_len :].values.reshape(-1, 1)
        df_stamp = quote_h[market][-self.forecast_args.seq_len :]
        df_stamp['datetime'] = pd.to_datetime(df_stamp.index)
        data_stamp = time_features(pd.to_datetime(df_stamp['datetime'].values), freq=self.forecast_args.freq)
        data_stamp = data_stamp.transpose(1, 0)

        x = self.__predict__(x, data_stamp, market)

        if not self.__is_positive_slope__(x):
            return True, f"forecast sig({True})"
        else:
            return False, f"forecast sig({False})"

    def __predict__(self, x, x_mark, market):
        x = self.scaler[market].transform(x)

        x_mark = torch.Tensor(x_mark).to(self.device)
        x = torch.Tensor(x).to(self.device)
        x = x.unsqueeze(0)

        predicted = self.forecast_model[market](x, x_mark)
        predicted = predicted.reshape(-1)

        current_close = x[:, -1, :]
        current_close = current_close.reshape(-1)

        x = torch.cat([current_close, predicted], dim=0)
        x = x.detach().cpu().numpy().reshape(-1, 1)
        x = self.scaler[market].inverse_transform(x)
        return x

    def __is_detected__(self, x, market):
        x = self.scaler[market].transform(x)
        x = torch.Tensor(x).to(self.device)
        x = x.unsqueeze(0)
        reconstructed = self.anomaly_model[market](x, None)
        loss = torch.nn.functional.mse_loss(reconstructed, x, reduce=False)

        if loss[:, -1, :] > self.threshold:
            return True
        else:
            return False

    def __is_positive_slope__(self, y_values):
        array = np.array(y_values)
        normalized_array = ((2 * array) - np.max(array) - np.min(array)) / (np.max(array) - np.min(array))
        x_values = range(len(normalized_array))
        slope, _ = np.polyfit(x_values, normalized_array, 1)

        if slope >= 0:
            return True
        elif slope < 0:
            return False

    def load_tai_params(self, params):
        self.candle_type = params['candle_type']
        self.tai_ma1 = params['tai_ma1']
        self.tai_ma2 = params['tai_ma2']

    def extract_tai(self, tmgr):
        market_ma = get_unary_tai(tmgr, self.tai_ma1)
        market_ma2 = get_unary_tai(tmgr, self.tai_ma2)
        return market_ma, market_ma2

    def __is_rebalance_time__(self, time_dt):
        remainder = time_dt.minute % self.candle_type.value  # Rebalance every candle time
        if remainder == (self.candle_type.value - 1):
            return True
        return False

    def __is_settlement_time__(self, time_dt):
        return True if time_dt.hour == 8 and time_dt.minute == 59 else False
