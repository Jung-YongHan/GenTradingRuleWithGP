from talib import abstract

from bt4.utils.mylog import init_log
from bt4.utils.python_utils import load_func_from_module
import numpy as np
log = init_log()
import pandas as pd
class TAIMgr:

    def __init__(self, quote = None, ex_type = None, market_dfs = None):
        self.quote = quote
        if quote is not None:
            self.cdl_market_dfs = self.quote.get_candle_types(ex_type)
        self.ex_type = ex_type
        self.market_dfs = market_dfs
        if self.market_dfs is None:
            self.compute_multi_markets = True
        else:
            self.compute_multi_markets = False

    def get_quote(self):
        return self.quote

    # def compute_tai(self, ):
    def get_nary(self, func_name, func_params, cdl_type, sources, return_raw = False, alias=None, market_tai=None):
        """
                :param func_name: functions in tailib
                :param func_params: function argumenets
                :param cdl_type: CandleType.DAYS, ...
                :param sources: QItem.open, QItem.high
                :return: dict[market, returns]
                """

        def __call_func_unit__(market_df, func_name, func_params, sources, market):
            nonlocal market_tai
            nonlocal alias
            nonlocal cdl_type
            input_list = []
            for source in sources :
                if source in market_df.columns :
                    temp_float = market_df[source].astype(float)
                    input_list.append(temp_float.to_numpy())
                else:
                    if (market_tai is not None) and (alias is not None) and (market is not None):
                        for key in market_tai.keys():
                            if key.startswith(market):
                                if source.endswith("]"):  #[0], [1], [2] # for nary variables
                                    src_alias = source[:source.index("[")]
                                    raw_vals = market_tai[key][f"{src_alias}_raw"]
                                    idx =  int(source[source.index("[")+1: source.index("]")])
                                    if isinstance(raw_vals[idx], (list, np.ndarray)) :
                                        input_list.append(raw_vals[idx])
                                    else :
                                        input_list.append(raw_vals[idx].to_numpy())
                                else:
                                    raw_vals = market_tai[key][f"{source}_raw"]
                                    input_list.append(raw_vals)

            dfs = {}
            context = {}
            dfs[cdl_type] = market_df
            context["candle_type"] = cdl_type
            context["dfs"] = dfs

            result, result_raw = self.__call_talib_nary__(func_name, func_params, input_list, context)
            return result, result_raw

        tai = {}

        if self.compute_multi_markets :
            market_dfs = self.cdl_market_dfs[cdl_type]

            for market in market_dfs:
                input_list = []
                market_df = market_dfs[market]
                result, result_raw = __call_func_unit__(market_df, func_name, func_params, sources, market)

                if return_raw == True:
                    tai[market + '_raw'] = result_raw
                tai[market] = result
        else:
            market_df = market_dfs[cdl_type]
            result, result_raw = __call_func_unit__(market_df, func_name, func_params, sources, None)

            if return_raw == True :
                tai[func_name + '_raw'] = result_raw
            tai[func_name] = result
        return tai

    def get_unary(self, func_name, func_args, cdl_type, func_in_cols, return_raw = False, alias=None, market_tai=None):
        result = self.get_nary(func_name, func_args, cdl_type, func_in_cols, return_raw, alias, market_tai)
        for market in result:
            if not market.endswith('_raw'):
                result[market] = result[market][0]
        return result

    def call_talib_unary(self, func_name, func_args, input_list, context = None, return_raw = False):
        result, result_raw = self.__call_talib_nary__(func_name, func_args, input_list, context)
        if not return_raw:
            return result[0]
        else:
            return result[0], result_raw

    def call_talib_nary(self, func_name, func_args, input_list, context = None, return_raw = False):
        result, result_raw = self.__call_talib_nary__(func_name, func_args, input_list, context)

        if not return_raw :
            return result
        else :
            return result, result_raw

    def __call_talib_nary__(self, func_name, func_args, input_list, context):
        try:
            func = abstract.Function(func_name)
            result_raw = func(*input_list, *func_args)  ### TALib CALL Function
        except TypeError as e:
            log.error(f"Error of TALIB:", e)
        except Exception as e:
            # print(f'The designated function ({func_name}) does not exist in talib. Call custom function.')
            if func_name.startswith('__ai__'):
                func = load_func_from_module(__package__ + '.CustomAIIndicators', func_name)
                func_args.append(context["candle_type"])
                func_args.append(context["dfs"])
                result_raw = func(*input_list, *func_args, **context)  # Custom AI Function
            else:
                func = load_func_from_module(__package__ + '.CustomTAIndicators', func_name)
                result_raw = func(*input_list, *func_args, **context)  # Custom CALL Function


        result = []
        if isinstance(result_raw, list):
            for result_elem in result_raw:
                result_elem = np.round(result_elem, decimals=4)  ## Result round up (e.g., 3.3333333333 --> 3.3333)
                if isinstance(result_elem, (list, np.ndarray)):
                    result.append(float(result_elem[-1]))
                elif isinstance(result_elem, pd.Series):
                    result.append(float(result_elem.iloc[-1]))
                else:
                    result.append(float(result_elem))
        else:
            if result_raw.dtype.kind == "f":
                result_raw = np.round(result_raw, decimals=4)  ## Result round up (e.g., 3.3333333333 --> 3.3333)
                if isinstance(result_raw, pd.Series):
                    result.append(float(result_raw.iloc[-1]))
                else:
                    result.append(float(result_raw[-1]))
            else:
                result.append(result_raw.iloc[-1])
        return result, result_raw