from aiohttp import web
from common import Logger
from common import Socket
from common import utils

class Websocket(Socket):
    def __init__(self, source=None, websocket=None):
        super(Websocket, self).__init__(source=source)
        self.__websocket = websocket

    async def listen(self):
        try:
            async for message in self.__websocket:
                if isinstance(self.__websocket, web.WebSocketResponse):
                    if message.type == WSMsgType.TEXT:
                        if message.data == 'close':
                            message = None
                        else:
                            message = message.data
                    elif msg.type == WSMsgType.ERROR:
                        message = None

                if message is not None:
                    message = utils.parse_data(message)
                    if message.get('type', None) is not None:
                        Logger.log_info('message')
                        Logger.log_info(message)

                    if (message.get('type', None) == 'service'
                            and message.get('action', None) is not None):
                        Logger.log_info('action accepted, trying to pass')
                        result = await self.execute(
                                message.get('action', None),
                                *message.get('args', []),
                                **message.get('kwargs', {}),)
                        response = {
                                'type':'service',
                                'id':message['id'],
                                'action_result':utils.pandas_to_dict(result),}
                        Logger.log_info('action resolved, trying to response')
                        await self.on_data(response)
                    else:
                        await self.push(message)
        except Exception as e:
            Logger.log_error(e)

        finally:
            await self.close()

    async def on_data(self, data):
        if data.get('type', None) is not None:
            Logger.log_info('message out')
            Logger.log_info(data)
        data = utils.stringify_data(data)
        if isinstance(self.__websocket, web.WebSocketResponse):
            await self.__websocket.send_str(data)
        else:
            await self.__websocket.send(data)
