import time
import datetime

from stocks.bitfinex.defines import DEFINES

from stocks.bitfinex.storage import Storage
from stocks.bitfinex.rest_socket import RESTSocket
from stocks.bitfinex.web_socket import WEBSocket

class Bitfinex ():
    _storage = None
    _rest_socket = None
    _web_socket = None

    def __init__ (self):
        self._storage = Storage ()
        self._rest_socket = RESTSocket (self._storage)
        self._web_socket = WEBSocket ()

    async def verify_period (self):
        now = datetime.datetime.now()
        missing_periods = await self._storage.get_missing_periods ({
            'start':time.mktime((now - datetime.timedelta (days=DEFINES.REQUIRED_PERIOD)).timetuple()),
            'end': time.mktime(now.timetuple())
            })

        for period in missing_periods:
            await self._rest_socket.get_tick_period (period)

    async def run (self):
        await self.verify_period ()
        #await self._web_socket.listen()