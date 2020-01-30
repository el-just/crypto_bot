import asyncio
from testing.stock import Stock
import json
import ast
import pandas as pd
import numpy as np
from testing.logging import Logging
from stocks.bitfinex.rest_socket import RESTSocket

modes = [
	'csv',
	'db',
	'noch',
	'trade_emulation',
	'trade_emulation_with_inserts'
	]

try:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(Stock (modes[4]).run())
    loop.close()
except Exception as e:
    Logging.log_error (e)