import asyncio
import datetime
import traceback

from stocks.bitfinex import Bitfinex

try:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(Bitfinex().run())
    loop.close()
except Exception as e:
    f = open ('./logs/errors.log', 'a+')
    f.write ('{0}: {1}\n'.format(datetime.datetime.now().isoformat(), str(traceback.format_exc())))
    f.close ()