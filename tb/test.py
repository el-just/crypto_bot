import asyncio
import numpy as np
from testing.stock import Stock
import traceback
import pandas as pd
import datetime
import time
import matplotlib.pyplot as plt
from scipy.signal import argrelextrema
from sklearn import linear_model

try:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(Stock().run())
    loop.close()
except Exception as e:
    print (e)
    print (str(traceback.format_exc()))