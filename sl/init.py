import asyncio

from common.logger import Logger
from stocks.bittrex import Bittrex
from stocks.binance import Binance

try:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(Binance().custom_action())
    loop.close()
except Exception as e:
    Logger.log_error (e)
