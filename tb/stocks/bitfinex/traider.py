import pandas as pd
import datetime
import time

from abstract.logging import Logging
from stocks.bitfinex.defines import DEFINES

class Traider (Logging):
    _ready = False
    _positions = pd.DataFrame(data=[], columns=['amount', 'type'])
    _frame = pd.DataFrame (data=[], columns=['timestamp', 'base', 'quot', 'close', 'volume'])
    _stock = None

    def __init__ (self, stock=None):
        self._stock = stock

    def magic (self):
        self.log_info (self._frame.tail(1))
        return True

    async def position_in (self):
        if self._stock._balance.at['usd'] > 0:
            position = pd.Series (data=[self._stock._balance.at['usd'], -1], index=['amount', 'type'])
            position.name = datetime.datetime.now()
            self._positions.append (position)
            self._stock._balance.at['btc'] = self._stock._balance.at['usd'] / self._frame.tail(1).at['close']
            self._stock._balance.at['usd'] = 0

    async def position_out (self):
        if self._stock._balance.at['btc'] > 0:
            position = pd.Series (data=[volume, self._frame.tail(1).at['close'], 1], index=['amount', 'type'])
            position.name = datetime.datetime.now()
            self._positions.append (position)
            self._stock._balance.at['usd'] = self._stock._balance.at['btc'] * self._frame.tail(1).at['close']
            self._stock._balance.at['btc'] = 0

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
            self._ready = True
        except Exception as e:
            self.log_error (e)

    async def resolve (self, tick):
        self._frame = self._frame.append (tick)
        self._frame = self._frame.loc[tick.name-datetime.timedelta(seconds=DEFINES.FRAME_PERIOD):tick.name]
        if self._ready:
            if self.magic () == True:
                await self.position_in ()
            elif self.magic () == False:
                await self.position_out ()
            