import asyncio
import datetime
import time

import pandas as pd

from common import utils
from common import formats
from common import Logger
from common import RESTSocket

from exchanges import Exchange

class Bithumb(Exchange):
    name = 'bithumb'

    _run_rest = True
    _rest_limit = 1200
    _rest_path = 'https://api.bithumb.com/'


    __currency_rate = None
    __currency_rest = None
    __currency_path = 'http://free.currencyconverterapi.com/api/v5/'

    def __init__(self):
        super(Bithumb, self).__init__()

        self.__currency_rest = RESTSocket(url=self.__currency_path)
        self._add_custom_task(self.__currency_watcher)

######################    Private    #########################################
    async def __currency_watcher(self):
        while True:
            try:
                currency_data = await self.__currency_rest.request('convert', {
                        'q': 'KRW_USD',
                        'compact':'y'})
                self.__currency_rate = float(currency_data['KRW_USD']['val'])
                await asyncio.sleep(60)
            except Exception as e:
                Logger.log_error(e)
                await asyncio.sleep(1)

###########################    API    ########################################
    async def get_ticks(self):
        ticks = pd.DataFrame(data=[], columns=formats.tick)

        try:
            request_url = 'public/ticker/all'
            stock_data = await self.rest_send(request_url)

            current_date = datetime.datetime.now()
            for base_name in stock_data['data'].keys():
                if isinstance(stock_data['data'][base_name], dict):
                    tick = pd.Series(
                            data=[
                                self.name,
                                int(time.mktime(current_date.timetuple()))*1000,
                                '_'.join([base_name.lower(), 'krw']),
                                stock_data['data'][base_name]['closing_price'],],
                            index=formats.tick,
                            name=current_date,)
                    ticks = ticks.append(tick)

                    if self.__currency_rate is not None:
                        usd_tick = tick.copy()
                        usd_tick.at['market'] = '%s_usd'%(base_name.lower())
                        usd_tick.at['price'] = round(
                                (float(usd_tick.at['price'])
                                    * self.__currency_rate), 2)
                        ticks = ticks.append(usd_tick)

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
