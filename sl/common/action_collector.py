import inspect
import pandas as pd

from common import decorators
from common import Logger

class ActionCollector():
    __source = None

    def __init__ (self, source):
        self.__source = source

    async def execute(self, pure_action, connection):
        path = pure_action['action'].split('.')
        payload = pure_action['payload']

        args = list()
        kwargs = dict()
        if isinstance(payload, list):
            args = payload
        elif isinstance(payload, dict):
            kwargs = payload

        Logger.log_info('action')
        if path[0] == 'connection':
            action = getattr(connection, path[1])
            payload = pd.Series(data=[
                    [value] for value in args[0].values()],
                    index=args[0].keys(),)
            if inspect.iscoroutinefunction(action):
                return await action(*[payload], **kwargs)
            else:
                return action(*[payload], **kwargs)
        else:
            Logger.log_info('action await')
            return await getattr(
                    self.__source.at[path[0]], path[1])(*args, **kwargs)
