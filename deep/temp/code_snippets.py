import http.client
import json

import pandas as pd
import matplotlib.pyplot as plt
from sklearn import linear_model

class Test ():
    def __init__ (self):
        pass

    def get_data (self):
        for date in range (1,32):
            day = str(date) if date > 9 else '0'+str(date)
            connect = http.client.HTTPSConnection('cex.io', 443)
            connect.putrequest('GET', '/api/ohlcv/hd/201710'+day+'/BTC/USD')
            connect.endheaders() 
            response = connect.getresponse ()

            data = json.loads (response.read().decode('utf8'))

            f = open ('./data/BTC_USD_201710'+day+'.d', 'w+')
            f.write ((',').join (['timestamp', 'open', 'high', 'low', 'close', 'volume'])+'\n')
            for frame in json.loads(data['data1m']):
                f.write ((',').join ([str(fr) for fr in frame])+'\n')
            f.close ()

    def get_plot (self, _type):
        frame = pd.read_csv ('../data/BTC_USD_20171121.d')
        frame['timestamp'] = pd.to_datetime (frame['timestamp'], unit='s')
        frame.set_index ('timestamp', inplace=True)

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

test_source = Test()
test_source.get_plot ('simple')