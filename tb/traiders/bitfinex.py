from clickhouse.clickhouse import insert_tick_frame

class Traider ():
    def __init__ (self, channel):
        self._channel = channel

    def open (self):
        end_timestamp = time.mktime(datetime.datetime.now().timetuple())
        start_timestamp = time.mktime(datetime.datetime.now() - datetime.timedelta (days=90))

        missing_periods = get_missing_periods (base=self._channel.at['base'], quot=self._channel.at['quot'], start=start_timestamp, end=end_timestamp)

        for period in periods:
            print (period)