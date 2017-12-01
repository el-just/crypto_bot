import pandas as pd
import matplotlib.pyplot as plt

frame = pd.read_csv ('./data/BTC_USD_20171121.d')

N = 3
frame['close_avg'] = frame[['close']].shift().rolling(N, min_periods=1).mean()
frame['timestamp'] = pd.to_datetime (frame['timestamp'], unit='s')

#frame.set_index ('timestamp', inplace=True)


#---line
#plt.plot(frame['timestamp'], frame['close_avg'], '-')
#plt.show()

#---bar
#plt.bar(frame.index, frame['volume'])
#plt.gcf().set_size_inches(12,6)
#plt.show()

#---line + bar
# top = plt.subplot2grid((4,4), (0, 0), rowspan=3, colspan=4)
# top.plot(frame.index, frame['close_avg'], label='Close Avarage')
# plt.title('BTC_USD_20171121')
# plt.legend(loc=2)
# bottom = plt.subplot2grid((4,4), (3,0), rowspan=1, colspan=4)
# bottom.bar(frame.index, frame['volume'])
# plt.title('Volume')
# plt.gcf().set_size_inches(12,8)
# plt.subplots_adjust(hspace=0.75)
# plt.show()

#print (frame.head())
