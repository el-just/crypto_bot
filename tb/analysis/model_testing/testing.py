import os
import time
import datetime
import pickle

import numpy as np
import pandas as pd
# import matplotlib.pyplot as plt
from sklearn import linear_model, tree, model_selection, neighbors, metrics, ensemble, externals

import methods.mvag as mvag
import methods.extremums as extremums
import factors.basic as factors

def get_frame (data_path, index_col=None):
    frame = pd.read_csv (data_path, dtype={'close':np.float64, 'volume':np.float64}, index_col=index_col)
    frame.loc[:, 'tick_time'] = pd.to_datetime(frame.loc[:, 'tick_time'])
    frame = frame.set_index (pd.to_datetime(frame.loc[:, 'tick_time']).values)
    frame['timestamp'] = frame.loc[:, 'tick_time'].apply (lambda tick_time: time.mktime (tick_time.timetuple()))

    return frame

def get_trend (frame, tick, window):
    trend_frame = frame.loc[tick.name-datetime.timedelta(**window):tick.name]
    clf = linear_model.LinearRegression()
    clf.fit (trend_frame.loc[:,'timestamp'].values.reshape(-1,1), trend_frame.loc[:, 'avg'].values)

    return clf

def log_info (message):
    try:
        f = open ('./logs/info.log', 'a+')
    except IOError as e:
        os.makedirs('logs')
        f = open ('./logs/info.log', 'w+')
    
    f.write ('{0}:\n\t{1}\n'.format(datetime.datetime.now().isoformat(), message))
    f.close ()

class Traider ():
    _diff_field = 'diff'

    _balance = None

    _positions = None
    _position = None
    _model = None
    _name = None

    def __init__ (self, model=None, name=''):
        self._model = model
        self._positions = pd.DataFrame ()
        self._name = name

        self._balance = {
            'usd': 2000.00,
            'btc': 0.00
            }

    def position_in (self, tick):
        self._balance['btc'] = self._balance['usd'] / tick.at['close'] - self._balance['usd'] / tick.at['close']*0.002
        self._balance['usd'] = 0.

        self._position = pd.Series (data=[tick.at['close'], tick.at['avg'], None, None, None, 'single'], index=['in_price', 'in_avg', 'assume_range', 'out_price', 'out_date', 'trend_type'])
        self._position.name = tick.name

    def position_out (self, tick):
        self._balance['usd'] = tick.at['close'] * self._balance['btc'] - tick.at['close'] * self._balance['btc']*0.002
        self._balance['btc'] = 0.
        
        self._position.at['out_price'] = tick.at['close']
        self._position.at['out_date'] = tick.name
        self._positions = self._positions.append (self._position)

        log_info ('name={0}, close_in={1}, close_out={2}, balance={3}'.format(self._name, self._position.at['in_price'], self._position.at['out_price'], self._balance['usd']))
        self._position = None

    def decide (self, tick=None, cave=None):
        if self._position is None and cave is not None:
            cave = cave.copy()
            cave = cave.drop (['out_max', 'out_min', 'prev_out_max', 'prev_out_min', 'out_10', 'max', 'max_time', 'min', 'min_time'])
            prepared_cave = pd.Series (data=[cave.at['hill_hrz_range'], cave.at['hill_vrt_range'], cave.at['hrz_range'], cave.at['in_close'], cave.at['trend1'], cave.at['trend13'], cave.at['trend2'], cave.at['trend21'], cave.at['trend3'], cave.at['trend5'], cave.at['trend8'], cave.at['vrt_range'], cave.at['volume']], index=['hill_hrz_range', 'hill_vrt_range', 'hrz_range', 'in_close', 'trend1', 'trend13', 'trend2', 'trend21', 'trend3', 'trend5', 'trend8', 'vrt_range', 'volume'])
            if self._model.predict([prepared_cave])[0] == 1:
                self.position_in (tick)
        elif self._position is not None:
            if factors.fee (self._position.at['in_price'], tick.at['close']) > 0 and tick.at[self._diff_field] < 0:
                self.position_out (tick)
            elif self._position.at['in_price'] - tick.at['close'] > 100 and tick.at[self._diff_field] < 0:
                self.position_out (tick)

    def to_csv (self):
        self._positions.to_csv ('data/positions_'+self._name+'.csv', index=True, header=True)

