import gevent.monkey
gevent.monkey.patch_all()

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

from exchanges import Exchange

class Bittrex(Exchange):
    name = 'bittrex'

    _key = '00c786da0d6643a5824486ca3c9f2361'
    _pattern = '56ff213321a14f7ea8d93181a5065e9e'

    _rest_path = 'https://bittrex.com/api/v1.1/public/'

    __protocol_version = '1.5'
    __signalr_path = 'https://beta.bittrex.com/signalr'
    __data = json.dumps([{'name': hub_name} for hub_name in ['c2']])

    __session = None
    __callbacks = None
    __token = None

######################    Exchange required   ################################
    async def _prepare_ws_connection(self):
        try:
            self.__callbacks = dict()

            self.__session = Session()
            self.__token = self.__negotiate()['ConnectionToken']

            self._ws_path = self.__get_ws_url(self.__get_url('connect'))
            self._ws_headers = {h.split(':')[0]:h.split(':')[1].strip()
                    for h in self.__get_headers ()}
        except Exception as e:
            Logger.log_error(e)

    async def _ws_auth(self):
        try:
            await self.signalr_send(
                    'GetAuthContext',
                    self._key,
                    callback=self.__sign)
        except Exception as e:
            Logger.log_error(e)

    async def _resolve_message(self, message):
        payload = None

        try:
            message = utils.parse_data(message)

            if message.get('I', None) in self.__callbacks:
                await self.__callbacks[message['I']](message)
                del self.__callbacks[message['I']]
            elif len(message.get('M', [])) > 0:
                if message['M'][0]['M'] == 'uE':
                    await self.__assume_order_book_update(message['M'][0])
                elif message['M'][0]['M'] == 'uL':
                    payload = await self.__assume_tick_package(message['M'][0])
        except Exception as e:
            Logger.log_error(e)

        finally:
            return payload

    async def _close_ws_connection(self):
        self.__session.close()

######################    Private    #########################################
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
        loader = Bittrex.HeadersLoader(headers)

        if self.__session.auth:
            self.__session.auth(loader)

        headers['Cookie'] = self.__get_cookie_str()
        return ['%s: %s' % (name, headers[name]) for name in headers]

    def __decompress_data(self, data):
        return utils.parse_data(zlib.decompress(
            base64.b64decode(data),
            wbits=-15,).decode('utf8'))

    async def __sign(self, message):
        try:
            sign = hmac.new(
                    self._pattern.encode(),
                    message['R'].encode(),
                    hashlib.sha512,).hexdigest()
            await self.signalr_send(
                    'Authenticate',
                    self._key,
                    sign,
                    callback=self.__subscribe_channels)
        except Exception as e:
            Logger.log_error(e)

    async def __get_exchange_state(self):
        try:
            await self.signalr_send('QueryExchangeState', 'BTC-ETH')
        except Exception as e:
            Logger.log_error(e)

    async def __subscribe_channels(self, message):
        try:
            if message.get('R', None) == True:
                #await self.signalr_send('SubscribeToExchangeDeltas', 'BTC-ETH')
                await self.signalr_send('SubscribeToSummaryLiteDeltas')
            else:
                raise Warning(*['Auth failed']*2)
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
                tick = self.__assume_tick(tick_data)
                if tick is not None:
                    tick_package = tick_package.append(tick)

            Logger.log_info(tick_package)
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
            market = self._get_markets().loc[tick_data['M']]
            tick = pd.Series (
                    data=[
                            self.name,
                            int(time.mktime(current_date.timetuple()))*1000,
                            '_'.join([market.at['base'], market.at['quot']]),
                            tick_data['l'],],
                    index=formats.tick,
                    name=current_date,)
        except Exception as e:
            Logger.log_error(e)

        finally:
            return tick

    async def __assume_exchange_state(self, message):
        try:
            state_data = self.__decompress_data(message['R'])
        except Exception as e:
            Logger.log_error(e)

###########################    API    ########################################
    async def signalr_send(self, method_name, *args, callback=None):
        try:
            if callback is not None:
                self.__callbacks[str(self._get_request_counter())] = callback

            await self.ws_send({
                    'H': 'c2',
                    'M': method_name,
                    'A': args,
                    'I': self._get_request_counter(),})
        except Exception as e:
            Logger.log_error(e)

    async def get_markets(self):
        markets = pd.DataFrame(data=[], columns=formats.market)

        try:
            request_url = 'getmarkets'

            stock_data = await self.rest_send(request_url)
            for market_data in stock_data['result']:
                if market_data['IsActive']:
                    markets = markets.append(pd.Series(
                            data=[
                                self.name,
                                market_data['BaseCurrency'].lower(),
                                market_data['MarketCurrency'].lower(),
                                market_data['MinTradeSize'],
                                None],
                            index=formats.market,
                            name=market_data['MarketName']))
        except Exception as e:
            Logger.log_error(e)

        finally:
            return markets
