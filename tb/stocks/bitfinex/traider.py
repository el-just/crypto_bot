import pandas as pd
import numpy as np
import datetime
import time

from abstract.logging import Logging
from testing.logging import Logging as TLog
from stocks.bitfinex.defines import DEFINES
from sklearn import linear_model
from scipy.signal import argrelextrema

class Traider (Logging):
    _ready = False
    _position = None
    _frame = pd.DataFrame (data=[], columns=['timestamp', 'base', 'quot', 'close', 'volume'])
    _stock = None
    _profit = 0.01
    _trend_model = None
    _cross = None
    _current_tick = None
    _stop_range = None

    def set_stock (self, stock):
        self._stock = stock

    async def magic (self):
        try:
            self.update_avg ()
            self.update_avg_diff ()

            if self._position is not None:
                if self._frame.iloc[self._frame.shape[0]-1].at['avg_diff'] < 0 and self._frame.iloc[self._frame.shape[0]-1].at['avg'] >= self._position.at['price'] + self._position.at['stop_range']*1.618:
                    await self.position_out (self._frame.iloc[self._frame.shape[0]-1])
                elif self._frame.iloc[self._frame.shape[0]-1].at['avg_diff'] < 0 and self._frame.iloc[self._frame.shape[0]-1].at['avg'] / self._position.at['price'] <= 1.01:
                    await self.position_out (self._frame.iloc[self._frame.shape[0]-1])
                elif self._frame.iloc[self._frame.shape[0]-1].at['avg'] / self._position.at['price'] <= 0.99:
                    await self.position_out (self._frame.iloc[self._frame.shape[0]-1])                
            else:
                self.update_trend ()
                self.update_stop_range ()
                if self._trend_model.coef_ > 0:
                    if self._frame.iloc[self._frame.shape[0]-1].at['close'] < self._frame.iloc[self._frame.shape[0]-1].at['trend']:
                        if self._frame.iloc[self._frame.shape[0]-1].at['avg_diff'] > 0:
                            if (self._frame.iloc[self._frame.shape[0]-1].at['close'] + self._stop_range*1.618) - (self._frame.iloc[self._frame.shape[0]-1].at['close'] + self._stop_range*1.618)*0.02 - self._frame.iloc[self._frame.shape[0]-1].at['close']*0.02 > 0:
                                self.log_info (self._frame.iloc[self._frame.shape[0]-1].at['close'])
                                await self.position_in (self._frame.iloc[self._frame.shape[0]-1])
        except Exception as e:
            self.log_error (e)

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
        inverted_avg = self._frame.apply (self.invert_local_mins, axis=1, args=[self._frame.loc[:,'avg'].min()])
        self._stop_range = self.holt_winters_second_order_ewma(argrelextrema(inverted_avg.values, np.greater)[0][1:-1])[-1]

    def update_trend (self):
        clf = linear_model.LinearRegression()
        self._trend_model = clf.fit (self._frame.loc[:,'timestamp'].values.reshape(-1,1), self._frame.loc[:,'close'].values)
        self._frame['trend'] = clf.predict (self._frame.loc[:,'timestamp'].values.reshape(-1,1))

    def update_avg (self):
        self._frame['avg'] = self.holt_winters_second_order_ewma(self._frame.loc[:, 'close'].values)

    def update_avg_diff (self):
        self._frame['avg_diff'] = self._frame.loc[:, 'avg'].diff()
        
    async def position_in (self, current_tick):
        try:
            if self._stock._balance.at['usd'] > 0:
                self._position = pd.Series (data=[current_tick.at['close'], self._stop_range], index=['price', 'stop_range'])
                self._position.name = datetime.datetime.now()

                self._stock._balance.at['btc'] = self._stock._balance.at['usd'] / current_tick.at['close']
                self._stock._balance.at['usd'] = 0

                self.log_info (self._stock._balance)
                self.log_info (current_tick.name)
        except Exception as e:
            self.log_error (e)

    async def position_out (self, current_tick):
        try:
            self.log_info ('try out')
            if self._stock._balance.at['btc'] > 0:
                self._position = None
                self._stock._balance.at['usd'] = self._stock._balance.at['btc'] * current_tick.at['close']
                self._stock._balance.at['btc'] = 0

                self.log_info (self._stock._balance)
                self.log_info (self._frame.iloc[self._frame.shape[0]-1].name)
        except Exception as e:
            self.log_error (e)

    await 

    async def run (self):
        try:
            now = datetime.datetime.now()
            period = {
                'start':time.mktime((now - datetime.timedelta (minutes=90)).timetuple()),
                'end': time.mktime(now.timetuple())
                }
            

            #TODO: actions for rest socket on miss data


            missing_periods = await self._stock._storage.get_missing_periods (period)

            if len(missing_periods) > 0:
                self.log_info ('Missing periods:\n\t{0}'.format(str(missing_periods)))
                for miss in missing_periods:
                    tick_period = await self._stock._rest_socket.get_tick_period (miss)
                    self._frame = self._frame.append (tick_period)
            else:
                self._frame = await self._storage.get_tick_frame (period)
            self._ready = True
        except Exception as e:
            self.log_error (e)

    async def resolve (self, tick):
        try:
            self._frame = self._frame.append (tick)
            if self._position is not None:
                self._frame = self._frame.loc[self._frame.iloc[self._frame.shape[0]-1].name-datetime.timedelta(minutes=90):]
            if self._ready:
                await self.magic ()
        except Exception as e:
            self.log_error (e)
            