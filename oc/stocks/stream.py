import asyncio
import websockets
import datetime

import pandas as pd

from common import formats
from common import utils
from common import Logger
from common import ActionCollector
from common import Connection

from stocks import Binance
from stocks import Bitfinex
from stocks import Bittrex
from stocks import CEX
from stocks import GDAX
from stocks import Huobi
from stocks import Okex

class Stream():
    __ip = None
    __port = None
    __connections = None

    __stocks = None
    __action_collector = None

    def __init__(self):
        self.__ip = '127.0.0.1'
        self.__port = 8765
        self.__connections = set()

        self.__stocks = pd.Series(
                data=[
#                    Binance(stream=self),
                    Bitfinex(stream=self),
                    Bittrex(stream=self),
                    Huobi(stream=self),
                    Okex(stream=self),
                    CEX(stream=self),
                    GDAX(stream=self),],
                index=[
#                    'binance',
                    'bitfinex',
                    'bittrex',
                    'huobi',
                    'okex',
                    'cex',
                    'gdax',],)

        self.__action_collector = ActionCollector(source=self.__stocks)

    async def __connector(self, websocket, path):
        try:
            connection = await self.connect(websocket)
        except Exception as e:
            Logger.log_error(e)

        finally:
            await self.disconnect(connection)

    async def __resolve_message(self, message, connection):
        try:
            if isinstance(message, dict):
                await self.__action_collector.execute(
                        message,connection,)
        except Exception as e:
            Logger.log_error(e)

###########################  API  ############################################

    def run(self):
        tasks = [websockets.serve(self.__connector, self.__ip, self.__port)]
        for stock in self.__stocks.values:
            stock_task = stock.run()
            if isinstance(stock_task, list):
                tasks += stock_task
            else:
                tasks.append(stock_task)

        return asyncio.gather(*tasks)

    async def connect(self, socket):
        try:
            connection = Connection(
                    source=self,
                    recipient=socket,
                    buffer_size=datetime.timedelta(seconds=1),)

            self.__connections.add(connection)

            async for message in socket:
                await self.__resolve_message(
                        utils.parse_data(message), connection)

            return connection
        except Exception as e:
            Logger.log_error(e)

    async def disconnect(self, connection):
        try:
            await connection.close()
            self.__connections.remove(connection)
        except Exception as e:
            Logger.log_error(e)

    async def publish(self, message):
        try:
            for connection in self.__connections:
                await connection.send(message)
        except Exception as e:
            Logger.log_error(e)