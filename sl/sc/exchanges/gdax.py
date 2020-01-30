import datetime
import json
import time

import pandas as pd

from common import utils
from common import formats
from common import Logger

from exchanges import Exchange

class Gdax(Exchange):
    name = 'gdax'

    _ws_path = 'wss://ws-feed.gdax.com/'
    _rest_path = 'https://api.gdax.com/'

######################    Exchange required   ################################
    async def _subscribe_channels(self):
        try:
            await self.ws_send({
                    'type': 'subscribe',
                    'product_ids': self._get_markets().index.values.tolist(),
                    'channels': ['ticker'],})
        except Exception as e:
            Logger.log_error(e)

    async def _resolve_message(self, message):
        reaction = None

        try:
            message = utils.parse_data(message)
            if message.get('type', None) == 'ticker':
                reaction = self.__assume_tick (message)
        except Exception as e:
            Logger.log_error(e)

        finally:
            return reaction

######################    Private    #########################################
    def __assume_tick(self, message):
        tick = None

        try:
            current_date = datetime.datetime.now()
            market = self._get_markets().loc[message['product_id'].lower()]
            tick = pd.Series (
                    data=[
                        self.name,
                        int(time.mktime(current_date.timetuple()))*1000,
                        '_'.join([market.at['base'], market.at['quot']]),
                        message['price'],],
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
            request_url = 'products'
            stock_data = await self.rest_send(request_url)
            for market_data in stock_data:
                markets = markets.append(pd.Series(
                        data=[
                            self.name,
                            market_data['base_currency'].lower(),
                            market_data['quote_currency'].lower(),
                            market_data['min_market_funds'],
                            market_data['max_market_funds'],],
                        index=formats.market,
                        name=market_data['id'].lower(),))

        except Exception as e:
            Logger.log_error(e)

        finally:
            return markets
