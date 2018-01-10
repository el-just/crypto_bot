from clickhouse_driver import Client
import datetime
from settings.consts import SYMBOLS
import actions.sql as sql

clickhouse = Client('localhost')
def insert_tick (tick):
    clickhouse.execute ('''INSERT INTO tb.ticker (tick_date, tick_time, base, quot, close, volume) VALUES''', [{
        'tick_date': datetime.datetime.fromtimestamp(tick.at['timestamp']),
        'tick_time': datetime.datetime.fromtimestamp(tick.at['timestamp']),
        'base': tick.at['base'],
        'quot': tick.at['quot'],
        'close': tick.at['close'],
        'volume': tick.at['volume']
        }])

def insert_tick_frame (tick_frame):
    rows = []
    for idx, tick in tick_frame.iterrows():
        tick.append ({
            'tick_date': datetime.datetime.fromtimestamp(tick.at['timestamp']),
            'tick_time': datetime.datetime.fromtimestamp(tick.at['timestamp']),
            'base': tick.at['base'],
            'quot': tick.at['quot'],
            'close': tick.at['close'],
            'volume': tick.at['volume']
            })

    clickhouse.execute ('''INSERT INTO tb.ticker (tick_date, tick_time, base, quot, close, volume) VALUES''', rows)

def get_missing_periods (base=None, quot=None, start=None, end=None):
    available_data = clickhouse.execute (sql.missing_data_periods.format (base=base, quot=quot, start=start, end=end))

    periods = []
    if len (available_data) > 0:
        if time.mktime(available_data[0][0].timetuple()) - start > 600:
            periods.append ({'start': start, 'end': time.mktime(available_data[0][0].timetuple())})

        for idx in range(2,len(available_data)):
            period_start = time.mktime(available_data[idx][0].timetuple()) - int(available_data[idx][3])
            period_end = time.mktime(available_data[idx][0].timetuple())

            periods.append ({'start':period_start, 'end':period_end-60})
        
        if end - time.mktime(available_data[1][0].timetuple()) > 600:
            periods.append ({'start': time.mktime(available_data[1][0].timetuple()), 'end': end})
    else:
        periods.append ({'start': start, 'end': end})

    return periods
