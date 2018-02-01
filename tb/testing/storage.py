import time
import datetime

from testing.logging import Logging
from stocks.bitfinex.storage import Storage as BTFXStorage
from stocks.bitfinex.defines import DEFINES

class Storage (BTFXStorage):
    def __init__ (self):
        self.log_info = Logging.log_info
        self.log_error = Logging.log_error

    async def is_available (self):
        return True

    async def insert_ticks (self, ticks):
        pass

    async def get_missing_periods (self, period):
        now = datetime.datetime.now()
        interval = datetime.timedelta (DEFINES.REQUIRED_INTERVAL)
        periods = []

        # periods.append ({
        #   'start':
        #   'end': now
        #   })

        return periods