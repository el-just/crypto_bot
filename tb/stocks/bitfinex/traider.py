import pandas as pd
import datetime
import time

from abstract.logging import Logging
from testing.logging import Logging as TLog
from stocks.bitfinex.defines import DEFINES
from sklearn import linear_model
from scipy.signal import argrelextrema

class Traider (TLog):
    _ready = False
    _positions = pd.DataFrame(data=[], columns=['amount', 'type'])
    _frame = pd.DataFrame (data=[], columns=['timestamp', 'base', 'quot', 'close', 'volume'])
    _stock = None
    _profit = 0.01
    _trend_model = None
    _cross = None
    _current_tick = None
    _stop_range = None

    def __init__ (self, stock=None):
        self._stock = stock

    def magic (self):
        self.update_trend ()
        self.update_avg ()
        self.update_avg_diff ()
        self.update_stop_range ()

        if self._positions.iloc[self._positions.shape[0]-1].at['type'] == -1:
            position = self._positions.iloc[self._positions.shape[0]-1]


        else:
            if self._trend_model.coef_ > 0:
                if self._current_tick.at['close'] < self._current_tick.at['trend']:
                    if self._current_tick.at['diff'] > 0:
                        (self._current_tick.at['close'] + self._stop_range*2) - (self._current_tick.at['close'] + self._stop_range*2)*0.02 - self._current_tick.at['close']*0.02 > 0:
                            self.position_in ()

    @staticmethod
    def holt_winters_second_order_ewma (x):
        span = 10
        beta = 0.3

        N = x.size
        alpha = 2.0 / ( 1 + span )
        s = np.zeros(( N, ))
        b = np.zeros(( N, ))
        s[0] = x[0]
        for i in range( 1, N ):
            s[i] = alpha * x[i] + ( 1 - alpha )*( s[i-1] + b[i-1] )
            b[i] = beta * ( s[i] - s[i-1] ) + ( 1 - beta ) * b[i-1]

        return s

    @staticmethod
    def invert_local_mins (tick, avg_min):
        avg = tick.at['avg'] - avg_min
        trend = tick.at['trend'] - avg_min

        return trend - avg if avg < trend else avg - trend

    def update_stop_range (self):
        inverted_avg = self._frame.apply (invert_local_mins, axis=1, params=[self._frame.loc[:,'avg'].min()])
        self._stop_range = self.holt_winters_second_order_ewma(argrelextrema(inverted_avg.values, np.greater)[0][1:-1]).pop()
        
        #diff = extremums_avg.diff()
        #extremums_avg = extremums_avg.pop()
        #self._stop_range = [extremums_avg-diff, extremums_avg+diff]

    def update_trend (self):
        clf = linear_model.LinearRegression()
        self._trend_model = clf.fit (self._frame.loc[:,'timestamp'].values.reshape(-1,1), self._frame.loc[:,'close'].values)
        self._frame['trend'] = clf.predict (self._frame.loc[:,'timestamp'].values.reshape(-1,1))

    def update_avg (self):
        self._frame['avg'] = self.holt_winters_second_order_ewma(self._frame.loc[:, 'close'].values)

    def update_avg_diff (self):
        self._frame['avg_diff'] = self._frame.loc[:, 'avg'].diff()

        last_series = self._frame.iloc[self._frame.shape[0]-1]
        last_series.at['avg_diff'] = self._frame.iloc[self._frame.shape[0]-3].at['avg_diff']

        self._frame.iloc[self._frame.shape[0]-1] = last_series

    def update_cross (self):
        if self._current_tick.at['trend'] == self._current_tick.at['avg']:
            self._cross = self._current_tick
        elif self._current_tick.at['avg'] < self._current_tick.at['trend']:
            prev_tick = self._frame.iloc[self._frame.index.get_loc(self._current_tick.name) - 1]
            if prev_tick.at['avg'] > prev_tick.at['trend']:
                self._cross = self._current_tick
        elif self._current_tick.at['avg'] > self._current_tick.at['trend']:
            prev_tick = self._frame.iloc[self._frame.index.get_loc(self._current_tick.name) - 1]
            if prev_tick.at['avg'] < prev_tick.at['trend']:
                self._cross = self._current_tick    
        
    async def position_in (self):
        try:
            if self._stock._balance.at['usd'] > 0:
                position = pd.Series (data=[self._stock._balance.at['usd'], -1], index=['amount', 'type'])
                position.name = datetime.datetime.now()
                self._positions.append (position)
                self._stock._balance.at['btc'] = self._stock._balance.at['usd'] / self._frame.iloc[self._frame.shape[0]-1].at['close']
                self._stock._balance.at['usd'] = 0
        except Exception as e:
            self.log_error (e)

    async def position_out (self):
        try:
            if self._stock._balance.at['btc'] > 0:
                position = pd.Series (data=[self._stock._balance.at['btc'] * self._frame.iloc[self._frame.shape[0]-1].at['close'], 1], index=['amount', 'type'])
                position.name = datetime.datetime.now()
                self._positions.append (position)
                self._stock._balance.at['usd'] = self._stock._balance.at['btc'] * self._frame.iloc[self._frame.shape[0]-1].at['close']
                self._stock._balance.at['btc'] = 0
        except Exception as e:
            self.log_error (e)

    async def run (self):
        try:
            now = datetime.datetime.now()
            missing_periods = await self._stock._storage.get_missing_periods ({
                'start':time.mktime((now - datetime.timedelta (days=DEFINES.REQUIRED_PERIOD)).timetuple()),
                'end': time.mktime(now.timetuple())
                })

            self.log_info ('Missing periods:\n\t{0}'.format(str(missing_periods)))
            for period in missing_periods:
                tick_period = await self._stock._rest_socket.get_tick_period (period)
                self._frame = self._frame.append (tick_period)
            self._ready = True
        except Exception as e:
            self.log_error (e)

    async def resolve (self, tick):
        try:
            self._frame = self._frame.append (tick)
            self._current_tick = self._frame.iloc[self._frame.shape[0]-1]
            self._frame = self._frame.loc[self._frame.iloc[self._frame.shape[0]-1].name - datetime.timedelta(minutes=30) : self._frame.iloc[self._frame.shape[0]-1].name]
            if self._ready:
                if self.magic () == True:
                    await self.position_in ()
                elif self.magic () == False:
                    await self.position_out ()
        except Exception as e:
            self.log_error (e)
            