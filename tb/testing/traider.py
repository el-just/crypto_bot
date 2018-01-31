from stocks.bitfinex.traider import Traider as BFT
import asyncio
import datetime
from testing.logging import Logging

class Traider (BFT):
    def __init__ (self, stock=None):
        super().__init__(stock)
        self.log_info = Logging.log_info
        self.log_error = Logging.log_error

    async def run (self):
        try:
            while self._ready == False:
                if self._frame.shape[0] > 0:
                    if self._frame.iloc[self._frame.shape[0]-1].name - self._frame.iloc[0].name <= datetime.timedelta(minutes=89):
                        await asyncio.sleep (0)
                    else:
                        self._ready = True
                        self.log_info ('ready for trade')
                else:
                    await asyncio.sleep (0)
        except Exception as e:
            self.log_error (e)