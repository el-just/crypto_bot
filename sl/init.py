import asyncio

from common import Logger
from stocks import Stream

try:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(Stream().run())
    loop.run_forever()
except Exception as e:
    Logger.log_error (e)
