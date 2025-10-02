from collections import OrderedDict
import sys
import argparse
from os.path import dirname
from pickle import load

import numpy as np
import torch

from bt4.Constants import CandleType, QItem
from bt4.quote.TAIMgr import TAIMgr
from bt4.utils.market_utils import (
    compute_sell_timeframes,
    compute_vol5,
    match_time_frame,
    pick_market_unary_tais,
)
from bt4.utils.mylog import init_log
from bt4.utils.python_utils import (
    dt2str,
    is_the_time,
    split_hour_min,
    to_curr_unit_str2,
)
from bt4.utils.tai_utils import get_unary_tai
from bt4.strategy.Strategy import AbstractStrategy, AbstractHedgingStrategy
from stgy_lab._04_deeplearning.models.d_linear import DLinear

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


class LinearStrategy(AbstractStrategy):
    def __init__(self):
        super(LinearStrategy, self).__init__()
        self.ex_type = None
        root_dir = dirname(dirname(__file__))

        checkpoint_path = "stgy_lab/_04_deeplearning/checkpoints"
        experiment = "exp_exp_forecast__dat_KRW-BTC_HOUR_csv__mod_DLinear__id_DLinear_BTC_Hourly_k4__dat_BTCh1__fea_S__fre_h__sca_M__seq_336__pre_24__bat_8__epo_1000__lr_3e-5__los_SMAPE__des_Walkforward_validations"
        model = "checkpoint.pth"
        dir_path = f'{root_dir}/{checkpoint_path}/{experiment}'
        model_path = f'{dir_path}/{model}'

        sys.argv = ['BullTraderMain']
        parser = argparse.ArgumentParser(description='Your model description')
        parser.add_argument('--seq_len', type=int, default=336)
        parser.add_argument('--pred_len', type=int, default=24)
        parser.add_argument('--c_in', type=int, default=1)
        self.args = parser.parse_args()

        self.model = DLinear(args=self.args)

        state_dict = torch.load(model_path)
        new_state_dict = OrderedDict()
        for k, v in state_dict.items():
            name = k[7:]
            new_state_dict[name] = v
        self.model.load_state_dict(new_state_dict)
        # self.model.load_state_dict(torch.load(model_path))
        self.device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
        self.model.eval()

        self.scaler = load(open(f'{dir_path}/scaler.pkl', 'rb'))

    def set_params(self, am, report_storage, markets, params):
        self.ex_type = params['quote_provider']
        super(LinearStrategy, self).set_params(am, report_storage, markets, self.ex_type)
        self.buy_timeframes = params['timeframes']
        self.buy_sell_time_gap = params['timegap']
        self.buy_sell_tf, self.sell_buy_tf, self.sell_timeframes = compute_sell_timeframes(self.buy_timeframes, self.buy_sell_time_gap)

        self.market_buy_tai_values = {}
        self.market_sell_tai_values = {}
        self.load_tai_params(params)

    def load_tai_params(self, params):
        self.tai_ma1_tf = params['tai_ma1_tf']
        self.tai_ma2_tf = params['tai_ma2_tf']
        self.tai_ma3_tf = params['tai_ma3_tf']
        self.tai_ma4_tf = params['tai_ma4_tf']

    def __isBuySignal__(self, market, price, quote_h):
        x = x = quote_h[market]['close'][-self.args.seq_len :].values.reshape(-1, 1)
        x = self._predict(x)

        signal = self._calc_slope(x)
        return signal

    def __isSellSignal__(self, market, price, quote_h):
        x = x = quote_h[market]['close'][-self.args.seq_len :].values.reshape(-1, 1)
        x = self._predict(x)

        signal = self._calc_slope(x)
        return not signal

    def _predict(self, x):
        x = self.scaler.transform(x)

        x = torch.Tensor(x).to(self.device)
        x = x.unsqueeze(0)

        predicted = self.model(x)
        predicted = predicted.reshape(-1)

        current_close = x[:, -1, :]
        current_close = current_close.reshape(-1)

        x = torch.cat([current_close, predicted], dim=0)
        x = x.detach().cpu().numpy().reshape(-1, 1)
        x = self.scaler.inverse_transform(x)
        return x

    def _calc_slope(self, y_values):
        array = np.array(y_values)
        normalized_array = ((2 * array) - np.max(array) - np.min(array)) / (np.max(array) - np.min(array))
        x_values = range(len(normalized_array))
        slope, _ = np.polyfit(x_values, normalized_array, 1)

        if slope >= 0:
            return True
        elif slope < 0:
            return False

    def perform(self, quote):
        super(LinearStrategy, self).perform(quote)
        if self.is_paused:
            return

        time_pdt = quote.get_time()

        tmgr = TAIMgr(quote, self.ex_type)
        market_ticks = quote.get_market_ticks(self.ex_type)
        ################################################################
        is_vol_update_time = is_the_time(time_pdt, 8, 59)
        is_buy_time, expected_buy_timeframe_str, buy_tf_hour = match_time_frame(time_pdt, self.buy_timeframes)
        is_sell_time, expected_sell_timeframe_str, sell_tf_hour = match_time_frame(time_pdt, self.sell_timeframes)

        if is_vol_update_time:
            market_vol5 = compute_vol5(quote, tmgr, self.ex_type)
            self.asset_mgmt.append_supplements(market_vol5)
            if self.enable_asset_rebalance:
                self.asset_mgmt.rebalance(market_ticks)

        self.market_buy_tai_values, market_tai_str = self.extract_tai(tmgr, buy_tf_hour)

        for market in market_ticks:
            tick = market_ticks[market]

            #######################################################
            ## Processing Buy
            mas_str = market_tai_str[market]
            buy_trade_result = self.asset_mgmt.get_opened_buy_position(market, expected_buy_timeframe_str)
            if buy_trade_result is None:
                desc = (
                    f'price({to_curr_unit_str2(tick.close, None)}) > {mas_str}, '
                    f' Market Bal for tf({expected_buy_timeframe_str})'
                    f'({to_curr_unit_str2(self.asset_mgmt.get_market_cash_balance(market, expected_buy_timeframe_str), None)})'
                )

                log.info(f'[{tick.datetime}] {tick.market} Time Check for BUY Order(@{expected_buy_timeframe_str})::' + desc)

                if is_buy_time and self.__isBuySignal__(market, tick.close, quote.ex_quote[self.ex_type][CandleType.HOUR]):
                    super(LinearStrategy, self).process_enter_long_position(
                        market, tick, tick.close, f', {desc}', expected_buy_timeframe_str
                    )
            #######################################################
            ## Processing Sell
            for sell_elem_tf in self.sell_buy_tf:
                sell_elem_tf_hour, _ = split_hour_min(sell_elem_tf)
                sell_elem_tf_hour = sell_elem_tf_hour + 1
                sell_elem_tf_hour = 0 if sell_elem_tf_hour == 24 else sell_elem_tf_hour

                self.market_sell_tai_values, sell_market_mas = self.extract_tai(tmgr, sell_elem_tf_hour)
                mas_str = sell_market_mas[market]

                matched_buy_timeframe_str = self.sell_buy_tf[sell_elem_tf]
                matched_buy_trade_result = self.asset_mgmt.get_opened_buy_position(market, matched_buy_timeframe_str)

                if matched_buy_trade_result is not None and matched_buy_trade_result.date != dt2str(time_pdt):
                    desc = f'price({to_curr_unit_str2(tick.close, None)}) < {mas_str}'

                    log.info(
                        f'[{tick.datetime}] {tick.market} Time Check:checking '
                        f'for SELL Order(sell time ({sell_elem_tf}) for buy tf({matched_buy_timeframe_str})):: ' + desc
                    )
                    if (
                        is_sell_time
                        and sell_elem_tf == expected_sell_timeframe_str
                        and self.__isSellSignal__(market, tick.close, quote.ex_quote[self.ex_type][CandleType.HOUR])
                    ):  ## Sell Signal (NEW In WINNING SESSION)
                        super(LinearStrategy, self).process_exit_long_position(
                            matched_buy_trade_result, market, tick, tick.close, f', {desc}', matched_buy_timeframe_str
                        )

        super(LinearStrategy, self).update_trade_n_balance_states_hdging(
            time_pdt, market_ticks, self.buy_timeframes, self.buy_sell_tf, self.sell_buy_tf
        )

        if is_vol_update_time:
            super(LinearStrategy, self).process_settle(time_pdt, market_ticks)

        super(LinearStrategy, self).log_evaluated_balance(time_pdt, market_ticks)

    def extract_tai(self, tmgr, timeframe_hour):
        tai_ma_list = [self.tai_ma1_tf, self.tai_ma2_tf, self.tai_ma3_tf, self.tai_ma4_tf]
        market_mas_list = []
        for tai_ma in tai_ma_list:
            ma_key = f'DAYS_{timeframe_hour}'  # it should be matched with that of euote dispatcher
            cdl_type = CandleType[ma_key]
            tai_ma[2] = cdl_type
            market_ma = get_unary_tai(tmgr, tai_ma)
            market_mas_list.append(market_ma)

        ma_prefix_list = ['ma1_', 'ma2_', 'ma3_', 'ma4_']

        quote = tmgr.get_quote()
        market_ticks = quote.get_market_ticks(tmgr.ex_type)

        market_mas = {}
        market_tai_str = {}
        for market in market_ticks:
            market_mas[market] = {}
            ma_list = []
            for idx, mas in enumerate(market_mas_list):
                market_mas[market][f"ma{idx}"] = mas[market]
                ma_list.append(mas[market])

            market_tai_str[market] = get_mas_str2(ma_prefix_list, timeframe_hour, ma_list)

        return market_mas, market_tai_str



