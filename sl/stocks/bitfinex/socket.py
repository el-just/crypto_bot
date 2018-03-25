import websockets
import datetime
import time
import json

import pandas as pd

import common.utils as utils
import common.formats as formats
from common.logger import Logger

class Socket ():
    _socket = None
    _ws_path = 'wss://api.bitfinex.com/ws'
    _channels = None

    async def _subscribe_channels (self):
        try:
            for quot in ['btc']:
                for base in ['eth', 'xrp']:
                    market = (base+quot).upper()
                    await self._socket.send(json.dumps({'event':'subscribe', 'channel':'ticker', 'symbol':market}))
        except Exception as e:
            Logger.log_error(e)

    def _clear_channels (self):
        self._channels = pd.DataFrame (data=[], columns=['name'])

    def _register_channel (self, message):
        channel = pd.Series (data=[message['pair'].lower()], index=['name'])
        channel.name = int(message['chanId'])
        self._channels = self._channels.append (channel)

    async def _resolve_event(self, event_data):
        if event_data['event'] == 'subscribed':
            self._register_channel (event_data)

    async def _resolve_tick(self, tick_data):
        Logger.log_info(tick_data)
        '''
        if not self._channels.loc[int(tick[0])].empty:
            market_name = message['data']['s'].lower()
            tick = pd.Series (
                data=['bitfinex', int(message['data']['E']) // 1000, market_name, float(message['data']['k']['c']), None, None],
                index=formats.tick
            )
            tick.name = time.mktime(datetime.datetime.now().timetuple())

            tb_tick = pd.Series (data=tb_data, index=['timestamp', 'base', 'quot', 'close', 'volume'])
            tb_tick.name = datetime.datetime.fromtimestamp(tb_tick.at['timestamp'])
'''

    async def _resolve_message(self, message):
        if type(message) == dict:
            await self._resolve_event (message)
        elif type(message) == list and len(message) > 2:
            await self._resolve_tick (message)

    async def connect (self):
        try:
            async with websockets.connect(self._ws_path) as websocket:
                self._socket = websocket
                self._clear_channels()
                await self._subscribe_channels ()
                async for message in websocket:
                    Logger.log_info(message)
                    await self._resolve_message (utils.parse_data (message))
        except Exception as e:
            Logger.log_error(e)
