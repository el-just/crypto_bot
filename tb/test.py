import asyncio
import numpy as np
from scipy.signal import argrelextrema
from testing.stock import Stock
import traceback
import pandas as pd
import datetime
import time
import matplotlib.pyplot as plt
from sklearn import linear_model

window = {'minutes':60}

try:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(Stock().run())
    loop.close()
except Exception as e:
    print (e)
    print (str(traceback.format_exc()))
'''
def holt_winters_second_order_ewma( x, span, beta ):
    N = x.size
    alpha = 2.0 / ( 1 + span )
    s = np.zeros(( N, ))
    b = np.zeros(( N, ))
    s[0] = x[0]
    for i in range( 1, N ):
        s[i] = alpha * x[i] + ( 1 - alpha )*( s[i-1] + b[i-1] )
        b[i] = beta * ( s[i] - s[i-1] ) + ( 1 - beta ) * b[i-1]
    return s

def mirror_avg (tick):
    if float(tick.at['avg']) < float(tick.at['trend']):
        return float(tick.at['trend'])-float(tick.at['avg']) #+float(tick.at['trend'])
    else:
        return float(tick.at['avg']) - float(tick.at['trend'])

frame = pd.read_csv ('testing/day.csv')
frame.loc[:, 'tick_time'] = pd.to_datetime(frame.loc[:, 'tick_time'])
frame['timestamp'] = frame.loc[:, 'tick_time'].apply (lambda tick_time: time.mktime (tick_time.timetuple()))
frame.loc[:, 'close'] = frame.loc[:, 'close'].astype(float)
frame = frame.set_index (pd.to_datetime(frame.loc[:, 'tick_time']).values)
frame = frame.iloc[::-1]
frame = frame.loc[frame.iloc[0].name : frame.iloc[0].name + datetime.timedelta(**window)]

frame.loc[:, 'close'] = frame.loc[:, 'close'] - frame.loc[:,'close'].min()
frame['avg'] = holt_winters_second_order_ewma(frame.loc[:, 'close'].values , 10, 0.3 )
frame.loc[:,'avg'] = frame.loc[:,'avg'].shift(-2)

clf = linear_model.LinearRegression()
clf.fit (frame.loc[:,'timestamp'].values.reshape(-1,1), frame['close'].values)
frame['trend'] = clf.predict (frame.loc[:,'timestamp'].values.reshape(-1,1))



frame['mirror_avg'] = frame.apply(mirror_avg, axis=1)
frame['diff'] = frame.loc[:,'avg'].diff()

temp = frame.iloc[frame.shape[0]-1]
temp.at['diff'] = frame.iloc[frame.shape[0]-3].at['diff']
frame.iloc[frame.shape[0]-1] = temp

frame[['close', 'trend', 'avg']].plot(figsize=(12,8))

plt.show()


def predict_stop (frame):
    extremums = argrelextrema(frame.loc[:,'mirror_avg'].values, np.greater)[0][1:-1]
    extremums_avg = holt_winters_second_order_ewma(extremums , 10, 0.3 )
'''