async def ConnectionFactory(*args, **kwargs):
    connection = Connection(*args, **kwargs)
    await connection.init()
    return connection.requestor

class Connection():
    __reciever = None
    __requestor = None

    meta = None
    reciever = None
    requestor = None
    channels = None

    def __init__(self, requestor=None, reciever=None, meta=None):
        self.__requestor = requestor
        self.__reciever = reciever

        self.meta = meta
        self.requestor = Socket(to=reciever, connection=self, tags=tags)
        self.reciever = Socket(to=requestor, connection=self)
        self.channels = {}

    await def init(self):
        try:
            self.open_channel(name='main')

            self.__reciever._register_connection(self.reciever, tags={'incoming'})
            await self.__reciever._accept_connection(self.reciever)
        except Exception as e:
            Logger.log_error(e)

    async def close(self):
        try:
            self.__requestor.connections.drop(
                    [id(self.requestor)],
                    axis=0,
                    inplace=True,)
            self.__reciever.connections.drop(
                    [id(self.reciever)],
                    axis=0,
                    inplace=True,)

            await self.__requestor._close_connection(self.requestor)
            await self.__reciever._close_connection(self.reciever)
        except Exception as e:
            Logger.log_error(e)

    def open_channel(self, **kwargs):
        self.channels[kwargs['name']] = Channel(self, **kwargs)
