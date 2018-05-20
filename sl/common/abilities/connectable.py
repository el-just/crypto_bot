from common import Connection
from common import Logger

class Connectable():
    connections = None

    def connect(self, reciever, groups=[], **kwargs):
        connection = Connection(
                requestor=self,
                reciever=reciever,
                groups=groups,
                **kwargs)

        return connection.requestor

    async def publish(self, message, groups=set(), channel=None):
        try:
            for key, connection in self.__filter_connections(groups).iterrows():
                await connection.at['socket'].send(message)
        except Exception as e:
            Logger.log_error(e)

    def __filter_connections(self, groups):
        if groups is None or len(groups) == 0:
            return self.connections

        return self.connections[self.connections.apply(
            lambda row: groups.issubset(row.at['groups']),
            axis=1)]

    def _accepted_connection(self, connection):
        pass

    async def _recieve_message(self, message, connection, channel=None):
        pass

    async def _close_connection(self, connection):
        pass
