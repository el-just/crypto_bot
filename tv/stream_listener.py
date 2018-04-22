import asyncio
import websockets

from common.logger import Logger

class Connection():
    name = None
    status = None
    __stream = None
    __action = None

    def __init__(self, stream=None, action=None, name=None):
        self.name = name
        self.__stream = stream
        self.__action = action

    async def close(self):
        await self.__stream.disconnect(self)
        self.status = 'closed'

    async def send(self, message):
        await self.__action(message)

class StreamListener():
    __ws_path = None
    __stock_socket = None
    __clients = None

    def __init__(self):
        self.__ws_path = 'ws://127.0.0.1:8765'
        self.__clients = []

    async def __resolve_message(self, message):
        try:
            Logger.log_info(message)
            if len(self.__clients) > 0:
                for client in self.__clients:
                    await client.send(message)
        except Exception as e:
            Logger.log_error(e)

    async def connect(self, socket):
        connection = Connection(self, socket, len(self.__clients))
        self.__clients.append(connection)

        return connection

    async def disconnect(self, client):
        if client.status != 'closed':
            self.__clients.remove(client)

    async def send(self, message):
        if self.__stock_socket is not None:
            await self.__stock_socket.send(message)

    async def run(self):
        while True:
            try:
                async with websockets.connect(self.__ws_path) as websocket:
                    self.__stock_socket = websocket
                    async for message in self.__stock_socket:
                        await self.__resolve_message(message)
            except Exception as e:
                Logger.log_error(e)

            finally:
                await asyncio.sleep(1)
