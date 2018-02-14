import os
import time
import datetime

import numpy as np
import pandas as pd
#import matplotlib.pyplot as plt
from sklearn import linear_model

import methods.mvag as mvag
import methods.extremums as extremums
import factors.basic as factors

def log_info (message):
    try:
        f = open ('./logs/info.log', 'a+')
    except IOError as e:
        os.makedirs('logs')
        f = open ('./logs/info.log', 'w+')
    
    f.write ('{0}:\n\t{1}\n'.format(datetime.datetime.now().isoformat(), message))
    f.close ()

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

def analise ():
    position = None
    balance = {
        'usd': 2000.,
        'btc': 0.
        }
    
    predicts = pd.DataFrame (data=[], columns=['timestamp', 'gap', 'price', 'range'])

    def position_in (tick, balance):
        balance['btc'] = balance['usd'] / tick.at['close'] - balance['usd'] / tick.at['close']*0.002
        balance['usd'] = 0.

        log_info (balance)

    def position_out (tick, balance):
        balance['usd'] = tick.at['close'] * balance['btc'] - tick.at['close'] * balance['btc']*0.002
        balance['btc'] = 0.

        log_info (balance)

    frame = get_frame ('data/month.csv')
    frame = frame.reset_index().drop_duplicates(subset='index', keep='last').set_index('index')
    frame['trend_coef'] = None
    frame['trend_intercept'] = None
    frame['avg'] = frame.loc[:, 'close'].rolling (62).mean()
    
    frame = frame.iloc[62:].copy()
    watch_cave = frame.loc[frame.iloc[0].name+datetime.timedelta(minutes=60*24):].iloc[:2].copy()
    caves = pd.DataFrame()
    current_idx = frame.index.get_loc(frame.loc[frame.iloc[0].name+datetime.timedelta(minutes=60*24):].iloc[0].name)
    for idx, tick in frame.loc[frame.iloc[0].name+datetime.timedelta(minutes=60*24):].iloc[2:].iterrows():
        if current_idx % int(frame.shape[0] / 100) == 0:
            log_info(current_idx // int(frame.shape[0] / 100))

        trend_frame = frame.loc[tick.name-datetime.timedelta(minutes=60*24):tick.name]
        clf = linear_model.LinearRegression()
        clf.fit (trend_frame.loc[:,'timestamp'].values.reshape(-1,1), trend_frame.loc[:, 'avg'].values)
        frame.at[idx, 'trend_coef'] = clf.coef_[0]
        frame.at[idx, 'trend_intercept'] = clf.intercept_

        watch_cave = watch_cave.append (frame.loc[tick.name])
        watch_cave = watch_cave.loc[watch_cave.iloc[watch_cave.shape[0]-1].name - datetime.timedelta (minutes=60*24/1.618):]
        cave = factors.cave (watch_cave)
        if cave is not None:
            predict = factors.predict_out (watch_cave)
            if factors.fee (tick.at['close'], predict.at['price']) > 0:
                caves = caves.append (cave)
                predict.name = tick.name
                predicts = predicts.append (predict)
                if position is None:
                    position_in (tick, balance)
                    position = predict
                watch_cave = pd.DataFrame()
                watch_cave = watch_cave.append (frame.loc[tick.name])
        if tick.at['avg'] > watch_cave.iloc[0].at['avg']:
            watch_cave = pd.DataFrame()
            watch_cave = watch_cave.append (frame.loc[tick.name])

        if position is not None and tick.name >= datetime.datetime.fromtimestamp(position.at['timestamp']):
            position_out (tick, balance)
            position = None

        # watch_hill = watch_hill.append (tick)
        # hill = factors.hill (watch_hill)
        # if hill is not None:
        #     hills = hills.append (hill)
        #     watch_hill = pd.DataFrame()
        #     watch_hill = watch_hill.append (tick)

        # if tick.at['avg'] < watch_hill.iloc[0].at['avg']:
        #     watch_hill = pd.DataFrame()
        #     watch_hill = watch_hill.append (tick)

        current_idx = frame.index.get_loc (tick.name) + 1

    predicts.to_csv ('data/month_predicts.csv', index=False, header=True)
    frame.to_csv ('data/month_prepared.csv', index=False, header=True)
    caves.to_csv ('data/month_caves.csv', index=True, header=True)

    #frame.loc[ : , ['close', 'avg', 'avg2', 'avg3']].plot(figsize=(12,8))
    # plt.plot (caves.index, caves.loc[:,'avg'], 'm*')
    # plt.plot (predicts.loc[:, 'timestamp'].apply (lambda timestamp: datetime.datetime.fromtimestamp(timestamp)), predicts.loc[:,'price'], 'g*')
    #plt.show()

analise ()