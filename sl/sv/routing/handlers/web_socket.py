from aiohttp import web, WSMsgType

from common import Logger
from common.abilities import Connectable

class WebSocket(web.View, Connectable):
    async def get(self):
        client_socket = web.WebSocketResponse()
        await client_socket.prepare(self.request)

        connection = self.connect(self.request.app['controller'])

        async for msg in client_socket:
            if msg.type == WSMsgType.TEXT:
                if msg.data == 'close':
                    await client_socket.close()
                else:
                    connection.send(msg.data)
            elif msg.type == WSMsgType.ERROR:
                pass

        connection.close()
        return socket

    async def _recieve_message(self, message, connection):
        pass