class Testing ():
    _traiders = []
    def __init__ (self, model=None):
        self._traiders.append ( Traider (model=model, name='model_testing') )

    def run (self):
        frame = get_frame ('data/month_prepared.csv')
        frame.loc[:, 'avg'] = frame.loc[:, 'close'].rolling (12).mean()
        frame['diff'] = frame.loc[:, 'avg'].diff()
        frame = frame.loc [frame.iloc[0].name+datetime.timedelta (minutes=60*24):,:].copy()

        edge_date = frame.iloc[frame.shape[0]-1].name

        watch_caves = frame.iloc[:2].copy()
        caves = pd.DataFrame()

        watch_hills = frame.iloc[:2].copy()
        hills = pd.DataFrame()

        frame = frame.loc[:edge_date].iloc[2:].copy()

        current_idx = 0
        for idx, tick in frame.loc[:edge_date].iloc[2:].iterrows():
            if current_idx % int(frame.shape[0] / 100) == 0:
                log_info(current_idx // int(frame.shape[0] / 100))

            if caves.shape[0] > 0:
                last_cave = caves.iloc[caves.shape[0]-1]
                if tick.at['close'] > last_cave.at['in_close'] and tick.at['close'] > last_cave.at['out_max']:
                    caves.at[last_cave.name, 'out_max'] = tick.at['close']
                if tick.at['close'] < last_cave.at['out_min']:
                    caves.at[last_cave.name, 'out_min'] = tick.at['close']
                if factors.fee (last_cave.at['in_close'], tick.at['close']) > 10:
                    caves.at[last_cave.name, 'out_10'] = 1

            watch_caves = watch_caves.append (frame.loc[tick.name])
            cave = factors.cave (watch_caves)
            current_cave = None
            if cave is not None and cave.name not in caves.index.values:
                if factors.fee(cave.at['min'], cave.at['max']) > 0:
                    cave['hill_hrz_range'] = None
                    cave['hill_vrt_range'] = None
                    cave['out_10'] = 0
                    cave['out_max'] = 0.0
                    cave['out_min'] = cave.at['min']
                    cave['prev_out_max'] = 0.0
                    cave['prev_out_min'] = 0.0
                    if hills.shape[0] > 0:
                        prev_hills = hills.loc[hills.index < cave.at['min_time']]
                        prev_hill = prev_hills.iloc[prev_hills.shape[0]-1]
                        cave.at['hill_hrz_range'] = prev_hill.at['hrz_range']
                        cave.at['hill_vrt_range'] = prev_hill.at['vrt_range']
                    if caves.shape[0] > 1:
                        cave.at['prev_out_max'] = caves.iloc[caves.shape[0]-2].at['out_max']
                        cave.at['prev_out_min'] = caves.iloc[caves.shape[0]-2].at['out_min']
                    cave['trend1'] = get_trend (frame, tick, {'minutes':60*1}).coef_[0]
                    cave['trend2'] = get_trend (frame, tick, {'minutes':60*2}).coef_[0]
                    cave['trend3'] = get_trend (frame, tick, {'minutes':60*3}).coef_[0]
                    cave['trend5'] = get_trend (frame, tick, {'minutes':60*5}).coef_[0]
                    cave['trend8'] = get_trend (frame, tick, {'minutes':60*8}).coef_[0]
                    cave['trend13'] = get_trend (frame, tick, {'minutes':60*13}).coef_[0]
                    cave['trend21'] = get_trend (frame, tick, {'minutes':60*21}).coef_[0]
                    cave['volume'] = tick.at['volume']
                    caves = caves.append (cave)
                    watch_caves = pd.DataFrame()
                    watch_caves = watch_caves.append (frame.loc[tick.name])

                    current_cave = cave
            
            if tick.at['avg'] > watch_caves.iloc[0].at['avg']:
                watch_caves = pd.DataFrame()
                watch_caves = watch_caves.append (frame.loc[tick.name])

            watch_hills = watch_hills.append (frame.loc[tick.name])
            hill = factors.hill (watch_hills)

            if hill is not None and hill.name not in hills.index.values:
                if factors.fee(hill.at['min'], hill.at['max']) > 0:
                    hills = hills.append (hill)
                    watch_hills = pd.DataFrame()
                    watch_hills = watch_hills.append (frame.loc[tick.name])
            
            if tick.at['avg'] < watch_hills.iloc[0].at['avg']:
                watch_hills = pd.DataFrame()
                watch_hills = watch_hills.append (frame.loc[tick.name])

            for traider in self._traiders:
                traider.decide (tick=tick, cave=current_cave)

            current_idx = frame.index.get_loc (tick.name) + 1

        caves.to_csv ('data/caves.csv')
        hills.to_csv ('data/hills.csv')