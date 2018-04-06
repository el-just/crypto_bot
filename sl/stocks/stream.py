import asyncio
import websockets

from common.logger import Logger
import common.formats as formats

class Stream ():
    def __init__(self):
        self.__ip = '127.0.0.1'
        self.__port = 8765
        self.__socket = None

    async def run (self):
        try:
            await websockets.serve (self.__listener, self.__ip, self.__port)
        except Exception as e:
            Logger.log_error(e)

    async def __resolve_message (self, message):
        try:
            await self.__socket.send ('pong' if message == 'ping' else message)
        except Exception as e:
            Logger.log_error(e)
    
    async def __listener (self, websocket, path):
        try:
            self.__socket = websocket

            async for message in websocket:
        except Exception as e:
            Logger.log_error(e)
