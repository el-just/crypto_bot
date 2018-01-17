import sys
import time
import asyncio
import datetime
import json
import websockets
import hmac
import hashlib
import time
import pandas as pd
from stocks.bitfinex.defines import DEFINES
from stocks.bitfinex import Bitfinex
from stocks.bitfinex.storage import Storage
from stocks.bitfinex.rest_socket import RESTSocket
from abstract.logging import Logging

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

def login ():
    nonce = int(time.time() * 1000000)
    auth_payload = 'AUTH{}'.format(nonce)
    signature = hmac.new(
        DEFINES.PATTERN.encode(),
        msg = auth_payload.encode(),
        digestmod = hashlib.sha384
        ).hexdigest()

    return {
        'apiKey': DEFINES.PATH,
        'event': 'auth',
        'authPayload': auth_payload,
        'authNonce': nonce,
        'authSig': signature
        }

async def websocket_start ():
    async with websockets.connect('wss://api.bitfinex.com/ws') as websocket:
        await websocket.send(json.dumps({"event":"subscribe", "channel":"ticker", "pair":'btcusd'}))
        await websocket.send(json.dumps(login()))
        async for message in websocket:
            Logging.log_info (message)

async def straregy_testing ():
    now = datetime.datetime.now()
    
    start = int(time.mktime((now - datetime.timedelta (days=DEFINES.REQUIRED_PERIOD)).timetuple()))
    end = int(time.mktime(now.timetuple()))

    query = '''
        SELECT * FROM tb.ticker
        WHERE tick_time >= toDateTime({start}) AND tick_time <= toDateTime ({end})
        ORDER BY tick_time DESC FORMAT CSVWithNames
        '''.format (start=start, end=end)
    data_frame = await storage.execute (query)
    data_frame.loc[:, 'tick_time'] = pd.to_datetime(data_frame.loc[:, 'tick_time']).astype(int) / 1000000000
    data_frame = data_frame.set_index (pd.to_datetime(data_frame.loc[:, 'tick_time']))

    print (data_frame.shape)
    print (data_frame.head())

# loop = asyncio.get_event_loop()
# loop.run_until_complete(websocket_start())
# loop.close()

if sys.argv[1] == 'missing_periods':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_missing_periods())
    loop.close()
elif sys.argv[1] == 'websocket_start':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(websocket_start())
    loop.close()
elif sys.argv[1] == 'strategy':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(straregy_testing())
    loop.close()