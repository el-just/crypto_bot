import pandas as pd
import numpy as np
import aiohttp
import datetime
import asyncio
import urllib.parse

from abstract.logging import Logging
from stocks.bitfinex.defines import DEFINES

class RESTSocket (Logging):
    _url = 'https://api.bitfinex.com/v2/'
    _tick_period_url = 'candles/trade:1m:tBTCUSD/hist?'
    _timeline = pd.DataFrame (data=[], columns=['request'])
    _queue = []
    _stock = None

    def __init__ (self, stock):
        self._stock = stock

    async def _process_request (self, request):
        try:
            request.name = datetime.datetime.now()
            self._timeline = self._timeline.append (request)
            async with aiohttp.ClientSession() as session:
                self.log_info ('Bitfinex request:\n\t{0}'.format(str(request.at["request"])))
                async with session.get(request.at["request"]) as resp:
                    text = await resp.text()
                    return text
        except Exception as e:
            self.log_error (e)

    async def _request (self, url, params):
        try:
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
        except Exception as e:
            self.log_error (e)

    def fract_period (sekf, period):
        request_periods = []
        step_date = period['start']
        while step_date < period['end']:
            end_date = step_date + DEFINES.AVAILABLE_GAP if period['end'] - (step_date + DEFINES.AVAILABLE_GAP) > 0 else period['end']
            request_periods.append ({
                'start': step_date,
                'end': end_date
                })

            step_date = end_date + DEFINES.TICK_PERIOD

        return request_periods

    def request_text (self, period):
        params = {'limit':1000, 'start':str(int(period['start']))+'000', 'end':str(int(period['end']))+'000'}
        return (self._url+self._tick_period_url+urllib.parse.urlencode(params))

    async def get_tick_period (self, period):
        try:
            request_periods = self.fract_period(period)
            tick_frame = pd.DataFrame (data=[], columns=['timestamp', 'base', 'quot', 'close', 'volume'], dtype={'close':np.float64})

            for period in request_periods:
                params = {'limit':1000, 'start':str(int(period['start']))+'000', 'end':str(int(period['end']))+'000'}
                period_pure_data = await self._request (self._url + self._tick_period_url, params)
                
                period_frame = self._parse_data (period_pure_data)
                tick_frame = tick_frame.append (period_frame)

                if period_frame is not None:
                    await self._stock._storage.insert_ticks (period_frame)
            
            return tick_frame
        except Exception as e:
            self.log_error (e)

    def _parse_data (self, pure_data):
        if pure_data[0] != '[':
            self.log_error (str(pure_data))

        if pure_data == '[]':
            return None

        frame = pd.DataFrame (data=[], columns=['timestamp', 'base', 'quot', 'close', 'volume'], dtype={'close':np.float64})
        for tick_data in [text_array.split(',') for text_array in pure_data[2:-2].split('],[')]:
            tick = pd.Series (data=[int(tick_data[0][:-3]), 'btc', 'usd', float(tick_data[2]), float(tick_data[5])], index=['timestamp', 'base', 'quot', 'close', 'volume'], dtype={'close':np.float64})
            tick.name = datetime.datetime.fromtimestamp(tick.at['timestamp'])
            frame = frame.append (tick)

        return frame