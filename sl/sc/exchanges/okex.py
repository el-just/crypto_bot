import asyncio
import datetime

import pandas as pd

from common import utils
from common import formats
from common import Logger

from exchanges import Exchange

class Okex(Exchange):
    name = 'okex'

    _key = '173bf8bc-0500-49bc-91d8-4d874145f04a'
    _pattern = '99BC86EC44CC35065D767118F511C7DD'

    _ws_path = 'wss://real.okex.com:10440/websocket'
    _rest_path = 'https://www.okex.com/v2/'

    def __init__(self):
        super(Okex, self).__init__()

        self._add_custom_task(self.__connection_watcher)

######################    Exchange required   ################################
    async def _subscribe_channels(self):
        try:
            subscription = []
            for market_name, market in self._get_markets().iterrows():
                subscription.append({
                        'event':'addChannel',
                        'channel':'ok_sub_spot_%s_ticker'%(
                            market_name)})
            await self.ws_send(subscription)
        except Exception as e:
            Logger.log_error(e)

    async def _resolve_message(self, message):
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

######################    Private    #########################################
    def __assume_tick(self, tick_data):
        tick = None
        try:
            market = self._get_channel_market(tick_data['channel'])
            tick = pd.Series(
                    data=[
                        self.name,
                        tick_data['data']['timestamp'],
                        '_'.join([market.at['base'], market.at['quot']]),
                        tick_data['data']['close'],],
                    index=formats.tick,
                    name=datetime.datetime.now(),)

            Logger.log_info(tick)
        except Exception as e:
            Logger.log_error(e)

        finally:
            return tick

    def __assume_channel(self, message):
        try:
            self._register_channel(
                    channel_name=message['data']['channel'],
                    market_name='_'.join(
                        message['data']['channel'].split('_')[3:5]),)
        except Exception as e:
            Logger.log_error(e)

    async def __connection_watcher(self):
        while True:
            try:
                await self.ws_send({'event':'ping'})
                await asyncio.sleep(28)
            except Exception as e:
                Logger.log_error(e)
                await asyncio.sleep(1)

###########################    API    ########################################
    async def get_markets(self):
        markets = pd.DataFrame(data=[], columns=formats.market)

        try:
            request_url = 'markets/products'

            stock_data = await self.rest_send(request_url)
            for market_data in stock_data['data']:
                markets = markets.append(pd.Series(
                        data=[
                            self.name,
                            market_data['symbol'].split('_')[0],
                            market_data['symbol'].split('_')[1],
                            market_data['minTradeSize'],
                            None,],
                        index=formats.market,
                        name=market_data['symbol']))

        except Exception as e:
            Logger.log_error(e)

        finally:
            return markets
