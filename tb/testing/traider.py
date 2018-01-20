from stocks.bitfinex.traider import Traider as BFT
import asyncio
from testing.logging import Logging

class Traider (BFT, Logging):
    async def run (self):
        try:
            while self._frame.shape[0] < 30:
                self.log_info (self._frame.shape[0])
                await asyncio.sleep (0)
            self._ready = True
        except Exception as e:
            self.log_error (e)