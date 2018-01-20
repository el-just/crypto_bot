import http.client
import json

import pandas as pd
import matplotlib.pyplot as plt
from sklearn import linear_model

class Test ():
    def __init__ (self):
        pass

    def get_plot (self, _type):
        frame = pd.read_csv ('../data/BTC_USD_20171121.d')
        #frame['timestamp'] = pd.to_datetime (frame['timestamp'], unit='s')
        #frame.set_index ('timestamp', inplace=True)

        if _type == 'simple':
            frame['close'].plot(figsize=(12,8))
        elif _type == 'wavg':
            frame['weighted_avg'] = frame["close"].ewm(com=10).mean()

            frame['weighted_avg'].plot(figsize=(12,8))
        elif _type == 'wavg+':
            frame['weighted_avg'] = frame["close"].ewm(com=10).mean()
            clf = linear_model.LinearRegression()
            clf.fit (frame['timestamp'].values.reshape(-1,1), frame['weighted_avg'].values)
            frame['line'] = pd.Series (clf.predict (frame['timestamp'].values.reshape(-1,1)))

            frame[['weighted_avg', 'line']].plot(figsize=(12,8))
        elif _type == 'diff':
            frame['diff'] = frame['weighted_avg'].diff()
            frame['diff'].plot(figsize=(12,8))
        elif _type == 'bar':
            plt.bar(frame.index, frame['volume'])
            plt.gcf().set_size_inches(12,6)
        elif _type == 'line+bar':
            top = plt.subplot2grid((4,4), (0, 0), rowspan=3, colspan=4)
            top.plot(frame.index, frame['close_avg'], label='Close Avarage')
            plt.title('BTC_USD_20171121')
            plt.legend(loc=2)
            bottom = plt.subplot2grid((4,4), (3,0), rowspan=1, colspan=4)
            bottom.bar(frame.index, frame['volume'])
            plt.title('Volume')
            plt.gcf().set_size_inches(12,8)
            plt.subplots_adjust(hspace=0.75)

        plt.show()

    #for tick in list(Test().listen()):
    def listen (self):
        frame = pd.read_csv ('./data/BTC_USD_20171121.d')
        frame['timestamp'] = pd.to_datetime (frame['timestamp'], unit='s')
        frame.set_index ('timestamp', inplace=True)
        frame['diff'] = None
        
        for index in range(frame.shape[0]):
            yield frame.iloc [index]

Test().get_plot ('wavg+')