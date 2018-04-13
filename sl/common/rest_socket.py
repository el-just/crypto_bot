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

            async with aiohttp.ClientSession() as session:
                async with session.get(full_url) as resp:
                    text = await resp.text()
                    return utils.parse_data(text)
        except Exception as e:
            Logger.log_error(e)

######################## API ########################
    async def request(self, request_url, params=None):
        response = None

        try:
            full_url = self.__base_url + request_url
            if params is not None:
                full_url += '?'+urllib.parse.urlencode(params)

            now = datetime.datetime.now()
            self.__timeline = self.__timeline.loc[now - datetime.timedelta(
                    seconds=REQUEST_INTERVAL_SECONDS): now]
            if (self.__timeline.loc[:, "request"].count()
                    <= self.__request_limit):
                response = await self.__process_request(full_url)
            else:
                self.__queue.append(full_url)
                await asyncio.sleep(
                        REQUEST_INTERVAL_SECONDS + len(self._queue)
                        // self.__request_limit * REQUEST_INTERVAL_SECONDS)
                response = await self.__process_request(full_url)

            return response
        except Exception as e:
            Logger.log_error(e)

        finally:
            return response
