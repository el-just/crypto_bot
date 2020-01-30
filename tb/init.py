import asyncio
from abstract.logging import Logging

from stocks.bitfinex import Bitfinex

try:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(Bitfinex().run())
    loop.close()
except Exception as e:
	Logging.log_error (e)