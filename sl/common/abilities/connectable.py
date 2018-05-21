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
            connections = self.connections
            if groups is not None and len(groups) > 0:
                connections = self.connections[self.connections.apply(
                    lambda row: groups.issubset(row.at['groups']),
                    axis=1)]

            for key, connection in connections.iterrows():
                await connection.at['socket'].send(message, channel=channel)
        except Exception as e:
            Logger.log_error(e)

    def _accepted_connection(self, connection, meta):
        pass

    async def _recieve_message(self, message, connection, channel=None):
        pass

    async def _close_connection(self, connection):
        pass
