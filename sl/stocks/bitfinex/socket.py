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
    _tick_buffers = None
    _last_ticks = None

    def __init__ (self):
        self._last_ticks = {}
        self._tick_buffers = {}

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

        self._tick_buffers[int(message['chanId'])] = pd.DataFrame(data=[], columns=formats.tick) 
        self._last_ticks[int(message['chanId'])] = None

    async def _assume_event(self, event_data):
        if event_data['event'] == 'subscribed':
            self._register_channel (event_data)

    async def _assume_tick(self, tick_data):
        if not self._channels.loc[int(tick_data[0])].empty and (len(tick_data) > 2 or self._last_ticks[int(tick_data[0])] is not None):
            current_date = datetime.datetime.now()
            current_close = float(tick_data[7]) if len(tick_data) > 2 else self._last_ticks[int(tick_data[0])].at['price']
            current_volume = float(tick_data[8]) if len(tick_data) > 2 else self._last_ticks[int(tick_data[0])].at['base_volume']

            tick = pd.Series (
                data=[
                    'bitfinex',
                    int(time.mktime(current_date.timetuple())),
                    self._channels.loc[int(tick_data[0])].at['name'],
                    current_close,
                    None,
                    None
                ],
                index=formats.tick
            )
            tick.name = current_date

            if self._last_ticks[int(tick_data[0])] is not None:
                buffer_tick = tick.copy()
                buffer_tick.at['base_volume'] = current_volume - self._last_ticks[int(tick_data[0])].at['base_volume'] if current_volume > self._last_ticks[int(tick_data[0])].at['base_volume'] else 0.
                self._tick_buffers[int(tick_data[0])] = self._tick_buffers[int(tick_data[0])].append(buffer_tick)

            self._last_ticks[int(tick_data[0])] = tick.copy()
            self._last_ticks[int(tick_data[0])].at['base_volume'] = current_volume 

            if self._tick_buffers[int(tick_data[0])].shape[0] > 0 and tick.name - self._tick_buffers[int(tick_data[0])].iloc[0].name >= datetime.timedelta(seconds=60):
                self._tick_buffers[int(tick_data[0])] = self._tick_buffers[int(tick_data[0])].loc[tick.name - datetime.timedelta(seconds=70):, :]
                tick.at['base_volume'] = self._tick_buffers[int(tick_data[0])].loc[tick.name - datetime.timedelta(seconds=60):,'base_volume'].sum()

            Logger.log_info(tick_data)
            Logger.log_info(tick)

    async def _resolve_message(self, message):
        if type(message) == dict:
            await self._assume_event (message)
        elif type(message) == list:
            await self._assume_tick (message)

    async def connect (self):
        try:
            async with websockets.connect(self._ws_path) as websocket:
                self._socket = websocket
                self._clear_channels()
                await self._subscribe_channels ()
                async for message in websocket:
                    await self._resolve_message (utils.parse_data (message))
        except Exception as e:
            Logger.log_error(e)
