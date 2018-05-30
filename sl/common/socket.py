import asyncio

from common import Logger
from common import utils

class Socket():
    source = None

    __await_events = None
    __events_results = None
    def __init__(self, source=None):
        self.source = source
        if source is not None:
            source.connect(self)

        self.__await_events = dict()
        self.__events_results = dict()

    async def push(self, data):
        try:
            await self.source.push(source=self, data=data)
        except Exception as e:
            Logger.log_error(e)

    async def close(self):
        self.source.disconnect(self)

    async def on_data(self, data): pass

    async def _data_recieved(self, data):
        try:
            if (isinstance(data, dict)
                    and data.get('type', None) == 'service'
                    and data['id'] in self.__await_events.keys()):
                pd_item = utils.dict_to_pandas(
                        data['action_result'])
                result = (pd_item if pd_item is not None
                        else data['action_result'])
                self.__events_results[data['id']] = result
                self.__await_events[data['id']].set()
            else:
                await self.on_data(data)
        except Exception as e:
            Logger.log_error(e)

    async def execute(self, action, *args, **kwargs):
        result = None

        try:
            nonce = utils.get_nonce()
            await self.push({
                'type':'service',
                'id': utils.get_nonce(),
                'action':action,
                'args':args,
                'kwargs':kwargs,})

            self.__await_events[nonce] = asyncio.Event()
            await self.__await_events[str(nonce)].wait()

            result = self.__events_results[nonce]
            del self.__events_results[nonce]
            del self.__await_events[nonce]
        except Exception as e:
            Logger.log_error(e)

        finally:
            return result
