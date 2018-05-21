from aiohttp import web, WSMsgType
import json

from common import Logger
from common.abilities import Connectable

class WebSocket(web.View, Connectable):
    __socket = None

    async def get(self):
        self.__socket = web.WebSocketResponse()
        await self.__socket.prepare(self.request)

        connection = self.request.app['controller'].connect(
                self,
                tags={'clients'},)

        async for msg in self.__socket:
            if msg.type == WSMsgType.TEXT:
                if msg.data == 'close':
                    await client_socket.close()
                    self.__socket = None
                else:
                    connection.send(msg.data, channel='action')
            elif msg.type == WSMsgType.ERROR:
                pass

        await connection.close()

        return self.__socket

    async def _recieve_message(self, message, connection, channel=None):
        try:
            await self.__socket.send_str(json.dumps(message))
        except Exception as e:
            Logger.log_error(e)

    async def _close_connection(self, connection):
        try:
            if self.__socket is not None:
                await self.__socket.close(code=1001, message='Server shutdown')
                self.__socket = None
        except Exception as e:
            Logger.log_error(e)
