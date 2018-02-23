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

def get_frame (data_path, index_col=None):
    frame = pd.read_csv (data_path, dtype={'close':np.float64, 'volume':np.float64}, index_col=index_col)
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

def show (item):
    ranges = [100, 200, 300, 500]
    frame = get_frame ('data/month_prepared.csv', index_col=0)

    date_start = frame.iloc[0].name+datetime.timedelta(minutes=60*24*1)
    date_ready = date_start + datetime.timedelta(minutes=60*24*7)
    date_end = date_ready + datetime.timedelta (minutes=60*24*10)
    frame = frame.loc[date_ready:date_end].copy()

    frame.loc[ : , ['close', 'avg']].plot(figsize=(12,8))
    item_colors = ['m', 'g', 'b', 'c']

    items = get_frame ('data/'+item+'.csv')
    for idx in range (0, len(ranges)):
        plt.plot (items.loc[items.loc[:, 'range'] == ranges[idx]].index, items.loc[items.loc[:, 'range'] == ranges[idx]].loc[:,'avg'], item_colors[idx]+'*')
    plt.show()

def show_results (file_name):
    frame = get_frame ('data/month_prepared.csv')

    date_start = frame.iloc[0].name+datetime.timedelta(minutes=60*24*1)
    date_ready = date_start + datetime.timedelta(minutes=60*24*7)
    date_end = date_ready + datetime.timedelta (minutes=60*24*10)
    
    frame = frame.loc[date_start:date_end].copy()
    frame['avg2'] = frame.loc[:, 'close'].rolling(38).mean()
    frame['avg3'] = frame.loc[:, 'close'].rolling(23).mean()
    frame = frame.loc[date_ready:date_end].copy()

    frame.loc[ : , ['close', 'avg']].plot(figsize=(12,8))

    positions = pd.read_csv ('data/positions_'+file_name+'.csv', index_col=0)
    positions.loc[:, 'out_date'] = pd.to_datetime(positions.loc[:, 'out_date'])
    positions = positions.set_index (pd.to_datetime(positions.index.values))

    plt.plot (positions.index, positions.loc[:,'in_price'], 'm*')
    plt.plot (positions.loc[:, 'out_date'], positions.loc[:,'out_price'], 'c*')

    plt.show()

def get_trend (frame, tick, window):
    trend_frame = frame.loc[tick.name-datetime.timedelta(**window):tick.name]
    clf = linear_model.LinearRegression()
    clf.fit (trend_frame.loc[:,'timestamp'].values.reshape(-1,1), trend_frame.loc[:, 'avg'].values)

    return clf
    
