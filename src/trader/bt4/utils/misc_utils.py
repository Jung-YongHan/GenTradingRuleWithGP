

### Extract Simulation Times from timeframes
from bt4.Constants import R
from bt4.resource_path_mgr import RPath
from bt4.utils.market_utils import compute_sell_timeframes
from bt4.utils.python_utils import split_hour_min, load_class_from_module


def convert_float_2_int_of_dict(dict):
    for key in dict:
        try:
            f_val = float(dict[key])
            dict[key] = int(f_val)
        except ValueError:
            pass

def calibrate_simul_env2(r, parameters):
    if 'timeframes' in parameters[r.STGY.PARAMS]:
        timeframe_list = parameters[r.STGY.PARAMS]['timeframes']
        if 'timegap' in parameters[r.STGY.PARAMS]:
            timegap = parameters[r.STGY.PARAMS]['timegap']

            simul_time_set = {'08:59'}
            simul_time_set.update(timeframe_list)
            _, _, sell_timeframe_list = compute_sell_timeframes(timeframe_list, timegap)
            simul_time_set.update(sell_timeframe_list)

            parameters[r.OP.BT.TIME] = list(simul_time_set)

    return parameters


def load_bt3_config(stgy_config_path):
    '''
        config: bt3_config.upbit.ws_day_hdg_vol
    :param config:
    :return:
    '''
    r = R()
    params = {}

    ## Load Strategy Config
    stgy_cfg_obj = load_class_from_module(stgy_config_path, 'Config')
    stgy_cfg_obj.load_params(r, params)

    ## Load Common Config
    exchange = stgy_config_path.split('.')[1]
    comm_cfg_module = f'bt3_config.{exchange}.bt_{exchange}_common_conf'
    comm_cls = f'Bt_{exchange}_CommonConfig'
    common_config = load_class_from_module(comm_cfg_module, comm_cls)
    common_config.load_params(r, params)
    return params

def load_bt4_config(stgy_config_path):
    '''
        config: bt3_config.upbit.ws_day_hdg_vol
    :param config:
    :return:
    '''
    r = R()
    params = {}

    ## Load Strategy Config
    stgy_cfg_obj = load_class_from_module(stgy_config_path, 'Config')
    stgy_cfg_obj.load_params(r, params)

    ## Load Common Config
    exchange = stgy_config_path.split('.')[1]
    cfg_root = RPath.instance().bt_cfg_root_module()
    comm_cfg_module = f"{cfg_root}.{exchange}.bt_{exchange}_common_conf"
    comm_cls = f'Bt_{exchange}_CommonConfig'
    common_config = load_class_from_module(comm_cfg_module, comm_cls)
    common_config.load_params(r, params)
    return params

@DeprecationWarning
def calibrate_simul_env(r, parameters):
    if 'timeframes' in parameters[r.STGY.PARAMS]:
        timeframe_list = parameters[r.STGY.PARAMS]['timeframes']
        if 'timegap' in parameters[r.STGY.PARAMS]:
            timegap = parameters[r.STGY.PARAMS]['timegap']

            simul_time_set = {'08:59'}
            simul_time_set.update(timeframe_list)
            _, _, sell_timeframe_list = compute_sell_timeframes(timeframe_list, timegap)
            simul_time_set.update(sell_timeframe_list)

            parameters[r.OP.BT.TIME] = list(simul_time_set)

        tai_list = parameters[r.OP.BT.TA_INDICATORS]
        adjusted_tai_list = []
        for tai in tai_list:
            if tai.endswith('_'):
                for simul_time in parameters[r.OP.BT.TIME]:
                    t_hour, t_min = split_hour_min(simul_time)
                    t_hour = t_hour + 1
                    t_hour = 0 if t_hour == 24 else t_hour
                    t_h_prefix = '0' if t_hour == 24 else ''
                    target_tai = f'{tai}{t_h_prefix}{t_hour}'
                    adjusted_tai_list.append(target_tai)
                # tai_list.remove(tai)
            else:
                adjusted_tai_list.append(tai)
        parameters[r.OP.BT.TA_INDICATORS] = adjusted_tai_list
    return parameters


def rearrange_market_tais(markets, tai_holder, tai_name, tai, signature=None):
    for market in markets:
        if signature is None:
            key = market
        else:
            key = f"{market}_{signature}"

        if key not in tai_holder :
            tai_holder[key] = {}

        if tai_name not in tai_holder[key] :
            tai_holder[key][tai_name] = tai[market]
            tai_holder[key][f"{tai_name}_raw"] = tai[f"{market}_raw"]
            if isinstance(tai[market], list):
                for idx, nary_val in enumerate(tai[market]):
                    tai_holder[key][f"{tai_name}[{idx}]"] = nary_val
