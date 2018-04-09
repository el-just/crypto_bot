import asyncio
import websockets

from common import formats
from common import utils 
from common import Logger

from stocks import Binance
from stocks import Bitfinex
from stocks import Bittrex
from stocks import CEX
# from stocks import GDAX

class Stream():
    def __init__(self):
        self.__ip = '127.0.0.1'
        self.__port = 8765
        self.__connections = set()

    def run(self):
        return asyncio.gather(
                websockets.serve(self.__listener, self.__ip, self.__port),
                Binance(stream=self).run(),
                Bitfinex(stream=self).run(),
                Bittrex(stream=self).run(),
                CEX(stream=self).run(),)

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
