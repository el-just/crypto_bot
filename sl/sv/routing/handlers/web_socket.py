from aiohttp import web, WSMsgType
import json

from common import Logger
from common import Buffer
from common import Websocket

class WebSocket(web.View):
    async def get(self):
        pure_socket = web.WebSocketResponse()
        await pure_socket.prepare(self.request)
        websocket = Websocket(websocket=pure_socket)

        Buffer('stream').connect(websocket)
        await websocket.listen()

        return pure_socket
