import json
import time
import datetime
import websockets
import pandas as pd

from abstract.logging import Logging
from stocks.bitfinex.defines import DEFINES

class WEBSocket (Logging):
    _channels = pd.DataFrame (data=[], columns=['base', 'quot', 'traid_status'])
    _storage = None

    def __init__ (self, storage):
        self._storage = storage

    def parse_message (self, pure_data):
        if pure_data[0] == '{':
            return json.loads (pure_data)
        elif pure_data[0] == '[':
            return pure_data [1:-1].split (',')
        else:
            return pure_data

    def register_channel (self, message):
        channel = pd.Series (data=[message['pair'][0:3].lower(), message['pair'][3:6].lower()], index=['base', 'quot'])
        channel.name = int(message['chanId'])
        self._channels = self._channels.append (channel)

        return channel

    def process_tick (self, tick):
        if len(tick) > 2:
            tb_data = [
                int(time.mktime(datetime.datetime.now().timetuple())),
                self._channels.loc[int(tick[0])].at['base'],
                self._channels.loc[int(tick[0])].at['quot'],
                float(tick[7]),
                float(tick[8])
                ]
            tb_tick = pd.Series (data=tb_data, index=['timestamp', 'base', 'quot', 'close', 'volume'])
            self.log_info ('About to throw to clickhouse:\n\t{}'.format (tb_tick))
            self._storage.insert_ticks (tb_tick)

    def route (self, message):
        self.log_info ('Web Socket message:\n\t{}'.format (message))
        if type(message) == dict:
            if message['event'] == 'subscribed':
                channel = self.register_channel (message)
            elif message['event'] != 'info':
                self.log_error (str(message))
        elif type(message) == list:
            self.process_tick (message)
        else:
            self.log_error (str(message))

    async def listen(self):
        try:
            async with websockets.connect('wss://api.bitfinex.com/ws') as websocket:
                for quot in ['usd', 'btc']:
                    for base in DEFINES.LISTEN_SYMBOLS:
                        if base != 'usd' and quot != base:
                            await websocket.send(json.dumps({"event":"subscribe", "channel":"ticker", "pair":base+quot}))
                while True:
                    message = self.parse_message(await websocket.recv())
                    self.route (message)
        except Exception as e:
            self.log_error (e)