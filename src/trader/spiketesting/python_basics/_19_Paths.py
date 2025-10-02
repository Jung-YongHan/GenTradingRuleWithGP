import pandas as pd
import os
from os.path import dirname, join

print(__file__)
print(dirname(__file__))
print(dirname(dirname(__file__)))

file_name = 'KRW-BTC_DAYS.csv'

project_root = dirname(dirname(__file__))
output_path = join(project_root, f'data\\{file_name}')
print(output_path)
print(os.path.isfile(output_path))
if os.path.isfile(output_path):
    df = pd.read_csv(output_path, header=None)

    print(df.head())