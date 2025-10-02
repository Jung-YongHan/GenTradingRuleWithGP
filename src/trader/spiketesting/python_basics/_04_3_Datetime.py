import pandas as pd
from datetime import datetime
import datetime as dt


fmt = '%Y-%m-%d %H:%M:%S'
datetime_start = datetime.strptime('2010-01-01 17:31:22', fmt)
datetime_end = datetime.strptime('2010-01-03 17:31:22', fmt)

minutes_diff = (datetime_end - datetime_start).total_seconds() / 60.0
print(minutes_diff)

datetime_start = datetime.strptime('2010-01-01 17:31:22', fmt)
datetime_end = datetime.strptime('2010-01-01 17:32:22', fmt)

minutes_diff = (datetime_end - datetime_start).total_seconds() / 30.0
print(minutes_diff)