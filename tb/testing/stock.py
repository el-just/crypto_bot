from stocks.bitfinex import Bitfinex
from testing.web_socket import WEBSocket
from testing.traider import Traider
from testing.logging import Logging

class Stock (Bitfinex, Logging):
    def __init__ (self):
        super().__init__()
        self._web_socket = WEBSocket(self)
        self._traider = Traider(self)

    async def process_tick (self, tick):
        try:
            await self._traider.resolve (tick)
        except Exception as e:
            self.log_error (e)