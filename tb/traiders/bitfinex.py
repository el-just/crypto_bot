from clickhouse.clickhouse import insert_tick_frame

class Traider ():
    _ready = False

    def __init__ (self, channel):
        self._channel = channel

    def is_ready (self):
        end_timestamp = time.mktime(datetime.datetime.now().timetuple())
        start_timestamp = time.mktime(datetime.datetime.now() - datetime.timedelta (days=90))

        missing_periods = get_missing_periods (base=self._channel.at['base'], quot=self._channel.at['quot'], start=start_timestamp, end=end_timestamp)

        for period in periods:
            stock_data = self.get_stock_data (period)
            self.save_stock_data (stock_data)

    def open (self):
        self._ready = self.is_ready ()
