import pandas as pd
import numpy as np
import websockets
import datetime
import json
import time

import common.utils as utils
import common.formats as formats
from common.logger import Logger
from common.rest_socket import RESTSocket

class Socket ():
    _ws_path = 'wss://ws-feed.gdax.com/'

    def __init__ (self):
        #self._rest = RESTSocket (url='https://api.binance.com/api/v1/')
        pass

    async def _subscribe_channels (self):
        try:
            await self._socket.send(json.dumps({
                'type':'subscribe',
                'product_ids':['BTC-USD', 'ETH-USD'],
                'channels': ['ticker']
            }))
        except Exception as e:
            Logger.log_error(e)

    async def _assume_tick (self, message):
        current_date = datetime.datetime.now()
            
        tick = pd.Series (
            data=[
                'gdax',
                int(time.mktime(current_date.timetuple())),
                message['product_id'].lower(),
                float(message['price']),
                None,
                None
            ],
            index=formats.tick
        )
        tick.name = current_date

        Logger.log_info(tick)


    async def _resolve_message (self, message):
        if 'type' in message and message['type'] == 'ticker':
            await self._assume_tick (message)

    async def connect (self):
        try:
            while True:
                try:
                    async with websockets.connect (self._ws_path) as websocket:
                        self._socket = websocket
                        await self._subscribe_channels()
                        async for message in websocket:
                            await self._resolve_message (utils.parse_data (message))
                except Exception as e:
                    Logger.log_error (e)
        except Exception as e:
            Logger.log_error (e)

