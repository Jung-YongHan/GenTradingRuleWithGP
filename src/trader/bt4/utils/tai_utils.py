

def get_unary_tai(tmgr, param, alias, market_tai, return_raw=False):
    '''
        param[0] : talib_func name               (e.g., 'sma')
        param[1] : talib func params as list     (e.g., [5])
        param[2] : CandleType as CandleType Enum (e.g., CandleType.DAYS)
        param[3] : QItem as a list               (e.g., [QItem.open, QItem.close]
    :param tmgr:
    :param param:
    :return:
    '''
    return tmgr.get_unary(param[0], param[1], param[2], param[3], return_raw, alias, market_tai)


def get_nary_tai(tmgr, param, alias, market_tai, return_raw=False):
    '''
        param[0] : talib_func name               (e.g., 'sma')
        param[1] : talib func params as list     (e.g., [5])
        param[2] : CandleType as CandleType Enum (e.g., CandleType.DAYS)
        param[3] : QItem as a list               (e.g., [QItem.open, QItem.close]
    :param tmgr:
    :param param:
    :return:
    '''
    return tmgr.get_nary(param[0], param[1], param[2], param[3], return_raw, alias, market_tai,)


def get_last_series_val_of_nary_tais(unary_sers, is_custom_tai=False):
    ret_list = []
    for ser in unary_sers:
        if not is_custom_tai:
            ret_list.append(ser.iloc[-1])
        else:
            ret_list.append(ser)
    return tuple(ret_list)
