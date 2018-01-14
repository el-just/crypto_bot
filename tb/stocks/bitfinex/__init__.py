import time
import datetime
import asyncio

from abstract.logging import Logging, async_error_log

from stocks.bitfinex.defines import DEFINES

from stocks.bitfinex.storage import Storage
from stocks.bitfinex.rest_socket import RESTSocket
from stocks.bitfinex.web_socket import WEBSocket

class Bitfinex (Logging):
    _storage = None
    _rest_socket = None
    _web_socket = None

    def __init__ (self):
        self._storage = Storage ()
        self._rest_socket = RESTSocket (self._storage)
        self._web_socket = WEBSocket (self._storage)

    async def verify_period (self):
        try:
            now = datetime.datetime.now()
            missing_periods = await self._storage.get_missing_periods ({
                'start':time.mktime((now - datetime.timedelta (days=DEFINES.REQUIRED_PERIOD)).timetuple()),
                'end': time.mktime(now.timetuple())
                })

            self.log_info ('Missing periods:\n\t{0}'.format(str(missing_periods)))
            for period in missing_periods:
                await self._rest_socket.get_tick_period (period)
        except Exception as e:
            self.log_error (e)
    
    def run (self):
        return asyncio.gather(
            self.verify_period ()
            self._web_socket.listen()
            )