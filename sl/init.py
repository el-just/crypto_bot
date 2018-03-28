# import asyncio

# from common.logger import Logger
# from stocks.bittrex import Bittrex
# from stocks.binance import Binance
# from stocks.bitfinex import Bitfinex

# try:
#     loop = asyncio.get_event_loop()
#     loop.run_until_complete(Bittrex().custom_action())
#     loop.close()
# except Exception as e:
#     Logger.log_error (e)