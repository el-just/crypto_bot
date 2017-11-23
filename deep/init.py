import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random

frame = pd.read_csv ('./data/BTC_USD_20171121.d')

plt.plot(frame[['timestamp']], frame[['close']], '-')
plt.show()