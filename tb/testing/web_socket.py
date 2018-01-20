import time
import datetime
import pandas as pd
from stocks.bitfinex.web_socket import WEBSocket as BWS
from testing.logging import Logging

class WEBSocket (BWS, Logging):
    _iter_frame = None

    async def get_data (self):
        try:
            now = datetime.datetime.now()
        
            start = int(time.mktime((now - datetime.timedelta (days=90)).timetuple()))
            end = int(time.mktime(now.timetuple()))

            query = '''
                SELECT * FROM tb.ticker
                WHERE tick_time >= toDateTime({start}) AND tick_time <= toDateTime ({end})
                ORDER BY tick_time DESC FORMAT CSVWithNames
                '''.format (start=start, end=end)
            self._iter_frame = await self._stock._storage.execute (query)
            self._iter_frame.loc[:, 'tick_time'] = pd.to_datetime(self._iter_frame.loc[:, 'tick_time']).astype(int) / 1000000000
            self._iter_frame['timestamp'] = self._iter_frame.loc[:, 'tick_time']
            self._iter_frame = self._iter_frame.set_index (pd.to_datetime(self._iter_frame.loc[:, 'tick_time']).values)
        except Exception as e:
            self.log_error (e)

    async def listen (self):
        try:
            await self.get_data ()
            self.log_info (str(self._iter_frame))
            for idx, tick in self._iter_frame.iterrows():
                self.log_info (str(tick))
                await self._stock.process_tick (tick)
        except Exception as e:
            self.log_error (e)