import time
import datetime

import pandas as pd

from common import utils
from common import formats
from common import Logger

from exchanges.exchange import Exchange

class Gateio(Exchange):
    name = 'gateio'

    _ws_path = 'wss://ws.gate.io/v3/'
    _rest_path = 'http://data.gate.io/api2/1/'

######################    Exchange required   ################################
    async def _resolve_message(self, message):
        payload = None

        try:
            message = utils.parse_data(message)
            if message.get('method', None) == 'ticker.update':
                payload = self.__assume_tick(message)
        except Exception as e:
            Logger.log_error(e)

        finally:
            return payload

    async def _subscribe_channels(self):
        try:
            await self.ws_send({
                    "id": self._get_request_counter(),
                    "method": "ticker.subscribe",
                    "params": self._get_markets().index.values.tolist()},)
        except Exception as e:
            Logger.log_error(e)

######################    Private    #########################################
    def __assume_tick(self, tick_data):
        tick = None

        try:
            current_date = datetime.datetime.now()
            market = self._get_markets().loc[tick_data['params'][0]]
            tick = pd.Series(
                    data=[
                        self.name,
                        int(time.mktime(current_date.timetuple()))*1000,
                        '_'.join([
                            market.at['base'].lower(),
                            market.at['quot'].lower(),]),
                        tick_data['params'][1]['close'],],
                    index=formats.tick,
                    name=current_date,)
        except Exception as e:
            Logger.log_error(e)

        finally:
            return tick

###########################    API    ########################################
    async def get_markets(self):
        markets = pd.DataFrame(data=[], columns=formats.market)

        try:
            request_url = 'pairs'

            stock_data = await self.rest_send(request_url)
            for market_name in stock_data:
                markets = markets.append(pd.Series(
                        data=[
                            self.name,
                            market_name.split('_')[0],
                            market_name.split('_')[1],
                            None,
                            None,],
                        index=formats.market,
                        name=market_name.upper(),))
        except Exception as e:
            Logger.log_error(e)

        finally:
            return markets
