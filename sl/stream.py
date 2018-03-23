import asyncio
import websockets

class StocksStream ():
    _ip = '127.0.0.1'
    _port = 8765

    async def run (self):
        await websockets.serve (self._response, self._ip, self._port)
    
    async def _response (self, websocket, path):
        async for message in websocket:
            await websocket.send (message)
