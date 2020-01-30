import time
import datetime

import pandas as pd

from common import utils
from common import formats
from common import Logger

from exchanges.exchange import Exchange

class Zb(Exchange):
    name = 'zb'

    _ws_path = 'wss://api.zb.com:9999/websocket'
    _rest_path = 'http://api.zb.com/data/v1/'

######################    Exchange required   ################################
    async def _resolve_message(self, message):
        payload = None

        try:
            message = utils.parse_data(message)
            if message.get('ticker', None) is not None:
                payload = self.__assume_tick(message)
        except Exception as e:
            Logger.log_error(e)

        finally:
            return payload

    async def _subscribe_channels(self):
        try:
            for market_name, market in self._get_markets().iterrows():
                await self.ws_send({
                        'event':'addChannel',
                        'channel':'%s_ticker'%(market_name),})
        except Exception as e:
            Logger.log_error(e)

######################    Private    #########################################
    def __assume_tick(self, tick_data):
        tick = None

        try:
            current_date = datetime.datetime.now()
            market = self._get_markets().loc[
                    tick_data['channel'].split('_')[0]]
            tick = pd.Series(
                    data=[
                        self.name,
                        int(time.mktime(current_date.timetuple()))*1000,
                        '_'.join([market.at['base'], market.at['quot']]),
                        tick_data['ticker']['last'],],
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
                        name=market_name.replace('_', ''),))
        except Exception as e:
            Logger.log_error(e)

        finally:
            return markets
