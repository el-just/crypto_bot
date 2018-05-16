import pandas as pd

from aiohttp import web
import aiohttp_jinja2

class Index (web.View):
    @aiohttp_jinja2.template('index.html')
    async def get(self):
        
        exchanges = pd.DataFrame(
                data=[{'10', '11', '12'}, {'10', '11', '12'}, {'10', '11', '12'}],
                columns=['bitfinex', 'binance', 'bittrex'],
                index=['BTC', 'XRP', 'NEO'],)
        return {
                'sample':(''
                    + '{'
                    + '    "action":"binance.get_markets",'
                    + '    "payload":[]'
                    + '}'),
                'exchanges': exchanges,}
