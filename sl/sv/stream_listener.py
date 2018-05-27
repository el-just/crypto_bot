import asyncio
import websockets

from common import Logger
from common import Buffer
from common import Websocket

class StreamListener():
    __ws_path = None
    __exchanges_buffer = None

    def __init__(self):
        self.__ws_path = 'ws://127.0.0.1:8765'
        self.__exchanges_buffer = Buffer('exchanges', is_mirror=True)

    async def run(self):
        while True:
            try:
                async with websockets.connect(self.__ws_path) as websocket:
                    socket = Websocket(websocket=websocket)
                    await socket.listen()
            except Exception as e:
                Logger.log_error(e)

            finally:
                await asyncio.sleep(1)
