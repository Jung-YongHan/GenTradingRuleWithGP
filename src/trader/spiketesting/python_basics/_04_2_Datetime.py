
# from datetime import datetime as dt
from future.backports.datetime import datetime

from bulltrader.core.SimulationSupport import get_xh_before_string
import pytz
from dateutil.parser import parse
from datetime import datetime as dt, timedelta
import datetime

def get_hour(date):
    date_time = dt.strptime(date, "%Y-%m-%dT%H:%M:%S")
    hour = date_time.hour
    is_zero_minute = True if date_time.minute == 0 else False
    return hour, is_zero_minute

# test_date = '2018-10-01T09:00:00Z'
test_date = '2018-10-01T01:01:00'

hour, is_zero_minute = get_hour(test_date)
print(hour, is_zero_minute)

date_time = dt.strptime(test_date, "%Y-%m-%dT%H:%M:%S")
h4_before_string = get_xh_before_string(4,date_time)
print('4h_before_string:', h4_before_string)

##################################################
gmt_time = 'Mon, 15 Nov 2021 09:56:15 GMT'
dt_response = parse(gmt_time)
dt_korea = dt_response.astimezone(tz=pytz.timezone("Asia/Seoul"))

print(f"dt_response: {dt_response}")
print(f"dt_korea: {dt_korea}")
print(f'sec:{dt_korea.second}')

##################################################
base_time = '2019-01-01T01:00:00'
base_time = '2018-12-31T20:00:00'
base_time = '2018-12-31T09:00:00'
initial_time = dt.strptime(base_time, '%Y-%m-%dT%H:%M:%S')
time = datetime.time(9, 0, 0)

if initial_time.hour >= 9:
    date = datetime.date(initial_time.year, initial_time.month, initial_time.day)
    range_end = dt.combine(date, time)
else:
    range_end = initial_time - timedelta(days=1)
    date = datetime.date(range_end.year, range_end.month, range_end.day)
    range_end = dt.combine(date, time)

range_end_time = dt.strftime(range_end, "%Y-%m-%dT%H:%M:%S")
print(range_end_time)
