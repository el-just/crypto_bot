import time
import datetime
import pandas as pd
import numpy as np
import asyncio
from stocks.bitfinex.web_socket import WEBSocket as BWS
from testing.logging import Logging
from stocks.bitfinex.defines import DEFINES

class WEBSocket (BWS):
    _iter_frame = None
    _source = 'csv'
    _storage = None

    def __init__ (self):
        self.log_info = Logging.log_info
        self.log_error = Logging.log_error

    def set_source (self, source):
        self._source = source

    def set_storage (self, storage):
        self._storage = storage

    async def get_data_from_csv (self):
        try:
            self._iter_frame = pd.read_csv ('testing/day.csv', dtype={'close':np.float64})

            self._iter_frame.loc[:, 'tick_time'] = pd.to_datetime(self._iter_frame.loc[:, 'tick_time'])
            self._iter_frame['timestamp'] = self._iter_frame.loc[:, 'tick_time'].apply (lambda tick_time: time.mktime (tick_time.timetuple()))
            self._iter_frame = self._iter_frame.set_index (pd.to_datetime(self._iter_frame.loc[:, 'tick_time']).values)
            self._iter_frame = self._iter_frame.iloc[::-1]

            self._iter_frame = self._iter_frame.loc [self._iter_frame.iloc[0].name+datetime.timedelta(**DEFINES.REQUIRED_INTERVAL):]
        except Exception as e:
            self.log_error (e)

    async def day_data_generator (self):
        now = datetime.datetime.now()
        start = (now - datetime.timedelta (days=30)).replace(hour=0, minute=0, second=0, microsecond=0)

        for day in range (0, 30):
            day_start = start + datetime.timedelta (days=day)
            if day == 0:
                day_start += datetime.timedelta (minutes=90)
            day_end = day_start.replace (hour=23, minute=59, second=59)
            frame = await self._storage.get_tick_frame ({
                'start': time.mktime(day_start.timetuple()),
                'end': time.mktime(day_end.timetuple())
                }, real=True)

            frame.loc[:, 'tick_time'] = pd.to_datetime(frame.loc[:, 'tick_time'])
            frame['timestamp'] = frame.loc[:, 'tick_time'].apply (lambda tick_time: time.mktime (tick_time.timetuple()))
            frame = frame.set_index (pd.to_datetime(frame.loc[:, 'tick_time']).values)

            yield frame

    async def listen (self):
        try:
            if self._source == 'csv':
                await self.get_data_from_csv ()
                await self._process_actions (self._wallet_actions, [0,'ws',[['','btc',0.0],['','usd',2000.]]])
                
                current_idx = 0
                for idx, tick in self._iter_frame.iterrows():
                    if current_idx % int(self._iter_frame.shape[0] / 100) == 0:
                        self.log_info (current_idx // int(self._iter_frame.shape[0] / 100))
                    await self._process_actions (self._tick_actions, tick)
                    await asyncio.sleep (0)
                    current_idx += 1
            elif self._source == 'db':
                current_day = 1
                await self._process_actions (self._wallet_actions, [0,'ws',[['','btc',0.0],['','usd',1000.]]])
                async for day_frame in self.day_data_generator():
                    current_idx = 0
                    for idx, tick in day_frame.iterrows():
                        if current_idx % int(day_frame.shape[0] / 100) == 0:
                            self.log_info ('Day: {0}, Percent: {1}'.format ( str(current_day), str(current_idx // int(day_frame.shape[0] / 100)) ))
                        await self._process_actions (self._tick_actions, tick)
                        await asyncio.sleep (0)
                        current_idx += 1
                    current_day += 1
            else:
                await super().listen ()
        except Exception as e:
            self.log_error (e)