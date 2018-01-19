from pandas import pd
import datetime
import time

from abstract.logging import Logging
from stocks.bitfinex.defines import DEFINES

class Traider (Logging):
    _ready = False
    _frame = pd.DataFrame (data=[], columns=['timestamp', 'base', 'quot', 'close', 'volume'])
    _stock = None

    def __init__ (self, stock=None):
        self._stock = stock

    async def run (self):
        try:
            now = datetime.datetime.now()
            missing_periods = await self._stock._storage.get_missing_periods ({
                'start':time.mktime((now - datetime.timedelta (days=DEFINES.REQUIRED_PERIOD)).timetuple()),
                'end': time.mktime(now.timetuple())
                })

            self.log_info ('Missing periods:\n\t{0}'.format(str(missing_periods)))
            for period in missing_periods:
                tick_period = await self._stock._rest_socket.get_tick_period (period)
                self._frame = self._frame.append (tick_period)
        except Exception as e:
            self.log_error (e)

    async def resolve (self, tick):
        self._frame = self._frame.append (tick)
        self._frame = self._frame.loc[tick.name-datetime.timedelta(seconds=DEFINES.FRAME_PERIOD):tick.name]
        if self._ready:
            pass