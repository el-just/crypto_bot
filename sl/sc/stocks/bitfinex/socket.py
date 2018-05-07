import websockets
import datetime
import time
import json

import pandas as pd

from common import utils
from common import formats
from common import Logger
from common import RESTSocket

class Socket ():
    __ws_path = None
    __socket = None
    __rest_path = None
    __rest_socket = None

    __channels = None

    def __init__ (self):
        self.__ws_path = 'wss://api.bitfinex.com/ws'
        self.__rest_path = 'https://api.bitfinex.com/v1/'

        self.__rest_socket = RESTSocket(url=self.__rest_path)

    async def __subscribe_channels(self):
        try:
            markets = await self.__get_markets()
            for market in markets:
                await self.__socket.send(json.dumps({
                        'event':'subscribe',
                        'channel':'ticker',
                        'symbol':market,}))
        except Exception as e:
            Logger.log_error(e)

    async def __get_markets(self):
        try:
            markets = await self.get_markets()
            return (markets.loc[:, 'base'] + markets.loc[:, 'quot']).values
        except Exception as e:
            Logger.log_error(e)

    def __clear_channels(self):
        self.__channels = pd.DataFrame (data=[], columns=['name'])

    def __register_channel(self, message):
        channel = pd.Series (data=[message['pair'].lower()], index=['name'])
        channel.name = int(message['chanId'])
        self.__channels = self.__channels.append (channel)

    async def __assume_event(self, event_data):
        if event_data['event'] == 'subscribed':
            self.__register_channel (event_data)

    async def __assume_tick(self, tick_data):
        tick = None
        try:
            channel_id = int(tick_data[0])
            if not self.__channels.loc[channel_id].empty and len(tick_data) > 2:
                current_date = datetime.datetime.now()
                tick = pd.Series (
                        data=[
                            'bitfinex',
                            int(time.mktime(current_date.timetuple()))*1000,
                            self.__channels.loc[int(tick_data[0])].at['name'],
                            tick_data[7],],
                        index=formats.tick,)
                tick.name = current_date
        except Exception as e:
            Logger.log_error(e)

        finally:
            return tick

    async def __resolve_message(self, message):
        reaction = None

        try:
            if type(message) == dict:
                await self.__assume_event (message)
            elif type(message) == list:
                reaction = await self.__assume_tick (message)
        except Exception as e:
            Logger.log_error(e)

        finally:
            return reaction

###########################    API    ########################################
    async def get_markets(self):
        markets = pd.DataFrame(data=[], columns=formats.market)

        try:
            request_url = 'symbols_details'

            stock_data = await self.__rest_socket.request(request_url)
            for market_data in stock_data:
                market = pd.Series(
                        data=[None, None, None, None, None],
                        index=formats.market,)

                market.at['stock'] = 'bitfinex'
                market.at['base'] = market_data['pair'].lower()[:3]
                market.at['quot'] = market_data['pair'].lower()[3:]
                market.at['trade_min'] = market_data['minimum_order_size']
                market.at['trade_max'] = market_data['maximum_order_size']
                market.name = market.at['base'] + '-' + market.at['quot']

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
                        self.__clear_channels()
                        await self.__subscribe_channels ()
                        async for message in websocket:
                            reaction = await self.__resolve_message (
                                    utils.parse_data (message))
                            if reaction is not None:
                                yield reaction
                except Exception as e:
                    Logger.log_error(e)

                finally:
                    await asyncio.sleep(1)
        except Exception as e:
            Logger.log_error(e)
