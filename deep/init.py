import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

frame = pd.read_csv ('./data/BTC_USD_20171121.d')

frame['timestamp'] = pd.to_datetime (frame['timestamp'], unit='s')
frame.set_index ('timestamp', inplace=True)

frame['weighted_avg'] = frame["close"].ewm(com=10).mean()
frame['diff'] = frame['weighted_avg'].diff()

#frame['weighted_avg'].plot(figsize=(12,8))
frame['diff'].plot(figsize=(12,8))
plt.show()

'''

N = 3
frame['close_avg'] = frame[['close']].shift().rolling(N, min_periods=1).mean()
frame['timestamp'] = pd.to_datetime (frame['timestamp'], unit='s')

frame.set_index ('timestamp', inplace=True)
frame['MA7'] = frame['close_avg'].rolling(window='2400s', center=False).mean()

frame[['close_avg', 'MA7']].plot(figsize=(12,8))
print (frame['MA7'])

'''