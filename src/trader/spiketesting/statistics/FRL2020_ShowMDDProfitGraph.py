import pandas as pd

from bt4.common.ResultAnalyzer import analyze_result
from bt4.core.ReportSupport import FileReportStorage

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

filename = 'FRL_PLUS_MINUS_DI_Strategy_BeforeRefactoring_5208.csv'
# filename = 'FRL_Price_Strategy_BeforeRefactoring_22096.csv'

df = pd.read_csv(filename)

strategy_name = 'DMI'
rs = FileReportStorage()
rs.set_params('frl2020',True)
analyze_result(df, strategy_name, rs)
