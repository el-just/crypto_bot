from requests import Session
from signalr import Connection
import datetime
import hmac
import hashlib
from common.logger import Logger

def start ():
    with Session() as session:
        #create a connection
        path = 'https://beta.bittrex.com/signalr'
        key = '00c786da0d6643a5824486ca3c9f2361'
        pattern = '56ff213321a14f7ea8d93181a5065e9e'

        def sign (text):
            return hmac.new(pattern.encode(), text.encode(), hashlib.sha256).hexdigest()
        
        connection = Connection(path, session)
        hub = connection.register_hub('c2')

        #create new chat message handler
        def print_received_message(data):
            Logger.log_info(data)

        #create error handler
        def print_error(error):
            Logger.log_error(error)

        #receive new chat messages from the hub
        hub.client.on('uE', print_received_message)
        hub.client.on('uO', print_received_message)
        hub.client.on('uB', print_received_message)

        #process errors
        connection.error += print_error

        #start connection, optionally can be connection.start()
        with connection:
            #post new message
            text = chat.server.invoke('GetAuthContext', key)
            Logger.log_info ('context response')
            Logger.log_info (text)
            hub.server.invoke('Authenticate', key, sign(text))
            hub.server.invoke('SubscribeToExchangeDeltas', 'BTC-ETH')
            #wait a second before exit
            connection.wait(1)

            Logger.log_info('shut down')

        Logger.log_info('stopped')
