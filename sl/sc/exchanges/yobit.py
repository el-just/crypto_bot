import datetime
import time

import pandas as pd

from common import utils
from common import formats
from common import Logger

from exchanges import Exchange

class Yobit(Exchange):
    name = 'yobit'

    _run_rest = True
    _run_rest_delay = 10
    _filter = ('usd',)
    _rest_limit = 1200
    _rest_path = 'https://yobit.net/api/'

###########################    API    ########################################
    async def get_ticks(self):
        ticks = pd.DataFrame(data=[], columns=formats.tick)

        try:
            current_idx = 0
            markets = self._get_markets()
            while current_idx < self._get_markets().shape[0]:
                to_idx = current_idx + 30
                request_url = '3/ticker/%s'%('-'.join([
                        mkt for mkt in markets.index.values.tolist()[
                            current_idx:to_idx]]))
                stock_data = await self.rest_send(request_url, params={
                        'ignore_invalid':1})

                current_date = datetime.datetime.now()
                for market_name in stock_data.keys():
                    market = self._get_markets().loc[market_name]
                    ticks = ticks.append(pd.Series(
                            data=[
                                self.name,
                                int(time.mktime(
                                    current_date.timetuple()))*1000,
                                '_'.join([
                                    market.at['base'],
                                    market.at['quot']]),
                                stock_data[market_name]['last'],],
                            index=formats.tick,
                            name=current_date,))

                current_idx = to_idx

            Logger.log_info(ticks)
        except Exception as e:
            Logger.log_error(e)

        finally:
            return ticks

    async def get_markets(self):
        markets = pd.DataFrame(data=[], columns=formats.market)

        try:
            request_url = '3/info'
            stock_data = await self.rest_send(request_url)

            for market_name in stock_data['pairs'].keys():
                if market_name.split('_')[1] in self._filter:
                    markets = markets.append(pd.Series(
                            data=[
                                self.name,
                                market_name.split('_')[0],
                                market_name.split('_')[1],
                                None,
                                None,],
                            index=formats.market,
                            name=market_name))
        except Exception as e:
            Logger.log_error(e)

        finally:
            return markets
