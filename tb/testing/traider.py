from stocks.bitfinex.traider import Traider as BFT
import asyncio
from testing.logging import Logging

class Traider (BFT):
    async def run (self):
        try:
            while self._frame.shape[0] < 30:
                await asyncio.sleep (0)
            self._ready = True
        except Exception as e:
            Logging.log_error (e)