from common.logger import Logger
from stocks.binance.socket import Socket

class Binance ():
    _socket = None

    def __init__ (self):
        self._socket = Socket ()

    async def ping (self):
        try:
            print (await self._socket.ping())
        except Exception as e:
            Logger.log_error (e)

    async def custom_action (self):
        try:
            await self._socket.connect ()
        except Exception as e:
            Logger.log_error (e)
