import pandas as pd
import numpy as np

frame = pd.read_csv ('./data/BTC_USD_20171121.d')
frame['timestamp'] = pd.to_datetime (frame['timestamp'], unit='s')
frame.set_index ('timestamp', inplace=True)
frame['diff'] = None

def listen ():
    for index in range(frame.shape[0]):
        yield frame.iloc [index]