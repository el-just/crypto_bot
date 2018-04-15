from aiohttp import web
import aiohttp_jinja2

class Index (web.View):
    @aiohttp_jinja2.template('index.html')
    async def get(self):
        return {"sample":(''
                + '{'
                + '    "type":"action",'
                + '    "data":{'
                + '        "path":"binance.get_markets",'
                + '        "payload":[]'
                + '    }'
                + '}')}
