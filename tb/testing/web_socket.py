import time
import datetime
import pandas as pd
import asyncio
from stocks.bitfinex.web_socket import WEBSocket as BWS
from testing.logging import Logging

class WEBSocket (BWS):
    _iter_frame = None

    async def get_data (self):
        try:
            # now = datetime.datetime.now()
        
            # start = int(time.mktime((now - datetime.timedelta (days=1)).timetuple()))
            # end = int(time.mktime(now.timetuple()))

            # query = '''
            #     SELECT * FROM tb.ticker
            #     WHERE tick_time >= toDateTime({start}) AND tick_time <= toDateTime ({end})
            #     ORDER BY tick_time DESC FORMAT CSVWithNames
            #     '''.format (start=start, end=end)
            # self._iter_frame = await self._stock._storage.execute (query)

            # self._iter_frame.to_csv ('day.csv', index=True)

            self._iter_frame = pd.read_csv ('testing/day.csv')

            self._iter_frame.loc[:, 'tick_time'] = pd.to_datetime(self._iter_frame.loc[:, 'tick_time']).astype(int)
            self._iter_frame['timestamp'] = self._iter_frame.loc[:, 'tick_time']
            self._iter_frame = self._iter_frame.set_index (pd.to_datetime(self._iter_frame.loc[:, 'tick_time']).values)
        except Exception as e:
            Logging.log_error (e)

    async def listen (self):
        try:
            await self.get_data ()
            Logging.log_info (self._iter_frame.shape)
            for idx, tick in self._iter_frame.iterrows():
                await self._stock.process_tick (tick)
                await asyncio.sleep (0)
        except Exception as e:
            Logging.log_error (e)