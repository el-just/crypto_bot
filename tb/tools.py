import sys
import time
import asyncio
import datetime
from stocks.bitfinex.defines import DEFINES
from stocks.bitfinex import Bitfinex
from stocks.bitfinex.storage import Storage
from stocks.bitfinex.rest_socket import RESTSocket

storage = Storage()
rest_socket = RESTSocket(storage)
async def get_missing_periods ():
    now = datetime.datetime.now()
    with open('./stocks/bitfinex/sql/missing_periods.sql') as f:
        missing_periods_sql = f.read()

        available_data = await storage.execute (missing_periods_sql.format(base='btc', quot='usd', start=time.mktime((now - datetime.timedelta (days=DEFINES.REQUIRED_PERIOD)).timetuple()), end=time.mktime(now.timetuple()), default_miss_time=DEFINES.MISS_PERIOD))
        # missing_periods = await storage.get_missing_periods ({
        #     'start':time.mktime((now - datetime.timedelta (days=DEFINES.REQUIRED_PERIOD)).timetuple()),
        #     'end': time.mktime(now.timetuple())
        #     })

        print (available_data)

        raise Warning ('asd')

        requests = []
        if missing_periods is not None:
            for period in missing_periods:
                print ('{0} - {1}'.format (datetime.datetime.fromtimestamp(period['start']), datetime.datetime.fromtimestamp(period['end'])))
                for fracted in rest_socket.fract_period (period):
                    requests.append (fracted)
                    print (rest_socket.request_text (fracted))

            print ('About to send {0} requests. Which equals {1} minutes of time'. format (len(requests), len(requests) / 10 - 1))

        else:
            print ('periods are up to date')

if sys.argv[1] == 'missing_periods':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_missing_periods())
    loop.close()
