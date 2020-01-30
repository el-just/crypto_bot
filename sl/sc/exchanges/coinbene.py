import datetime
import time

import pandas as pd

from common import utils
from common import formats
from common import Logger

from exchanges import Exchange

class Coinbene(Exchange):
    name = 'coinbene'

    _run_rest = True
    _rest_limit = 1000
    _rest_path = 'http://api.coinbene.com/v1/'

###########################    API    ########################################
    async def get_ticks(self):
        ticks = pd.DataFrame(data=[], columns=formats.tick)

        try:
            request_url = 'market/ticker'
            stock_data = await self.rest_send(request_url, params={
                    'symbol': 'all'})

            current_date = datetime.datetime.now()
            for market in stock_data['ticker']:
                base = None
                quot = None
                if market['symbol'][-3:] in ('BTC', 'ETH'):
                    quot = market['symbol'][-3:].lower()
                    base = market['symbol'][:-3].lower()
                else:
                    quot = market['symbol'][-4:].lower()
                    base = market['symbol'][:-4].lower()
                ticks = ticks.append(pd.Series(
                        data=[
                            self.name,
                            int(time.mktime(current_date.timetuple()))*1000,
                            '_'.join([base, quot]),
                            market['last'],],
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
