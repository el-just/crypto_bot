import datetime
import time
import urllib.parse
import asyncio
import aiohttp

start = 1507833535
end = 1515609535

available_data = [(datetime.datetime(2018, 1, 10, 11, 36, 30), 'btc', 'usd', 0), (datetime.datetime(2018, 1, 10, 15, 39, 22), 'btc', 'usd', 0), (datetime.datetime(2018, 1, 10, 14, 15, 35), 'btc', 'usd', 1223)]

default_tick_period = 60
default_miss_period = 600
periods = []
if len (available_data) > 0:
    #если последняя доступная дата периода слишком поздняя, то нужно достать все что раньше, до доступной даты минус период тика
    if time.mktime(available_data[0][0].timetuple()) - start > default_miss_period:
        periods.append ({
            'start': start,
            'end': time.mktime(available_data[0][0].timetuple()) - default_tick_period
            })

    #посмотрим есть ли пропуски
    for idx in range(2,len(available_data)):
        periods.append ({
            'start':time.mktime(available_data[idx][0].timetuple()) - int(available_data[idx][3]),
            'end':time.mktime(available_data[idx][0].timetuple()) - default_tick_period
            })
    
    if end - time.mktime(available_data[1][0].timetuple()) > default_miss_period:
        periods.append ({
            'start': time.mktime(available_data[1][0].timetuple())+default_tick_period,
            'end': end
            })
else:
    periods.append ({'start': start, 'end': end})

available_gap = 59940
request_periods = []
for period in periods:
    step_date = period['start']
    while step_date < period['end']:
        end_date = step_date + available_gap if period['end'] - (step_date + available_gap) > 0 else period['end']
        request_periods.append ({
            'start': step_date,
            'end': end_date
            })

        step_date = end_date + default_tick_period


for period in request_periods:
    params = {'limit':1000, 'start':str(int(period['start']))+'000', 'end':str(int(period['end']))+'000'}
    print ('https://api.bitfinex.com//v2/candles/trade:1m:tBTCUSD/hist?'+urllib.parse.urlencode(params))