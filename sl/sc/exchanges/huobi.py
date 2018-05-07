import asyncio
import gzip
import datetime

import pandas as pd

from common import utils
from common import formats
from common import Logger

from exchanges import Exchange

class Huobi(Exchange):
    name = 'huobi'

    _ws_path = 'wss://api.huobi.pro/ws'
    _rest_path = 'https://api.huobi.pro/v1/'

######################    Exchange required   ################################
    async def _subscribe_channels(self):
        try:
            for market_name, market in self._get_markets().iterrows():
                await self.ws_send({
                        'sub':'market.%s.kline.1min'%(market_name),
                        'id':str(self._get_request_counter()),})
        except Exception as e:
            Logger.log_error(e)

    async def _resolve_message(self, message):
        payload = None

        try:
            message = utils.parse_data(
                    gzip.decompress(message).decode('utf8'))

            if message is not None:
                if 'ping' in message:
                    await self.ws_send({'pong': message['ping']})
                elif 'subbed' in message:
                    self.__assume_channel(message)
                elif 'tick' in message:
                    payload = self.__assume_tick(message)
        except Exception as e:
            Logger.log_error(e)

        finally:
            return payload

######################    Private    #########################################
    def __assume_channel(self, message):
        try:
            self._register_channel(
                    channel_name=message['subbed'],
                    market_name=message['subbed'].split('.')[1],)
        except Exception as e:
            Logger.log_error(e)

    def __assume_tick(self, tick_data):
        tick = None
        try:
            market = self._get_channel_market(tick_data['ch'])
            tick = pd.Series (
                    data=[
                        self.name,
                        tick_data['ts'],
                        '_'.join([market.at['base'], market.at['quot']]),
                        tick_data['tick']['close'],],
                    index=formats.tick,
                    name=datetime.datetime.now(),)

            Logger.log_info(tick)
        except Exception as e:
            Logger.log_error(e)

        finally:
            return tick

###########################    API    ########################################
    async def get_markets(self):
        markets = pd.DataFrame(data=[], columns=formats.market)

        try:
            request_url = 'common/symbols'

            stock_data = await self.rest_send(request_url)
            for market_data in stock_data['data']:
                markets = markets.append(pd.Series(
                        data=[
                            self.name,
                            market_data['base-currency'].lower(),
                            market_data['quote-currency'].lower(),
                            None,
                            None,],
                        index=formats.market,
                        name=(market_data['base-currency'].lower()
                            + market_data['quote-currency'].lower()),))

        except Exception as e:
            Logger.log_error(e)

        finally:
            return markets
