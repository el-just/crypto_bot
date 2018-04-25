import pandas as pd

from common import Logger
from common import formats
from stocks.binance.socket import Socket

class Binance ():
    name = 'binance'

    __socket = None
    __stream = None

    def __init__(self, stream=None):
        self.__socket = Socket ()
        self.__stream = stream

    async def get_markets(self):
        markets = pd.DataFrame(data=[], columns=formats.market)

        try:
            markets = await self.__socket.get_markets()
        except Exception as e:
            Logger.log_error(e)

        finally:
            return markets

    async def run(self):
        async for tick in self.__socket.run():
            if self.__stream is not None:
                await self.__stream.publish(tick)
