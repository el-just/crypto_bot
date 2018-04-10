class ActionCollector():
    __source = None

    def __init__ (self, source):
        self.__source = source

    async def execute (self, owner, action, *args, **kwargs):
        return await getattr(self.__source.at[owner], action)(*args, **kwargs)
