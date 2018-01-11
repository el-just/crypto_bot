import pandas as pd
import aiohttp
import datetime
import asyncio

class RESTSocket ():
    _url = 'https://api.bitfinex.com/v2/'
    _tick_period_url = 'candles/trade:1m:tBTCUSD/hist?'
    _timeline = pd.DataFrame (data=[], columns=['request'])
    _queue = []
    _limit = 10
    _default_tick_period = 60
    _available_gap = 59940

    async def _process_request (self, request):
        request.name = datetime.datetime.now()
        self._timeline = self._timeline.append (request)
        async with aiohttp.ClientSession() as session:
            async with session.get(request.at["request"]) as resp:
                text = await resp.text()
                return text

    async def _request (self, url, params):
        now = datetime.datetime.now()

        request = pd.Series (data=[url+urllib.parse.urlencode(params)], index=['request'])
        self._timeline = self._timeline.loc [now - datetime.timedelta(minutes=1): now]

        if self._timeline.loc[:, "request"].count() < self._limit:
            response = await self._process_request (request)
        else:
            self._queue.append (request)
            await asyncio.sleep (len(self._queue)*self._default_tick_period)
            response = await self._process_request (self._queue.pop (0))

        return response

    async def get_tick_period (self, period):
        request_periods = []

        step_date = period['start']
        while step_date < period['end']:
            end_date = step_date + self._available_gap if period['end'] - (step_date + self._available_gap) > 0 else period['end']
            request_periods.append ({
                'start': step_date,
                'end': end_date
                })

            step_date = end_date + self._default_tick_period

        #TODO: tick_format and tex parsing
        tick_period_frame = pd.DataFrame ()
        for period in request_periods:
            params = {'limit':1000, 'start':str(int(period['start']))+'000', 'end':str(int(period['end']))+'000'}
            period_pure_data = await self._request (self._url + self._tick_period_url, params)
            
            period_data = self._parse_data (period_pure_data)
            period_frame = pd.DataFrame ()
            tick_period_data.append(period_pure_data)

        return tick_period_data
