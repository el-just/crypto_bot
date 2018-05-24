

for connections in connections:
    for channel in connection.channels:

    connection.listen(message, 
    self.listen(connection, 'message')

def event_accured(initiator, event, *args, **kwargs):
    if event == 'message':
        await self._recieve_message(initiator, *args, **kwargs) 

def _recieve_message(self, message, channel):

stream

view


connection
    channel
        message



channel.listen
channel.send

class Channel()
    __listener = None

    def __init__(self, name=None):
        self.name = name

    def add_listener(self, listener, owner):
        self.__listeners.append(listener)

    async def send(self, message, owner):
        for idx in range(0,len(self.__listeners)):
            await listener(message, self)
