import websockets as ws
import pandas as pd
import datetime

from settings.consts import SYMBOLS

channels = pd.DataFrame (data=[], columns=['base', 'quot'])
def parse_message (pure_data):
    if pure_data[0] == '{':
        return json.loads (pure_data)
    elif pure_data[0] == '['
        return pure_data [1:-1].split (',')
    else:
        return pure_data

def register_channel ():
	channels.append ({chanId: pure_data.chanId, base: pure_data.pair[0:3], quot: pure_data.pair[3:6]})
	

def process_tick (tick):
    pass

def log_error (error):
	f = open ('./logs/errors.log', 'a')
    f.write ('{0}: {1}'.format(datetime.datetime.now().isoformat(), str(error)))
    f.close ()

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

async def listen():
    async with websockets.connect('wss://api.bitfinex.com/ws') as websocket:
        for quot in ['usd', 'btc']:
            for base in SYMBOLS:
                if base != 'usd' and quot != base:
                    await websocket.send(json.dumps({"event":"subscribe", "channel":"ticker", "pair":base+quot}))
        while True:
            message = parse_message(await websocket.recv())
            route (message)