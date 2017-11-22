import http.client
import json

for date in range (1,22):
    day = str(date) if date > 9 else '0'+str(date)
    connect = http.client.HTTPSConnection('cex.io', 443)
    connect.putrequest('GET', '/api/ohlcv/hd/201711'+day+'/BTC/USD')
    connect.endheaders() 
    response = connect.getresponse ()

    data = json.loads (response.read().decode('utf8'))

    f = open ('./data/BTC_USD_201711'+day+'.d', 'w+')
    f.write ((', ').join (['timestamp', 'open', 'high', 'low', 'close', 'volume'])+'\n')
    for frame in json.loads(data['data1m']):
        f.write ((', ').join ([str(fr) for fr in frame])+'\n')
    f.close ()