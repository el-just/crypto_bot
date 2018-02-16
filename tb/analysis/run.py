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
    watch_cave = frame.loc[frame.iloc[0].name+datetime.timedelta(minutes=60*24):].iloc[:2].copy()
    watch_hill = pd.DataFrame()
    caves = pd.DataFrame()
    outs = pd.DataFrame()
    ins = pd.DataFrame()
    positions = pd.DataFrame ()
    current_idx = frame.index.get_loc(frame.loc[frame.iloc[0].name+datetime.timedelta(minutes=60*24):].iloc[0].name)
    frame = frame.loc[frame.iloc[0].name+datetime.timedelta(minutes=60*24):frame.iloc[0].name+datetime.timedelta(minutes=60*24*8)].copy()
    for idx, tick in frame.iloc[2:].iterrows():
        if current_idx % int(frame.shape[0] / 100) == 0:
            log_info(current_idx // int(frame.shape[0] / 100))

        watch_cave = watch_cave.append (frame.loc[tick.name])
        watch_cave = watch_cave.loc[watch_cave.iloc[watch_cave.shape[0]-1].name - datetime.timedelta (minutes=60*24/2.618):]
        cave = factors.cave (watch_cave)
        if cave is not None and cave.name not in caves.index:
            predict = factors.predict_out (watch_cave)
            #  and factors.shape_proportion (predict) >= 1.618 
            if factors.fee (tick.at['close'], predict.at['price']) > 0:
                caves = caves.append (cave)
                predict.name = tick.name
                predicts = predicts.append (predict)
                if position is None and predict.at['range'] > 200 and (predict.at['range'] / predict.at['gap'] > 0.03 or predict.at['gap'] > 10000):
                    position_in (tick, balance)
                    log_info (predict)
                    ins = ins.append (tick)
                    position = get_empty_position ()
                    position.at['cave_price'] = cave.at['avg']
                    position.at['cave_max_price'] = watch_cave.loc[:, 'avg'].max()
                    position.at['cave_gap'] = predict.at['gap']
                    position.at['in_price'] = tick.at['close']
                    position.at['predicted_price'] = predict.at['price']
                    position.at['cave_timestamp'] = cave.at['timestamp']
                    position.at['in_timestamp'] = tick.at['timestamp']
                    position.at['predicted_timestamp'] = predict.at['timestamp']
                    
                watch_cave = pd.DataFrame()
                watch_cave = watch_cave.append (frame.loc[tick.name])
        if tick.at['avg'] > watch_cave.iloc[0].at['avg']:
            watch_cave = pd.DataFrame()
            watch_cave = watch_cave.append (frame.loc[tick.name])

        if position is not None and tick.name >= datetime.datetime.fromtimestamp(position.at['predicted_timestamp'] - position.at['cave_gap']/2/2.618):
            if watch_hill.shape[0] == 0:
                watch_hill = frame.loc[watch_cave.iloc[0].name:tick.name].copy()
            else:
                watch_hill = watch_hill.append(tick)

            hill = factors.hill (watch_hill, column='avg2', proportion=2.618*2.618)
            if hill is not None:
                position_out (tick, balance)
                outs = outs.append (tick)
                position.at['out_price'] = tick.at['close']
                position.at['out_timestamp'] = tick['timestamp']
                position.name = tick.name
                positions = positions.append (position)
                position = None
                watch_hill = pd.DataFrame()

        if position is not None and position.at['cave_price'] - tick.at['avg'] > (position.at['cave_max_price'] - position.at['cave_price'])/2.6218:
            position_out (tick, balance)
            outs = outs.append (tick)
            position.at['out_price'] = tick.at['close']
            position.at['out_timestamp'] = tick['timestamp']
            position.name = tick.name
            positions = positions.append (position)
            position = None
            watch_hill = pd.DataFrame()

        current_idx = frame.index.get_loc (tick.name) + 1

    frame.loc[ : , ['close', 'avg', 'avg2']].plot(figsize=(12,8))
    plt.plot (ins.index, ins.loc[:,'close'], 'm*')
    #plt.plot (predicts.loc[:, 'timestamp'].apply (lambda timestamp: datetime.datetime.fromtimestamp(timestamp)), predicts.loc[:,'price'], 'c*')
    plt.plot (outs.index, outs.loc[:,'close'], 'g*')
    #print(frame.iloc[frame.index.get_loc(outs.iloc[outs.shape[0]-1].name):frame.index.get_loc(outs.iloc[outs.shape[0]-1].name)+20].loc[:, 'diff2'])
    plt.show()

analise ()