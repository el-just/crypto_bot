from stocks.bitfinex.traider import Traider as BFT
import asyncio
from testing.logging import Logging

class Traider (BFT, Logging):
    async def run (self):
        while self._frame.shape[0] < 30:
            await asyncio.sleep (0)
        self._ready = True 