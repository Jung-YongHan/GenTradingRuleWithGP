
# from datetime import datetime as dt
from datetime import datetime as dt

simul_start = '2018-10-01T09:00:00Z'
simul_end = '2018-10-03T09:00:00Z'
# simul_start = '2018/10/01'
# simul_end = '2018/10/03'

start_date = dt.strptime(simul_start, "%Y-%m-%dT%H:%M:%SZ")
end_date = dt.strptime(simul_end, "%Y-%m-%dT%H:%M:%SZ")

# start_date = dt.strptime(simul_start, "%Y/%m/%d")
# end_date = dt.strptime(simul_end, "%Y/%m/%d")
print(start_date > end_date)
print(start_date < end_date)
#
# timeStr = '2018-07-28T12:11:32Z'
# d1 = dt.strptime(timeStr, '%Y-%m-%dT%H:%M:%SZ')
#
# timeStr2 = '2018-07-30T12:11:32Z'
# d2 = dt.strptime(timeStr, '%Y-%m-%dT%H:%M:%SZ')
# d1 = dt.datetime(2018, 5, 3)
# d2 = dt.datetime(2018, 6, 1)
# print("d1 is greater than d2 : ", d1 > d2)
# print("d1 is less than d2 : ", d1 < d2)
# print("d1 is not equal to d2 : ", d1 != d2)

from datetime import datetime as dt
a = dt.strptime("10/12/13", "%m/%d/%y")
b = dt.strptime("10/15/13", "%m/%d/%y")
print( a > b )
print( a < b )
