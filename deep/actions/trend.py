import pandas as pd
import matplotlib.pyplot as plt
from sklearn import linear_model
import math

TREND_PART = 0.2

frame = pd.read_csv ('../data/BTC_USD_20171121.d')
frame['diff'] = None

def get_trend (frame):
    trend_frame = frame[-int(frame.shape[0]*TREND_PART):]
    clf = linear_model.LinearRegression()
    clf.fit (trend_frame.loc[:,'timestamp'].values.reshape(-1,1), trend_frame.loc[:,'close'].values)
    trend_frame.loc[:,'line'] = clf.predict (trend_frame.loc[:,'timestamp'].values.reshape(-1,1))
    trend_frame[['close', 'line']].plot(figsize=(12,8))
    print (clf.coef_[0])
    plt.show()


get_trend (frame)