def analyse ():
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
    
    frame = frame.iloc[62:].copy()

    cave_ranges = [100, 200, 300, 500]
    watch_caves = [frame.loc[frame.iloc[0].name+datetime.timedelta(minutes=60*24):].iloc[:2].copy()]*len(cave_ranges)
    caves = [pd.DataFrame()]*len(cave_ranges)

    hill_ranges = [100, 200, 300, 500]
    watch_hills = [frame.loc[frame.iloc[0].name+datetime.timedelta(minutes=60*24):].iloc[:2].copy()]*len(hill_ranges)
    hills = [pd.DataFrame()]*len(hill_ranges)

    positions = pd.DataFrame ()
    trend = pd.DataFrame ()
    current_idx = frame.index.get_loc(frame.loc[frame.iloc[0].name+datetime.timedelta(minutes=60*24):].iloc[0].name)
    frame = frame.loc[frame.iloc[0].name+datetime.timedelta(minutes=60*24):].copy()
    for idx, tick in frame.iloc[2:].iterrows():
        if current_idx % int(frame.shape[0] / 100) == 0:
            log_info(current_idx // int(frame.shape[0] / 100))

        trend_s = get_trend (frame, tick, {'minutes': 60*24/2.618})
        trend_d = get_trend (frame, tick, {'minutes': 60*24/2.618/2.618})
        trend_t = get_trend (frame, tick, {'minutes': 60*24/2.618/2.618/2.618})

        trend_row = pd.Series (data=[trend_s.coef_[0], trend_d.coef_[0], trend_t.coef_[0]], index=['single', 'double', 'triple'])
        trend_row.name = tick.name
        trend = trend.append (trend_row)

        for idx in range(0, len(cave_ranges)):
            watch_caves[idx] = watch_caves[idx].append (frame.loc[tick.name])
            cave = factors.cave (watch_caves[idx])

            if cave is not None and cave.name not in caves[idx].index.values:
                if factors.fee (watch_caves[idx].loc[:, 'avg'].min(), watch_caves[idx].loc[:, 'avg'].max()) > cave_ranges[idx]:
                    cave['in_close'] = tick.at['close']
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

    trend.to_csv ('data/trend.csv', index=True, header=True)

    for idx in range(0, len(cave_ranges)):
        if caves[idx].shape[0] > 0:
            caves[idx].to_csv ('data/caves'+str(cave_ranges[idx])+'.csv', index=True, header=True)

    for idx in range(0, len(hill_ranges)):
        if hills[idx].shape[0] > 0:
            hills[idx].to_csv ('data/hills'+str(hill_ranges[idx])+'.csv', index=True, header=True)

def assume_hill (cave, caves, hills, trend_col):
    def pick_hill (cave, hills, caves):
        hill = hills.loc[hills.index > cave.name]
        hill = hill.iloc[0] if hill.shape[0] > 0 else None

        if hill is not None and caves.index.get_loc (cave.name) < caves.shape[0]-1:
            return hill.at['avg'] - cave.at['avg'] if hill.name < caves.iloc [caves.index.get_loc (cave.name)+1].name else None
        else:
            return None
    
    hill_range = None
     # & (caves.loc[:, trend_col] > 0)
    similar_caves = caves.loc[
        (caves.loc[:, 'range'] == cave.at['range']) & (caves.index <= cave.name)]
    relevant_hills = similar_caves.apply (pick_hill, args=(hills, similar_caves), axis=1)
    relevant_hills = relevant_hills.dropna ()

    return relevant_hills.median()

class Traider ():
    _trend_field = None
    _diff_field = None

    _balance = None

    _positions = pd.DataFrame ()
    _position = None

    def __init__ (self, trend_field=None, diff_field=None, trend_window=None):
        self._trend_field = trend_field if trend_window is None else 'trend_custom'
        self._diff_field = diff_field
        self._trend_window = trend_window

        self._balance = {
            'usd': 2000.00,
            'btc': 0.00
            }

    def position_in (self, tick, assume_range):
        self._balance['btc'] = self._balance['usd'] / tick.at['close'] - self._balance['usd'] / tick.at['close']*0.002
        self._balance['usd'] = 0.

        self._position = pd.Series (data=[tick.at['close'], tick.at['avg'], assume_range, None, None, 'single'], index=['in_price', 'in_avg', 'assume_range', 'out_price', 'out_date', 'trend_type'])
        self._position.name = tick.name

    def position_out (self, tick):
        self._balance['usd'] = tick.at['close'] * self._balance['btc'] - tick.at['close'] * self._balance['btc']*0.002
        self._balance['btc'] = 0.
        
        self._position.at['out_price'] = tick.at['close']
        self._position.at['out_date'] = tick.name
        self._positions = self._positions.append (self._position)

        log_info ('trend={0}, diff={1}, close_in={2}, close_out={3}, balance={4}'.format(self._trend_field, self._diff_field, self._position.at['in_price'], self._position.at['out_price'], self._balance['usd']))
        self._position = None

    def decide (self, current_caves=None, caves=None, hills=None, tick=None, frame=None):
        if self._position is None and current_caves.shape[0] > 0:
            assume_range = assume_hill (current_caves.iloc[current_caves.shape[0]-1], caves, hills, self._trend_field)
            # if factors.fee (tick.at['close'], (tick.at['close'] + assume_range)) > 0:
            #     if assume_range / abs(tick.at['close'] - tick.at['avg']) >= 2.618:
            self.position_in (tick, assume_range)
        elif self._position is not None:
            if tick.at['close'] >= (self._position.at['in_price'] + self._position.at['assume_range'] / 1.618) and tick.at[self._diff_field] < 0:
                self.position_out (tick)
            # elif tick.at['close'] / self._position.at['in_price'] < 1.01 and tick.at[self._diff_field] < 0:
                # self.position_out (tick)
            elif self._position.at['in_price'] - tick.at['close'] > self._position.at['assume_range']/2.618 and tick.at[self._diff_field] < 0:
                self.position_out (tick)

    def to_csv (self):
        self._positions.to_csv ('data/positions_'+self._trend_field+'_'+self._diff_field+'.csv', index=True, header=True)

def analyse_prepared ():
    traiders = [
        Traider (trend_field='custom', diff_field='diff', trend_window={'minutes':60*6})
        ]

    ranges = [100, 200, 300, 500]

    trend = pd.read_csv ('data/trend.csv', index_col=0)
    frame = get_frame ('data/month_prepared.csv')
    frame = frame.join (trend, how="inner")
    frame['diff'] = frame.loc[:, 'avg'].diff()
    frame['diff2'] = frame.loc[:, 'close'].rolling(38).mean().diff()
    frame['diff3'] = frame.loc[:, 'close'].rolling(23).mean().diff()
    frame['trend_custom'] = None

    date_start = frame.iloc[0].name+datetime.timedelta(minutes=60*24*1)
    date_ready = date_start + datetime.timedelta(minutes=60*24*7)
    date_end = date_ready + datetime.timedelta (minutes=60*24*7)
    
    frame = frame.loc[date_start:date_end].copy()

    caves = pd.DataFrame ()
    hills = pd.DataFrame ()
    for idx in range (0, len(ranges)):
        current_caves = get_frame ('data/caves'+str(ranges[idx])+'.csv', index_col=0)
        current_caves['range'] = ranges[idx]        
        current_caves = current_caves.join (trend, how="inner")
        caves = caves.append (current_caves)

        current_hills = get_frame ('data/hills'+str(ranges[idx])+'.csv', index_col=0)
        current_hills['range'] = ranges[idx]
        current_hills = current_hills.join (trend, how="inner")
        hills = hills.append (current_hills)

    caves.sort_index (inplace=True)
    hills.sort_index (inplace=True)
    
    caves = caves.loc[caves.index < date_ready].copy()
    hills = hills.loc[hills.index < date_ready].copy()

    cave_max = frame.loc[caves.iloc[caves.shape[0]-1].name:date_ready, 'avg'].max()
    cave_ext = frame.loc[caves.iloc[caves.shape[0]-1].name:date_ready, :].copy()
    watch_caves = [frame.loc[cave_ext.loc [cave_ext.loc[:, 'avg'] == cave_max].iloc[0].name: date_ready]]*len(ranges)

    hill_min = frame.loc[hills.iloc[hills.shape[0]-1].name:date_ready, 'avg'].min()
    hill_ext = frame.loc[hills.iloc[hills.shape[0]-1].name:date_ready, :].copy()
    watch_hills = [frame.loc[hill_ext.loc [hill_ext.loc[:, 'avg'] == hill_min].iloc[0].name: date_ready]]*len(ranges)

    current_idx = frame.index.get_loc(frame.loc[date_ready:].iloc[0].name)

    for idx, tick in frame.loc [date_ready:date_end].iterrows():
        if current_idx % int(frame.shape[0] / 100) == 0:
            log_info(current_idx // int(frame.shape[0] / 100))

        current_caves = pd.DataFrame ()
        for idx in range(0, len(ranges)):
            watch_caves[idx] = watch_caves[idx].append (frame.loc[tick.name])
            cave = factors.cave (watch_caves[idx])

            if cave is not None and cave.name not in caves.loc[caves.loc[:, 'range'] == ranges[idx]].index.values:
                if factors.fee (watch_caves[idx].loc[:, 'avg'].min(), watch_caves[idx].loc[:, 'avg'].max()) > ranges[idx]:
                    cave['range'] = ranges[idx]
                    caves = caves.append (cave)
                    caves.sort_index (inplace=True)
                    current_caves = current_caves.append (cave)
                    watch_caves[idx] = pd.DataFrame()
                    watch_caves[idx] = watch_caves[idx].append (frame.loc[tick.name])
            
            if tick.at['avg'] > watch_caves[idx].iloc[0].at['avg']:
                watch_caves[idx] = pd.DataFrame()
                watch_caves[idx] = watch_caves[idx].append (frame.loc[tick.name])

            watch_hills[idx] = watch_hills[idx].append (frame.loc[tick.name])
            hill = factors.hill (watch_hills[idx])

            if hill is not None and hill.name not in hills.loc[hills.loc[:, 'range'] == ranges[idx]].index.values:
                if factors.fee (watch_hills[idx].loc[:, 'avg'].min(), watch_hills[idx].loc[:, 'avg'].max()) > ranges[idx]:
                    hill['range'] = ranges[idx]
                    hills = hills.append (hill)
                    hills.sort_index (inplace=True)
                    watch_hills[idx] = pd.DataFrame()
                    watch_hills[idx] = watch_hills[idx].append (frame.loc[tick.name])
            
            if tick.at['avg'] < watch_hills[idx].iloc[0].at['avg']:
                watch_hills[idx] = pd.DataFrame()
                watch_hills[idx] = watch_hills[idx].append (frame.loc[tick.name])

        for traider in traiders:
            traider.decide (
                current_caves = current_caves,
                caves = caves,
                hills = hills,
                tick = tick,
                frame = frame
                )

        current_idx = frame.index.get_loc (tick.name) + 1

    for traider in traiders:
        traider.to_csv ()

    caves.to_csv ('data/caves.csv', index=True, header=True)
    caves.to_csv ('data/hills.csv', index=True, header=True)

show ('caves')
# show_results('trend_custom_diff2')
# analyse_prepared ()
