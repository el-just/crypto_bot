import asyncio
import websockets
import json

import pandas as pd

from common import formats
from common import Logger
from common import RESTSocket

class Exchange():
    name = None

    __key = None
    __pattern = None

    __ws_path = None
    __rest_path = None

    __ws_socket = None
    __rest_socket = None

    __markets = None
    __channels = None
    __request_counter = None

    __custom_tasks = None

    def __init__(self):
        self.__custom_tasks = []
        self.__rest_socket = RESTSocket(url=self.__rest_path)

    def __clear_channels(self):
        self.__channels = pd.DataFrame(data=[], columns=['market_name'])

    def __register_channel(self, channel_name=None, market_name=None):
        self.__channels = self.__channels.append(pd.Series(
                data=[market_name],
                index=['market_name'],
                name=channel_name,))

    async def __subscribe_channels(self):
        pass

    async def __run(self):
        try:
            while True:
                try:
                    self.__markets = await self.get_markets()
                    async with websockets.connect(self.__ws_path) as websocket:
                        self.__socket = websocket
                        self.__clear_channels()
                        await self.__subscribe_channels()
                        async for message in websocket:
                            payload = await self.__resolve_message (message)
                            if payload is not None:
                                await self.__stream.publish(payload)
                except Exception as e:
                    self.__socket = None
                    Logger.log_error(e)

                finally:
                    await asyncio.sleep(1)
        except Exception as e:
            Logger.log_error(e)

######################    API    #############################################
    async def get_markets(self):
        return pd.DataFrame(data=[], columns=formats.market)

    async def socket_send(self, message):
        try:
            if self.__socket is not None:
                self.__counter += 1
                await self.__socket.send(json.dumps(message))
        except Exception as e:
            Logger.log_error(e)

    def run(self):
        return [self.__run()] + self.__custom_tasks
