import json
import asyncio
import pandas as pd

from common import Logger
from common import utils
from common.abilities import Connectable

class Websocket(Connectable):
    self.__pending = None
    self.__pending_results = None

    def __init__(self, websocket):
        self.__socket = websocket
        self.__pending = dict()
        self.__pending_results = dict()

    async def _recieve_message(self, message, connection, channel=None):
        if isinstance(message, (pd.Series, pd.DataFrame)):
            message = message.to_json()
        elif not isinstance(message, str):
            message = json.dumps(message)

        await self.__socket.send(message)

    async def listen(self):
        async for message in self.__socket:
            parsed = utils.parse_data(message)
            if parsed.get('action_result', None) is not None:
                self.__pending_results[action] = parsed['action_result']
                self.__pending[action].set()
            elif parsed.get('action', None) is not None:

            else:
                await self.publish(message, tags={'incoming'})

    async def _execute(self, action, *args, **kwargs):
        await self.__socket.send(json.dumps({
                'action': action,
                'args': args,
                'kwargs': kwargs,}))

        self.__pending[action] = asyncio.Event()
        await self.__pending[action].wait()

        result = self.__pending_results[action]
        if 'columns' in result and 'index' in result and 'data' in result:
            result = pd.DataFrame(
                    data=result['data'],
                    index=result['index'],
                    columns=result['columns'],)
        elif 'index' in result and 'data' in result and 'name' in result:
            result = pd.DataFrame(
                    data=result['data'],
                    index=result['index'],
                    name=result['name'],)

        del self.__pending[action]
        del self.__pending_results[action]
        return result
