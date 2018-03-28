import ast
import datetime
import asyncio
import aiohttp
import urllib.parse

import pandas as pd
from common.logger import Logger

REQUEST_INTERVAL_SECONDS = 60

class RESTSocket ():
    _base_url = None

    _timeline = None
    _queue = None

    _request_limit = None

    def __init__ (self, url=None, request_limit=10):
        self._base_url = url
    
        self._timeline = pd.DataFrame (data=[], columns=['request'])
        self._queue = []

        self._request_limit = request_limit

    def _parse_response (self, response_text):
        try:
            reponse = None

            if response_text is not None and type(response_text) == str:
                response_text = response_text.replace ('null', 'None')
                response_text = response_text.replace ('undefined', 'None')
                response_text = response_text.replace ('true', 'True')
                response_text = response_text.replace ('false', 'False')
                response = ast.literal_eval(response_text)

            return response
        except Exception as e:
            Logger.log_error (e)

    async def _process_request (self, full_url):
        try:
            request = pd.Series (data=[full_url], index=['request'])
            request.name = datetime.datetime.now()
            self._timeline = self._timeline.append (request)

            async with aiohttp.ClientSession() as session:
                async with session.get(full_url) as resp:
                    text = await resp.text()
                    return self._parse_response (text)
        except Exception as e:
            Logger.log_error (e)

######################## API ########################
    async def request (self, request_url, params=None):
        try:
            response = None
            full_url = self._base_url + request_url
            if params:
                full_url += '?'+urllib.parse.urlencode(params)
            print (full_url)
            
            now = datetime.datetime.now()
            self._timeline = self._timeline.loc [now - datetime.timedelta(seconds=REQUEST_INTERVAL_SECONDS): now]
            if self._timeline.loc[:, "request"].count() <= self._request_limit:
                response = await self._process_request (full_url)
            else:
                self._queue.append (full_url)
                await asyncio.sleep (REQUEST_INTERVAL_SECONDS + len(self._queue) // self._request_limit * REQUEST_INTERVAL_SECONDS)
                response = await self._process_request (full_url)

            return response
        except Exception as e:
            Logger.log_error (e)
