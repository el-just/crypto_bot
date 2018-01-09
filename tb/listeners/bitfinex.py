import websockets as ws
import pandas as pd
import datetime
import time
import json
import clickhouse.clickhouse as clickhouse

from settings.consts import SYMBOLS

class Bitfinex ():
    _channels = pd.DataFrame (data=[], columns=['base', 'quot'])

    def parse_message (self, pure_data):
        if pure_data[0] == '{':
            return json.loads (pure_data)
        elif pure_data[0] == '[':
            return pure_data [1:-1].split (',')
        else:
            return pure_data

    def register_channel (self, message):
        channel = pd.Series (data=[message['pair'][0:3], message['pair'][3:6]], index=['base', 'quot'])
        channel.name = int(message['chanId'])
        self._channels = self._channels.append (channel)

    def process_tick (self, tick):
        if len(tick) > 2:
            tb_data = [
                time.mktime(datetime.datetime.now().timetuple()),
                self._channels.loc[int(tick[0])].at['base'],
                self._channels.loc[int(tick[0])].at['quot'],
                float(tick[7]),
                float(tick[8])
                ]
            tb_tick = pd.Series (data=tb_data, index=['timestamp', 'base', 'quot', 'close', 'volume'])
            
            clickhouse.insert_tick (tb_tick)
            raise Warning ('asd')

    def log_error (self, error):
        f = open ('./logs/errors.log', 'a')
        f.write ('{0}: {1}'.format(datetime.datetime.now().isoformat(), str(error)))
        f.close ()

    def route (self, message):
        if type(message) == dict:
            if message['event'] == 'subscribed':
                self.register_channel (message)
            elif message['event'] != 'info':
                self.log_error (str(message))
        elif type(message) == list:
            self.process_tick (message)
        else:
            self.log_error (str(message))

    async def listen(self):
        async with ws.connect('wss://api.bitfinex.com/ws') as websocket:
            for quot in ['usd', 'btc']:
                for base in SYMBOLS:
                    if base != 'usd' and quot != base:
                        await websocket.send(json.dumps({"event":"subscribe", "channel":"ticker", "pair":base+quot}))
            while True:
                message = self.parse_message(await websocket.recv())
                self.route (message)