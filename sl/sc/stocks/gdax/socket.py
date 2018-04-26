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
    __rest_path = None

    def __init__ (self):
        self.__ws_path = 'wss://ws-feed.gdax.com/'
        self.__rest_path = 'https://api.gdax.com/'

        self.__rest_socket = RESTSocket(url=self.__rest_path)

    async def __get_markets(self):
        try:
            markets = await self.get_markets()
            return [market.upper() for market in markets.index]
        except Exception as e:
            Logger.log_error(e)

    async def __subscribe_channels(self):
        try:
            markets = await self.__get_markets()
            await self.__socket.send(json.dumps({
                    'type':'subscribe',
                    'product_ids':markets,
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
                        int(time.mktime(current_date.timetuple()))*1000,
                        message['product_id'].lower(),
                        message['price'],],
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

###################    API    ################################################
    async def get_markets(self):
        markets = pd.DataFrame(data=[], columns=formats.market)

        try:
            request_url = 'products'

            stock_data = await self.__rest_socket.request(request_url)
            for market_data in stock_data:
                market = pd.Series(
                        data=[None, None, None, None, None],
                        index=formats.market,)

                market.at['stock'] = 'gdax'
                market.at['base'] = market_data['base_currency'].lower()
                market.at['quot'] = market_data['quote_currency'].lower()
                market.at['trade_min'] = market_data['min_market_funds']
                market.at['trade_max'] = market_data['max_market_funds']
                market.name = market_data['id'].lower()

                markets = markets.append(market)

        except Exception as e:
            Logger.log_error(e)

        finally:
            return markets

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

