import asyncio
import websockets

from common import Logger
from common.abilities import Connectable

class StreamListener(Connectable):
    __ws_path = None
    __socket = None

    def __init__(self):
        self.__ws_path = 'ws://127.0.0.1:8765'

    async def __resolve_message(self, message):
        try:
            await self.publish(message, tags={'incoming'}, channel='ticker')
        except Exception as e:
            Logger.log_error(e)

    async def run(self):
        while True:
            try:
                async with websockets.connect(self.__ws_path) as websocket:
                    self.__socket = websocket
                    async for message in self.__socket:
                        await self.__resolve_message(message)
            except Exception as e:
                Logger.log_error(e)

            finally:
                await asyncio.sleep(1)

######################    Connection    ######################################
    async def _recieve_message(self, message, connection, channel=None):
        pass

    async def _close_connection(self, connection):
        pass

    def _accept_connection(self, connection)
        pass
