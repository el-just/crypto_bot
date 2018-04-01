import gevent.monkey
gevent.monkey.patch_all()

import json
import websockets
import hmac
import hashlib
import common.utils as utils
from requests import Session
from urllib.parse import urlparse, urlunparse, quote_plus
from common.logger import Logger

class Signalr ():
    _key = '00c786da0d6643a5824486ca3c9f2361'
    _pattern = '56ff213321a14f7ea8d93181a5065e9e'
    _main_path = 'https://beta.bittrex.com/signalr'
    _session = None
    _socket = None
    _token = None
    _qs = {}
    _data = json.dumps([{'name': hub_name} for hub_name in ['c2']])
    _protocol_version = '1.5'
    _message_id = 0

    def _get_base_url(self, action, **kwargs):
        args = kwargs.copy()
        args.update(self._qs)
        args['clientProtocol'] = self._protocol_version
        query = '&'.join(['{key}={value}'.format(key=key, value=quote_plus(args[key])) for key in args])

        return '{url}/{action}?{query}'.format(url=self._main_path,
                                               action=action,
                                               query=query)

    def _negotiate(self):
        url = self._get_base_url('negotiate',
                                  connectionData=self._data)
        negotiate = self._session.get(url)

        negotiate.raise_for_status()

        return negotiate.json()

    def _get_url(self, action, **kwargs):
        args = kwargs.copy()
        args['transport'] = 'webSockets'
        args['connectionToken'] = self._token
        args['connectionData'] = self._data

        return self._get_base_url(action, **args)

    def _get_ws_url_from(self, url):
        parsed = urlparse(url)
        scheme = 'wss' if parsed.scheme == 'https' else 'ws'
        url_data = (scheme, parsed.netloc, parsed.path, parsed.params, parsed.query, parsed.fragment)

        return urlunparse(url_data)

    def _get_cookie_str(self):
        return '; '.join([
                             '%s=%s' % (name, value)
                             for name, value in self._session.cookies.items()
                             ])

    class HeadersLoader(object):
        def __init__(self, headers):
            self.headers = headers

    def _get_headers(self):
        headers = self._session.headers
        loader = Signalr.HeadersLoader(headers)

        if self._session.auth:
            self._session.auth(loader)

        headers['Cookie'] = self._get_cookie_str()
        return ['%s: %s' % (name, headers[name]) for name in headers]

    async def _send_auth_request(self):
        await self._socket.send(json.dumps({
            'H': 'c2', 'M': 'GetAuthContext', 'A': (self._key,), 'I': self._message_id
        }))
        self._message_id += 1

    async def _sign(self, message):
        sign = hmac.new(self._pattern.encode(), message['R'].encode(), hashlib.sha512).hexdigest()
        await self._socket.send(json.dumps({
            'H': 'c2', 'M': 'Authenticate', 'A': (self._key, sign), 'I': self._message_id
        }))
        self._message_id += 1

    async def _subscribe_channels(self):
        await self._socket.send(json.dumps({
            'H': 'c2', 'M': 'SubscribeToExchangeDeltas', 'A': ('BTC-ETH',), 'I': self._message_id
        }))
        self._message_id += 1

    async def _assume_tick(self, message):
        message
        #{'C': 'd-32D4F235-B,0|Cj,0|Ck,3|Cl,0|W,6E09', 'M': [{'H': 'C2', 'M': 'uE', 'A': ['fZHNSgQxEITfpc8x9G86naOy4EVBnYvKXn2JZd/dEGfXGTeYQyDUR1V15wRP0OB+ebg7LI+Q4BkaV3JL8AHt8wTLOzRM8NrvjGZFGSPBCzTL4TjOOU0wIh4YZQ9noagXjPYYDqw/JzYqRfXHRrIKG83jFNV8cMq5Suxq0Z4r/+RJaFnzNPfKpQ9rEx9WX8eb+mgN5NUnV8R5HbUh/bXZ6B6kNzFbvUbEVT8meJt9mfcd+kpp7MvwLxascikjIUEot5mFKQrbNvOrZx7P3w==']}]}
    async def _resolve_message (self, message):
        Logger.log_info(message)
        if 'I' in message and int(message['I']) == 0:
            await self._sign(message)
        elif 'I' in message and int(message['I']) == 1 and message['R'] == True:
            await self._subscribe_channels()
        elif 'M' in message:
            await self._assume_tick(message)

    async def connect (self):
        try:
            with Session() as session:
                self._session = session
                negotiate_data = self._negotiate()
                self._token = negotiate_data['ConnectionToken']
                ws_url = self._get_ws_url_from(self._get_url('connect'))
                headers = {h.split(':')[0]:h.split(':')[1].strip() for h in self._get_headers ()}

                async with websockets.connect(ws_url, extra_headers=headers) as websocket:
                    self._socket = websocket
                    await self._send_auth_request()
                    async for message in websocket:
                        await self._resolve_message (utils.parse_data (message))
        except Exception as e:
            Logger.log_error(e)
