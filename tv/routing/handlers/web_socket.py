from aiohttp import web, WSMsgType

class WebSocket(web.View):
    __socket = None

    async def __resolve_message(self, message):
        await self.__socket.send_str(message)

    async def get(self):
        self.__socket = web.WebSocketResponse()
        await self.__socket.prepare(self.request)

        self.request.app['websockets'].append(self.__socket)
        await self.request.app['stock_stream'].connect(self.__resolve_message)

        async for msg in self.__socket:
            if msg.type == WSMsgType.TEXT:
                if msg.data == 'close':
                    await self.__socket.close()
                else:
                    await self.__socket.send_str('message accepted: '+str(msg.data))
            elif msg.type == WSMsgType.ERROR:
                pass

        self.request.app['websockets'].remove(self.__socket)
        return ws
