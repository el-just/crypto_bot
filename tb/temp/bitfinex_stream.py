import json

import pandas as pd

import asyncio
import websockets

# CHANNEL_ID  integer Channel ID
# BID float   Price of last highest bid
# BID_SIZE    float   Size of the last highest bid
# ASK float   Price of last lowest ask
# ASK_SIZE    float   Size of the last lowest ask
# DAILY_CHANGE    float   Amount that the last price has changed since yesterday
# DAILY_CHANGE_PERC   float   Amount that the price has changed expressed in percentage terms
# LAST_PRICE  float   Price of the last trade.
# VOLUME  float   Daily volume
# HIGH    float   Daily high
# LOW float   Daily low

symbols = ['usd', 'btc', 'eth', 'ltc', 'etc', 'rrt', 'zec', 'xmr', 'dsh', 'xrp', 'iot', 'eos', 'san', 'omg', 'bch', 'neo', 'etp', 'qtm', 'avt', 'edo', 'btg', 'dat', 'qsh', 'yyw', 'gnt', 'snt', 'bat', 'mna', 'fun', 'zrx', 'tnb', 'spk']
channels = pd.DataFrame ()
async def connect():
    async with websockets.connect('wss://api.bitfinex.com/ws') as websocket:
        for quot in ['usd', 'btc']:
            for base in symbols:
                if base != 'usd' and quot != base:
                    await websocket.send(json.dumps({"event":"subscribe", "channel":"ticker", "pair":base+quot}))
        while True:
            message = parse_message(await websocket.recv())
            route (message)

            # f = open ('../data/stream.s', 'a')
            # f.write (str()+'\n')
            # f.close ()

def route (message):
    if type(message) = dict:
        if pure_data.event == 'subscribed':
            register_channel (message)
        elif pure_data.event != 'info':
            log_error (str(message))
    elif type(message) == list:
        process_tick (message)
    else:
        log_error (str(message))

def register_channel ():
    channel.append ({chanId: pure_data.chanId, base: pure_data.pair[0:3], quot: pure_data.pair[3:6]})

def process_tick (tick):
    pass

def log_error ():
    pass

def parse_message (pure_data):
    if pure_data[0] == '{':
        return json.loads (pure_data)
    elif pure_data[0] == '['
        return pure_data [1:-1].split (',')
    else:
        return pure_data



loop = asyncio.get_event_loop()
loop.run_until_complete(connect())
loop.close()