import sys
import time
import asyncio
import datetime
import websockets
from stocks.bitfinex.defines import DEFINES
from stocks.bitfinex import Bitfinex
from stocks.bitfinex.storage import Storage
from stocks.bitfinex.rest_socket import RESTSocket
from abstract.Logging import Logging

storage = Storage()
rest_socket = RESTSocket(storage)
async def get_missing_periods ():
    now = datetime.datetime.now()
    missing_periods = await storage.get_missing_periods ({
        'start':time.mktime((now - datetime.timedelta (days=DEFINES.REQUIRED_PERIOD)).timetuple()),
        'end': time.mktime(now.timetuple())
        })

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

async def websocket_start ():
    async with websockets.connect('wss://api.bitfinex.com/ws') as websocket:
        await websocket.send(json.dumps({"event":"subscribe", "channel":"ticker", "pair":'btcusd'}))
        async for message in websocket:
            Logging.log_info (message)

if sys.argv[1] == 'missing_periods':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_missing_periods())
    loop.close()
elif sys.argv[1] == 'websocket_start':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(websocket_start())
    loop.close()