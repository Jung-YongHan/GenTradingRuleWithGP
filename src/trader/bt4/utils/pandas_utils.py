
import numpy as np
import pandas as pd
from bt4.utils.python_utils import now_dt

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


def create_df_with_series(series):
    return pd.DataFrame(series)

def convert_index_into_datetime(df):
    # df.index = pd.to_datetime(df.index, format='%y-%m-%dT%H:%M:%S')
    df.index = pd.to_datetime(df.index)
    return df

def get_excluded_indexes_from_list(df, list):
    list_idx = pd.Index(list)
    result = list_idx.isin(df.index.tolist())
    not_existing_value_list = list_idx[result == False].tolist()
    return not_existing_value_list

def get_date_range(df, date_col, start_date_str, end_date_str):
    return df[(df[date_col] >= start_date_str) & (df[date_col] <= end_date_str)]

def get_first_row(df):
    return df.head(1)

def get_last_row(df):
    return df.tail(1)

def remove_first_row(df):
    df.drop(df.head(1).index, inplace=True)
    # df.drop(index=df.index[0],axis=0,inplace=True)

def remove_last_row(df: object) -> object:
    df.drop(df.tail(1).index, inplace=True)


@DeprecationWarning
def replicate_last_row(df):
    return pd.concat([df, pd.DataFrame(df.iloc[-1]).T])


def insert_dummy_last_row(df):
    return pd.concat([df, pd.DataFrame(data=0, index=[pd.to_datetime(now_dt())], columns=df.columns)])


def append_new_row(df, new_row, ignore_index = True):
    return pd.concat([df, pd.DataFrame(new_row).T], ignore_index=ignore_index)
    # return df.append(new_row, ignore_index)

def append_dummy_row_first(df, ignore_index = True):
    return pd.concat([pd.DataFrame({}, index=['dummy']), df], ignore_index=ignore_index)



def update_last_row(df: object, new_row: object) -> object:
    df.iloc[-1] = new_row
    # df.loc[df.index[-1]] = new_row

def rename_columns(df, old_new_col_name_dic):
    return df.rename(columns = old_new_col_name_dic, inplace = True)

def rename_columns2(df, old_new_col_name_dic):
    return df.rename(columns = old_new_col_name_dic)

def shift_rows_of_columns(df, column_list, period):
    for column in column_list:
        df[column] = df[column].shift(period)
    return df

def shift(arr, num):
    arr = np.roll(arr, num)
    if num < 0:
        np.put(arr, range(len(arr) + num, len(arr)), np.nan)
    elif num > 0:
        np.put(arr, range(num), np.nan)
    return arr

def sort_df(df, index_col, ascending=True):
    df.reset_index(drop=True)
    df.set_index([index_col], drop=False, inplace=True)
    df.sort_index(inplace=True, ascending=ascending)

def sort_df_with_multi_index(df, list_of_index_cols):
    df.reset_index(drop=True)
    df.set_index(list_of_index_cols, drop=False, inplace=True)
    df.sort_index(inplace=True, ascending=True)

import pandas as pd

def divide_period(start_pdt, end_pdt, num_of_split):
    bt_period = pd.date_range(start=start_pdt, end=end_pdt, freq='M')
    bins = pd.date_range(start=start_pdt, end=end_pdt, periods=num_of_split+1)
    results = pd.cut(bt_period, bins=bins)
    return results.categories