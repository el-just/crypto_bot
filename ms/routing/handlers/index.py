from aiohttp import web
from aiohttp_session import get_session
import time
import aiohttp_jinja2

class Index (web.View):
    @aiohttp_jinja2.template('index.html')
    async def get(self):
        return {'last_visit':time.time()}