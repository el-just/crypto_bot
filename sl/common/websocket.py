import json

from common import Logger
from common.abilities import Connectable

class Websocket(Connectable):
    def __init__(self, websocket):
        self.__socket = websocket

    async def _recieve_message(self, message, connection, channel=None):
        await self.__socket.send_str(json.dumps(message))

    async def listen(self):
        async for message in self.__socket:
            await self.publish(message, tags={'incoming'})
