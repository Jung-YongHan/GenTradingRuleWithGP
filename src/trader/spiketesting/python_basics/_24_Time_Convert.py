import logging
import logging.handlers
from datetime import timedelta

import pandas as pd

from bulltrader.utils.python_utils import str2dt


if __name__ == '__main__':
    # MyLogger()
    # TestLoggingClass()
    temp = pd.read_csv('../../data/cache/tais/daily_tais_cache_base_KRW-XRP.csv')
    print(temp)
    print(temp['candle_date_time_kst'] )
    temp['candle_date_time_kst'] = temp['candle_date_time_kst'].map( lambda x: str2dt(x) + timedelta(minutes=59))
    print(temp)
    temp.to_csv('../../data/cache/tais/daily_tais_cache_base_KRW-XRP.csv')
