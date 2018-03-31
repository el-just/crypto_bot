from common.logger import Logger
from stocks.bittrex.socket import Socket
from stocks.bittrex.signalr import Signalr

class Bittrex ():
    _socket = None

    def __init__ (self):
        self._socket = Signalr ()

    async def ping (self):
        try:
            print (await self._socket.get_order_book('BTC-ETH'))
        except Exception as e:
            Logger.log_error (e)

    async def custom_action (self):
        try:
            await self._socket.connect ()
        except Exception as e:
            Logger.log_error (e)
