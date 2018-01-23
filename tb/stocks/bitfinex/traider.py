import pandas as pd
import datetime
import time

from abstract.logging import Logging
from testing.logging import Logging as TLog
from stocks.bitfinex.defines import DEFINES
from sklearn import linear_model

class Traider (TLog):
    _ready = False
    _positions = pd.DataFrame(data=[], columns=['amount', 'type'])
    _frame = pd.DataFrame (data=[], columns=['timestamp', 'base', 'quot', 'close', 'volume'])
    _stock = None
    _profit = 0.01
    _trend_model = None
    _cross = None
    _current_tick = None

    def __init__ (self, stock=None):
        self._stock = stock

    def magic (self):
        self.update_trend ()
        self.update_diffs ()
        self.update_cross ()

        if self._current_tick.at['close'] < self._current_tick.at['trend']:
            if self._current_tick.at['avg_diff'] > 0:

        else:



        return self.check_out () if self._positions.iloc[self._positions.shape[0]-1].at['type'] == -1 else self.check_in ()

    def check_in ():
        pass
    def check_out ():
        pass

    def update_trend (self):
        clf = linear_model.LinearRegression()
        self._trend_model = clf.fit (self._frame.loc[:,'timestamp'].values.reshape(-1,1), self._frame.loc[:,'close'].values)
        self._frame['trend'] = clf.predict (self._frame.loc[:,'timestamp'].values.reshape(-1,1))

    def update_diffs (self):
        self._frame['close_diff'] = self._frame.loc[:,'close'].diff()
        self._frame['avg_diff'] = self._frame.loc[:,'avg'].diff()

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
            