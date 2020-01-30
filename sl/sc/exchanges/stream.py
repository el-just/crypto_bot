import asyncio
import websockets
import datetime

import pandas as pd

from common import formats
from common import utils
from common import Logger
from common import Websocket
from common import Buffer
from common import Socket

from common.abilities import Executable

from exchanges import all_exchanges
from exchanges.views import PriceFrame

class Stream():
    name = 'exchanges'

    __ip = None
    __port = None

    __exchanges = None
    __exchanges_buffer = None
    __exchanges_buffer_socket = None

    def __init__(self):
        self.__ip = '127.0.0.1'
        self.__port = 8765

        self.__exchanges = [Exchange() for Exchange in all_exchanges]

        self.__exchanges_buffer = Buffer('exchanges')
        self.__exchanges_buffer.add_view(PriceFrame())
        self.__exchanges_buffer_socket = self.__exchanges_buffer.connect()
        self.__exchanges_buffer_socket.set_owner(self)

    async def __client_connector(self, pure_websocket, path):
        try:
            websocket = Websocket(websocket=pure_websocket)
            self.__exchanges_buffer.connect(socket=websocket)

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

        return asyncio.gather(*tasks)

    def get_price_frame(self):
        return utils.pandas_to_dict(
                        self.__exchanges_buffer.views['price_frame'].state)

    def get_exchanges(self):
        return [exchange.name for exchange in self.__exchanges]
