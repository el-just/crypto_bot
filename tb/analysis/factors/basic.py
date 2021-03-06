import time
import pandas as pd

cave_window = {'minutes':90}
cave_proportion = 2.618

def fee (price_in, price_out):
    fee = 0.002

    return (price_out - price_in) - fee * (price_in + price_out)

def cave (frame, proportion=1/2.618/2.618):
    cave = None

    maximum = frame.loc[frame.loc[:, 'avg'] == frame.loc[:,'avg'].max()].iloc[0]

    minimum = frame.loc[frame.loc[:, 'avg'] == frame.loc[:,'avg'].min()]
    minimum = minimum.iloc[minimum.shape[0]-1]
    
    if frame.iloc[frame.shape[0]-1].at['avg'] > minimum.at['avg']:
        if minimum.name > maximum.name:
            if frame.iloc[frame.shape[0]-1].at['avg'] - minimum.at['avg'] >= (maximum.at['avg'] - minimum.at['avg']) * proportion:
                cave = pd.Series (
                    data=[
                        minimum.name,
                        maximum.name,
                        minimum.at['avg'],
                        maximum.at['avg'],
                        time.mktime(minimum.name.timetuple())-time.mktime(maximum.name.timetuple()),
                        maximum.at['avg']-minimum.at['avg'],
                        frame.iloc[frame.shape[0]-1].at['close']],
                    index=[
                        'min_time',
                        'max_time',
                        'min',
                        'max',
                        'hrz_range',
                        'vrt_range',
                        'in_close']
                    )
                cave.name = frame.iloc[frame.shape[0]-1].name

    return cave

def hill (frame, column='avg', proportion=1/2.618/2.618):
    hill = None
    maximum = frame.loc[frame.loc[:, column] == frame.loc[:,column].max()]
    maximum = maximum.iloc[maximum.shape[0]-1]

    minimum = frame.loc[frame.loc[:, column] == frame.loc[:,column].min()].iloc[0]

    if frame.iloc[frame.shape[0]-1].at[column] < maximum.at[column]:
        if maximum.name > minimum.name:
            if maximum.at[column] - frame.iloc[frame.shape[0]-1].at[column] >= (maximum.at[column] - minimum.at[column]) * proportion:
                hill = pd.Series (
                    data=[
                        minimum.name,
                        maximum.name,
                        minimum.at['avg'],
                        maximum.at['avg'],
                        time.mktime(maximum.name.timetuple())-time.mktime(minimum.name.timetuple()),
                        maximum.at['avg']-minimum.at['avg'],
                        frame.iloc[frame.shape[0]-1].at['close']],
                    index=[
                        'min_time',
                        'max_time',
                        'min',
                        'max',
                        'hrz_range',
                        'vrt_range',
                        'in_close']
                    )
                hill.name = frame.iloc[frame.shape[0]-1].name

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