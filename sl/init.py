import asyncio

from common.logger import Logger
from stocks.bittrex import Bittrex
from stocks.binance import Binance
from stocks.bitfinex import Bitfinex
from stocks.bittrex.signalr_socket import SignalrSocket
from stocks.gdax import GDAX
from stocks.cex import CEX

from stocks.stream import Stream

try:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(Stream().run())
    loop.run_forever()
except Exception as e:
    Logger.log_error (e)