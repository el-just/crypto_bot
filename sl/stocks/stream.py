import asyncio
import websockets
import datetime

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
    __action_collector = None

    __tick_buffer = None
    __last_publish = None

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

        self.__tick_buffer = pd.DataFrame(data=[], columns=formats.tick)
        self.__last_publish = datetime.datetime.now()

    def run(self):
        return asyncio.gather(
                websockets.serve(self.__listener, self.__ip, self.__port),
                *[stock.run() for stock in self.__stocks.values],)

    async def publish(self, message):
        try:
           await self.__publish_tick(message)
        except Exception as e:
            Logger.log_error(e)

    async def __publish_tick(self, tick):
        try:
            current_time = datetime.datetime.now()
            if (current_time - self.__last_publish
                    > datetime.timedelta(seconds=1)):
                data = self.__tick_buffer.loc[
                        self.__last_publish:current_time, :]
                self.__last_publish = current_time
                for connection in self.__connections:
                    await connection.send(utils.stringify_data(data))

                self.__tick_buffer = self.__tick_buffer.loc[current_time:, :]
            else:
                tick.name = current_time
                self.__tick_buffer = self.__tick_buffer.append(tick)

        except Exception as e:
            Logger.log_error(e)

    async def __resolve_message(self, message, client):
        re_action = None

        try:
            if isinstance(message, dict):
                re_action = await self.__action_collector.execute(message)
            elif isinstance(message, str):
                await client.send('pong' if message == 'ping' else message)
        except Exception as e:
            Logger.log_error(e)

        finally:
            return re_action

    async def __listener(self, websocket, path):
        self.__connections.add(websocket)

        try:
            async for message in websocket:
                action = await self.__resolve_message(
                        utils.parse_data(message), websocket)

                if action is not None:
                    await websocket.send(utils.stringify_data(action))
        except Exception as e:
            Logger.log_error(e)

        finally:
            self.__connections.remove(websocket)
