from stocks.bitfinex.traider import Traider as BFT
import asyncio
import datetime
from testing.logging import Logging

class Traider (BFT):
    async def run (self):
        try:
            while self._frame.iloc[self._frame.shape[0]-1].name - self._frame.iloc[0].name < datetime.timedelta(minutes=30):
                await asyncio.sleep (0)
            self._ready = True
        except Exception as e:
            Logging.log_error (e)