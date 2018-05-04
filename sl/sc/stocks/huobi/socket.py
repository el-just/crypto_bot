import asyncio
import gzip
import pandas as pd
import numpy as np
import websockets
import datetime
import json

from common import utils
from common import formats

from common import Logger
from common import RESTSocket

class Socket():
    __ws_path = None
    __rest_path = None
    __rest_socket = None
    __channels = None
    __markets = None
    __counter = 1

    def __init__(self):
        self.__ws_path = 'wss://api.huobi.pro/ws'
        self.__rest_path = 'https://api.huobi.pro/v1/'

        self.__rest_socket = RESTSocket(url=self.__rest_path)

    async def __subscribe_channels(self):
        try:
            markets = await self.__get_markets()
            for market in markets:
                await self.__socket.send(json.dumps({
                        'sub':'market.%s.kline.1min'%(market),
                        'id':str(self.__counter),}))
                self.__counter += 1
        except Exception as e:
            Logger.log_error(e)

    async def __get_markets(self):
        try:
            self.__markets = await self.get_markets()
            return (self.__markets.loc[:, 'base']
                    + self.__markets.loc[:, 'quot']).values
        except Exception as e:
            Logger.log_error(e)

    def __clear_channels(self):
        self.__channels = pd.DataFrame(data=[], columns=formats.market)

    def __register_channel(self, message):
        channel = self.__markets.loc[message['subbed'].split('.')[1], :]
        if not channel.empty:
            self.__channels = self.__channels.append (channel)

    async def __assume_event(self, event_data):
        if 'subbed' in event_data:
            self.__register_channel (event_data)

    async def __assume_tick(self, tick_data):
        tick = None
        try:
            channel_id = tick_data['ch'].split('.')[1]
            if not self.__channels.loc[channel_id].empty:
                current_date = datetime.datetime.now()
                tick = pd.Series (
                        data=[
                            'huobi',
                            tick_data['ts'],
                            (self.__channels.loc[channel_id].at['base']
                                + '-'
                                + self.__channels.loc[channel_id].at['quot']),
                            tick_data['tick']['close'],],
                        index=formats.tick,)
                tick.name = current_date
        except Exception as e:
            Logger.log_error(e)

        finally:
            return tick

    async def __resolve_message(self, message):
        reaction = None
        try:
            if message is not None:
                if 'subbed' in message:
                    await self.__assume_event (message)
                elif 'tick' in message:
                    reaction = await self.__assume_tick (message)
        except Exception as e:
            Logger.log_error(e)

        finally:
            return reaction

##################### STOCK API #############################
    async def get_markets(self):
        markets = pd.DataFrame(data=[], columns=formats.market)

        try:
            request_url = 'common/symbols'

            stock_data = await self.__rest_socket.request(request_url)
            for market_data in stock_data['data']:
                market = pd.Series(
                        data=[None, None, None, None, None],
                        index=formats.market,)

                market.at['stock'] = 'huobi'
                market.at['base'] = market_data['base-currency']
                market.at['quot'] = market_data['quote-currency']
                market.name = market.at['base'] + market.at['quot']

                markets = markets.append(market)

        except Exception as e:
            Logger.log_error(e)

        finally:
            return markets

#################################################################

    async def run(self):
        try:
            while True:
                try:
                    async with websockets.connect(self.__ws_path) as websocket:
                        self.__socket = websocket
                        self.__clear_channels()
                        await self.__subscribe_channels ()
                        async for message in websocket:
                            if message[:7] == '{"ping"':
                                ts=message[8:21]
                                pong='{"pong":'+ts+'}'
                                await websocket.send(pong)
                            else:
                                reaction = await self.__resolve_message (
                                        utils.parse_data(gzip.decompress(
                                            message).decode('utf8')))
                                if reaction is not None:
                                    yield reaction
                except Exception as e:
                    Logger.log_error(e)

                finally:
                    asyncio.sleep(1)
        except Exception as e:
            Logger.log_error(e)
