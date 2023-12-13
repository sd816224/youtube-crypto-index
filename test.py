import datetime
import datetime


now = datetime.datetime.now()
one_hour_ago = now - datetime.timedelta(hours=1)
time_line_str=one_hour_ago.strftime("%Y-%b-%d %H:%M:%S")
print(time_line_str)