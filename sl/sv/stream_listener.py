import asyncio
import websockets

from common import Logger
from common import Buffer
from common import Websocket

class StreamListener():
    __ws_path = None
    __socket = None

    __stream_buffer = None
    __buffer_socket = None

    def __init__(self):
        self.__ws_path = 'ws://127.0.0.1:8765'
        self.__stream_buffer = Buffer('stream').connect()

    async def run(self):
        while True:
            try:
                async with websockets.connect(self.__ws_path) as websocket:
                    self.__socket = Websocket(websocket)
                    self.__stream_buffer.connect(self.__socket)
                    await self.__socket.listen()
            except Exception as e:
                Logger.log_error(e)

            finally:
                await asyncio.sleep(1)
