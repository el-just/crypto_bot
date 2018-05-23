class Socket():
    tags = None

    __side = None
    __connection = None

    def __init__(self, to=None, connection=None, tags=set()):
        self.tags = tags

        self.__side = to
        self.__connection = connection

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

    async def execute(self, action, *args, **kwargs)
        try:
            await self.__side._execute(action, *args, **kwargs)
        except Exception as e:
            Logger.log_error(e)
