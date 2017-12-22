import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn import linear_model, datasets

frame = pd.read_csv ('./data/BTC_USD_20171121.d')
#frame['timestamp'] = pd.to_datetime (frame['timestamp'], unit='s')
#frame.set_index ('timestamp', inplace=True)

diabetes = datasets.load_diabetes()


# Use only one feature
diabetes_X = diabetes.data[:, np.newaxis, 2]

# Split the data into training/testing sets
diabetes_X_train = diabetes_X[:-20]
diabetes_X_test = diabetes_X[-20:]

# Split the targets into training/testing sets
diabetes_y_train = diabetes.target[:-20]
diabetes_y_test = diabetes.target[-20:]

frame['weighted_avg'] = frame["close"].ewm(com=10).mean()
frame['diff'] = frame['weighted_avg'].diff()

#frame['weighted_avg'].plot(figsize=(12,8))
#frame['diff'].plot(figsize=(12,8))
#plt.show()

#print (frame['timestamp'].values.reshape(-1,1))

clf = linear_model.LinearRegression()
clf.fit (frame['timestamp'].values.reshape(-1,1), frame['weighted_avg'].values)
frame['line'] = pd.Series (clf.predict (frame['timestamp'].values.reshape(-1,1)))
# y = clf.coef_ * x
print (clf.coef_)

frame[['weighted_avg', 'line']].plot(figsize=(12,8))
plt.show()

'''

N = 3
frame['close_avg'] = frame[['close']].shift().rolling(N, min_periods=1).mean()
frame['timestamp'] = pd.to_datetime (frame['timestamp'], unit='s')

frame.set_index ('timestamp', inplace=True)
frame['MA7'] = frame['close_avg'].rolling(window='2400s', center=False).mean()


print (frame['MA7'])

'''