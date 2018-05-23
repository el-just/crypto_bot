from common import Connection
from common import Logger

class Connectable():
    _connections = None

    async def connect(self, reciever, tags=set(), **kwargs):
        connection = await Connection(
                requestor=self,
                reciever=reciever,
                **kwargs,)
        self._register_connection(connection, tags=({'outgoing'} | tags))

    def _register_connection(self, connection, tags=set()):
        if self.connections is None:
            self.connections = self.__empty_connections()

        connection.tags = tags
        self.connections = self.connections.append(
                pd.Series(
                    data=[tags, connection],
                    index=['tags', 'socket'],
                    name=id(connection),))

    def get_connections(self, tags=None):
        connections = set()
        if tags is not None and len(tags) > 0:
            connections = set(self.connections[self.connections.apply(
                lambda row: tags.issubset(row.at['tags']),
                axis=1)].loc[:, 'socket'].values.tolist())

        return connections

    async def publish(self, message, tags=set(), channel=None):
        try:
            for connection in self.get_connections(tags=tags):
                await connection.send(message, channel=channel)
        except Exception as e:
            Logger.log_error(e)

    async def _accept_connection(self, connection):
        pass

    async def _recieve_message(self, message, connection, channel=None):
        pass

    async def _close_connection(self, connection):
        pass
