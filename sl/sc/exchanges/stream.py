import asyncio
import websockets
import datetime

import pandas as pd

from common import formats
from common import utils
from common import Logger
from common import Connection

from exchanges import all_exchanges

class Stream():
    __ip = None
    __port = None
    __connections = None

    __data_snapshot = None
    __exchanges = None
    __exchanges_connections = None

    __action_collector = None

    def __init__(self):
        self.__ip = '127.0.0.1'
        self.__port = 8765
        self.__client_connections = set()

        self.__exchanges = [Exchange() for Exchange in all_exchanges]
        self.__exchanges_names = [exchange.name
                for exchange in self.__exchanges]
        self.__exchanges_connections = set()

    async def _recieve_message(self, message=None, connection=None):
        try:
            Logger.log_info(message)
        except Exception as e:
            Logger.log_error(e)

    async def __connector(self, websocket, path):
        try:
            async for message in websocket:
                pass

            return connection
        except Exception as e:
            Logger.log_error(e)

###########################  API  ############################################
    def run(self):
        tasks = [websockets.serve(self.__connector, self.__ip, self.__port)]
        for exchange in self.__exchanges:
            task = exchange.run()
            if isinstance(task, list):
                tasks += task
            else:
                tasks.append(task)

            connection = exchange.connect(self, fltr=None)
            self.__exchanges_connections.add(connection)

        return asyncio.gather(*tasks)
