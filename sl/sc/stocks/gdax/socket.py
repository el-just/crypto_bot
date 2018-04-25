import websockets
import datetime
import json
import time

import pandas as pd

from common import utils
from common import formats
from common import Logger
from common import RESTSocket

class Socket ():
    __ws_path = None
    __socket = None

    def __init__ (self):
        self.__ws_path = 'wss://ws-feed.gdax.com/'

    async def __subscribe_channels(self):
        try:
            await self.__socket.send(json.dumps({
                    'type':'subscribe',
                    'product_ids':['BTC-USD', 'ETH-USD'],
                    'channels': ['ticker'],}))
        except Exception as e:
            Logger.log_error(e)

    def __assume_tick(self, message):
        tick = None

        try:
            current_date = datetime.datetime.now()
            tick = pd.Series (
                    data=[
                        'gdax',
                        int(time.mktime(current_date.timetuple())),
                        message['product_id'].lower(),
                        float(message['price']),],
                    index=formats.tick,)
            tick.name = current_date
        except Exception as e:
            Logger.log_error(e)

        finally:
            return tick

    async def __resolve_message(self, message):
        reaction = None

        try:
            if 'type' in message and message['type'] == 'ticker':
                reaction = self.__assume_tick (message)
        except Exception as e:
            Logger.log_error(e)

        finally:
            return reaction

    async def run(self):
        try:
            while True:
                try:
                    async with websockets.connect(self.__ws_path) as websocket:
                        self.__socket = websocket
                        await self.__subscribe_channels()
                        async for message in websocket:
                            reaction = await self.__resolve_message (
                                    utils.parse_data (message))

                            if reaction is not None:
                                yield reaction
                except Exception as e:
                    Logger.log_error (e)
        except Exception as e:
            Logger.log_error (e)

