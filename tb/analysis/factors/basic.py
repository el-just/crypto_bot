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

def hill (frame):
    hill = None
    maximum = frame.loc[frame.loc[:, 'avg'] == frame.loc[:,'avg'].max()]
    maximum = maximum.iloc[maximum.shape[0]-1]

    minimum = frame.loc[frame.loc[:, 'avg'] == frame.loc[:,'avg'].min()].iloc[0]

    if frame.iloc[frame.shape[0]-1].at['avg'] < maximum.at['avg']:
        if maximum.name > minimum.name:
            if maximum.at['avg'] - frame.iloc[frame.shape[0]-1].at['avg'] >= (maximum.at['avg'] - minimum.at['avg']) / cave_proportion:
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