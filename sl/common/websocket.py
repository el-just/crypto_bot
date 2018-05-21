import json
import pandas as pd

from common import Logger
from common.abilities import Connectable

class Websocket(Connectable):
    def __init__(self, websocket):
        self.__socket = websocket

    async def _recieve_message(self, message, connection, channel=None):
        if isinstance(message, (pd.Series, pd.DataFrame)):
            message = message.to_json()
        await self.__socket.send(json.dumps(message))

    async def listen(self):
        async for message in self.__socket:
            await self.publish(message, tags={'incoming'})
