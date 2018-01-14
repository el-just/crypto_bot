import sys
import time
import asyncio
import datetime
from stocks.bitfinex.defines import DEFINES
from stocks.bitfinex import Bitfinex
from stocks.bitfinex.storage import Storage

storage = Storage()
async def get_missing_periods ():
    now = datetime.datetime.now()
    missing_periods = await storage.get_missing_periods ({
        'start':time.mktime((now - datetime.timedelta (days=DEFINES.REQUIRED_PERIOD)).timetuple()),
        'end': time.mktime(now.timetuple())
        })

    if missing_periods is not None:
        for period in missing_periods:
            print ('{0} - {1}'.format (datetime.datetime.fromtimestamp(period['start'])), datetime.datetime.fromtimestamp(period['end']))
    else:
        print ('periods are up to date')

if sys.argv[1] == 'missing_periods':
    task = get_missing_periods

loop = asyncio.get_event_loop()
loop.run_until_complete(task())
loop.close()