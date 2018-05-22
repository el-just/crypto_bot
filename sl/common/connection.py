import datetime
import asyncio
import pandas as pd

from common import utils
from common import Logger

class Socket():
    def __init__(self, side, connection):
        self.__side = side
        self.__connection = connection
        self.meta = connection.meta

    async def send(self, message, channel=None):
        try:
            channel = channel if channel is not None else 'main'
            await self.__connection.channels[channel].send(
                    message, self.__side)
        except Exception as e:
            Logger.log_error(e)

    async def close(self):
        try:
            await self.__connection.close()
        except Exception as e:
            Logger.log_error(e)

    def open_channel(self, **kwargs):
       self.__connection.open_channel(**kwargs)

class Channel():
    __data_snapshot = None

    def __init__(self,
            connection,
            name=None,
            type_=None):
        self.name = name
        self.type_ = type_
        self.__connection = connection

        self.__data_snapshot = pd.DataFrame()

    async def send(self, message, reciever):
        if self.type_ == 'frame':
            message = (message if isinstance(message, pd.DataFrame) else
                    pd.DataFrame().append(message))

            combined = message.combine_first(self.__data_snapshot)
            message = self.__get_diff(self.__data_snapshot, combined)

            if not message.empty:
                self.__data_snapshot = combined
            else:
                message = None

        if message is not None:
            await reciever._recieve_message(
                    message,
                    reciever.connections.loc[id(self.__connection), :],
                    channel=self.name)

    def __get_diff(self, old, new):
        diff = pd.DataFrame()
        concat = old.append(new).drop_duplicates()

        if self.__data_snapshot.shape[0] != concat.shape[0]:
            pre_diff = concat.iloc[old.shape[0]:, :]

            for idx, row in pre_diff.iterrows():
                for column in row.index.values:
                    if idx in old.index and column in old.columns:
                        if row.at[column] == old.loc[idx, :].at[column]:
                            row.at[column] = None

            diff = pre_diff.dropna(how='all')

        return diff

class Connection():
    reciever = None
    requestor = None
    meta = None
    channels = None

    __reciever = None
    __requestor = None
    __tags = None
    def __init__(self, requestor=None, reciever=None, tags=set(), meta=None):
        self.__requestor = requestor
        self.__reciever = reciever
        self.__tags = set(tags)

        self.meta = meta
        self.requestor = Socket(self.__reciever, self)
        self.reciever = Socket(self.__requestor, self)

        self.channels = {}

        self.__register_connections()
        self.open_channel(name='main')

    def __empty_connections(self):
        return pd.DataFrame(data=[], columns=[
                'tags', 'socket'])

    def __register_connections(self):
        if self.__requestor.connections is None:
            self.__requestor.connections = self.__empty_connections()
        self.__requestor.connections = self.__requestor.connections.append(
                pd.Series(
                    data=[
                        {'outgoing'} | self.__tags,
                        self.requestor,],
                    index=['tags', 'socket'],
                    name=id(self),))

        if self.__reciever.connections is None:
            self.__reciever.connections = self.__empty_connections()
        self.__reciever.connections = self.__reciever.connections.append(
                pd.Series(
                    data=[
                        {'incoming'},
                        self.reciever,],
                    index=['tags', 'socket'],
                    name=id(self),))

        self.__reciever._accept_connection(
                self.__reciever.connections.loc[id(self)])

    async def close(self):
        self.__requestor.connections.drop(
                [id(self)],
                axis=0,
                inplace=True,)
        self.__reciever.connections.drop(
                [id(self)],
                axis=0,
                inplace=True,)

        await self.__requestor._close_connection(
                self.__requestor.connections.loc[id(self)])
        await self.__reciever._close_connection(
                self.__reciever.connections.loc[id(self)])

    def open_channel(self, **kwargs):
        self.channels[kwargs['name']] = Channel(self, **kwargs)

class Connection_old():
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
            await self.__initiator.send(data)
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
