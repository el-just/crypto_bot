from stocks.bitfinex.traider import Traider as BFT
import asyncio
import datetime
from testing.logging import Logging

class Traider (BFT):
    def __init__ (self):
        self.log_info = Logging.log_info
        self.log_error = Logging.log_error