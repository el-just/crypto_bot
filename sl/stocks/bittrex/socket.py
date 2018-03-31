import json
import websockets
from common.logger import Logger
from common.rest_socket import RESTSocket

class Socket ():
    _rest = None
    _key = '00c786da0d6643a5824486ca3c9f2361'
    _pattern = '56ff213321a14f7ea8d93181a5065e9e'
    _ws_path = 'https://beta.bittrex.com/signalr'

    def __init__ (self):
        self._rest = RESTSocket (url='https://bittrex.com/api/')

    async def _resolve_message (self, message):
        Logger.log_info(message)

##################### API #############################
    ########### API v1.1 ##############
    async def get_currencies (self):
        try:
            request_url = 'v1.1/public/getcurrencies'

            return await self._rest.request (request_url)
        except Exception as e:
            Logger.log_error (e)

    async def get_markets (self):
        try:
            request_url = 'v1.1/public/getmarkets'

            return await self._rest.request (request_url)
        except Exception as e:
            Logger.log_error (e)

    async def get_markets_summaries (self):
        try:
            request_url = 'v1.1/public/getmarketsummaries'

            return await self._rest.request (request_url, {})
        except Exception as e:
            Logger.log_error (e)

    async def get_market_summary (self, market):
        try:
            request_url = 'v1.1/public/getmarketsummary'

            return await self._rest.request (request_url, {'market': market})
        except Exception as e:
            Logger.log_error (e)

    async def get_market_last_trades (self, market):
        try:
            request_url = 'v1.1/public/getmarkethistory'

            return await self._rest.request (request_url, {'market': market})
        except Exception as e:
            Logger.log_error (e)

    # type in ('buy', 'sell', 'both')
    async def get_order_book (self, market, order_type='both'):
        try:
            request_url = 'v1.1/public/getorderbook'

            return await self._rest.request (request_url, {'market': market, 'type': order_type})
        except Exception as e:
            Logger.log_error (e)

    ########### API v2.0 ##############
    async def get_ticker (self, market, interval='onemin'):
        try:
            request_url = 'v2.0/pub/market/getlatesttick'

            return await self._rest.request (request_url, {'marketname': market, 'tickinterval':'onemin'})
        except Exception as e:
            Logger.log_error (e)

    ########### WebSocket #############
    async def connect (self):
        pass
