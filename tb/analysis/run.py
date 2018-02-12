import os
import time
import datetime

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import methods.mvag as mvag
import methods.extremums as extremums
import factors.basic as factors

frame = pd.read_csv ('data/month.csv', dtype={'close':np.float64, 'volume':np.float64})
frame.loc[:, 'tick_time'] = pd.to_datetime(frame.loc[:, 'tick_time'])
frame = frame.set_index (pd.to_datetime(frame.loc[:, 'tick_time']).values)
frame['timestamp'] = frame.loc[:, 'tick_time'].apply (lambda tick_time: time.mktime (tick_time.timetuple()))
frame = frame.loc[datetime.datetime(2018, 1, 17, 0, 0):datetime.datetime(2018, 2, 9, 0, 0)]

frame['avg'] = frame.loc[:,'close'].rolling (62).mean()

frame = frame.loc[frame.iloc[0].name:frame.iloc[0].name+datetime.timedelta(minutes=60*48)]

watch_cave = frame.iloc[62:64].copy()
watch_hill = frame.iloc[62:64].copy()
caves = pd.DataFrame()
hills = pd.DataFrame()
current_idx = 64
current_cave = None
current_hill = None
for idx, tick in frame.iloc[64:].iterrows():
    if current_idx % int(frame.shape[0] / 100) == 0:
        print(current_idx // int(frame.shape[0] / 100))
    
    watch_cave = watch_cave.append (tick)
    cave = factors.cave (watch_cave)
    if cave is not None:
        caves = caves.append (cave)
        watch_cave = pd.DataFrame()
        watch_cave = watch_cave.append (tick)
    if tick.at['avg'] > watch_cave.iloc[0].at['avg']:
        watch_cave = pd.DataFrame()
        watch_cave = watch_cave.append (tick)

    watch_hill = watch_hill.append (tick)
    hill = factors.hill (watch_hill)
    if hill is not None:
        hills = hills.append (hill)
        watch_hill = pd.DataFrame()
        watch_hill = watch_hill.append (tick)

    if tick.at['avg'] < watch_hill.iloc[0].at['avg']:
        watch_hill = pd.DataFrame()
        watch_hill = watch_hill.append (tick)

    current_idx += 1
frame.loc[ : , ['close', 'avg']].plot(figsize=(12,8))
plt.plot (caves.index, caves.loc[:,'avg'], 'm*')
plt.plot (hills.index, hills.loc[:,'avg'], 'g*')
plt.show()