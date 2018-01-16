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
    _socket = None

    def __init__ (self, storage=None):
        self._storage = storage

    def parse_message (self, pure_data):
        if type(pure_data) == str:
            if pure_data[0] == '{':
                return json.loads (pure_data)
            elif pure_data[0] == '[':
                return pure_data [1:-1].split (',')
            else:
                return pure_data
        else:
            return pure_data

    def register_channel (self, message):
        channel = pd.Series (data=[message['pair'][0:3].lower(), message['pair'][3:6].lower()], index=['base', 'quot'])
        channel.name = int(message['chanId'])
        self._channels = self._channels.append (channel)

        return channel

    def clear_channels (self):
        self._channels = pd.DataFrame (data=[], columns=['base', 'quot', 'traid_status'])

    async def process_tick (self, tick):
        try:
            if len(tick) > 2:
                if self._channels.loc[int(tick[0])]:
                    tb_data = [
                        int(time.mktime(datetime.datetime.now().timetuple())),
                        self._channels.loc[int(tick[0])].at['base'],
                        self._channels.loc[int(tick[0])].at['quot'],
                        float(tick[7]),
                        float(tick[8])
                        ]
                    tb_tick = pd.Series (data=tb_data, index=['timestamp', 'base', 'quot', 'close', 'volume'])
                    self.log_info ('About to throw to clickhouse:\n\t{}'.format (tb_tick))
                    await self._storage.insert_ticks (tb_tick)
                else:
                    raise Warning (str(tick), 'Data for unknown channel')
        except Exception as e:
            self.log_error (e)

    async def process_event (self, message):
        if message['event'] == 'subscribed':
            self.register_channel (message)
        elif message['event'] == 'info':
            if 'code' in message:
                code = int(str(event['code']).replace ('"',''))

                # Stop/Restart Websocket Server (please reconnect)
                if code == 20051:
                    self.log_telegram ('Stock requested for restarting webcosket connection. Closing connection...')
                    self.clear_channels()
                    await self._socket.close(code=1000, reason='Request of the stock')
                # Entering in Maintenance mode. Please pause any activity and resume after receiving the info message 20061 (it should take 120 seconds at most)
                elif code == 20060:
                    self.log_telegram ('Entering in Maintenance mode')
                # Maintenance ended. You can resume normal activity. It is advised to unsubscribe/subscribe again all channels
                elif code == 20061:
                    self.log_telegram ('Maintenance ended. Restarting webcosket connection')
                    self.clear_channels()
                    await self._socket.close(code=1000, reason='Restart because of maintenance ended')
                else:
                    self.log_error ('ERROR::Unknown event\n\t{0}'.format(str(message)))
            # right after connecting you receive an info message that contains the actual version of the websocket stream
            elif 'version' in message:
                self.log_info ('version:{0}:{1}'.format(type(message['version']), str(message['version'])))
            else:
                self.log_error ('ERROR::Unknown event\n\t{0}'.format(str(message)))
        else:
            self.log_error (str(message))

    async def route (self, message):
        try:
            self.log_info ('Web Socket message:\n\t{}'.format (message))
            if type(message) == dict:
                await self.process_event (message)
            elif type(message) == list:
                await self.process_tick (message)
            else:
                self.log_error (str(message))
        except Exception as e:
            self.log_error (e)

    async def subscribe_channels (self):
        for quot in ['usd', 'btc']:
            for base in DEFINES.LISTEN_SYMBOLS:
                if base != 'usd' and quot != base:
                    await self._socket.send(json.dumps({"event":"subscribe", "channel":"ticker", "pair":base+quot}))

    async def listen(self):
        try:
            while True:
                try:
                    self.log_telegram ('Connecting to bitfinex websocket...')
                    async with websockets.connect('wss://api.bitfinex.com/ws') as websocket:
                        self._socket = websocket
                        self.log_telegram ('Connection established')
                        await self.subscribe_channels ()
                        async for message in websocket:
                            await self.route (self.parse_message(message))
                except Exception as e:
                    self.log_error (e)
        except Exception as e:
            self.log_error (e)