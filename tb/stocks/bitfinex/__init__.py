import time
import datetime
import asyncio

from abstract.logging import Logging
from stocks.bitfinex.defines import DEFINES

from stocks.bitfinex.storage import Storage
from stocks.bitfinex.rest_socket import RESTSocket
from stocks.bitfinex.web_socket import WEBSocket
from stocks.bitfinex.traider import Traider

class Bitfinex (Logging):
    _storage = None
    _rest_socket = None
    _web_socket = None
    _traider = None

    def __init__ (self):
        self._storage = Storage ()
        self._rest_socket = RESTSocket (self)
        self._web_socket = WEBSocket (self)
        self._traider = Traider (self)

    async def process_tick (self, tick):
        self.log_info ('About to throw to clickhouse:\n\t{}'.format (tick))
        await self._storage.insert_ticks (tick)
        await self._traider.resolve (tick)

    def run (self):
        return asyncio.gather(
            self._traider.run (),
            self._web_socket.listen()
            )