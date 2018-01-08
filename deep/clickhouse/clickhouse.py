import http.client
import urllib.parse
import pandas as pd

def create_table ():
    pass

def query (request):
    data = None

    connect = http.client.HTTPConnection('localhost', 8123)
    response = connect.putrequest('GET', '/?'+urllib.parse.urlencode({'query':request}))
    connect.endheaders() 
    response = connect.getresponse ()

    if response is not None:
        data = pd.read_csv (response, header=None)

    return data