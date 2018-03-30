from requests import Session
from signalr import Connection
import datetime
import hmac
import hashlib
from common.logger import Logger

#{'H': 'c2', 'M': 'GetAuthContext', 'A': ('00c786da0d6643a5824486ca3c9f2361',), 'I': 0}

class SignalrSocket ():

    async def connect (self):
        pass

class SignalrSocket_pure ():
    _hub = None
    _path = 'https://beta.bittrex.com/signalr'
    _key = '00c786da0d6643a5824486ca3c9f2361'
    _pattern = '56ff213321a14f7ea8d93181a5065e9e'

    def process_auth_context (self, proof_seed):
        response = hmac.new(self._pattern.encode(), proof_seed.encode(), hashlib.sha256).hexdigest()
        self._hub.server.invoke('Authenticate', self._key, response)
        self._connection.wait(5)
        self._hub.server.invoke('SubscribeToExchangeDeltas', 'BTC-ETH')
        self._connection.wait(5)

    def connect (self):
        with Session() as session:
            self._connection = Connection(self._path, session)
            self._hub = self._connection.register_hub('c2')

            #create new chat message handler
            def print_received_message(data):
                Logger.log_info(data)

            #create error handler
            def print_error(error):
                Logger.log_error(error)

            def process_response (response):
                Logger.log_info (response)

            #start connection, optionally can be connection.start()
            with self._connection:
                #receive new chat messages from the hub
                self._hub.client.on('uE', print_received_message)
                self._hub.client.on('uO', print_received_message)
                self._hub.client.on('uB', print_received_message)

                #process errors
                self._connection.error += print_error

                #post new message
                self._hub.server.invoke('GetAuthContext', self._key, response=process_response)
                self._connection.wait(5)
