import pandas as pd
import numpy as np
import websockets
import datetime
import json
import time
import hmac
import hashlib

import common.utils as utils
import common.formats as formats
from common.logger import Logger
from common.rest_socket import RESTSocket

class Socket ():
    _ws_path = 'wss://ws.cex.io/ws'
    _key = 'LbjBXHmk3pPI2Ur4p2S3bCUSpD4'
    _pattern = 'OVelFsTeuwd5IeycU72Rp1Itj78'

    def __init__ (self):
        #self._rest = RESTSocket (url='')
        pass

    async def _subscribe_channels (self):
        try:
            await self._socket.send(json.dumps({
                "rooms": [
                    "tickers"
                ],
                "e": "subscribe",
                "oid": str(int(datetime.datetime.now().timestamp()))+'_subscribe'
            }))
        except Exception as e:
            Logger.log_error(e)

    async def _auth (self):
        try:
            timestamp = int(datetime.datetime.now().timestamp())  # UNIX timestamp in seconds
            string = "{}{}".format(timestamp, self._key)
            signature = hmac.new(self._pattern.encode(), string.encode(), hashlib.sha256).hexdigest()

            await self._socket.send(json.dumps({
                'e': 'auth',
                'auth': {'key': self._key, 'signature': signature, 'timestamp': timestamp},
                'oid': 'auth'
            }))
        except Exception as e:
            Logger.log_error(e)

    async def _assume_tick (self, message):
        current_date = datetime.datetime.now()
            
        tick = pd.Series (
            data=[
                'cex',
                int(time.mktime(current_date.timetuple())),
                message['data']['symbol1'].lower()+'-'+message['data']['symbol2'].lower(),
                float(message['data']['price']),
                None,
                None
            ],
            index=formats.tick
        )
        tick.name = current_date

        Logger.log_info(tick)

    async def _resolve_message (self, message):
        if message['e'] == 'ping':
            await self._socket.send(json.dumps({
                'e': 'pong'
            }))
        elif message['e'] == 'tick':
            await self._assume_tick (message)

    async def connect (self):
        try:
            while True:
                try:
                    async with websockets.connect (self._ws_path) as websocket:
                        self._socket = websocket
                        await self._auth()
                        await self._subscribe_channels()
                        async for message in websocket:
                            await self._resolve_message (utils.parse_data (message))
                except Exception as e:
                    Logger.log_error (e)
        except Exception as e:
            Logger.log_error (e)

