from stocks.bitfinex.traider import Traider as BFT
import asyncio
import datetime
from testing.logging import Logging

class Traider (BFT):
    async def run (self):
        try:
            while self._ready == False:
                #Logging.log_info (self._frame.iloc[self._frame.shape[0]-1])
                if self._frame.shape[0] > 0:
                    if self._frame.iloc[self._frame.shape[0]-1].name - self._frame.iloc[0].name <= datetime.timedelta(minutes=89):
                        await asyncio.sleep (0)
                    else:
                        self._ready = True
                        Logging.log_info ('nice')
                else:
                    await asyncio.sleep (0)
        except Exception as e:
            Logging.log_error (e)