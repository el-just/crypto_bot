from common.logger import Logger
from stocks.bittrex.socket import Socket

class Bittrex ():
    _socket = None

    def __init__ (self):
        self._socket = Socket ()

    async def ping (self):
        try:
            print (await self._socket.get_order_book('BTC-ETH'))
        except Exception as e:
            Logger.log_error (e)