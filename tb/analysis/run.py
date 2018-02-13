import os
import time
import datetime

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn import linear_model

import methods.mvag as mvag
import methods.extremums as extremums
import factors.basic as factors

def get_frame (data_path):
    frame = pd.read_csv (data_path, dtype={'close':np.float64, 'volume':np.float64})
    frame.loc[:, 'tick_time'] = pd.to_datetime(frame.loc[:, 'tick_time'])
    frame = frame.set_index (pd.to_datetime(frame.loc[:, 'tick_time']).values)
    frame['timestamp'] = frame.loc[:, 'tick_time'].apply (lambda tick_time: time.mktime (tick_time.timetuple()))

    return frame 

def trend_to_csv ():
    frame = get_frame('data/month.csv')
    frame['avg'] = frame.loc[:, 'close'].rolling(62).mean()

    frame = frame.iloc[63:].copy()
    frame = frame.loc[frame.iloc[0].name:frame.iloc[0].name+datetime.timedelta(minutes=60*48)].copy()
    frame = frame.reset_index().drop_duplicates(subset='index', keep='last').set_index('index')
    frame['trend_coef'] = None
    frame['trend_intercept'] = None
    for idx, tick in frame.loc[frame.iloc[0].name+datetime.timedelta(minutes=60*24):].iterrows():
        trend_frame = frame.loc[tick.name-datetime.timedelta(minutes=60*24):tick.name]

        clf = linear_model.LinearRegression()
        clf.fit (trend_frame.loc[:,'timestamp'].values.reshape(-1,1), trend_frame.loc[:, 'avg'].values)
    
        frame.at[idx, 'trend_coef'] = clf.coef_[0]
        frame.at[idx, 'trend_intercept'] = clf.intercept_

    frame.to_csv ('data/month_plus_trend.csv', index=False, header=True)

position = None
predicts = return pd.DataFrame (data=[], columns=['timestamp', 'gap', 'price', 'range'])
usd = 2000.
btc = 0.
def position_in (tick, predict):
    btc = usd / tick.at['close'] - usd / tick.at['close']*0.002
    usd = 0

    predict.name = tick.name
    predicts.append (predict)
    position = True

def position_out (tick):
    usd = tick.at['close'] * btc - tick.at['close'] * btc*0.002
    btc = 0.
    
    position = None

def analise ():
    frame = get_frame ('data/month_plus_trend.csv')
    frame = frame.loc[frame.iloc[0].name+datetime.timedelta(minutes=60*24):].copy()

    watch_cave = frame.iloc[:2].copy()
    watch_hill = frame.iloc[:2].copy()
    caves = pd.DataFrame()
    hills = pd.DataFrame()
    current_idx = 2
    current_cave = None
    current_hill = None
    
    for idx, tick in frame.iloc[2:].iterrows():
        if current_idx % int(frame.shape[0] / 100) == 0:
            print(current_idx // int(frame.shape[0] / 100))

        watch_cave = watch_cave.append (tick)
        watch_cave = watch_cave.loc[watch_cave.iloc[watch_cave.shape[0]-1].name - datetime.timedelta (minutes=60*24/1.618):]
        cave = factors.cave (watch_cave)
        if cave is not None:
            predict = factors.predict_out (watch_cave)
            if factors.fee (tick.at['close'], predict.at['price']) > 0:
                caves = caves.append (cave)
                if position is None:
                    position_in (tick, pridict)
                watch_cave = pd.DataFrame()
                watch_cave = watch_cave.append (tick)
        if tick.at['avg'] > watch_cave.iloc[0].at['avg']:
            watch_cave = pd.DataFrame()
            watch_cave = watch_cave.append (tick)

        # watch_hill = watch_hill.append (tick)
        # hill = factors.hill (watch_hill)
        # if hill is not None:
        #     hills = hills.append (hill)
        #     watch_hill = pd.DataFrame()
        #     watch_hill = watch_hill.append (tick)

        # if tick.at['avg'] < watch_hill.iloc[0].at['avg']:
        #     watch_hill = pd.DataFrame()
        #     watch_hill = watch_hill.append (tick)

        current_idx += 1

    frame.loc[ : , ['close', 'avg']].plot(figsize=(12,8))
    plt.plot (caves.index, caves.loc[:,'avg'], 'm*')
    #plt.plot (hills.index, hills.loc[:,'avg'], 'g*')
    plt.show()

analise ()