from clickhouse_driver import Client
import datetime

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