import datetime
import pandas as pd

from common import utils
from common import Logger
from common import decorators

class Connection():
    __stream = None
    __client = None
    __filter = None

    __interval = None
    __buffer = None
    __last_request = None

    def __init__(self, stream=None, client=None, fltr=None, interval=None):
        self.__stream = stream
        self.__client = client
        self.__filter = fltr or pd.Series()

        self.__interval = interval or datetime.timedelta(seconds=0)
        self.__buffer = pd.DataFrame()
        self.__last_request = datetime.datetime.now()

    async def __send(self, message):
        try:
            if (len(self.__filter.index) == 0
                    or self.__compare_with_filter(message)):
                current_time = datetime.datetime.now()
                if current_time - self.__last_request >= self.__interval:
                    data = self.__buffer.loc[
                            self.__last_request:current_time, :]
                    data = data.iloc[0] if data.shape[0] == 1 else data

                    self.__last_request = current_time
                    Logger.log_info('send')
                    self.__client.send(utils.stringify_data(data))

                    self.__buffer = self.__buffer.loc[current_time:, :]
                else:
                    message.name = current_time
                    self.__buffer = self.__buffer.append(message)

        except Exception as e:
            Logger.log_error(e)

    @decorators.validate(pd.Series)
    def add_filter(self, fltr):
        for item in fltr.index:
            if item in self.__filter.index:
                if isnstance(fltr.at[item], (list, set,)):
                    self.__filter.at[item] = (self.__filter.at[item]
                            + list(fltr.at[item]))
                else:
                    self.__filter.at[item] = self.__filter.at[item].append(
                            fltr.at[item])
            else:
                if isnstance(fltr.at[item], (list, set,)):
                    self.__filter.at[item] = list(fltr.at[item])
                else:
                    self.__filter.at[item] = [fltr.at[item]]

    def set_filter(self, fltr):
        self.__filter = fltr

    def __compare_with_filter(self, message):
        fit = True
        for item in self.__filter.index:
            if (item not in message.index
                    or message.at[item] not in self.__filter.at[item]):
                fit = False
                break
        return fit

################################   API   #####################################

    async def send(self, message):
        try:
            await self.__send(message)
        except Exception as e:
            Logger.log_error(e)
