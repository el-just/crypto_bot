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
def show (item):
    ranges = [100, 200, 300, 500]
    frame = get_frame ('data/month_prepared.csv')
    frame = frame.loc[frame.iloc[0].name+datetime.timedelta(minutes=60*24*4):frame.iloc[0].name+datetime.timedelta(minutes=60*24*8)].copy()

    frame.loc[ : , ['close', 'avg']].plot(figsize=(12,8))
    item_colors = ['m', 'g', 'b', 'c']

    items = []
    for idx in range (0, len(ranges)):
        items.append (get_frame ('data/'+item+str(ranges[idx])+'.csv'))
        if items[idx].shape[0] > 0:
            plt.plot (items[idx].index, items[idx].loc[:,'avg'], item_colors[idx]+'*')
    plt.show()
    
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

    cave_ranges = [100, 200, 300, 500]
    watch_caves = [frame.loc[frame.iloc[0].name+datetime.timedelta(minutes=60*24):].iloc[:2].copy()]*len(cave_ranges)
    caves = [pd.DataFrame()]*len(cave_ranges)

    hill_ranges = [100, 200, 300, 500]
    watch_hills = [frame.loc[frame.iloc[0].name+datetime.timedelta(minutes=60*24):].iloc[:2].copy()]*len(hill_ranges)
    hills = [pd.DataFrame()]*len(hill_ranges)
    
    frame = frame.iloc[62:].copy()
    positions = pd.DataFrame ()
    current_idx = frame.index.get_loc(frame.loc[frame.iloc[0].name+datetime.timedelta(minutes=60*24):].iloc[0].name)
    frame = frame.loc[frame.iloc[0].name+datetime.timedelta(minutes=60*24*4):frame.iloc[0].name+datetime.timedelta(minutes=60*24*8)].copy()
    for idx, tick in frame.iloc[2:].iterrows():
        if current_idx % int(frame.shape[0] / 100) == 0:
            log_info(current_idx // int(frame.shape[0] / 100))

        for idx in range(0, len(cave_ranges)):
            watch_caves[idx] = watch_caves[idx].append (frame.loc[tick.name])
            cave = factors.cave (watch_caves[idx])

            if cave is not None and cave.name not in caves[idx].index.values:
                if factors.fee (watch_caves[idx].loc[:, 'avg'].min(), watch_caves[idx].loc[:, 'avg'].max()) > cave_ranges[idx]:
                    caves[idx] = caves[idx].append (cave)
                    watch_caves[idx] = pd.DataFrame()
                    watch_caves[idx] = watch_caves[idx].append (frame.loc[tick.name])
            
            if tick.at['avg'] > watch_caves[idx].iloc[0].at['avg']:
                watch_caves[idx] = pd.DataFrame()
                watch_caves[idx] = watch_caves[idx].append (frame.loc[tick.name])

        for idx in range(0, len(hill_ranges)):
            watch_hills[idx] = watch_hills[idx].append (frame.loc[tick.name])
            hill = factors.hill (watch_hills[idx])

            if hill is not None and hill.name not in hills[idx].index.values:
                if factors.fee (watch_hills[idx].loc[:, 'avg'].min(), watch_hills[idx].loc[:, 'avg'].max()) > hill_ranges[idx]:
                    hills[idx] = hills[idx].append (hill)
                    watch_hills[idx] = pd.DataFrame()
                    watch_hills[idx] = watch_hills[idx].append (frame.loc[tick.name])
            
            if tick.at['avg'] < watch_hills[idx].iloc[0].at['avg']:
                watch_hills[idx] = pd.DataFrame()
                watch_hills[idx] = watch_hills[idx].append (frame.loc[tick.name])


        current_idx = frame.index.get_loc (tick.name) + 1

    for idx in range(0, len(cave_ranges)):
        if caves[idx].shape[0] > 0:
            caves[idx].to_csv ('data/caves'+str(cave_ranges[idx])+'.csv', index=True, header=True)

    for idx in range(0, len(hill_ranges)):
        if hills[idx].shape[0] > 0:
            hills[idx].to_csv ('data/hills'+str(hill_ranges[idx])+'.csv', index=True, header=True)

analise ()
#show ('caves')