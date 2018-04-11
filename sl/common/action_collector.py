from common import decorators

class ActionCollector():
    __source = None

    def __init__ (self, source):
        self.__source = source

    @decorators.pass_if_empty
    async def execute(self, pure_action):
        path = pure_action['data']['path'].split('.')
        payload = pure_action['data']['payload']

        args = list()
        kwargs = dict()
        if isinstance(payload, list):
            args = payload
        elif isinstance(payload, dict):
            kwargs = payload

        return await getattr(
                self.__source.at[path[0]], path[1])(*args, **kwargs)
