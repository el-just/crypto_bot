import datetime

import pandas as pd

from common import utils
from common import formats
from common import Logger

from exchanges import Exchange

class Binance(Exchange):
    name = 'binance'
    _rest_path = 'https://api.binance.com/api/v1/'

    __ws_main_path = 'wss://stream.binance.com:9443/'

######################    Exchange required   ################################
    async def _prepare_ws_connection(self):
        try:
            self._ws_path = (self.__ws_main_path
                    + 'stream?streams='
                    + '/'.join(self.__get_streams()))
        except Exception as e:
            Logger.log_error(e)

    async def _resolve_message(self, message):
        try:
            return self.__assume_tick(utils.parse_data(message))
        except Exception as e:
            Logger.log_error(e)

######################    Private    #########################################
    def __get_streams(self):
        return [market_name+'@kline_1m'
                for market_name, market in self._get_markets().iterrows()]

    def __assume_tick(self, message):
        tick = None

        try:
            market = self._get_markets().loc[message['data']['s'].lower()]
            tick = pd.Series(
                    data=[
                        self.name,
                        message['data']['E'],
                        '_'.join([market.at['base'], market.at['quot']]),
                        message['data']['k']['c'],],
                    index=formats.tick,
                    name=datetime.datetime.now(),)
        except Exception as e:
            Logger.log_error(e)

        finally:
            return tick

###########################    API    ########################################
    async def get_markets(self):
        markets = pd.DataFrame(data=[], columns=formats.market)

        try:
            request_url = 'exchangeInfo'
            exchange_info = await self.rest_send(request_url)

            for market_data in exchange_info['symbols']:
                if market_data['status'].lower() == 'trading':
                    market = pd.Series(
                            data=[None, None, None, None, None],
                            index=formats.market,)

                    market.at['stock'] = self.name
                    market.at['base'] = market_data['baseAsset'].lower()
                    market.at['quot'] = market_data['quoteAsset'].lower()

                    for limit in market_data['filters']:
                        if limit['filterType'].lower() == 'lot_size':
                            market.at['trade_min'] = limit['minQty']
                            market.at['trade_max'] = limit['maxQty']
                    market.name = market.at['base'] + market.at['quot']

                    markets = markets.append(market)
        except Exception as e:
            Logger.log_error(e)

        finally:
            return markets
