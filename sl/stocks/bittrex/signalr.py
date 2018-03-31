import gevent.monkey
gevent.monkey.patch_all()

import json
import websockets
import common.utils as utils
from requests import Session
from urllib.parse import urlparse, urlunparse, quote_plus
from common.logger import Logger

class Signalr ():
    _main_path = 'https://beta.bittrex.com/signalr'
    _session = None
    _socket = None
    _token = None
    _qs = {}
    _data = json.dumps([{'name': hub_name} for hub_name in ['c2']])
    _protocol_version = '1.5'

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

    async def _resolve_message (self, message):
        Logger.log_info(message)

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
                    async for message in websocket:
                        await self._resolve_message (utils.parse_data (message))
        except Exception as e:
            Logger.log_error(e)
