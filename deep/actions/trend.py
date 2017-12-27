import pandas as pd
import matplotlib.pyplot as plt
from sklearn import linear_model
import math

def weighted_std (tick, frame):
    if tick.name > 0:
        frame.loc [tick.name, 'std'] = frame.loc[:tick.name, 'weighted_avg'].std().mean()

TREND_PART = 0.2

frame = pd.read_csv ('../data/BTC_USD_20171121.d')
frame['std'] = None
frame['trend'] = None
frame['weighted_avg'] = frame["close"].ewm(com=10).mean()

frame.apply (weighted_std, args=[frame], axis=1)
frame['std1'] = frame.loc[:, 'weighted_avg'] + frame.loc[:, 'std']
frame['std2'] = frame.loc[:, 'weighted_avg'] - frame.loc[:, 'std']

def get_trend (frame):
    trend_frame = frame.iloc[-int(frame.shape[0]*TREND_PART):]
    
    clf = linear_model.LinearRegression()
    clf.fit (trend_frame.loc[:,'timestamp'].values.reshape(-1,1), trend_frame.loc[:,'close'].values)

    trend_frame.loc[:, 'trend'] = clf.predict (trend_frame.loc[:,'timestamp'].values.reshape(-1,1))
      
    trend_frame[['close', 'weighted_avg', 'std1', 'std2', 'trend']].plot(figsize=(12,8))
    plt.show()    

get_trend (frame)