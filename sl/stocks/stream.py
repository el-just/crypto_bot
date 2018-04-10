import asyncio
import websockets

import pandas as pd

from common import formats
from common import utils
from common import Logger
from common import ActionCollector

from stocks import Binance
from stocks import Bitfinex
from stocks import Bittrex
from stocks import CEX
from stocks import GDAX

class Stream():
    __ip = None
    __port = None
    __connections = None

    __stocks = None
    __command_processor = None

    def __init__(self):
        self.__ip = '127.0.0.1'
        self.__port = 8765
        self.__connections = set()

        self.__stocks = pd.Series(
                data=[
                    Binance(stream=self),
                    Bitfinex(stream=self),
                    Bittrex(stream=self),
                    CEX(stream=self),
                    GDAX(stream=self),],
                index=[
                    'binance',
                    'bitfinex',
                    'bittrex',
                    'cex',
                    'gdax',],)

        self.__action_collector = ActionCollector(source=self.__stocks)

    def run(self):
        return asyncio.gather(
                websockets.serve(self.__listener, self.__ip, self.__port),
                *[stock.run() for stock in self.__stocks.values],)

    async def publish(self, message):
        for connection in self.__connections:
            await connection.send(utils.stringify_data(message))

    async def __resolve_message(self, message, client):
        try:
            await client.send('pong' if message == 'ping' else message)
        except Exception as e:
            Logger.log_error(e)

    async def __listener(self, websocket, path):
        self.__connections.add(websocket)

        try:
            async for message in websocket:
                await self.__resolve_message(message, websocket)
        except Exception as e:
            Logger.log_error(e)

        finally:
            self.__connections.remove(websocket)
