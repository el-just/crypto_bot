from aiohttp import web
from common import Logger
from common import Socket
from common import utils

class Websocket(Socket):
    __await_events = None
    __events_results = None

    def __init__(self, source=None, websocket=None):
        super(Websocket, self).__init__(source=source)
        self.__websocket = websocket
        self.__await_events = dict()
        self.__events_results = dict()

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
                    message = utils.parse_data(message)
                    if (isinstance(message, dict)
                            and message.get('type', None) == 'service'):
                        if message['id'] in self.__await_events.keys():
                            data = utils.dict_to_pandas(
                                    message['action_result'])
                            data = (data if data is not None
                                    else message['action_result'])
                            self.__events_results[message['id']] = data
                            self.__await_events[message['id']].set()
                    else:
                        await self.push(message)

        except Exception as e:
            Logger.log_error(e)

        finally:
            await self.close()

    async def on_data(self, data):
        data = utils.stringify_data(data)
        if isinstance(self.__websocket, web.WebSocketResponse):
            await self.__websocket.send_str(data)
        else:
            await self.__websocket.send(data)

    async def execute(self, action, *args, **kwargs):
        nonce = utils.get_nonce()
        await self.push({
            'type':'service',
            'id': utils.get_nonce(),
            'action':action,
            'args':args,
            'kwargs':kwargs,})

        self.__await_events[nonce] = asyncio.event()
        await self.__await_events[str(nonce)].wait()

        result = self.__events_results[nonce]
        del self.__events_results[nonce]
        del self.__await_events[nonce]

        return result
