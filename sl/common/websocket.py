from aiohttp import web

class Webscoket(Socket):
    def __init__(self, source=None, websocket=None):
        super(Websocket, self).__init__(source=source)
        self.__websocket = websocket

    async def listen(self):
        try:
            async for message in self.__websocket:
                if isinstance(self.__websocket, web.WebSocketResponse):
                    if message.type == WSMsgType.TEXT:
                        if message.data == 'close':
                            pass
                        else:
                            await self.push(utils.parse_data(message))
                    elif msg.type == WSMsgType.ERROR:
                        pass
                else:
                    await self.push(utils.parse_data(message))

        except Exception as e:
            Logger.log_error(e)

    async def on_data(self, data):
        data = utils.dump_data(data) 
        if isinstance(self.__websocket, web.WebSocketResponse):
            await self.__websocket.send_str(data)
        else:
            await self.__websocket.send(data)
