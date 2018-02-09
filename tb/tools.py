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
import numpy as np
from scipy.signal import argrelextrema
from sklearn import linear_model
import scipy
from stocks.bitfinex.defines import DEFINES
from stocks.bitfinex import Bitfinex
from stocks.bitfinex.storage import Storage
from stocks.bitfinex.rest_socket import RESTSocket
from stocks.bitfinex.traider import Traider
from abstract.logging import Logging
#import matplotlib.pyplot as plt

window = {'minutes':60}

storage = Storage()
rest_socket = RESTSocket()

async def get_missing_periods ():
    now = datetime.datetime.now()
    period = {
        'start':time.mktime((now - datetime.timedelta (**DEFINES.REQUIRED_INTERVAL)).timetuple()),
        'end': time.mktime(now.timetuple())
        }

    missing_periods = await storage.get_missing_periods (period)

    print (period)
    print (missing_periods)

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
    data_frame = data_frame.set_index (pd.to_datetime(data_frame.loc[:, 'tick_time']).values)

    print (data_frame.shape)
    print (data_frame.head())

def no_args ():
    def holt_winters_second_order_ewma( x, span, beta ):
        N = x.size
        alpha = 2.0 / ( 1 + span )
        s = np.zeros(( N, ))
        b = np.zeros(( N, ))
        s[0] = x[0]
        for i in range( 1, N ):
            s[i] = alpha * x[i] + ( 1 - alpha )*( s[i-1] + b[i-1] )
            b[i] = beta * ( s[i] - s[i-1] ) + ( 1 - beta ) * b[i-1]
        return s

    def mirror_avg (tick):
        if float(tick.at['avg']) < float(tick.at['trend']):
            return float(tick.at['trend'])-float(tick.at['avg']) #+float(tick.at['trend'])
        else:
            return float(tick.at['avg']) - float(tick.at['trend'])

    frame = pd.read_csv ('testing/day.csv')
    frame.loc[:, 'tick_time'] = pd.to_datetime(frame.loc[:, 'tick_time'])
    frame['timestamp'] = frame.loc[:, 'tick_time'].apply (lambda tick_time: time.mktime (tick_time.timetuple()))
    frame.loc[:, 'close'] = frame.loc[:, 'close'].astype(float)
    frame = frame.set_index (pd.to_datetime(frame.loc[:, 'tick_time']).values)
    frame = frame.iloc[::-1]
    #frame = frame.loc[frame.iloc[0].name : frame.iloc[0].name + datetime.timedelta(**window)]

    frame.loc[:, 'close'] = frame.loc[:, 'close'] - frame.loc[:,'close'].min()
    frame['avg'] = holt_winters_second_order_ewma(frame.loc[:, 'close'].values , 10, 0.3 )
    frame['avg2'] = holt_winters_second_order_ewma(frame.loc[:, 'avg'].values , 10, 0.3 )
    frame.loc[:,'avg2'] = frame.loc[:,'avg2'].shift(-2)

    clf = linear_model.LinearRegression()
    clf.fit (frame.loc[:,'timestamp'].values.reshape(-1,1), frame['close'].values)
    frame['trend'] = clf.predict (frame.loc[:,'timestamp'].values.reshape(-1,1))



    frame['mirror_avg'] = frame.apply(mirror_avg, axis=1)
    frame['diff'] = frame.loc[:,'avg'].diff()

    temp = frame.iloc[frame.shape[0]-1]
    temp.at['diff'] = frame.iloc[frame.shape[0]-3].at['diff']
    frame.iloc[frame.shape[0]-1] = temp

    frame[['close', 'trend', 'avg2']].plot(figsize=(12,8))

    plt.show()

if sys.argv is not None and len (sys.argv) > 1:
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
        loop.run_until_complete(Traider().run())
        loop.close()
else:
    no_args ()