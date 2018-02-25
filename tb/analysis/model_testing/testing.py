class Traider ():
    _trend_field = None
    _diff_field = None

    _balance = None

    _positions = pd.DataFrame ()
    _position = None
    _model = None

    def __init__ (self, diff_field='diff', model=None):
        self._trend_field = trend_field if trend_window is None else 'trend_custom'
        self._diff_field = diff_field
        self._trend_window = trend_window
        self._model = model

        self._balance = {
            'usd': 2000.00,
            'btc': 0.00
            }

    def position_in (self, tick, assume_range):
        self._balance['btc'] = self._balance['usd'] / tick.at['close'] - self._balance['usd'] / tick.at['close']*0.002
        self._balance['usd'] = 0.

        self._position = pd.Series (data=[tick.at['close'], tick.at['avg'], assume_range, None, None, 'single'], index=['in_price', 'in_avg', 'assume_range', 'out_price', 'out_date', 'trend_type'])
        self._position.name = tick.name

    def position_out (self, tick):
        self._balance['usd'] = tick.at['close'] * self._balance['btc'] - tick.at['close'] * self._balance['btc']*0.002
        self._balance['btc'] = 0.
        
        self._position.at['out_price'] = tick.at['close']
        self._position.at['out_date'] = tick.name
        self._positions = self._positions.append (self._position)

        log_info ('trend={0}, diff={1}, close_in={2}, close_out={3}, balance={4}'.format(self._trend_field, self._diff_field, self._position.at['in_price'], self._position.at['out_price'], self._balance['usd']))
        self._position = None

    def decide (self, current_caves=None, caves=None, hills=None, tick=None, frame=None):
        if self._position is None and self._model.predict([cave])[0] == 1:
            self.position_in (tick, assume_range)
        elif self._position is not None:
            if factors.fee (self._position.at['in_price'], tick.at['close']) > 0 and tick.at[self._diff_field] < 0:
                self.position_out (tick)
            elif tick.at['close'] / position.at['in_price'] > 1.001 and tick.at[self._diff_field] < 0:
                self.position_out (tick)

    def to_csv (self):
        self._positions.to_csv ('data/positions_'+self._trend_field+'_'+self._diff_field+'.csv', index=True, header=True)

class Testing ():