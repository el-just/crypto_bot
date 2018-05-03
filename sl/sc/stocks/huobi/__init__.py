import pandas as pd

from common import Logger
from common import formats
from stocks.huobi.socket import Socket

class Binance ():
    name = 'huobi'

    __socket = None
    __stream = None

    def __init__(self, stream=None):
        self.__socket = Socket ()
        self.__stream = stream

    async def run(self):
        async for tick in self.__socket.run():
            if self.__stream is not None:
                await self.__stream.publish(tick)
