import datetime
import time

end = time.mktime(datetime.datetime.now().timetuple())
start = time.mktime((datetime.datetime.now() - datetime.timedelta (days=90)).timetuple())

print (end, start)

