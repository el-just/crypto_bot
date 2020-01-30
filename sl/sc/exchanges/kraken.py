import datetime
import time

import pandas as pd

from common import utils
from common import formats
from common import Logger

from exchanges import Exchange

class Kraken(Exchange):
    name = 'kraken'

    _run_rest = True
    _run_rest_delay = 3
    _rest_limit = 1200
    _rest_path = 'https://api.kraken.com/0/'

###########################    API    ########################################
    async def get_ticks(self):
        ticks = pd.DataFrame(data=[], columns=formats.tick)

        try:
            request_url = 'public/Ticker'
            stock_data = await self.rest_send(
                    request_url,
                    params={'pair':','.join(
                        self._get_markets().index.values.tolist())},)

            current_date = datetime.datetime.now()
            for market_name in stock_data['result'].keys():
                market = self._get_markets().loc[market_name]
                ticks = ticks.append(pd.Series(
                        data=[
                            self.name,
                            int(time.mktime(current_date.timetuple()))*1000,
                            '_'.join([market.at['base'], market.at['quot']]),
                            stock_data['result'][market_name]['c'][0],],
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
            request_url = 'public/AssetPairs'
            stock_data = await self.rest_send(request_url)

            for market_name in stock_data['result'].keys():
                markets = markets.append(pd.Series(
                        data=[
                            self.name,
                            stock_data['result'][market_name]['base'].lower(),
                            stock_data['result'][market_name]['quote'].lower(),
                            None,
                            None,],
                        index=formats.market,
                        name=market_name))

        except Exception as e:
            Logger.log_error(e)

        finally:
            return markets
