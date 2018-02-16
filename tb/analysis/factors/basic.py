import pandas as pd

cave_window = {'minutes':90}
cave_proportion = 2.618

def fee (price_in, price_out):
    fee = 0.002

    return (price_out - price_in) - fee * (price_in + price_out)

def cave (frame):
    cave = None

    maximum = frame.loc[frame.loc[:, 'avg'] == frame.loc[:,'avg'].max()].iloc[0]

    minimum = frame.loc[frame.loc[:, 'avg'] == frame.loc[:,'avg'].min()]
    minimum = minimum.iloc[minimum.shape[0]-1]
    
    if frame.iloc[frame.shape[0]-1].at['avg'] > minimum.at['avg']:
        if minimum.name > maximum.name:
            if frame.iloc[frame.shape[0]-1].at['avg'] - minimum.at['avg'] >= (maximum.at['avg'] - minimum.at['avg']) / cave_proportion:
                cave = minimum

    return cave

def hill (frame, column='avg', proportion=2.618*1.618):
    hill = None
    maximum = frame.loc[frame.loc[:, column] == frame.loc[:,column].max()]
    maximum = maximum.iloc[maximum.shape[0]-1]

    minimum = frame.loc[frame.loc[:, column] == frame.loc[:,column].min()].iloc[0]

    if frame.iloc[frame.shape[0]-1].at[column] < maximum.at[column]:
        if maximum.name > minimum.name:
            if maximum.at[column] - frame.iloc[frame.shape[0]-1].at[column] >= (maximum.at[column] - minimum.at[column]) / proportion:
                hill = maximum

    return hill

def predict_out (watch_cave):
    maximum = watch_cave.loc[watch_cave.loc[:, 'avg'] == watch_cave.loc[:,'avg'].max()].iloc[0]

    minimum = watch_cave.loc[watch_cave.loc[:, 'avg'] == watch_cave.loc[:,'avg'].min()]
    minimum = minimum.iloc[minimum.shape[0]-1]

    current = watch_cave.iloc[watch_cave.shape[0]-1]

    predicted_timestamp = minimum['timestamp'] + (minimum.at['timestamp'] - maximum['timestamp'])

    maximum_trend = maximum.at['timestamp'] * current.at['trend_coef'] + current.at['trend_intercept']
    predict_trend = predicted_timestamp * current.at['trend_coef'] + current.at['trend_intercept']

    predicted_price = maximum.at['avg'] + (predict_trend - maximum_trend)
    
    return pd.Series (data=[predicted_timestamp, predicted_timestamp - maximum['timestamp'], predicted_price, predicted_price - minimum.at['avg']], index=['timestamp', 'gap', 'price', 'range'])

def shape_proportion (predict):
    e_gap = 60*60*3
    e_range = 618
    
    return (predict.at['range'] / e_range) / (predict.at['gap'] / e_gap)



timestamp = [26280, 13920, 16200, 5166, 1858, 20518, 4680, 10500]
price = [664, 269, 218, 224, 139, 815, 407, 559]

for i in range (0, len(timestamp)):
    print (price[i] / timestamp[i])

print ('==============')

timestamp = [14400, 25320, 4320, 2902]
price = [190, 221, 218, 184]

for i in range (0, len(timestamp)):
    print (price[i] / timestamp[i])