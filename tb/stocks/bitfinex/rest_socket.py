import pandas as pd
import aiohttp
import datetime
import asyncio
import urllib.parse

from stocks.bitfinex.defines import DEFINES

class RESTSocket ():
    _url = 'https://api.bitfinex.com/v2/'
    _tick_period_url = 'candles/trade:1m:tBTCUSD/hist?'
    _timeline = pd.DataFrame (data=[], columns=['request'])
    _queue = []

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

        if self._timeline.loc[:, "request"].count() < DEFINES.REST_REQUEST_LIMIT:
            response = await self._process_request (request)
        else:
            self._queue.append (request)
            await asyncio.sleep (len(self._queue)*DEFINES.TICK_PERIOD)
            response = await self._process_request (self._queue.pop (0))

        return response

    async def get_tick_period (self, period):
        request_periods = []

        step_date = period['start']
        while step_date < period['end']:
            end_date = step_date + DEFINES.AVAILABLE_GAP if period['end'] - (step_date + DEFINES.AVAILABLE_GAP) > 0 else period['end']
            request_periods.append ({
                'start': step_date,
                'end': end_date
                })

            step_date = end_date + DEFINES.TICK_PERIOD

        tick_period_frame = pd.DataFrame (data=[], columns=['timestamp', 'base', 'quot', 'close', 'volume'])
        for period in request_periods:
            params = {'limit':1000, 'start':str(int(period['start']))+'000', 'end':str(int(period['end']))+'000'}
            period_pure_data = await self._request (self._url + self._tick_period_url, params)
            
            period_frame = self._parse_data (period_pure_data)
            tick_period_frame = tick_period_frame.append(period_frame, ignore_index=True)

        return tick_period_frame

    def _parse_data (self, pure_data):
        if pure_data[0] != '[':
            f = open ('./logs/error.log', 'a+')
            f.write ('{0}: {1}\n'.format(datetime.datetime.now().isoformat(), str(pure_data)))
            f.close ()
        frame = pd.DataFrame (data=[], columns=['timestamp', 'base', 'quot', 'close', 'volume'])
        for tick_data in [text_array.split(',') for text_array in pure_data[2:-2].split('],[')]:
            tick = pd.Series (data=[int(tick_data[0][:-3]), 'btc', 'usd', float(tick_data[2]), float(tick_data[5])], index=['timestamp', 'base', 'quot', 'close', 'volume'])
            frame = frame.append (tick, ignore_index=True)

        return frame