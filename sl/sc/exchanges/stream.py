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

from exchanges import all_exchanges
from exchanges.views import PriceFrame

class Stream():
    __ip = None
    __port = None

    __exchanges = None
    __exchanges_buffer = None

    def __init__(self):
        self.__ip = '127.0.0.1'
        self.__port = 8765

        self.__exchanges = [Exchange() for Exchange in all_exchanges]
        self.__exchanges_buffer = Buffer('exchanges')
        self.__ecchanges_buffer.add_view(PriceFrame())

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
