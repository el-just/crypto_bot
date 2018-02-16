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

def get_empty_position ():
    index = [
        'cave_price'
        , 'cave_max_price'
        , 'cave_gap'
        , 'in_price'
        , 'predicted_price'
        , 'out_price'
        , 'cave_timestamp'
        , 'in_timestamp'
        , 'predicted_timestamp'
        , 'out_timestamp'
        ]

    return pd.Series (data=[None, None, None, None, None, None, None, None, None, None], index=index)

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

    frame = get_frame ('data/month_prepared.csv')
    frame['avg2'] = frame.loc[:, 'close'].rolling(38).mean()
    frame['diff2'] = frame.loc[:, 'avg2'].diff()
    
    frame = frame.iloc[62:].copy()
    watch_cave100 = frame.loc[frame.iloc[0].name+datetime.timedelta(minutes=60*24):].iloc[:2].copy()
    watch_cave200 = frame.loc[frame.iloc[0].name+datetime.timedelta(minutes=60*24):].iloc[:2].copy()
    watch_cave300 = frame.loc[frame.iloc[0].name+datetime.timedelta(minutes=60*24):].iloc[:2].copy()
    watch_cave500 = frame.loc[frame.iloc[0].name+datetime.timedelta(minutes=60*24):].iloc[:2].copy()
    watch_hill = pd.DataFrame()
    caves100 = pd.DataFrame()
    caves200 = pd.DataFrame()
    caves300 = pd.DataFrame()
    caves500 = pd.DataFrame()
    outs = pd.DataFrame()
    ins = pd.DataFrame()
    positions = pd.DataFrame ()
    current_idx = frame.index.get_loc(frame.loc[frame.iloc[0].name+datetime.timedelta(minutes=60*24):].iloc[0].name)
    frame = frame.loc[frame.iloc[0].name+datetime.timedelta(minutes=60*24*4):frame.iloc[0].name+datetime.timedelta(minutes=60*24*8)].copy()
    for idx, tick in frame.iloc[2:].iterrows():
        if current_idx % int(frame.shape[0] / 100) == 0:
            log_info(current_idx // int(frame.shape[0] / 100))

        watch_cave100 = watch_cave100.append (frame.loc[tick.name])
        watch_cave200 = watch_cave200.append (frame.loc[tick.name])
        watch_cave300 = watch_cave300.append (frame.loc[tick.name])
        watch_cave500 = watch_cave500.append (frame.loc[tick.name])
        cave100 = factors.cave (watch_cave100)
        cave200 = factors.cave (watch_cave200)
        cave300 = factors.cave (watch_cave300)
        cave500 = factors.cave (watch_cave500)
        
        if cave100 is not None and cave100.name not in caves100.index and factors.fee (watch_cave100.loc[:, 'avg'].min(), watch_cave100.loc[:, 'avg'].max()) > 100:
            caves100 = caves100.append (cave100)
            watch_cave100 = pd.DataFrame()
            watch_cave100 = watch_cave100.append (frame.loc[tick.name])
        if tick.at['avg'] > watch_cave100.iloc[0].at['avg']:
            watch_cave100 = pd.DataFrame()
            watch_cave100 = watch_cave100.append (frame.loc[tick.name])

        if cave200 is not None and cave200.name not in caves200.index and factors.fee (watch_cave200.loc[:, 'avg'].min(), watch_cave200.loc[:, 'avg'].max()) > 200:
            caves200 = caves200.append (cave200)
            watch_cave200 = pd.DataFrame()
            watch_cave200 = watch_cave200.append (frame.loc[tick.name])
        if tick.at['avg'] > watch_cave200.iloc[0].at['avg']:
            watch_cave200 = pd.DataFrame()
            watch_cave200 = watch_cave200.append (frame.loc[tick.name])

        if cave300 is not None and cave300.name not in caves300.index and factors.fee (watch_cave300.loc[:, 'avg'].min(), watch_cave300.loc[:, 'avg'].max()) > 300:
            caves300 = caves300.append (cave300)
            watch_cave300 = pd.DataFrame()
            watch_cave300 = watch_cave300.append (frame.loc[tick.name])
        if tick.at['avg'] > watch_cave300.iloc[0].at['avg']:
            watch_cave300 = pd.DataFrame()
            watch_cave300 = watch_cave300.append (frame.loc[tick.name])

        if cave500 is not None and cave500.name not in caves500.index and factors.fee (watch_cave500.loc[:, 'avg'].min(), watch_cave500.loc[:, 'avg'].max()) > 500:
            caves500 = caves500.append (cave500)
            watch_cave500 = pd.DataFrame()
            watch_cave500 = watch_cave500.append (frame.loc[tick.name])
        if tick.at['avg'] > watch_cave500.iloc[0].at['avg']:
            watch_cave500 = pd.DataFrame()
            watch_cave500 = watch_cave500.append (frame.loc[tick.name])

        current_idx = frame.index.get_loc (tick.name) + 1

    frame.loc[ : , ['close', 'avg']].plot(figsize=(12,8))
    if caves100.shape[0] > 0:
        caves100.to_csv ('data/caves100.csv', index=True, header=True)
        plt.plot (caves100.index, caves100.loc[:,'avg'], 'm*')
    if caves200.shape[0] > 0:
        caves200.to_csv ('data/caves200.csv', index=True, header=True)
        plt.plot (caves200.index, caves200.loc[:,'avg'], 'g*')
    if caves300.shape[0] > 0:
        caves300.to_csv ('data/caves300.csv', index=True, header=True)
        plt.plot (caves300.index, caves300.loc[:,'avg'], 'b*')
    if caves500.shape[0] > 0:
        caves500.to_csv ('data/caves500.csv', index=True, header=True)
        plt.plot (caves500.index, caves500.loc[:,'avg'], 'c*')
    #plt.plot (predicts.loc[:, 'timestamp'].apply (lambda timestamp: datetime.datetime.fromtimestamp(timestamp)), predicts.loc[:,'price'], 'c*')
    #plt.plot (outs.index, outs.loc[:,'close'], 'g*')
    #print(frame.iloc[frame.index.get_loc(outs.iloc[outs.shape[0]-1].name):frame.index.get_loc(outs.iloc[outs.shape[0]-1].name)+20].loc[:, 'diff2'])
    plt.show()

analise ()