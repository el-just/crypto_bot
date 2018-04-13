import pandas as pd
import numpy as np
import websockets
import datetime

from common import utils
from common import formats
from common import Logger
from common import RESTSocket

class Socket ():
    __ws_path = None
    __rest_path = None
    __rest_socket = None

    def __init__ (self):
        self.__ws_path = 'wss://stream.binance.com:9443/'
        self.__rest_path = 'https://api.binance.com/api/v1/'

        self.__rest_socket = RESTSocket (url=self.__rest_path)

    def __get_markets (self):
        return ['ethbtc', 'bnbbtc']

    def __get_streams (self, markets):
        return [market+'@kline_1m' for market in markets]

    def __assume_tick (self, message):
        tick = None

        try:
            market_name = message['data']['s'].lower()
            tick = pd.Series (
                    data=[
                            'binance',
                            int(message['data']['E']) // 1000,
                            market_name,
                            float(message['data']['k']['c']),],
                    index=formats.tick,)
            tick.name = datetime.datetime.fromtimestamp(
                    int(message['data']['E']) // 1000)
        except Exception as e:
            Logger.log_error (e)

        finally:
            return tick

    async def __resolve_message (self, message):
        tick = self.__assume_tick (message)
        if tick is not None:
            return tick

##################### API #############################
    async def ping (self):
        try:
            request_url = 'ping'

            return await self.__rest_socket.request (request_url)
        except Exception as e:
            Logger.log_error (e)

    async def exchange_info (self):
        try:
            request_url = 'exchangeInfo'

            return await self.__rest_socket.request (request_url)
        except Exception as e:
            Logger.log_error (e)

    async def get_server_time (self):
        try:
            request_url = 'time'

            return await self.__rest_socket.request (request_url)
        except Exception as e:
            Logger.log_error (e)

    async def get_last_trades (self, market, limit='500'):
        try:
            request_url = 'trades'

            return await self.__rest_socket.request (request_url,
                    {'symbol':market, 'limit':limit},)
        except Exception as e:
            Logger.log_error (e)

    async def run (self):
        try:
            full_path = (self.__ws_path
                    + 'stream?streams='
                    + '/'.join(self.__get_streams (self.__get_markets())))

            while True:
                try:
                    async with websockets.connect (full_path) as websocket:
                        async for message in websocket:
                            tick = await self.__resolve_message (
                                    utils.parse_data (message))
                            if tick is not None:
                                yield tick
                except Exception as e:
                    Logger.log_error (e)
        except Exception as e:
            Logger.log_error (e)
