from common import Logger
from common import Socket

class Buffer():
    def __init__(self, name):
        self.__dict__['name'] = name
        if name not in Buffer.instances.keys():
            self.instances[name] = _Buffer(name)

    def __getattr__(self, name):
        return getattr(self.instances[self.__dict__['name']], name)

    def __setattr__(self, name, value):
            self.instances[self.__dict__['name']].__dict__[name] = value
Buffer.instances = dict()

class _Buffer():
    name = None

    __sockets = None
    def __init__(self, name):
        self.name = name

    def connect(self, socket):
        if socket is None:
            socket = Socket(self)
        else:
            socket.source = self

        self.__sockets.add(socket)
        return socket

    def disconnect(self, socket):
        if socket in self.__sockets:
            self.__sockets.remove(socket)

    async def close(self):
        for socket in self._sockets():
            await socket.close()

    async def push(self, source=None, data=None):
        try:
            for socket in self.__sockets:
                if socket != source:
                    await socket.on_data(data)
        except Exception as e:
            Logger.log_error(e)
