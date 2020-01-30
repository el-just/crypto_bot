import asyncio
import inspect

from common import Logger
from common import utils

class Socket():
    source = None
    owner = None

    __await_events = None
    __events_results = None
    def __init__(self, source=None, owner=None):
        self.source = source
        self.owner = owner
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

    def set_owner(self, owner):
        self.owner = owner

    async def on_data(self, data): pass

    async def _data_recieved(self, data):
        try:
            action_result = await self.__assume_action(data)
            if data.get('type', None) == 'service':
                Logger.log_info('data_recieved')
                Logger.log_info(self.__await_events.keys())
            if action_result is not None:
                await self.push(data=action_result)
            elif (isinstance(data, dict)
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

    async def __assume_action(self, data):
        response = None

        try:
            if (self.owner is not None
                    and data.get('type', None) == 'service'
                    and data.get('action', None) is not None
                    and data['action'].split('.')[0] == self.owner.name):

                if not hasattr(self.owner, data['action'].split('.')[1]):
                    raise Warning('%s have not action %s'%(
                            data['action'].split('.')[0],
                            data['action'].split('.')[1],))

                Logger.log_info('accepted_action')

                action = getattr(self.owner, data['action'].split('.')[1])
                if inspect.iscoroutinefunction(action):
                    action_result = await action(
                            *data.get('args', []),
                            **data.get('kwargs', {}),)
                elif inspect.ismethod(action):
                    action_result = action(
                            *data.get('args', []),
                            **data.get('kwargs', {}),)
                else:
                    action_result = action

                Logger.log_info('action produced')
                response = {
                        'type':'service',
                        'id':data['id'],
                        'action_result':action_result,}
                Logger.log_info(response)
        except Exception as e:
            response = {
                    'type':'service',
                    'id':data['id'],
                    'action_result':{'error':str(e)},}
        finally:

            return response

    async def execute(self, action, *args, **kwargs):
        result = None

        try:
            nonce = utils.get_nonce()
            Logger.log_info('execute')
            Logger.log_info(nonce)
            self.__await_events[nonce] = asyncio.Event()
            await self.push({
                'type':'service',
                'id': nonce,
                'action':action,
                'args':args,
                'kwargs':kwargs,})

            await self.__await_events[nonce].wait()
            Logger.log_info('executed')
            result = self.__events_results[nonce]
            Logger.log_info(result)
            del self.__events_results[nonce]
            del self.__await_events[nonce]
        except Exception as e:
            Logger.log_error(e)

        finally:
            return result
