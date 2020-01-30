import json
import time
import datetime
import websockets
import pandas as pd
import numpy as np
import hmac
import hashlib
import ast

from abstract.logging import Logging
from stocks.bitfinex.defines import DEFINES

class WEBSocket (Logging):
    _channels = None
    _auth_channel = None
    _socket = None
    _tick_actions = []
    _wallet_actions = []
    _order_actions = []
    _reconnect_actions = []

    def add_tick_action (self, tick_action):
        self._tick_actions.append(tick_action)

    def add_wallet_action (self, wallet_action):
        self._wallet_actions.append (wallet_action)

    def add_order_action (self, order_action):
        self._order_actions.append (order_action)

    def add_reconnect_action (self, reconnect_action):
        self._reconnect_actions.append (reconnect_action)

    async def _process_actions (self, actions, *args):
        try:
            if len (actions) > 0:
                for action in actions:
                    await action (*args)
        except Exception as e:
            self.log_error (e)

    def parse_message (self, pure_data):
        if type(pure_data) == str:
            if pure_data[0] == '{':
                return json.loads (pure_data)
            elif pure_data[0] == '[':
                pure_data = pure_data.replace ('null', 'None')
                pure_data = pure_data.replace ('true', 'True')
                pure_data = pure_data.replace ('false', 'False')
                return ast.literal_eval(pure_data)
            else:
                return pure_data
        else:
            return pure_data

    def auth (self):
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
                if not self._channels.loc[int(tick[0])].empty:
                    tb_data = [
                        int(time.mktime(datetime.datetime.now().timetuple())),
                        self._channels.loc[int(tick[0])].at['base'],
                        self._channels.loc[int(tick[0])].at['quot'],
                        float(tick[7]),
                        float(tick[8])
                        ]
                    tb_tick = pd.Series (data=tb_data, index=['timestamp', 'base', 'quot', 'close', 'volume'])
                    tb_tick.name = datetime.datetime.fromtimestamp(tb_tick.at['timestamp'])
                    
                    await self._process_actions (self._tick_actions, tb_tick)
                else:
                    raise Warning (str(tick), 'Data for unknown channel')
        except Exception as e:
            self.log_error (e)

    async def process_event (self, message):
        try:
            if message['event'] == 'subscribed':
                self.register_channel (message)
            elif message['event'] == 'info':
                if 'code' in message:
                    code = int(str(message['code']).replace ('"',''))

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
                    pass
                else:
                    self.log_error ('ERROR::Unknown event\n\t{0}'.format(str(message)))
            elif message['event'] == 'auth':
                if message['status'].lower() == 'ok':
                    self._auth_channel = pd.Series (data=[int(message['chanId']), int(message['userId'])], index=['chanId', 'userId'])
                else:
                    self.log_error ('Authentification failed')
            else:
                self.log_error (str(message))
        except Exception as e:
            self.log_error (e)

    async def process_auth_message (self, message):
        try:
            if message[1] == 'ws' or message[1] == 'wu':
                await self._process_actions (self._wallet_actions, message)
            elif message[1] in ('on', 'oc', 'te'):
                await self._process_actions (self._order_actions, message)
        except Exception as e:
            self.log_error (e)

    async def route (self, message):
        try:
            if type(message) == dict:
                await self.process_event (message)
            elif type(message) == list:
                if self._auth_channel is not None and int(message[0]) == int(self._auth_channel.at['chanId']):
                    await self.process_auth_message (message)
                else:
                    await self.process_tick (message)
            else:
                self.log_error (str(message))
        except Exception as e:
            self.log_error (e)

    async def subscribe_channels (self):
        try:
            await self._socket.send(json.dumps(self.auth()))
            for quot in ['usd', 'btc']:
                for base in DEFINES.LISTEN_SYMBOLS:
                    if base != 'usd' and quot != base:
                        await self._socket.send(json.dumps({"event":"subscribe", "channel":"ticker", "pair":base+quot}))
        except Exception as e:
            self.log_error (e)
    
    async def run (self):
        try:
            await self.listen ()
        except Exception as e:
            self.log_error (e)

    async def listen(self):
        try:
            while True:
                try:
                    self.clear_channels()
                    self.log_telegram ('Connecting to bitfinex websocket...')
                    async with websockets.connect('wss://api.bitfinex.com/ws') as websocket:
                        self._socket = websocket
                        self.log_telegram ('Connection established')
                        await self.subscribe_channels ()
                        await self._process_actions (self._reconnect_actions)
                        async for message in websocket:
                            await self.route (self.parse_message(message))
                except Exception as e:
                    self.log_error (e)
        except Exception as e:
            self.log_error (e)