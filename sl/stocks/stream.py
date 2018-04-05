import asyncio
import websockets

from common.logger import Logger

class Stream ():
    _ip = '127.0.0.1'
    _port = 8765

    async def run (self):
        try:
            await websockets.serve (self._response, self._ip, self._port)
        except Exception as e:
            Logger.log_error(e)
    
    async def _response (self, websocket, path):
        try:
            async for message in websocket:
                await websocket.send ('pong' if message == 'ping' else message)
        except Exception as e:
            Logger.log_error(e)
