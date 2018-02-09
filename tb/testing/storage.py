import time
import datetime
import pandas as pd
import numpy as np

from testing.logging import Logging
from stocks.bitfinex.storage import Storage as BTFXStorage
from stocks.bitfinex.defines import DEFINES

class Storage (BTFXStorage):
    _iter_frame = None
    _source = 'csv'

    def __init__ (self):
        self.log_info = Logging.log_info
        self.log_error = Logging.log_error

    def set_source (self, source):
        self._source = source

    async def insert_ticks (self, ticks):
        if self._source = 'trade_emulation_with_inserts':
            super().insert_ticks (self, ticks)

    async def get_missing_periods (self, period):
        if self._source not in ('trade_emulation', 'trade_emulation_with_inserts'):
            now = datetime.datetime.now()
            interval = datetime.timedelta (**DEFINES.REQUIRED_INTERVAL)
            periods = []

            # periods.append ({
            #   'start':
            #   'end': now
            #   })

            return periods
        else:
            return await super().get_missing_periods(self, period)

    async def get_tick_frame (self, period, real=False):
        if real == True or self._source in ('trade_emulation', 'trade_emulation_with_inserts'):
            return await super().get_tick_frame (period)
        elif self._source == 'db':
            now = datetime.datetime.now()
            start = (now - datetime.timedelta (days=30)).replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + datetime.timedelta (minutes=90)
            frame = await super().get_tick_frame ({
                'start': time.mktime(start.timetuple()),
                'end': time.mktime(end.timetuple())
                })

            frame.loc[:, 'tick_time'] = pd.to_datetime(frame.loc[:, 'tick_time'])
            frame['timestamp'] = frame.loc[:, 'tick_time'].apply (lambda tick_time: time.mktime (tick_time.timetuple()))
            frame = frame.set_index (pd.to_datetime(frame.loc[:, 'tick_time']).values)

            return frame
        elif self._source == 'csv':
            self._iter_frame = pd.read_csv ('testing/day.csv', dtype={'close':np.float64})

            self._iter_frame.loc[:, 'tick_time'] = pd.to_datetime(self._iter_frame.loc[:, 'tick_time'])
            self._iter_frame['timestamp'] = self._iter_frame.loc[:, 'tick_time'].apply (lambda tick_time: time.mktime (tick_time.timetuple()))
            self._iter_frame = self._iter_frame.set_index (pd.to_datetime(self._iter_frame.loc[:, 'tick_time']).values)
            self._iter_frame = self._iter_frame.iloc[::-1]

            return self._iter_frame.loc[:self._iter_frame.iloc[0].name+datetime.timedelta(**DEFINES.REQUIRED_INTERVAL)]
        else:
            return pd.DataFrame (data=[], columns=['timestamp', 'base', 'quot', 'close', 'volume'])