class SuperLinearStrategy(AbstractHedgingStrategy):
    def __init__(self):
        super(SuperLinearStrategy, self).__init__()

        root_dir = dirname(dirname(__file__))
        checkpoint_path = "models/forecast/DLinear"

        btc_path = "BTC"
        btc_dir_path = f'{root_dir}/{checkpoint_path}/{btc_path}'
        btc_model_path = f'{btc_dir_path}/checkpoint.pth'

        eth_path = "ETH"
        eth_dir_path = f'{root_dir}/{checkpoint_path}/{eth_path}'
        eth_model_path = f'{eth_dir_path}/checkpoint.pth'

        xrp_path = "XRP"
        xrp_dir_path = f'{root_dir}/{checkpoint_path}/{xrp_path}'
        xrp_model_path = f'{xrp_dir_path}/checkpoint.pth'

        sys.argv = ['BullTraderMain']
        parser = argparse.ArgumentParser(description='Your model description')
        parser.add_argument('--seq_len', type=int, default=336)
        parser.add_argument('--pred_len', type=int, default=24)
        parser.add_argument('--c_in', type=int, default=1)
        self.args = parser.parse_args()

        self.device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

        self.model = {
            'KRW-BTC': self.__load_model__(btc_model_path),
            'KRW-ETH': self.__load_model__(eth_model_path),
            'KRW-XRP': self.__load_model__(xrp_model_path),
        }

        self.scaler = {
            'KRW-BTC': load(open(f'{btc_dir_path}/scaler.pkl', 'rb')),
            'KRW-ETH': load(open(f'{eth_dir_path}/scaler.pkl', 'rb')),
            'KRW-XRP': load(open(f'{xrp_dir_path}/scaler.pkl', 'rb')),
        }

    def __load_model__(self, model_path):
        model = DLinear(args=self.args)
        state_dict = torch.load(model_path)
        new_state_dict = OrderedDict()
        for k, v in state_dict.items():
            name = k[7:]
            new_state_dict[name] = v
        model.load_state_dict(new_state_dict)
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
            x = quote_h[market]['close'][-self.args.seq_len :].values.reshape(-1, 1)
            x = self.__predict__(x, market)

            is_positive = self.__is_positive_slope__(x)
            return is_positive, f"positive({is_positive}) and (ma1({ma1}) < price({price}) and ma2({ma2}) < price({price})))"
        else:
            return False, f"ma1({ma1}) < price({price}) and ma2({ma2}) < price({price})"

    def __isSellSignal__(self, mkt_sell_tais, tmgr, market, price, time_dt, tf_hour) :
        quote = tmgr.get_quote()
        quote_h = quote.ex_quote[self.ex_type][CandleType.HOUR]

        ma1 = mkt_sell_tais[market]['ma0']
        ma2 = mkt_sell_tais[market]['ma1']

        sws_sell_sig = ma1 > price or ma2 > price
        sws_sell_log = f"sws_sell_sig({sws_sell_sig})= ma1({ma1}) > price({price}) or ma2({ma2}) > price({price})"

        x = quote_h[market]['close'][-self.args.seq_len :].values.reshape(-1, 1)
        x = self.__predict__(x, market)
        dlinear_sell_sig = not self.__is_positive_slope__(x)
        dlinear_sell_log = f"dlinear_sell_sig({dlinear_sell_sig})"

        return sws_sell_sig or dlinear_sell_sig, f"{sws_sell_log} / {dlinear_sell_log}"

    def __predict__(self, x, market):
        x = self.scaler[market].transform(x)

        x = torch.Tensor(x).to(self.device)
        x = x.unsqueeze(0)

        predicted = self.model[market](x)
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
