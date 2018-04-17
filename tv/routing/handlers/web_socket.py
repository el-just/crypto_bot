from aiohttp import web, WSMsgType

class WebSocket(web.View):
    __socket = None
    __error_counter = 0

    async def __resolve_message(self, message):
        try:
            await self.__socket.send_str(message)
            self.__error_counter = 0
        except Exception as e:
            Logger.log_error(e)

            self.__error_counter += 1
            if self.__error_counter > 5:
                await self.__stock_socket.close()

    async def get(self):
        self.__socket = web.WebSocketResponse()
        await self.__socket.prepare(self.request)

        self.request.app['websockets'].append(self.__socket)
        self.__stock_socket = await self.request.app['stock_stream'].connect(
                self.__resolve_message)

        async for msg in self.__socket:
            if msg.type == WSMsgType.TEXT:
                if msg.data == 'close':
                    await self.__socket.close()
                else:
                    await self.request.app['stock_stream'].send(msg.data)
            elif msg.type == WSMsgType.ERROR:
                pass

        self.request.app['websockets'].remove(self.__socket)
        await self.__stock_socket.close()

        return self.__socket
