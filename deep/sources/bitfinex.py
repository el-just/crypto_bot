import pandas as pd
import http.client
import urllib.parse
import asyncio
from time import sleep

# CHANNEL_ID  integer Channel ID
# BID float   Price of last highest bid
# BID_SIZE    float   Size of the last highest bid
# ASK float   Price of last lowest ask
# ASK_SIZE    float   Size of the last lowest ask
# DAILY_CHANGE    float   Amount that the last price has changed since yesterday
# DAILY_CHANGE_PERC   float   Amount that the price has changed expressed in percentage terms
# LAST_PRICE  float   Price of the last trade.
# VOLUME  float   Daily volume
# HIGH    float   Daily high
# LOW float   Daily low

def get_ticker (start=None, end=None):
    columns = ['tick_time', 'open', 'close', 'high', 'low', 'volume']
    frame = pd.DataFrame (data=[], columns=columns)

    current_end = end
    if end - start > 59940000:
        current_end = start + 59940000

    while current_end <= end:
        params = {'limit':1000, 'start':start, 'end':current_end}
        
        connect = http.client.HTTPSConnection('api.bitfinex.com', 443)
        response = connect.putrequest('GET', '/v2/candles/trade:1m:tBTCUSD/hist?'+urllib.parse.urlencode(params))
        
        connect.endheaders() 
        response = connect.getresponse ()

        response = response.read().decode('utf8') if response is not None else None
        connect.close()

        data = [item.split (',') for item in response[2:-2].split('],[')]
        data = pd.DataFrame (data=data, columns=columns)

        frame = pd.concat ([frame, data])

        start = current_end + 60000
        current_end = start + 59940000

        sleep (5)

    return frame

print(get_ticker (start=1512086400000, end=1512678400000).shape)
