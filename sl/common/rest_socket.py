import ast
import datetime
import asyncio
import aiohttp
import urllib.parse

import pandas as pd
from common import Logger
from common import utils

REQUEST_INTERVAL_SECONDS = 60

class RESTSocket():
    __base_url = None

    __timeline = None
    __queue = None

    __request_limit = None

    def __init__(self, url=None, request_limit=10):
        self.__base_url = url

        self.__timeline = pd.DataFrame(data=[], columns=['request'])
        self.__queue = []

        self.__request_limit = request_limit

    async def __process_request(self, full_url):
        try:
            request = pd.Series(data=[full_url], index=['request'])
            request.name = datetime.datetime.now()
            self.__timeline = self.__timeline.append(request)
            headers={
                    'Accept': ('text/html,application/xhtml+xml'
                        + ',application/xml;q=0.9,image/webp,'
                        + 'image/apng,*/*;q=0.8'),
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Cache-Control': 'max-age=0',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'User-Agent': ('Mozilla/5.0 (Macintosh;'
                        + ' Intel Mac OS X 10_11_6) AppleWebKit/537.36 '
                        + '(KHTML, like Gecko) Chrome/66.0.3359.139'
                        + ' Safari/537.36'),}

            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(full_url) as resp:
                    text = await resp.text()
                    return utils.parse_data(text)
        except Exception as e:
            Logger.log_error(e)

    async def __post(self, url, params=None):
        try:
            request = pd.Series(data=[url], index=['request'])
            request.name = datetime.datetime.now()
            self.__timeline = self.__timeline.append(request)

            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=params) as resp:
                    text = await resp.text()
                    return utils.parse_data(text)
        except Exception as e:
            Logger.log_error(e)

######################## API ########################
    async def request(self, request_url, params=None, type_='get'):
        response = None

        try:
            full_url = self.__base_url + request_url

            if type_ == 'get' and params is not None:
                full_url += '?'+urllib.parse.urlencode(params)

            now = datetime.datetime.now()
            self.__timeline = self.__timeline.loc[now - datetime.timedelta(
                    seconds=REQUEST_INTERVAL_SECONDS): now]
            if (self.__timeline.loc[:, "request"].count()
                    > self.__request_limit):
                self.__queue.append(full_url)
                await asyncio.sleep(
                        REQUEST_INTERVAL_SECONDS + len(self._queue)
                        // self.__request_limit * REQUEST_INTERVAL_SECONDS)

            if type_ == 'get':
                response = await self.__process_request(full_url)
            else:
                response = await self.__post(full_url, params=params)

            return response
        except Exception as e:
            Logger.log_error(e)

        finally:
            return response
