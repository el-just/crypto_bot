import time
import datetime
import pandas as pd
import numpy as np

from testing.logging import Logging
from stocks.bitfinex.storage import Storage as BTFXStorage
from stocks.bitfinex.defines import DEFINES

class Storage (BTFXStorage):
    _iter_frame = None

    def __init__ (self):
        self.log_info = Logging.log_info
        self.log_error = Logging.log_error

    async def is_available (self):
        return True

    async def insert_ticks (self, ticks):
        pass

    async def get_missing_periods (self, period):
        now = datetime.datetime.now()
        interval = datetime.timedelta (**DEFINES.REQUIRED_INTERVAL)
        periods = []

        # periods.append ({
        #   'start':
        #   'end': now
        #   })

        return periods

    async def get_tick_frame (self, period):
        self._iter_frame = pd.read_csv ('testing/day.csv', dtype={'close':np.float64})

        self._iter_frame.loc[:, 'tick_time'] = pd.to_datetime(self._iter_frame.loc[:, 'tick_time'])
        self._iter_frame['timestamp'] = self._iter_frame.loc[:, 'tick_time'].apply (lambda tick_time: time.mktime (tick_time.timetuple()))
        self._iter_frame = self._iter_frame.set_index (pd.to_datetime(self._iter_frame.loc[:, 'tick_time']).values)
        self._iter_frame = self._iter_frame.iloc[::-1]

        return self._iter_frame.loc[:self._iter_frame.iloc[0].name+datetime.timedelta(**DEFINES.REQUIRED_INTERVAL)]