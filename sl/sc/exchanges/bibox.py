import datetime
import time

import pandas as pd

from common import utils
from common import formats
from common import Logger

from exchanges import Exchange

class Bibox(Exchange):
    name = 'bibox'

    _run_rest = True
    _rest_limit = 1200
    _rest_path = 'https://api.bibox.com/'

    _key = 'fbf3b49e51f1df161dea69e64c974ca18ce451be'
    _pattern = '6e05463781eb384edf6e12c4bd55d9c5a3017c49'

###########################    API    ########################################
    async def get_ticks(self):
        ticks = pd.DataFrame(data=[], columns=formats.tick)

        try:
            request_url = 'v1/mdata'
            stock_data = await self.rest_send(
                    request_url,
                    params={
                        'cmd':'marketAll',},)

            current_date = datetime.datetime.now()
            for market_data in stock_data['result']:
                market = self._get_markets().loc[market_data['id']]
                ticks = ticks.append(pd.Series(
                        data=[
                            self.name,
                            int(time.mktime(current_date.timetuple()))*1000,
                            '_'.join([market.at['base'], market.at['quot']]),
                            market_data['last'],],
                        index=formats.tick,
                        name=current_date,))

            Logger.log_info(ticks)
        except Exception as e:
            Logger.log_error(e)

        finally:
            return ticks

    async def get_markets(self):
        markets = pd.DataFrame(data=[], columns=formats.market)

        try:
            request_url = 'v1/mdata'
            stock_data = await self.rest_send(
                    request_url,
                    params={
                        'cmd':'pairList',},)

            for market in stock_data['result']:
                markets = markets.append(pd.Series(
                        data=[
                            self.name,
                            market['pair'].split('_')[0].lower(),
                            market['pair'].split('_')[1].lower(),
                            None,
                            None,],
                        index=formats.market,
                        name=market['id']))

        except Exception as e:
            Logger.log_error(e)

        finally:
            return markets
