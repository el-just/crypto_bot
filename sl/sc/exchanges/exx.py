import time
import datetime

import pandas as pd

from common import utils
from common import formats
from common import Logger

from exchanges.exchange import Exchange

class Exx(Exchange):
    name = 'exx'

    _ws_path = 'wss://ws.exx.com/websocket'
    _rest_path = 'https://api.exx.com/data/v1/'

######################    Exchange required   ################################
    async def _resolve_message(self, message):
        payload = None

        try:
            message = utils.parse_data(message)
            if message.get('market', None) is not None:
                payload = self.__assume_tick_package(message)
        except Exception as e:
            Logger.log_error(e)

        finally:
            return payload

    async def _subscribe_channels(self):
        try:
            await self.ws_send({
                    'dataType':'EXX_MARKET_LIST_ALL',
                    'dataSize':1,
                    'action':'ADD',})
        except Exception as e:
            Logger.log_error(e)

######################    Private    #########################################
    def __assume_tick_package(self, package_data):
        tick_package = pd.DataFrame(data=[], columns=formats.tick)

        try:
            current_date = datetime.datetime.now()
            for market_data in package_data['market']:
                market = self._get_markets().loc[
                        '_'.join([market_data[2], market_data[1]])]
                tick_package = tick_package.append(pd.Series(
                        data=[
                            self.name,
                            int(time.mktime(current_date.timetuple()))*1000,
                            '_'.join([market.at['base'], market.at['quot']]),
                            market_data[4],],
                        index=formats.tick,
                        name=current_date,))

            Logger.log_info(tick_package)
        except Exception as e:
            Logger.log_error(e)

        finally:
            return tick_package

###########################    API    ########################################
    async def get_markets(self):
        markets = pd.DataFrame(data=[], columns=formats.market)

        try:
            request_url = 'markets'

            stock_data = await self.rest_send(request_url)
            for market_name in stock_data.keys():
                markets = markets.append(pd.Series(
                        data=[
                            self.name,
                            market_name.split('_')[0],
                            market_name.split('_')[1],
                            None,
                            None,],
                        index=formats.market,
                        name=market_name,))
        except Exception as e:
            Logger.log_error(e)

        finally:
            return markets
