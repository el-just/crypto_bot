import http.client
import urllib.parse
import pandas as pd

def create_table ():
    pass

def process_query (request):
    data = None

    connect = http.client.HTTPConnection('localhost', 8123)
    response = connect.putrequest('GET', '/?'+urllib.parse.urlencode({'query':request}))
    connect.endheaders() 
    response = connect.getresponse ()

    if response is not None:
        data = pd.read_csv (response, header=None)

    return data

def insert_tick (tick):
	query = '''INSERT INTO tb.ticker VALUES (toDate({timestamp}), toDateTime({timestamp}), {base}, {quot}, {close}, {volume})'''.format(
		timestamp = tick.at['timestamp'],
		base = tick.at['base'],
		quot = tick.at['quot'],
		close = tick.at['close'],
		volume = tick.at['volume'],
		)

	process_query (query)

