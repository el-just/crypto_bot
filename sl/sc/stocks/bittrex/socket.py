import gevent.monkey
gevent.monkey.patch_all()

import websockets
import json
import hmac
import hashlib
import base64
import zlib
import datetime
import time
from requests import Session
from urllib.parse import urlparse, urlunparse, quote_plus

import pandas as pd
from common import utils
from common import formats
from common import Logger

class Socket():
    __protocol_version = None

    __signalr_path = None
    __key = None
    __pattern = None

    __session = None
    __socket = None
    __token = None
    __data = json.dumps([{'name': hub_name} for hub_name in ['c2']])
    __message_id = 0
    __markets = ['btc-eth']

    def __init__(self):
        self.__protocol_version = '1.5'

        self.__signalr_path = 'https://beta.bittrex.com/signalr'
        self.__key = '00c786da0d6643a5824486ca3c9f2361'
        self.__pattern = '56ff213321a14f7ea8d93181a5065e9e'

    def __get_base_url(self, action, **kwargs):
        args = kwargs.copy()
        args['clientProtocol'] = self.__protocol_version
        query = '&'.join(['{key}={value}'.format(
                key=key,
                value=quote_plus(args[key])) for key in args],)

        return '{url}/{action}?{query}'.format(
                url=self.__signalr_path,
                action=action,
                query=query,)

    def __negotiate(self):
        url = self.__get_base_url(
                'negotiate',
                connectionData=self.__data,)

        negotiate = self.__session.get(url)
        negotiate.raise_for_status()

        return negotiate.json()

    def __get_url(self, action, **kwargs):
        args = kwargs.copy()
        args['transport'] = 'webSockets'
        args['connectionToken'] = self.__token
        args['connectionData'] = self.__data

        return self.__get_base_url(action, **args)

    def __get_ws_url(self, url):
        parsed = urlparse(url)
        scheme = 'wss' if parsed.scheme == 'https' else 'ws'
        url_data = (
                scheme,
                parsed.netloc,
                parsed.path,
                parsed.params,
                parsed.query,
                parsed.fragment,)

        return urlunparse(url_data)

    def __get_cookie_str(self):
        return '; '.join([
                '%s=%s' % (name, value)
                    for name, value in self.__session.cookies.items()])

    class HeadersLoader(object):
        def __init__(self, headers):
            self.headers = headers

    def __get_headers(self):
        headers = self.__session.headers
        loader = Socket.HeadersLoader(headers)

        if self.__session.auth:
            self.__session.auth(loader)

        headers['Cookie'] = self.__get_cookie_str()
        return ['%s: %s' % (name, headers[name]) for name in headers]

    def __decompress_data(self, data):
        return utils.parse_data(zlib.decompress(
            base64.b64decode(data),
            wbits=-15,).decode('utf8'))

    async def __send_request(self, method_name, *args):
        try:
            await self.__socket.send(json.dumps({
                    'H': 'c2',
                    'M': method_name,
                    'A': args,
                    'I': self.__message_id,}))
            self.__message_id += 1
        except Exception as e:
            Logger.log_error(e)

    async def __send_auth_request(self):
        try:
            await self.__send_request('GetAuthContext', self.__key)
        except Exception as e:
            Logger.log_error(e)

    async def __sign(self, message):
        try:
            sign = hmac.new(
                    self.__pattern.encode(),
                    message['R'].encode(),
                    hashlib.sha512,).hexdigest()
            await self.__send_request('Authenticate', self.__key, sign)
        except Exception as e:
            Logger.log_error(e)

    async def __get_exchange_state(self):
        try:
            await self.__send_request('QueryExchangeState', 'BTC-ETH')
        except Exception as e:
            Logger.log_error(e)

    async def __subscribe_channels(self):
        try:
            await self.__send_request('SubscribeToExchangeDeltas', 'BTC-ETH')
            await self.__send_request('SubscribeToSummaryLiteDeltas')
        except Exception as e:
            Logger.log_error(e)

    async def __assume_order_book_update(self, message):
        try:
            order_book_data = self.__decompress_data(message['A'][0])
        except Exception as e:
            Logger.log_error(e)

    async def __assume_tick_package(self, message):
        tick_package = pd.DataFrame (data=[], columns=formats.tick)

        try:
            tick_package_data = self.__decompress_data(message['A'][0])

            for tick_data in tick_package_data['D']:
                if tick_data['M'].lower() in self.__markets:
                    tick = self.__assume_tick(tick_data)
                    if tick is not None:
                        tick_package = tick_package.append(tick)
        except Exception as e:
            Logger.log_error(e)

        finally:
            if tick_package.shape[0] == 0:
                tick_package = None
            elif tick_package.shape[0] == 1:
                tick_package = tick_package.iloc[0]

            return tick_package

    def __assume_tick(self, tick_data):
        tick = None

        try:
            current_date = datetime.datetime.now()
            tick = pd.Series (
                    data=[
                            'bittrex',
                            int(time.mktime(current_date.timetuple())),
                            tick_data['M'].lower(),
                            tick_data['l'],],
                    index=formats.tick,)
            tick.name = current_date
        except Exception as e:
            Logger.log_error(e)

        finally:
            return tick

    async def __assume_exchange_state(self, message):
        try:
            state_data = self.__decompress_data(message['R'])
        except Exception as e:
            Logger.log_error(e)

    async def __resolve_message(self, message):
        reaction = None

        try:
            if 'I' in message and int(message['I']) == 0:
                await self.__sign(message)
            elif ('I' in message and int(message['I']) == 1
                    and 'R' in message and message['R'] == True):
                await self.__get_exchange_state()
                await self.__subscribe_channels()
            elif 'I' in message and int(message['I']) == 2 and 'R' in message:
                await self.__assume_exchange_state(message)
            elif ('M' in message and len(message['M']) > 0
                    and message['M'][0]['M'] == 'uE'):
                await self.__assume_order_book_update (message['M'][0])
            elif ('M' in message and len(message['M']) > 0
                    and message['M'][0]['M'] == 'uL'):
                reaction = await self.__assume_tick_package(message['M'][0])
        except Exception as e:
            Logger.log_error(e)

        finally:
            return reaction

    async def run (self):
        try:
            with Session() as session:
                self.__session = session
                negotiate_data = self.__negotiate()
                self.__token = negotiate_data['ConnectionToken']
                ws_url = self.__get_ws_url(self.__get_url('connect'))
                headers = {h.split(':')[0]:h.split(':')[1].strip()
                        for h in self.__get_headers ()}

                async with websockets.connect(
                        ws_url,
                        extra_headers=headers,) as websocket:
                    self.__socket = websocket
                    await self.__send_auth_request()
                    async for message in websocket:
                        reaction = await self.__resolve_message(
                                utils.parse_data (message))
                        if reaction is not None:
                            yield reaction
        except Exception as e:
            Logger.log_error(e)
