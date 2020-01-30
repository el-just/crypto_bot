import datetime

import pandas as pd

from common import utils
from common import formats
from common import Logger

from exchanges import Exchange

class Hitbtc(Exchange):
    name = 'hitbtc'

    _ws_path = 'wss://api.hitbtc.com/api/2/ws'
    _rest_path = 'https://api.hitbtc.com/api/2/'

######################    Exchange required   ################################
    async def _subscribe_channels(self):
        try:
            subscription = []
            for market_name, market in self._get_markets().iterrows():
                await self.ws_send({
                        'method': 'subscribeTicker',
                        'params': {
                            'symbol': market_name
                            },
                        'id': self._get_request_counter()})
        except Exception as e:
            Logger.log_error(e)

    async def _resolve_message(self, message):
        payload = None

        try:
            message = utils.parse_data(message)
            if message.get('method', None) == 'ticker':
                payload = self.__assume_tick(message)
        except Exception as e:
            Logger.log_error(e)

        finally:
            return payload

######################    Private    #########################################
    def __assume_tick(self, tick_data):
        tick = None

        try:
            market = self._get_markets().loc[tick_data['params']['symbol']]
            tick = pd.Series(
                    data=[
                        self.name,
                        int(datetime.datetime.strptime(
                            tick_data['params']['timestamp'].split('.')[0],
                            '%Y-%m-%dT%H:%M:%S',).timestamp()*1000),
                        '_'.join([market.at['base'].lower(), market.at['quot']]),
                        tick_data['params']['last'],],
                    index=formats.tick,
                    name=datetime.datetime.now(),)
        except Exception as e:
            Logger.log_info(tick_data['params']['timestamp'].split('.')[0])
            Logger.log_error(e)

        finally:
            return tick

###########################    API    ########################################
    async def get_markets(self):
        markets = pd.DataFrame(data=[], columns=formats.market)

        try:
            request_url = 'public/symbol'

            stock_data = await self.rest_send(request_url)
            for market_data in stock_data:
                markets = markets.append(pd.Series(
                        data=[
                            self.name,
                            market_data['baseCurrency'].lower(),
                            market_data['quoteCurrency'].lower(),
                            None,
                            None,],
                        index=formats.market,
                        name=market_data['id']))

        except Exception as e:
            Logger.log_error(e)

        finally:
            return markets
