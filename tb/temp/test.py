'''
BotFather, [12.01.18 17:14]
Done! Congratulations on your new bot. You will find it at t.me/ej_dev_tb_bot. You can now add a description, about section and profile picture for your bot, see /help for a list of commands. By the way, when you've finished creating your cool bot, ping our Bot Support if you want a better username for it. Just make sure the bot is fully operational before you do this.

Use this token to access the HTTP API:
509542441:AAF3UMLVxRKLD1jT9W9IRc6fcFMnT7pBFTk

https://api.telegram.org/bot509542441:AAF3UMLVxRKLD1jT9W9IRc6fcFMnT7pBFTk/sendMessage?chat_id=276455649&text=wtf

For a description of the Bot API, see this page: https://core.telegram.org/bots/api

===========


{"event":"info","version":1.1}
{"event":"subscribed","channel":"ticker","chanId":1,"pair":"BTCUSD"}
[1,14572,64.62977371,14583,48.78065323,-779,-0.0507,14585,63518.10813398,15479,13755]
{"event":"subscribed","channel":"ticker","chanId":3,"pair":"ETHUSD"}
[3,1191.4,156.95650816,1192.4,919.04951283,55.2,0.0486,1191.6,349747.62944201,1250,965.18]
{"event":"subscribed","channel":"ticker","chanId":10,"pair":"LTCUSD"}
[10,244.96,1682.60984158,245.55,869.76850418,-11.33,-0.0442,244.96,319916.10135213,259.26,230.18]
{"event":"subscribed","channel":"ticker","chanId":19,"pair":"ETCUSD"}
'''

import datetime
import time
import urllib.parse
import asyncio
import aiohttp
import pandas as pd

PYTHONASYNCIODEBUG=1

class RestRequest ():
    _url = 'https://api.bitfinex.com//v2/candles/trade:1m:tBTCUSD/hist?'
    _timeline = pd.DataFrame (data=[], columns=['request'])
    _queue = []
    _limit = 10

    def __init__ (self):
        pass

    async def make_request (self, request):
        request.name = datetime.datetime.now()
        self._timeline = self._timeline.append (request)
        async with aiohttp.ClientSession() as session:
            async with session.get(request.at["request"]) as resp:
                text = await resp.text()
                f = open ('../logs/errors.log', 'a+')
                f.write ('{}\n'.format(str(text)))
                f.close ()

    async def send_request (self, params):
        now = datetime.datetime.now()

        request = pd.Series (data=[self._url + urllib.parse.urlencode(params)], index=['request'])
        self._timeline = self._timeline.loc [now - datetime.timedelta(minutes=1): now]

        if self._timeline.loc[:, "request"].count() < self._limit:
            await self.make_request (request)
        else:
            self._queue.append (request)
            print(len(self._queue))
            await asyncio.sleep (len(self._queue)*60)
            await self.make_request (self._queue.pop (0))

# start = 1507833535
# end = 1515609535

# available_data = [(datetime.datetime(2018, 1, 10, 11, 36, 30), 'btc', 'usd', 0), (datetime.datetime(2018, 1, 10, 15, 39, 22), 'btc', 'usd', 0), (datetime.datetime(2018, 1, 10, 14, 15, 35), 'btc', 'usd', 1223)]

# default_tick_period = 60
# default_miss_period = 600
# periods = []
# if len (available_data) > 0:
#     #если последняя доступная дата периода слишком поздняя, то нужно достать все что раньше, до доступной даты минус период тика
#     if time.mktime(available_data[0][0].timetuple()) - start > default_miss_period:
#         periods.append ({
#             'start': start,
#             'end': time.mktime(available_data[0][0].timetuple()) - default_tick_period
#             })

#     #посмотрим есть ли пропуски
#     for idx in range(2,len(available_data)):
#         periods.append ({
#             'start':time.mktime(available_data[idx][0].timetuple()) - int(available_data[idx][3]),
#             'end':time.mktime(available_data[idx][0].timetuple()) - default_tick_period
#             })
    
#     if end - time.mktime(available_data[1][0].timetuple()) > default_miss_period:
#         periods.append ({
#             'start': time.mktime(available_data[1][0].timetuple())+default_tick_period,
#             'end': end
#             })
# else:
#     periods.append ({'start': start, 'end': end})

# available_gap = 59940
# request_periods = []
# for period in periods:
#     step_date = period['start']
#     while step_date < period['end']:
#         end_date = step_date + available_gap if period['end'] - (step_date + available_gap) > 0 else period['end']
#         request_periods.append ({
#             'start': step_date,
#             'end': end_date
#             })

#         step_date = end_date + default_tick_period

# req_processor = RestRequest()
# async def get_all_data (period):
#     for period in request_periods:
#         params = {'limit':1000, 'start':str(int(period['start']))+'000', 'end':str(int(period['end']))+'000'}
#         await req_processor.send_request (params)

# ioloop = asyncio.get_event_loop()
# ioloop.run_until_complete(get_all_data(request_periods))
# ioloop.close()

class Defines ():
    #for traiding in days
    REQUIRED_PERIOD = 90

    #interval in seconds which assuming as miss
    MISS_PERIOD = 600

    #default gap between ticks in seconds
    TICK_PERIOD = 60

    #available gap for rest request
    AVAILABLE_GAP = 59940

    #requests per minute
    REST_REQUEST_LIMIT = 10

    #available assets
    SYMBOLS = ['usd', 'btc', 'eth', 'ltc', 'etc', 'rrt', 'zec', 'xmr', 'dsh', 'xrp', 'iot', 'eos', 'san', 'omg', 'bch', 'neo', 'etp', 'qtm', 'avt', 'edo', 'btg', 'dat', 'qsh', 'yyw', 'gnt', 'snt', 'bat', 'mna', 'fun', 'zrx', 'tnb', 'spk']

    #TODO: убрать в базу
    WITHDRAWAL_FEES = [5.0, 0.0005, 0.01, 0.001, 0.01, '', 0.001, 0.04, 0.01, 0.02, None, 0.1, 0.1, 0.1, 0.0001, None, 0.01, 0.01, 0.5, 0.5, None, 1.0, None, None, '', '', '', '', '', '', '', '']

    #The minimum order size is 0.01 for BTC and ZEC and 0.1 for all other cryptocurrencies    
    def MINIMUM_ORDER_SIZE (self, symbol):
        return 0.01 if symbol in ('btc', 'zec') else 0.1   

DEFINES = Defines ()

now = datetime.datetime.now()
print(time.mktime((now - datetime.timedelta (days=DEFINES.REQUIRED_PERIOD)).timetuple()))
print (time.mktime(now.timetuple()))