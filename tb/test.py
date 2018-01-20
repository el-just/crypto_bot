import asyncio
from testing.stock import Stock
import traceback

try:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(Stock().run())
    loop.close()
except Exception as e:
    print (e)
    print (str(traceback.format_exc()))