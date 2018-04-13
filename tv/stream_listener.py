import asyncio
import websockets

from common.logger import Logger

class StreamListener():
    __ws_path = None
    __stock_socket = None
    __client_sockets = None

    def __init__(self):
        self.__ws_path = 'ws://127.0.0.1:8765'
        self.__client_sockets = []

    async def __resolve_message(self, message):
        try:
            if len(self.__client_sockets) > 0:
                for client in self.__client_sockets:
                    await client(message)
        except Exception as e:
            Logger.log_error(e)

    async def connect(self, socket):
        self.__client_sockets.append(socket)

    async def send(self, message):
        if self.__stock_socket is not None:
            await self.__stock_socket.send(message)

    async def run(self):
        while True:
            try:
                async with websockets.connect(self.__ws_path) as websocket:
                    self.__stock_socket = websocket
                    async for message in websocket:
                        await self.__resolve_message(message)
            except Exception as e:
                Logger.log_error(e)

            finally:
                await asyncio.sleep(1)
