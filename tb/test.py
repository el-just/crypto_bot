import asyncio
from testing.stock import Stock
import json
import ast
import pandas as pd
import numpy as np
from testing.logging import Logging

try:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(Stock().run())
    loop.close()
except Exception as e:
    Logging.log_error (e)