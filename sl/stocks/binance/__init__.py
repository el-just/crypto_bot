from common import Logger
from stocks.binance.socket import Socket

class Binance ():
    __socket = None
    __stream = None

    def __init__(self, stream=None):
        self.__socket = Socket ()
        self.__stream = stream

    async def get_markets(self):
        return await self.__socket.exchange_info()

    async def run(self):
        async for tick in self.__socket.run():
            if self.__stream is not None:
                await self.__stream.publish(tick)
