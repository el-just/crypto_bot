import asyncio

from common.logger import Logger
from stocks.bittrex import Bittrex

try:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(Bittrex().get())
    loop.close()
except Exception as e:
    Logger.log_error (e)