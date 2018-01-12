from stocks.bitfinex.rest_socket import RESTSocket
from stocks.bitfinex.web_socket import WEBSocket
from stocks.bitfinex.storage import Storage

class Bitfinex ():
    _storage = Storage ()
    _rest_socket = RESTSocket ()
    _rest_socket = WEBSocket ()
    _required_period = 90

    def __init__ (self):
        pass

    async def verify_period (self):
        now = datetime.datetime.now()
        missing_periods = await self._storage.get_missing_periods ({
            'start':time.mktime((now - datetime.timedelta (days=self._required_period)).timetuple()),
            'end': time.mktime(now.timetuple())
            })

        for period in periods:
            tick_frame = await self._rest_socket.get_tick_period (period)
            await self._storage.insert_tick_frame (tick_frame)

    async def run (self):
        await self.verify_period ()
        await self._web_socket.listen()

        