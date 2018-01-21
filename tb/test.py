import asyncio
from testing.stock import Stock
import traceback
import pandas as pd
import datetime
import matplotlib.pyplot as plt
from sklearn import linear_model

def weighted_std (tick, frame):

    return tick.at['close'] * frame.index.get_loc(tick.name) / frame.shape[0] if frame.index.get_loc(tick.name) != 0 else tick.at['close']

# try:
#     loop = asyncio.get_event_loop()
#     loop.run_until_complete(Stock().run())
#     loop.close()
# except Exception as e:
#     print (e)
#     print (str(traceback.format_exc()))

frame = pd.read_csv ('testing/day.csv')
frame.loc[:, 'tick_time'] = pd.to_datetime(frame.loc[:, 'tick_time']).astype(int)
frame['timestamp'] = (frame.loc[:, 'tick_time'] / 1000000000).astype(int)
frame = frame.set_index (pd.to_datetime(frame.loc[:, 'tick_time']).values)
frame = frame.iloc[::-1]
frame = frame.loc[frame.iloc[0].name : frame.iloc[0].name + datetime.timedelta(minutes=30)]

frame.loc[:, 'close'] = frame.loc[:, 'close'] - frame.loc[:,'close'].min()
frame['avg'] = frame.apply (weighted_std, args=[frame], axis=1)
print (frame['avg'])
clf = linear_model.LinearRegression()
clf.fit ((frame.loc[:,'timestamp']-frame.loc[:,'timestamp'].min()).values.reshape(-1,1), frame['close'].values)
frame['trend'] = clf.predict ((frame.loc[:,'timestamp']-frame.loc[:,'timestamp'].min()).values.reshape(-1,1))
frame[['close', 'trend', 'avg']].plot(figsize=(12,8))

clf.coef_

plt.show()