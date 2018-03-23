import pandas as pd
import numpy as np
import websockets
import datetime

import common.utils as utils
import common.formats as formats
from common.logger import Logger
from common.rest_socket import RESTSocket

class Socket ():
    _ws_path = 'wss://stream.binance.com:9443/'
    _volume_watcher = None

    _true_tick = None 
    _tick_buffer = None 
    _kline_buffer = None 

    def __init__ (self):
        self._rest = RESTSocket (url='https://api.binance.com/api/v1/')

        self._volume_watcher = {}
        for market in self._get_markets():
            self._volume_watcher[market] = {
                'true_tick': None,
                'tick_buffer': pd.DataFrame (data=[], columns=formats.tick),
                'kline_buffer': pd.DataFrame (data=[], columns=formats.tick)
            }

    def _get_markets (self):
        return ['ethbtc', 'bnbbtc']

    def _get_streams (self, markets):
        return [market+'@kline_1m' for market in markets]

    def _assume_tick (self, message):
        tick = None

        try:
            market_name = message['data']['s'].lower()
            tick = pd.Series (
                data=[int(message['data']['E']) // 1000, market_name, float(message['data']['k']['c']), None, None],
                index=formats.tick
            )
            tick.name = datetime.datetime.fromtimestamp(int(message['data']['E']) // 1000)

            current_base_volume = float(message['data']['k']['v'])
            current_quot_volume = float(message['data']['k']['q'])

            if self._volume_watcher[market_name]['true_tick'] is not None:
                buffer_tick = tick.copy()

                previous_base_volume = self._volume_watcher[market_name]['kline_buffer'].loc[:, 'base_volume'].sum() if not np.isnan(self._volume_watcher[market_name]['kline_buffer'].loc[:, 'base_volume'].sum()) else 0.
                previous_quot_volume = self._volume_watcher[market_name]['kline_buffer'].loc[:, 'quot_volume'].sum() if not np.isnan(self._volume_watcher[market_name]['kline_buffer'].loc[:, 'quot_volume'].sum()) else 0.

                buffer_tick.at['base_volume'] = current_base_volume - previous_base_volume 
                buffer_tick.at['quot_volume'] = current_quot_volume - previous_quot_volume 
            
                self._volume_watcher[market_name]['tick_buffer'] = self._volume_watcher[market_name]['tick_buffer'].append(buffer_tick)
                self._volume_watcher[market_name]['kline_buffer'] = self._volume_watcher[market_name]['kline_buffer'].append(buffer_tick)

            if self._volume_watcher[market_name]['tick_buffer'].shape[0] > 0 and tick.name - self._volume_watcher[market_name]['tick_buffer'].iloc[0].name >= datetime.timedelta(seconds=60):
                self._volume_watcher[market_name]['tick_buffer'] = self._volume_watcher[market_name]['tick_buffer'].loc[buffer_tick.name - datetime.timedelta(seconds=60):, :]
                tick.at['base_volume'] = self._volume_watcher[market_name]['tick_buffer'].loc[:, 'base_volume'].sum()
                tick.at['quot_volume'] = self._volume_watcher[market_name]['tick_buffer'].loc[:, 'quot_volume'].sum()

            if message['data']['k']['x'] == True:
                self._volume_watcher[market_name]['true_tick'] = tick.copy()
                self._volume_watcher[market_name]['kline_buffer'] = pd.DataFrame (data=[], columns=formats.tick)
        except Exception as e:
            Logger.log_error (e)

        return tick

    async def _resolve_message (self, message):
        tick = self._assume_tick (message)
        if tick is not None:
            Logger.log_info(tick)
            return tick

##################### API #############################
    async def ping (self):
        try:
            request_url = 'ping'

            return await self._rest.request (request_url)
        except Exception as e:
            Logger.log_error (e)

    async def get_server_time (self):
        try:
            request_url = 'time'

            return await self._rest.request (request_url)
        except Exception as e:
            Logger.log_error (e)

    async def get_last_trades (self, market, limit='500'):
        try:
            request_url = 'trades'

            return await self._rest.request (request_url, {'symbol':market, 'limit':limit})
        except Exception as e:
            Logger.log_error (e)

    async def connect (self):
        try:
            full_path = self._ws_path + 'stream?streams=' + '/'.join(self._get_streams (self._get_markets()))
            while True:
                try:
                    async with websockets.connect (full_path) as websocket:
                        async for message in websocket:
                            await self._resolve_message (utils.parse_data (message))
                except Exception as e:
                    Logger.log_error (e)
        except Exception as e:
            Logger.log_error (e)
