from common import Logger
from common import Socket
from common import utils

class Buffer():
    def __init__(self, name, is_mirror=False):
        self.__dict__['name'] = name
        if name not in Buffer.instances.keys():
            self.instances[name] = _Buffer(name, is_mirror=is_mirror)

    def __getattr__(self, name):
        return getattr(self.instances[self.__dict__['name']], name)

    def __setattr__(self, name, value):
            self.instances[self.__dict__['name']].__dict__[name] = value
Buffer.instances = dict()

class _Buffer():
    name = None
    views = None

    remote_master = None

    __sockets = None
    def __init__(self, name, is_mirror=False):
        self.name = name
        self.views = dict()
        self.__is_mirror = is_mirror
        self.__sockets = set()

    def connect(self, socket=None):
        Logger.log_info('connect')
        if socket is None:
            socket = Socket(self)
        else:
            socket.source = self

        self.__sockets.add(socket)
        return socket

    def disconnect(self, socket):
        if socket in self.__sockets:
            self.__sockets.remove(socket)

    def add_view(self, views):
        if not isinstance(views, list):
            views = [views]

        for view in views:
            self.views[view.name] = view

    async def close(self):
        try:
            for socket in self._sockets():
                self.disconnect(socket)
        except Exception as e:
            Logger.log_error(e)

    async def push(self, source=None, data=None):
        try:
            if isinstance(data, dict) and data.get('type', None) == 'service':
                if (not self.__is_mirror
                        and data.get('action', None) is not None):
                    await self._process_service_message(data)
                else:
                    for socket in self.__sockets:
                        if socket != source:
                            await socket._data_recieved(data)
            else:
                if self.views is not None:
                    for view_name in self.views:
                        self.views[view_name].update(data)
                for socket in self.__sockets:
                    if socket != source:
                        await socket._data_recieved(data)
        except Exception as e:
            Logger.log_error(e)

    async def _process_service_message(self, message):
        try:
            if message['action'] == 'get_view':
                await self.push({
                    'type':'service',
                    'id':message['id'],
                    'action_result':utils.pandas_to_dict(
                        self.views[message['args'][0]].state),})
        except Exception as e:
            Logger.log_error(e)
