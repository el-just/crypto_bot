from clickhouse_driver import Client

def insert_tick (tick):
    query = '''INSERT INTO tb.ticker VALUES (toDate({timestamp}), toDateTime({timestamp}), {base}, {quot}, {close}, {volume})'''.format(
        timestamp = int(tick.at['timestamp']),
        base = tick.at['base'],
        quot = tick.at['quot'],
        close = tick.at['close'],
        volume = tick.at['volume'],
        )

    clickhouse = Client('localhost')
    clickhouse.execute (query)