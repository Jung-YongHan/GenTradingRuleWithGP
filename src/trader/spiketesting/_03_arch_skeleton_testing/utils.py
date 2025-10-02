
import pandas as pd

def divide_period(start_pdt, end_pdt, num_of_split):
    bt_period = pd.date_range(start=start_pdt, end=end_pdt, freq='M')
    bins = pd.date_range(start=start_pdt, end=end_pdt, periods=num_of_split+1)
    results = pd.cut(bt_period, bins=bins)
    return results.categories