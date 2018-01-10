from clickhouse_driver import Client

clickhouse = Client('localhost')

def insert_tick (tick):
	query = '''INSERT INTO tb.ticker VALUES (toDate({timestamp}), toDateTime({timestamp}), {base}, {quot}, {close}, {volume})'''.format(
		timestamp = tick.at['timestamp'],
		base = tick.at['base'],
		quot = tick.at['quot'],
		close = tick.at['close'],
		volume = tick.at['volume'],
		)

	clickhouse.execute (query)