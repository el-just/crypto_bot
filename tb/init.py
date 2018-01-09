import asyncio
from watchers.bitfinex import listen


loop = asyncio.get_event_loop()
loop.run_until_complete(listen())
loop.close()