from common import Logger

class Socket():
    source = None

    def __init__(self, source=None):
        self.source = source
        if source is not None:
            source.connect(self)

    async def push(self, data):
        try:
            await self.source.push(source=self, data=data)
        except Exception as e:
            Logger.log_error(e)

    async def close(self):
        self.source.disconnect(self)

    async def on_data(self, data): pass
