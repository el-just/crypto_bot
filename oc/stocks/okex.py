import asyncio
import datetime

import pandas as pd

from common import utils
from common import formats
from common import Logger

from exchanges import Exchange

class Okex(Exchange):
    name = 'okex'

    __key = '173bf8bc-0500-49bc-91d8-4d874145f04a'
    __pattern = '99BC86EC44CC35065D767118F511C7DD'

    __ws_path = 'wss://real.okex.com:10440/websocket'
    __rest_path = 'https://www.okex.com/v2/'

    def __init__(self):
        super(Okex, self).__init__(self)

        self.__custom_tasks.append(self.__connection_watcher)

    async def __subscribe_channels(self):
        try:
            subscription = []
            for index, market in self.__markets.iterrows():
                subscription.append({
                        'event':'addChannel',
                        'channel':'ok_sub_spot_%s_ticker'%(
                            market.name)})
            await self.socket_send(subscription)
        except Exception as e:
            Logger.log_error(e)

    async def __resolve_message(self, message):
        payload = None
        try:
            message = utils.parse_data(message)
            if isinstance(message, list):
                message = message[0]
                if message.get('channel', None) == 'addChannel':
                    self.__assume_channel(message)
                else:
                    payload = self.__assume_tick(message)
        except Exception as e:
            Logger.log_error(e)

        finally:
            return payload

    def __assume_tick(self, tick_data):
        tick = None
        try:
            tick = pd.Series(
                    data=[
                        'okex',
                        tick_data['data']['timestamp'],
                        '_'.join(tick_data['channel'].split('_')[3:5]),
                        tick_data['data']['close'],],
                    index=formats.tick,
                    name=datetime.datetime.now(),)
        except Exception as e:
            Logger.log_error(e)

        finally:
            return tick

    def __assume_channel(self, message):
        try:
            self.__register_channel(
                    channel_name=message['data']['channel'],
                    market_name='_'.join(
                        message['data']['channel'].split('_')[3:5]),)
        except Exception as e:
            Logger.log_error(e)

    async def __connection_watcher(self):
        while True:
            try:
                if self.__socket is not None:
                    await self.socket_send({'event':'ping'})
                    await asyncio.sleep(28)
                else:
                    await asyncio.sleep(1)
            except Exception as e:
                Logger.log_error(e)

##################### STOCK API #############################
    async def get_markets(self):
        markets = pd.DataFrame(data=[], columns=formats.market)

        try:
            request_url = 'markets/products'

            stock_data = await self.__rest_socket.request(request_url)
            for market_data in stock_data['data']:
                market = pd.Series(
                        data=[None, None, None, None, None],
                        index=formats.market,)

                market.at['stock'] = 'okex'
                market.at['base'] = market_data['symbol'].split('_')[0]
                market.at['quot'] = market_data['symbol'].split('_')[1]
                market.at['trade_min'] = market_data['minTradeSize']
                market.name = market_data['symbol']

                markets = markets.append(market)

        except Exception as e:
            Logger.log_error(e)

        finally:
            return markets
