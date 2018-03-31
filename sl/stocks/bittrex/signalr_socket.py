import gevent.monkey
gevent.monkey.patch_all()

from requests import Session
from signalr import Connection
from urllib.parse import urlparse, urlunparse
import websockets
import datetime
import hmac
import hashlib
from common.logger import Logger

#{'H': 'c2', 'M': 'GetAuthContext', 'A': ('00c786da0d6643a5824486ca3c9f2361',), 'I': 0}

class SignalrSocket ():
    _ws_path = 'wss://beta.bittrex.com/signalr'
    _session = None
    _data = json.dumps([{'name': hub_name} for hub_name in ['c2']])

    def _get_cookie_str(self):
        return '; '.join([
                             '%s=%s' % (name, value)
                             for name, value in self._session.cookies.items()
                             ])

    def _get_url(self, action, **kwargs):
        args = kwargs.copy()
        args['transport'] = 'webSockets'
        args['connectionToken'] = self._connection.token
        args['connectionData'] = self._data

        return self._get_base_url(action, **args)

    @staticmethod
    def _get_base_url(action, **kwargs):
        args = kwargs.copy()
        args.update(connection.qs)
        args['clientProtocol'] = connection.protocol_version
        query = '&'.join(['{key}={value}'.format(key=key, value=quote_plus(args[key])) for key in args])

        return '{url}/{action}?{query}'.format(url=connection.url,
                                               action=action,
                                               query=query)
    def negotiate(self):
        url = self._get_base_url( 'negotiate',
                                  connectionData=self._data)
        negotiate = self._session.get(url)

        negotiate.raise_for_status()

        return negotiate.json()

    @staticmethod
    def _get_ws_url_from(url):
        parsed = urlparse(url)
        scheme = 'wss' if parsed.scheme == 'https' else 'ws'
        url_data = (scheme, parsed.netloc, parsed.path, parsed.params, parsed.query, parsed.fragment)

        return urlunparse(url_data)

    class HeadersLoader(object):
        def __init__(self, headers):
            self.headers = headers

    def _get_headers(self):
        headers = self._session.headers
        loader = SignalrSocket.HeadersLoader(headers)

        if self._session.auth:
            self._session.auth(loader)

        headers['Cookie'] = self.__get_cookie_str()
        return ['%s: %s' % (name, headers[name]) for name in headers]

    async def _resolve_message(self, message):
        Logger.log_info(message)

    async def connect (self):
        try:
            with Session() as session:
                self._session = session
                ws_url = self._get_ws_url_from(self._get_url('connect'))
                headers = self._get_headers()
                async with websockets.connect(ws_url, extra_headers=headers) as websocket:
                    self._session.get(self._get_url('start'))
                    self._socket = websocket
                    async for message in websocket:
                        await self._resolve_message (utils.parse_data (message))
        except Exception as e:
            Logger.log_error(e)

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
