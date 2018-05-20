import asyncio
import websockets
import datetime

import pandas as pd

from common import formats
from common import utils
from common import Logger
from common import Websocket

from common.abilities import Connectable

from exchanges import all_exchanges

class Stream(Connectable):
    __ip = None
    __port = None
    __connections = None

    __exchanges = None
    __exchanges_connections = None

    def __init__(self):
        self.__ip = '127.0.0.1'
        self.__port = 8765

        self.__exchanges = [Exchange() for Exchange in all_exchanges]
        self.__exchanges_names = [exchange.name
                for exchange in self.__exchanges]

    async def __client_connector(self, pure_websocket, path):
        try:
            websocket = Websocket(pure_websocket)
            self.connect(websocket, groups=set(['clients']))

            await websocket.listen()
        except Exception as e:
            Logger.log_error(e)

###########################  API  ############################################
    def run(self):
        tasks = [websockets.serve(
                self.__client_connector, self.__ip, self.__port)]
        for exchange in self.__exchanges:
            task = exchange.run()
            if isinstance(task, list):
                tasks += task
            else:
                tasks.append(task)

            self.connect(exhange, groups=set(['exchanges', exchange.name]))

        return asyncio.gather(*tasks)

    async def _recieve_message(self, message, connection):
        try:
            if 'exchanges' in connection.at['groups']:
                await self.publish(message, groups=set(['clients']))
        except Exception as e:
            Logger.log_error(e)
