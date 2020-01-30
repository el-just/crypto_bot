import datetime
import time

import pandas as pd

from common import utils
from common import formats
from common import Logger

from exchanges import Exchange

class Simex(Exchange):
    name = 'simex'

    _run_rest = True
    _rest_limit = 1000
    _rest_path = 'https://simex.global/api/'

###########################    API    ########################################
    async def get_ticks(self):
        ticks = pd.DataFrame(data=[], columns=formats.tick)

        try:
            request_url = 'pairs'
            stock_data = await self.rest_send(request_url)

            current_date = datetime.datetime.now()
            for market in stock_data['data']:
                if market['last_price'] is not None:
                    ticks = ticks.append(pd.Series(
                            data=[
                                self.name,
                                int(time.mktime(current_date.timetuple()))*1000,
                                '_'.join([
                                    market['base']['name'].lower(),
                                    market['quote']['name'].lower()]),
                                market['last_price'],],
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
            ticks = await self.get_ticks()

            for key, tick in ticks.iterrows():
                markets = markets.append(pd.Series(
                        data=[
                            self.name,
                            tick.at['market'].split('_')[0],
                            tick.at['market'].split('_')[1],
                            None,
                            None,],
                        index=formats.market,
                        name=tick.at['market'].split('_')[0].upper()))

        except Exception as e:
            Logger.log_error(e)

        finally:
            return markets
