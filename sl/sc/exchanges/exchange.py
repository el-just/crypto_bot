import asyncio
import websockets
import datetime
import json

import pandas as pd

from common import formats
from common import Logger
from common import RESTSocket

class Exchange():
    name = None

    _run_rest = False
    _rest_limit = 10
    _run_rest_delay = 1

    _key = None
    _pattern = None

    _ws_path = None
    _rest_path = None

    _ws_headers = None

    __ws_socket = None
    __rest_socket = None

    __markets = None
    __channels = None
    __request_counter = None

    __custom_tasks = None

    def __init__(self):
        self.__custom_tasks = []
        self.__rest_socket = RESTSocket(
                url=self._rest_path,
                request_limit=self._rest_limit)
        self.__request_counter = 0

    def __clear_channels(self):
        self.__channels = pd.DataFrame(data=[], columns=['market_name'])

    async def __run(self):
        try:
            while True:
                try:
                    self.__markets = await self.get_markets()
                    await self._prepare_ws_connection()
                    async with websockets.connect(
                            self._ws_path,
                            extra_headers=self._ws_headers,) as websocket:
                        self.__ws_socket = websocket
                        self.__clear_channels()
                        await self._ws_auth()
                        await self._subscribe_channels()
                        async for message in websocket:
                            payload = await self._resolve_message (message)
                except Exception as e:
                    self.__ws_socket = None
                    Logger.log_error(e)

                finally:
                    self._close_ws_connection()
                    await asyncio.sleep(1)
        except Exception as e:
            Logger.log_error(e)

    async def __run_rest(self):
        try:
            self.__markets = await self.get_markets()
            while True:
                try:
                    await self.get_ticks()
                except Exception as e:
                    Logger.log_error(e)

                finally:
                    await asyncio.sleep(self._run_rest_delay)
        except Exception as e:
            Logger.log_error(e)

######################    Exchange required    ##############################
    async def _prepare_ws_connection(self):
        pass

    async def _subscribe_channels(self):
        pass

    async def _resolve_message(self, mesasge):
        pass

    async def _ws_auth(self):
        pass

######################    Protected API    ###################################
    def _get_nonce(self):
        return str(int(datetime.datetime.now().timestamp()))
    def _get_request_counter(self):
        return self.__request_counter

    def _get_markets(self):
        return self.__markets
    def _set_markets(self, markets):
        self.__markets = markets

    def _get_channel_market(self, channel_name):
        return self.__markets.loc[
                self.__channels.loc[channel_name].at['market_name']]

    def _get_channels(self):
        return self.__channels
    def _set_channels(self, channels):
        self.__channels = channels

    def _register_channel(self, channel_name=None, market_name=None):
        self.__channels = self.__channels.append(pd.Series(
                data=[market_name],
                index=['market_name'],
                name=channel_name,))

    def _add_custom_task(self, task):
        self.__custom_tasks.append(task)

######################    API    #############################################
    async def ws_send(self, message):
        try:
            if self.__ws_socket is not None:
                self.__request_counter += 1
                await self.__ws_socket.send(json.dumps(message))
        except Exception as e:
            Logger.log_error(e)

    async def rest_send(self, message, params=None, type_='get'):
        response = None

        try:
            response = await self.__rest_socket.request(
                    message,
                    params=params,
                    type_=type_)
        except Exception as e:
            Logger.log_error(e)

        finally:
            return response

    async def get_markets(self):
        return pd.DataFrame(data=[], columns=formats.market)

    async def get_ticks(self):
        return pd.DataFrame(data=[], columns=formats.tick)

    def run(self):
        base_tasks = ([self.__run()] if self._run_rest is False
                else [self.__run_rest()])

        return base_tasks + [task() for task in self.__custom_tasks]

