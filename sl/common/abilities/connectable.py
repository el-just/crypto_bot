from common import Connection
from common import Logger

class Connectable():
    connections = None

    def connect(self, reciever, tags=set(), **kwargs):
        connection = Connection(
                requestor=self,
                reciever=reciever,
                tags=tags,
                **kwargs)

        return connection.requestor

    async def publish(self, message, tags=set(), channel=None):
        try:
            connections = self.connections
            if tags is not None and len(tags) > 0:
                connections = self.connections[self.connections.apply(
                    lambda row: tags.issubset(row.at['tags']),
                    axis=1)]

            for key, connection in connections.iterrows():
                await connection.at['socket'].send(message, channel=channel)
        except Exception as e:
            Logger.log_error(e)

    def _accepted_connection(self, connection, meta=None):
        pass

    async def _recieve_message(self, message, connection, channel=None):
        pass

    async def _close_connection(self, connection):
        pass
