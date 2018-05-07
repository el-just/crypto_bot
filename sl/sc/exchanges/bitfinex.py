import time
import datetime

import pandas as pd

from common import utils
from common import formats
from common import Logger

from exchanges.exchange import Exchange

class Bitfinex(Exchange):
    name = 'bitfinex'

    _ws_path = 'wss://api.bitfinex.com/ws'
    _rest_path = 'https://api.bitfinex.com/v1/'

######################    Exchange required   ################################
    async def _resolve_message(self, message):
        payload = None

        try:
            message = utils.parse_data(message)
            if type(message) == dict:
                self.__assume_channel(message)
            elif type(message) == list:
                payload = self.__assume_tick(message)
        except Exception as e:
            Logger.log_error(e)

        finally:
            return payload

    async def _subscribe_channels(self):
        try:
            for market_name, market in self._get_markets().iterrows():
                await self.ws_send({
                        'event':'subscribe',
                        'channel':'ticker',
                        'symbol':market_name,})
        except Exception as e:
            Logger.log_error(e)

######################    Private    #########################################
    def __assume_channel(self, message):
        try:
            if message.get('event', None) == 'subscribed':
                self._register_channel(
                        channel_name=message['chanId'],
                        market_name=message['pair'].lower(),)
        except Exception as e:
            Logger.log_error(e)

    def __assume_tick(self, tick_data):
        tick = None

        try:
            channel_id = int(tick_data[0])
            if len(tick_data) > 2:
                current_date = datetime.datetime.now()
                market = self._get_channel_market(tick_data[0])
                tick = pd.Series(
                        data=[
                            self.name,
                            int(time.mktime(current_date.timetuple()))*1000,
                            '_'.join([market.at['base'], market.at['quot']]),
                            tick_data[7],],
                        index=formats.tick,
                        name=current_date,)

                Logger.log_info(tick)
        except Exception as e:
            Logger.log_error(e)

        finally:
            return tick

###########################    API    ########################################
    async def get_markets(self):
        markets = pd.DataFrame(data=[], columns=formats.market)

        try:
            request_url = 'symbols_details'

            stock_data = await self.rest_send(request_url)
            for market_data in stock_data:
                markets = markets.append(pd.Series(
                        data=[
                            self.name,
                            market_data['pair'].lower()[:3],
                            market_data['pair'].lower()[3:],
                            market_data['minimum_order_size'],
                            market_data['maximum_order_size'],],
                        index=formats.market,
                        name=market_data['pair'].lower(),))

        except Exception as e:
            Logger.log_error(e)

        finally:
            return markets
