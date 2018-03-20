from common.logger import Logger
from common.rest_socket import RESTSocket

class Socket ():
    def __init__ (self):
        self._rest = RESTSocket (url='https://api.binance.com/api/v1/')

##################### API #############################
    async def ping (self):
        try:
            request_url = 'ping'

            return await self._rest.request (request_url)
        except Exception as e:
            Logger.log_error (e)

    async def get_server_time (self):
        try:
            request_url = 'time'

            return await self._rest.request (request_url)
        except Exception as e:
            Logger.log_error (e)

    async def get_last_trades (self, market, limit='500'):
        try:
            request_url = 'trades'

            return await self._rest.request (request_url, {'symbol':market, 'limit':limit})
        except Exception as e:
            Logger.log_error (e)
