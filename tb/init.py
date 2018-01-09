import asyncio
from listeners.bitfinex import Bitfinex

loop = asyncio.get_event_loop()
loop.run_until_complete(Bitfinex().listen())
loop.close()