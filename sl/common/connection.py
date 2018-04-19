import datetime
import pandas as pd

from common import utils
from common import Logger

class Connection():
    __stream = None
    __client = None
    __filter = None

    __interval = None
    __buffer = None
    __last_request = None

    def __init__(self, stream=None, client=None, filter=None, interval=None):
        self.__stream = stream
        self.__client = client
        self.__filter = filter

        self.__interval = interval or datetime.timedelta(seconds=0)
        self.__buffer = pd.DataFrame()
        self.__last_request = datetime.datetime.now()

    async def __send(self, message):
        try:
            if self._filter is None or message.name in self.__filter:
                current_time = datetime.datetime.now()
                if current_time - self.__last_request >= self.__interval:
                    data = self.__buffer.loc[
                            self.__last_request:current_time, :]
                    data = data.iloc[0] if data.shape[0] == 1 else data

                    self.__last_request = current_time
                    self.__client.send(utils.stringify_data(data))

                    self.__buffer = self.__buffer.loc[current_time:, :]
                else:
                    message.name = current_time
                    self.__buffer = self._buffer.append(message)

        except Exception as e:
            Logger.log_error(e)

################################   API   #####################################

    async def send(self, message):
        try:
            await self.__send(message)
        except Exception as e:
            Logger.log_error(e)
