import asyncio
from testing.stock import Stock
import json
import ast
import pandas as pd
import numpy as np
from testing.logging import Logging
from stocks.bitfinex.rest_socket import RESTSocket

try:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(Stock ('csv').run())
    loop.close()
except Exception as e:
    Logging.log_error (e)