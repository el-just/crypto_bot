import asyncio
import websockets

from common import Logger
from common import Connection

class StreamListener():
    __ws_path = None
    __socket = None
    __clients = None

    def __init__(self):
        self.__ws_path = 'ws://127.0.0.1:8765'
        self.__clients = []

    async def __resolve_message(self, message):
        try:
            if len(self.__clients) > 0:
                for client in self.__clients:
                    await client.send(message)
        except Exception as e:
            Logger.log_error(e)

    async def send(self):
        pass

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
    def connect(self, initiator, **kwargs):
        try:
            connection = Connection(
                    source=self,
                    initiator=initiator,
                    **kwargs,)

            self.__clients.add(connection)

            return connection.client
        except Exception as e:
            Logger.log_error(e)

    async def close(self, connection):
        try:
            self.__clients.remove(connection)
        except Exception as e:
            Logger.log_error(e)
    async def disconnect(self, connection):
        try:
            await connection.close()
            self.client.remove(connection)
        except Exception as e:
            Logger.log_error(e)
