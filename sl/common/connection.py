import datetime
import asyncio
import pandas as pd

from common import utils
from common import Logger

class Client():
    def __init__(self, connection):
        self.__connection = connection

    def send(self):
        self.__connection.source._recieve_message(message, self.__connection)

class Connection():
    source = None
    __initiator = None
    __filter = None

    __buffer_size = None
    __buffer = None
    __last_request = None

    __data_snapshot = None

    def __init__(self,
            source=None, initiator=None, fltr=None, buffer_size=None):
        self.source = source
        self.__initiator = initiator
        self.__filter = fltr

        self.__buffer_size = buffer_size or datetime.timedelta(seconds=0)
        self.__buffer = pd.DataFrame()
        self.__last_request = datetime.datetime.now()

        self.__data_snapshot = pd.DataFrame()

        self.client = Client(self)

    def __get_diffs(self, message):
        key_fields = ['exchange', 'market',]
        diff = pd.DataFrame()

        concat = pd.concat(
                self.__data_snapshot,
                data,).drop_duplicates().reset_index(drop=True)

        if self.__data_snapshot.shape[0] != concat.shape[0]:
            diff = concat.iloc[self.__data_snapshot.shape[0]:, :].reset_index(
                    drop=True)

            resulted_idxs = [max(group) for group in concat.groupby(
                    key_fields).groups.values()]

            resulted_frame = concat.reindex(resulted_idxs)
            self.__data_snapshot = resulted_frame

        return diff

    async def __send(self, message):
        try:
            message = self.__apply_filter(self.__get_diffs(message))

            if message is not None:
                current_time = datetime.datetime.now()

                message.index = [current_time]*message.shape[0]

                self.__buffer = self.__buffer.append(message)
                if current_time - self.__last_request >= self.__buffer_size:
                    await self.__release_buffer()
                else:
                    await asyncio.sleep(1
                            - (current_time
                                - self.__last_request).total_seconds())
                    current_time = datetime.datetime.now()
                    if (current_time - self.__last_request >= self.__buffer_size
                            and self.__buffer.shape[0] > 0):
                        await self.__release_buffer()

        except Exception as e:
            Logger.log_error(e)

    async def __release_buffer(self):
        try:
            current_time = datetime.datetime.now()
            data = self.__buffer.loc[
                    self.__last_request:current_time, :]

            self.__last_request = current_time
            await self.__initiator._recieve_message(
                    data,
                    self.client)
            self.__buffer = self.__buffer.loc[current_time:, :]
        except Exception as e:
            Logger.log_error(e)

    def __apply_filter(self, message):
        if self.__filter is None:
            return message
        elif self.__filter.empty:
            return None

        filtered = message
        for item in self.__filter.index:
            if item not in message.columns:
                return pd.DataFrame()
            else:
                filtered = filtered.loc[
                        filtered.loc[:, item].isin(self.__filter.at[item])]

        return filtered if not filtered.empty else None

################################   API   #####################################
    async def send(self, message):
        try:
            message = (message if isinstance(message, pd.DataFrame) else
                    pd.DataFrame().append(message))
            await self.__send(message)
        except Exception as e:
            Logger.log_error(e)

    def set_filter(self, fltr):
        self.__filter = fltr

    def add_filter(self, fltr):
        for item in fltr.index:
            if item in self.__filter.index:
                if isinstance(fltr.at[item], (list, set,)):
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
