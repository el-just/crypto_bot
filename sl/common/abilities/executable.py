import inspect

class Executable():
    async def _assume_action(self, data):
        response = None

        try:
            if (data.get('type', None) == 'service'
                    and data.get('action', None) is not None
                    and data['action'].split('.')[0] == self.name
                    and data['action'].split('.')[1] in self.__dict__.keys()):

                action = self.__dict__[data['action'].split('.')[1]]
                if inspect.iscoroutinefunction(action):
                    action_result = await action(
                            *data.get('args', []),
                            **data.get('kwargs', {}),)
                elif inspect.isfunction():
                    action_result = action(
                            *data.get('args', []),
                            **data.get('kwargs', {}),)
                else:
                    action_result = action

                response = {
                        'type':'service',
                        'id':data['id'],
                        'action_result':action_result,}
        except Exception as e:
            response = {
                    'type':'service',
                    'id':data['id'],
                    'action_result':{'error':str(e)},}
        finally:
            return response
