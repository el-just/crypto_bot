import pandas as pd
import numpy as np
import websockets
import datetime
import json
import time
import hmac
import hashlib

from common import utils
from common import formats
from common import Logger
from common import RESTSocket

class Socket ():
    __ws_path = None
    __key = None
    __pattern = None

    __socket = None

    def __init__(self):
        self.__ws_path = 'wss://ws.cex.io/ws'
        self.__key = 'LbjBXHmk3pPI2Ur4p2S3bCUSpD4'
        self.__pattern = 'OVelFsTeuwd5IeycU72Rp1Itj78'

    def __get_nonce(self):
        return str(int(datetime.datetime.now().timestamp()))

    async def __subscribe_channels(self):
        try:
            await self.__socket.send(json.dumps({
                    "rooms": [
                        "tickers",],
                    "e": "subscribe",
                    "oid": self.__get_nonce() + '_subscribe',}))
        except Exception as e:
            Logger.log_error(e)

    async def __auth(self):
        try:
            timestamp = int(datetime.datetime.now().timestamp())  # UNIX timestamp in seconds
            string = "{}{}".format(timestamp, self.__key)
            signature = hmac.new(
                    self.__pattern.encode(),
                    string.encode(),
                    hashlib.sha256,).hexdigest()

            await self.__socket.send(json.dumps({
                    'e': 'auth',
                    'auth': {
                        'key': self.__key,
                        'signature': signature,
                        'timestamp': timestamp,},
                    'oid': 'auth',}))
        except Exception as e:
            Logger.log_error(e)

    def __assume_tick(self, message):
        tick = None

        try:
            current_date = datetime.datetime.now()
            tick = pd.Series (
                    data=[
                        'cex',
                        int(time.mktime(current_date.timetuple())),
                        '-'.join([
                            message['data']['symbol1'].lower(),
                            message['data']['symbol2'].lower(),]),
                        float(message['data']['price']),],
                    index=formats.tick,)
            tick.name = current_date
        except Exception as e:
            Logger.log_error(e)

        finally:
            return tick

    async def __resolve_message(self, message):
        reaction = None

        try:
            if message['e'] == 'ping':
                await self.__socket.send(json.dumps({
                    'e': 'pong',}))
            elif message['e'] == 'tick':
                reaction = self.__assume_tick(message)
               
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
                        await self.__auth()
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

